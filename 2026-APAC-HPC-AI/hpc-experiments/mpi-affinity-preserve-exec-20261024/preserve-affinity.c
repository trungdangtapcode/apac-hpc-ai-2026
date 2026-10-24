#define _GNU_SOURCE

#ifdef APAC_TESTING
#define sched_getaffinity apac_test_sched_getaffinity
#define sched_setaffinity apac_test_sched_setaffinity
#endif

#include <mpi.h>
#include <sched.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifdef APAC_TESTING
extern int apac_test_sched_getaffinity(pid_t, size_t, cpu_set_t *);
extern int apac_test_sched_setaffinity(pid_t, size_t, const cpu_set_t *);
#endif

#define APAC_ABORT_CODE 86
#define DIAG_CAPACITY 4096
#define MASK_CAPACITY 768

static _Thread_local unsigned int wrapper_depth;

typedef int (*init_fn)(int *, char ***);
typedef int (*init_thread_fn)(int *, char ***, int, int *);

static size_t mask_count(const cpu_set_t *mask)
{
    size_t count = 0;
    int cpu;
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu)
        if (CPU_ISSET(cpu, mask)) ++count;
    return count;
}

static void mask_text(const cpu_set_t *mask, char *buffer, size_t capacity,
                      int *truncated)
{
    size_t used = 0;
    int cpu, first = 1;
    *truncated = 0;
    if (!capacity) return;
    buffer[0] = '\0';
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        int written;
        if (!CPU_ISSET(cpu, mask)) continue;
        written = snprintf(buffer + used, capacity - used, "%s%d",
                           first ? "" : ",", cpu);
        if (written < 0 || (size_t)written >= capacity - used) {
            *truncated = 1;
            buffer[capacity - 1] = '\0';
            return;
        }
        used += (size_t)written;
        first = 0;
    }
}

static int parse_launch_cpu(int *cpu)
{
    const char *value = getenv("APAC_LAUNCH_CPU");
    char *end = NULL;
    long parsed;
    if (!value || !*value) return -1;
    for (const char *p = value; *p; ++p)
        if (*p < '0' || *p > '9') return -1;
    errno = 0;
    parsed = strtol(value, &end, 10);
    if (errno || !end || *end || parsed < 0 || parsed >= CPU_SETSIZE) return -1;
    *cpu = (int)parsed;
    return 0;
}

static void emit_preinit_error(const char *reason)
{
    char line[512];
    const char *pmi = getenv("PMI_RANK");
    char pmi_json[32] = "null";
    int valid_pmi = pmi && *pmi;
    if (valid_pmi) {
        for (const char *p = pmi; *p; ++p)
            if (*p < '0' || *p > '9') valid_pmi = 0;
    }
    if (valid_pmi && strlen(pmi) < sizeof(pmi_json) - 3)
        snprintf(pmi_json, sizeof(pmi_json), "\"%s\"", pmi);
    int length = snprintf(line, sizeof(line),
        "APAC_AFFINITY_JSON {\"stage\":\"before_mpi_init\",\"pid\":%ld,"
        "\"pmi_rank\":%s,\"success\":false,\"error\":\"%s\"}\n",
        (long)getpid(), pmi_json, reason);
    if (length > 0 && (size_t)length < sizeof(line))
        (void)write(STDERR_FILENO, line, (size_t)length);
}

static void emit_diagnostic(const char *entry, int rank, int launch_cpu,
                            int pre_status, const cpu_set_t *pre_mask,
                            int post_status, const cpu_set_t *post_mask,
                            int set_status, int verify_status,
                            const cpu_set_t *restored_mask, int success)
{
    char pre[MASK_CAPACITY], post[MASK_CAPACITY], restored[MASK_CAPACITY];
    int pre_truncated = 0, post_truncated = 0, restored_truncated = 0;
    char line[DIAG_CAPACITY];
    int length;
    mask_text(pre_mask, pre, sizeof(pre), &pre_truncated);
    mask_text(post_mask, post, sizeof(post), &post_truncated);
    mask_text(restored_mask, restored, sizeof(restored), &restored_truncated);
    length = snprintf(line, sizeof(line),
        "APAC_AFFINITY_JSON {\"entry\":\"%s\",\"rank\":%d,\"launch_cpu\":%d,"
        "\"mpi_pre_init_status\":%d,\"mpi_pre_init_cpus\":\"%s\",\"mpi_pre_init_truncated\":%s,"
        "\"post_init_status\":%d,\"post_init_cpus\":\"%s\",\"post_init_truncated\":%s,"
        "\"restore_set_status\":%d,\"restored_read_status\":%d,"
        "\"restored_cpus\":\"%s\",\"restored_truncated\":%s,\"success\":%s}\n",
        entry, rank, launch_cpu, pre_status, pre, pre_truncated ? "true" : "false",
        post_status, post, post_truncated ? "true" : "false",
        set_status, verify_status, restored,
        restored_truncated ? "true" : "false", success ? "true" : "false");
    if (length > 0 && (size_t)length < sizeof(line)) {
        (void)write(STDERR_FILENO, line, (size_t)length);
    } else {
        static const char fallback[] =
            "APAC_AFFINITY_JSON {\"success\":false,\"error\":\"diagnostic_overflow\"}\n";
        (void)write(STDERR_FILENO, fallback, sizeof(fallback) - 1);
    }
}

static int enabled(void)
{
    const char *value = getenv("APAC_PRESERVE_AFFINITY");
    return value && strcmp(value, "1") == 0;
}

static int run_init(const char *entry, init_fn init, init_thread_fn init_thread,
                    int *argc, char ***argv, int required, int *provided)
{
    cpu_set_t pre_mask, post_mask, restored_mask;
    int launch_cpu = -1, pre_status, post_status = -1;
    int set_status = -1, verify_status = -1, rank = -1, result, success = 0;
    int rank_status;

    if (!enabled() || wrapper_depth != 0)
        return init_thread ? init_thread(argc, argv, required, provided)
                           : init(argc, argv);

    if (parse_launch_cpu(&launch_cpu) != 0) {
        emit_preinit_error("missing_or_invalid_APAC_LAUNCH_CPU");
        _exit(126);
    }

    ++wrapper_depth;
    CPU_ZERO(&pre_mask);
    CPU_ZERO(&post_mask);
    CPU_ZERO(&restored_mask);
    pre_status = sched_getaffinity(0, sizeof(pre_mask), &pre_mask);
    if (pre_status != 0) {
        emit_preinit_error("cannot_read_mpi_pre_init_affinity");
        _exit(126);
    }

    result = init_thread ? init_thread(argc, argv, required, provided)
                         : init(argc, argv);
    if (result != MPI_SUCCESS) {
        --wrapper_depth;
        return result;
    }

    rank_status = PMPI_Comm_rank(MPI_COMM_WORLD, &rank);
    post_status = sched_getaffinity(0, sizeof(post_mask), &post_mask);

    /* Use only the singleton captured before exec; never infer a replacement CPU. */
    if (rank_status == MPI_SUCCESS) {
        cpu_set_t target;
        CPU_ZERO(&target);
        CPU_SET(launch_cpu, &target);
        set_status = sched_setaffinity(0, sizeof(target), &target);
        if (set_status == 0) {
            verify_status = sched_getaffinity(0, sizeof(restored_mask), &restored_mask);
            if (post_status == 0 && verify_status == 0 &&
                mask_count(&restored_mask) == 1 &&
                CPU_ISSET(launch_cpu, &restored_mask))
                success = 1;
        }
    }

    emit_diagnostic(entry, rank, launch_cpu, pre_status, &pre_mask,
                    post_status, &post_mask, set_status, verify_status,
                    &restored_mask, success);
    if (!success) {
        (void)PMPI_Abort(MPI_COMM_WORLD, APAC_ABORT_CODE);
        _exit(127);
    }

    --wrapper_depth;
    return result;
}

int MPI_Init(int *argc, char ***argv)
{
    return run_init("MPI_Init", PMPI_Init, NULL, argc, argv, 0, NULL);
}

int MPI_Init_thread(int *argc, char ***argv, int required, int *provided)
{
    return run_init("MPI_Init_thread", NULL, PMPI_Init_thread,
                    argc, argv, required, provided);
}
