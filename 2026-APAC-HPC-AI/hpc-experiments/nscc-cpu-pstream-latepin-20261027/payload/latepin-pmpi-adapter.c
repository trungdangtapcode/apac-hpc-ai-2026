#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <errno.h>
#include <glob.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/syscall.h>

#define EXPECTED_WORLD 512
#define EXPECTED_HOSTS 4
#define LOCAL_RANKS 128
#define PATH_SIZE 512
#define HOST_SIZE (MPI_MAX_PROCESSOR_NAME + 1)

typedef struct {
    int cpu;
    int package_id;
    int core_id;
    int node_id;
} CoreSlot;

typedef struct {
    int status;
    int error;
    cpu_set_t mask;
} AffinitySnapshot;

static void write_mask(FILE *stream, const cpu_set_t *mask);
static void write_json_string(FILE *stream, const char *value);

static int slot_compare(const void *left, const void *right)
{
    const CoreSlot *a = (const CoreSlot *)left;
    const CoreSlot *b = (const CoreSlot *)right;
    if (a->package_id != b->package_id) return (a->package_id > b->package_id) - (a->package_id < b->package_id);
    if (a->core_id != b->core_id) return (a->core_id > b->core_id) - (a->core_id < b->core_id);
    return (a->cpu > b->cpu) - (a->cpu < b->cpu);
}

static int read_integer(const char *path, int *value)
{
    FILE *stream = fopen(path, "r");
    int status;
    if (!stream) return -1;
    status = fscanf(stream, "%d", value) == 1 ? 0 : -1;
    if (fclose(stream) != 0) status = -1;
    return status;
}

static int cpulist_contains(const char *path, int cpu)
{
    FILE *stream = fopen(path, "r");
    char line[16384];
    char *cursor;
    if (!stream) return 0;
    if (!fgets(line, sizeof(line), stream) || fclose(stream) != 0) return 0;
    cursor = line;
    while (*cursor) {
        char *end = NULL;
        long first = strtol(cursor, &end, 10);
        long last = first;
        if (end == cursor || first < 0 || first >= CPU_SETSIZE) return 0;
        cursor = end;
        if (*cursor == '-') {
            last = strtol(cursor + 1, &end, 10);
            if (end == cursor + 1 || last < first || last >= CPU_SETSIZE) return 0;
            cursor = end;
        }
        if ((long)cpu >= first && (long)cpu <= last) return 1;
        if (*cursor == ',') ++cursor;
        else if (*cursor == '\n' || *cursor == '\0') break;
        else return 0;
    }
    return 0;
}

static int read_cpu_node(int cpu, int *node_id)
{
    char pattern[PATH_SIZE];
    glob_t paths;
    size_t i;
    int count = 0;
    int status = 0;
    snprintf(pattern, sizeof(pattern), "/sys/devices/system/cpu/cpu%d/node[0-9]*", cpu);
    status = glob(pattern, 0, NULL, &paths);
    if (status != 0 && status != GLOB_NOMATCH) return -1;
    if (status == 0) {
        for (i = 0; i < paths.gl_pathc; ++i) {
            const char *base = strrchr(paths.gl_pathv[i], '/');
            int value;
            char tail;
            if (base && sscanf(base + 1, "node%d%c", &value, &tail) == 1) {
                *node_id = value;
                ++count;
            }
        }
        globfree(&paths);
    }
    if (count == 1) return 0;
    if (count > 1) return -1;

    /* Some kernels expose NUMA membership only through node cpulist files. */
    snprintf(pattern, sizeof(pattern), "/sys/devices/system/node/node[0-9]*");
    status = glob(pattern, 0, NULL, &paths);
    if (status != 0) return -1;
    for (i = 0; i < paths.gl_pathc; ++i) {
        char cpulist[PATH_SIZE];
        const char *base = strrchr(paths.gl_pathv[i], '/');
        int value;
        char tail;
        if (!base || sscanf(base + 1, "node%d%c", &value, &tail) != 1) continue;
        if (snprintf(cpulist, sizeof(cpulist), "%s/cpulist", paths.gl_pathv[i]) >= (int)sizeof(cpulist)) continue;
        if (cpulist_contains(cpulist, cpu)) {
            *node_id = value;
            ++count;
        }
    }
    globfree(&paths);
    return count == 1 ? 0 : -1;
}

static int read_cpu_topology(int cpu, CoreSlot *slot)
{
    char path[PATH_SIZE];
    if (cpu < 0 || cpu >= CPU_SETSIZE || !cpulist_contains("/sys/devices/system/cpu/online", cpu)) return -1;
    slot->cpu = cpu;
    if (snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/topology/physical_package_id", cpu) >= (int)sizeof(path) ||
        read_integer(path, &slot->package_id) != 0 || slot->package_id < 0) return -1;
    if (snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/topology/core_id", cpu) >= (int)sizeof(path) ||
        read_integer(path, &slot->core_id) != 0 || slot->core_id < 0) return -1;
    if (read_cpu_node(cpu, &slot->node_id) != 0 || slot->node_id < 0) return -1;
    return 0;
}

static int build_slots(const cpu_set_t *allowed, CoreSlot slots[LOCAL_RANKS],
                       CoreSlot topology_rows[CPU_SETSIZE], int *topology_count)
{
    CoreSlot by_cpu[CPU_SETSIZE];
    size_t count = 0, unique = 0, i;
    int cpu;
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (!CPU_ISSET(cpu, allowed)) continue;
        if (read_cpu_topology(cpu, &by_cpu[count]) != 0) return -1;
        ++count;
    }
    if (count == 0) return -1;
    qsort(by_cpu, count, sizeof(by_cpu[0]), slot_compare);
    memcpy(topology_rows, by_cpu, count * sizeof(by_cpu[0]));
    *topology_count = (int)count;
    for (i = 0; i < count; ++i) {
        if (unique > 0 && by_cpu[i].package_id == slots[unique - 1].package_id &&
            by_cpu[i].core_id == slots[unique - 1].core_id) {
            if (by_cpu[i].node_id != slots[unique - 1].node_id) return -1;
            /* Sorting makes the first (lowest logical CPU) sibling the slot. */
            continue;
        }
        if (unique >= LOCAL_RANKS) return -1;
        slots[unique++] = by_cpu[i];
    }
    return unique == LOCAL_RANKS ? 0 : -1;
}

static int write_topology_record(const char *dir, int rank, int pmi_rank, const char *host,
                                 const cpu_set_t *allowed, int topology_source_world_rank, const cpu_set_t *topology_source_allowed,
                                 const CoreSlot rows[CPU_SETSIZE], int row_count, const CoreSlot slots[LOCAL_RANKS])
{
    char path[PATH_SIZE];
    FILE *stream;
    int i;
    if (snprintf(path, sizeof(path), "%s/host-topology-world-%04d.json", dir, rank) >= (int)sizeof(path)) return -1;
    stream = fopen(path, "wx");
    if (!stream) return -1;
    fprintf(stream, "{\"world_rank\":%d,\"pmi_rank\":%d,\"host\":", rank, pmi_rank);
    write_json_string(stream, host);
    fputs(",\"post_init_allowed\":", stream);
    write_mask(stream, allowed);
    fprintf(stream, ",\"topology_source_world_rank\":%d,\"topology_source_allowed\":", topology_source_world_rank);
    write_mask(stream, topology_source_allowed);
    fputs(",\"allowed_cpu_sysfs_map\":[", stream);
    for (i = 0; i < row_count; ++i) {
        fprintf(stream, "%s{\"cpu\":%d,\"online\":true,\"package\":%d,\"core\":%d,\"node\":%d}",
                i ? "," : "", rows[i].cpu, rows[i].package_id, rows[i].core_id, rows[i].node_id);
    }
    fputs("],\"selected_slots_sorted_package_core\":[", stream);
    for (i = 0; i < LOCAL_RANKS; ++i) {
        fprintf(stream, "%s{\"cpu\":%d,\"package\":%d,\"core\":%d,\"node\":%d}",
                i ? "," : "", slots[i].cpu, slots[i].package_id, slots[i].core_id, slots[i].node_id);
    }
    fputs("]}\n", stream);
    return fclose(stream) == 0 ? 0 : -1;
}

static AffinitySnapshot snapshot(void)
{
    AffinitySnapshot result;
    CPU_ZERO(&result.mask);
    errno = 0;
    result.status = sched_getaffinity(0, sizeof(result.mask), &result.mask);
    result.error = result.status == 0 ? 0 : errno;
    return result;
}

static int parse_pmi(const char *raw, int *rank)
{
    char *end = NULL;
    long value;
    if (!raw || !*raw) return -1;
    errno = 0;
    value = strtol(raw, &end, 10);
    if (errno || end == raw || *end || value < 0 || value >= EXPECTED_WORLD) return -1;
    *rank = (int)value;
    return 0;
}

static int count_hosts(const char *all_hosts, char names[EXPECTED_HOSTS][HOST_SIZE], int counts[EXPECTED_HOSTS])
{
    int i, j, unique = 0;
    for (i = 0; i < EXPECTED_HOSTS; ++i) counts[i] = 0;
    for (i = 0; i < EXPECTED_WORLD; ++i) {
        const char *entry = all_hosts + (size_t)i * HOST_SIZE;
        for (j = 0; j < unique; ++j) if (strcmp(names[j], entry) == 0) break;
        if (j == unique) {
            if (unique == EXPECTED_HOSTS) return -1;
            snprintf(names[unique], HOST_SIZE, "%s", entry);
            ++unique;
        }
        ++counts[j];
    }
    if (unique != EXPECTED_HOSTS) return -1;
    for (i = 0; i < EXPECTED_HOSTS; ++i) if (counts[i] != LOCAL_RANKS) return -1;
    return 0;
}

static void write_mask(FILE *stream, const cpu_set_t *mask)
{
    int cpu, first = 1;
    fputc('[', stream);
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, mask)) {
        fprintf(stream, "%s%d", first ? "" : ",", cpu);
        first = 0;
    }
    fputc(']', stream);
}

static void write_json_string(FILE *stream, const char *value)
{
    const unsigned char *cursor = (const unsigned char *)value;
    fputc('"', stream);
    while (*cursor) {
        if (*cursor == '"' || *cursor == '\\') {
            fputc('\\', stream);
            fputc(*cursor, stream);
        } else if (*cursor < 0x20) {
            fprintf(stream, "\\u%04x", (unsigned int)*cursor);
        } else {
            fputc(*cursor, stream);
        }
        ++cursor;
    }
    fputc('"', stream);
}

#include <pthread.h>
#include <sys/syscall.h>

static volatile int init_state;
static volatile int finalize_state;
static pthread_t init_thread;
static char init_hook[32] = "not_called";
static int requested_level = -1;
static int provided_level = -1;
static int saved_world_rank = -1;
static int saved_pmi_rank = -1;
static int saved_local_rank = -1;
static int saved_world_size = -1;
static int saved_local_size = -1;
static char saved_host[HOST_SIZE];
static char saved_audit_dir[PATH_SIZE];
static CoreSlot saved_target = {-1, -1, -1, -1};
static int saved_init_errors = 1;
static int saved_topology_status = -1;
static volatile int init_reentry_error;
static long saved_process_pid;
static long saved_init_tid;

static int init_was_reentered(void)
{
    return __sync_fetch_and_add(&init_reentry_error, 0) != 0;
}

static int write_affinity(FILE *f, const char *name, const AffinitySnapshot *s)
{
    fprintf(f, "\"%s_status\":%d,\"%s_errno\":%d,\"%s_mask\":", name, s->status, name, s->error, name);
    write_mask(f, &s->mask);
    return ferror(f) ? -1 : 0;
}

static int write_init_audit(const AffinitySnapshot *before, const AffinitySnapshot *after,
                            const AffinitySnapshot *pinned, int pin_status, int pin_error,
                            int hook_rc, int preflight_errors, int world_errors, int thread_match)
{
    char path[PATH_SIZE];
    FILE *f;
    if (!saved_audit_dir[0] || snprintf(path, sizeof(path), "%s/init.json", saved_audit_dir) >= (int)sizeof(path)) return -1;
    f = fopen(path, "wx");
    if (!f) return -1;
    fputs("{\"schema\":1,\"hook\":", f); write_json_string(f, init_hook);
    fprintf(f, ",\"requested_thread_level\":%d,\"provided_thread_level\":%d,\"underlying_init_rc\":%d,\"process_pid\":%ld,\"hook_thread_tid\":%ld,\"hook_thread_is_process_main\":%s,\"repeated_or_nested_init_rejected\":%s,", requested_level, provided_level, hook_rc, saved_process_pid, saved_init_tid, saved_init_tid == saved_process_pid ? "true" : "false", init_was_reentered() ? "true" : "false");
    fprintf(f, "\"world_rank\":%d,\"pmi_rank\":%d,\"world_size\":%d,\"local_rank\":%d,\"local_size\":%d,\"host\":", saved_world_rank, saved_pmi_rank, saved_world_size, saved_local_rank, saved_local_size);
    write_json_string(f, saved_host);
    fprintf(f, ",\"topology_status\":%d,\"target_cpu\":%d,\"physical_socket\":%d,\"physical_core\":%d,\"numa_node\":%d,\"init_thread_matches_hook_thread\":%s,\"sched_setaffinity_status\":%d,\"sched_setaffinity_errno\":%d,\"preflight_global_error_count\":%d,\"collective_init_error_count\":%d,",
            saved_topology_status, saved_target.cpu, saved_target.package_id, saved_target.core_id, saved_target.node_id,
            thread_match ? "true" : "false", pin_status, pin_error, preflight_errors, world_errors);
    write_affinity(f, "before_init", before); fputc(',', f);
    write_affinity(f, "post_init", after); fputc(',', f);
    write_affinity(f, "after_pin", pinned); fputs("}\n", f);
    if (fclose(f) != 0) return -1;
    return 0;
}

static int write_finalize_audit(const AffinitySnapshot *before, int thread_match, long finalize_pid, long finalize_tid,
                                int target_present, int singleton, int local_error,
                                int collective_errors)
{
    char path[PATH_SIZE];
    FILE *f;
    if (!saved_audit_dir[0] || snprintf(path, sizeof(path), "%s/finalize.json", saved_audit_dir) >= (int)sizeof(path)) return -1;
    f = fopen(path, "wx");
    if (!f) return -1;
    fputs("{\"schema\":1,\"hook\":", f); write_json_string(f, "MPI_Finalize");
    fprintf(f, ",\"world_rank\":%d,\"pmi_rank\":%d,\"world_size\":%d,\"local_rank\":%d,\"local_size\":%d,\"host\":", saved_world_rank, saved_pmi_rank, saved_world_size, saved_local_rank, saved_local_size);
    write_json_string(f, saved_host);
    fprintf(f, ",\"target_cpu\":%d,\"physical_socket\":%d,\"physical_core\":%d,\"numa_node\":%d,\"finalize_process_pid\":%ld,\"finalize_thread_tid\":%ld,\"finalize_thread_is_process_main\":%s,\"finalize_thread_matches_hook_thread\":%s,\"target_present\":%s,\"singleton_target_mask\":%s,\"repeated_or_nested_init_rejected\":%s,\"local_error\":%d,\"collective_finalize_error_count\":%d,\"audit_phase\":\"immediately_before_PMPI_Finalize\",\"pmpi_finalize_return_code\":null,",
            saved_target.cpu, saved_target.package_id, saved_target.core_id, saved_target.node_id, finalize_pid, finalize_tid,
            finalize_pid == saved_process_pid && finalize_tid == finalize_pid ? "true" : "false",
            thread_match ? "true" : "false", target_present ? "true" : "false", singleton ? "true" : "false",
            init_was_reentered() ? "true" : "false", local_error, collective_errors);
    write_affinity(f, "before_pmpi_finalize", before); fputs("}\n", f);
    if (fclose(f) != 0) return -1;
    return 0;
}

static int write_finalize_return(const char *dir, int pmpi_rc, long process_pid, long finalize_tid, int collective_errors, int pre_finalize_write_errors)
{
    char path[PATH_SIZE];
    FILE *f;
    if (!dir[0] || snprintf(path, sizeof(path), "%s/finalize-return.json", dir) >= (int)sizeof(path)) return -1;
    f = fopen(path, "wx");
    if (!f) return -1;
    fprintf(f, "{\"schema\":1,\"hook\":\"PMPI_Finalize_return\",\"world_rank\":%d,\"pmi_rank\":%d,\"local_rank\":%d,\"host\":", saved_world_rank, saved_pmi_rank, saved_local_rank);
    write_json_string(f, saved_host);
    fprintf(f, ",\"target_cpu\":%d,\"process_pid\":%ld,\"finalize_thread_tid\":%ld,\"pmpi_finalize_return_code\":%d,\"mpi_success_constant\":%d,\"collective_finalize_error_count\":%d,\"pre_finalize_audit_write_error_count\":%d}\n",
            saved_target.cpu, process_pid, finalize_tid, pmpi_rc, MPI_SUCCESS, collective_errors, pre_finalize_write_errors);
    if (fclose(f) != 0) return -1;
    return 0;
}

static int prepare_after_init(const AffinitySnapshot *before, int hook_rc)
{
    MPI_Comm local = MPI_COMM_NULL;
    int rank = -1, size = -1, local_rank = -1, local_size = -1, name_len = 0;
    int pmi = -1, local_bad = 0, preflight_errors = 0, world_bad = 0, topology_status = -1;
    int provided_query = -1, thread_match, pin_status = -1, pin_error = 0;
    int world_pmi[EXPECTED_WORLD], i, j;
    char host[HOST_SIZE], all_hosts[EXPECTED_WORLD * HOST_SIZE];
    char local_hosts[LOCAL_RANKS * HOST_SIZE];
    AffinitySnapshot after = snapshot(), pinned;
    CoreSlot slots[LOCAL_RANKS], rows[CPU_SETSIZE], own_topology;
    cpu_set_t topology_source_allowed;
    int topology_source_world_rank = -1;
    int row_count = 0, local_topology_ok = 0;
    int world_errors = 0, write_error = 0;
    cpu_set_t target_mask;
    const char *audit = getenv("NSCC_LATEPIN_AUDIT_DIR");

    memset(host, 0, sizeof(host)); memset(all_hosts, 0, sizeof(all_hosts));
    memset(local_hosts, 0, sizeof(local_hosts)); memset(slots, 0, sizeof(slots)); memset(rows, 0, sizeof(rows)); CPU_ZERO(&topology_source_allowed);
    saved_audit_dir[0] = '\0';
    if (audit && *audit && strlen(audit) < sizeof(saved_audit_dir)) strcpy(saved_audit_dir, audit);
    else local_bad = 1;
    if (PMPI_Query_thread(&provided_query) != MPI_SUCCESS) local_bad = 1;
    if (provided_query >= 0) provided_level = provided_query;
    if (PMPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS ||
        PMPI_Comm_size(MPI_COMM_WORLD, &size) != MPI_SUCCESS) local_bad = 1;
    if (PMPI_Get_processor_name(host, &name_len) != MPI_SUCCESS || name_len < 0 || name_len >= MPI_MAX_PROCESSOR_NAME) {
        strcpy(host, "MPI_Get_processor_name_error"); local_bad = 1;
    } else host[name_len] = '\0';
    saved_world_rank = rank; saved_world_size = size;
    snprintf(saved_host, sizeof(saved_host), "%s", host);
    if (parse_pmi(getenv("PMI_RANK"), &pmi) != 0) local_bad = 1;
    saved_pmi_rank = pmi;
    thread_match = pthread_equal(pthread_self(), init_thread) != 0 && saved_init_tid == saved_process_pid;
    if (init_was_reentered() || !thread_match || before->status != 0 || after.status != 0 || hook_rc != MPI_SUCCESS || provided_level < MPI_THREAD_SINGLE || (requested_level >= MPI_THREAD_SINGLE && provided_level < requested_level)) local_bad = 1;
    if (size != EXPECTED_WORLD || rank < 0 || rank >= EXPECTED_WORLD) local_bad = 1;

    if (size == EXPECTED_WORLD && rank >= 0 && rank < EXPECTED_WORLD) {
        if (PMPI_Allgather(&pmi, 1, MPI_INT, world_pmi, 1, MPI_INT, MPI_COMM_WORLD) != MPI_SUCCESS) local_bad = 1;
        else for (i = 0; i < EXPECTED_WORLD; ++i) {
            if (world_pmi[i] < 0 || world_pmi[i] >= EXPECTED_WORLD) local_bad = 1;
            for (j = 0; j < i; ++j) if (world_pmi[i] == world_pmi[j]) local_bad = 1;
        }
        if (PMPI_Allgather(host, HOST_SIZE, MPI_CHAR, all_hosts, HOST_SIZE, MPI_CHAR, MPI_COMM_WORLD) != MPI_SUCCESS) local_bad = 1;
        else {
            char names[EXPECTED_HOSTS][HOST_SIZE]; int counts[EXPECTED_HOSTS];
            if (count_hosts(all_hosts, names, counts) != 0) local_bad = 1;
        }
        if (PMPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, rank, MPI_INFO_NULL, &local) != MPI_SUCCESS || local == MPI_COMM_NULL) {
            local_bad = 1;
        } else {
            if (PMPI_Comm_rank(local, &local_rank) != MPI_SUCCESS || PMPI_Comm_size(local, &local_size) != MPI_SUCCESS) local_bad = 1;
            if (local_size != LOCAL_RANKS || local_rank < 0 || local_rank >= LOCAL_RANKS) local_bad = 1;
            if (local_size == LOCAL_RANKS) {
                if (PMPI_Allgather(host, HOST_SIZE, MPI_CHAR, local_hosts, HOST_SIZE, MPI_CHAR, local) != MPI_SUCCESS) local_bad = 1;
                else for (i = 0; i < LOCAL_RANKS; ++i) if (strcmp(host, local_hosts + (size_t)i * HOST_SIZE) != 0) local_bad = 1;
            }
            if (local_rank == 0) {
                topology_source_world_rank = rank;
                topology_source_allowed = after.mask;
                if (after.status != 0 || build_slots(&after.mask, slots, rows, &row_count) != 0) topology_status = -1;
                else topology_status = 0;
            }
            if (PMPI_Bcast(&topology_status, 1, MPI_INT, 0, local) != MPI_SUCCESS) local_bad = 1;
            if (PMPI_Bcast(&row_count, 1, MPI_INT, 0, local) != MPI_SUCCESS || row_count < 0 || row_count > CPU_SETSIZE) local_bad = 1;
            if (PMPI_Bcast(&topology_source_world_rank, 1, MPI_INT, 0, local) != MPI_SUCCESS) local_bad = 1;
            if (PMPI_Bcast(&topology_source_allowed, (int)sizeof(topology_source_allowed), MPI_BYTE, 0, local) != MPI_SUCCESS) local_bad = 1;
            if (PMPI_Bcast(rows, (int)sizeof(rows), MPI_BYTE, 0, local) != MPI_SUCCESS) local_bad = 1;
            if (PMPI_Bcast(slots, (int)sizeof(slots), MPI_BYTE, 0, local) != MPI_SUCCESS) local_bad = 1;
            if (local_rank >= 0 && local_rank < LOCAL_RANKS && topology_status == 0) {
                saved_target = slots[local_rank];
                local_topology_ok = read_cpu_topology(saved_target.cpu, &own_topology) == 0 &&
                    own_topology.package_id == saved_target.package_id && own_topology.core_id == saved_target.core_id &&
                    own_topology.node_id == saved_target.node_id && CPU_ISSET(saved_target.cpu, &after.mask);
                if (!local_topology_ok) local_bad = 1;
                if (write_topology_record(saved_audit_dir, rank, pmi, host, &after.mask, topology_source_world_rank, &topology_source_allowed, rows, row_count, slots) != 0) local_bad = 1;
            } else local_bad = 1;
        }
    }
    saved_local_rank = local_rank; saved_local_size = local_size; saved_topology_status = topology_status;
    /* Fail closed collectively before any process changes affinity. */
    if (PMPI_Allreduce(&local_bad, &preflight_errors, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        preflight_errors = EXPECTED_WORLD;
        local_bad = 1;
    }
    if (preflight_errors != 0) local_bad = 1;
    memset(&pinned, 0, sizeof(pinned)); pinned.status = -1; pinned.error = 0;
    CPU_ZERO(&target_mask);
    if (preflight_errors == 0 && !local_bad && saved_target.cpu >= 0 && saved_target.cpu < CPU_SETSIZE) {
        CPU_SET(saved_target.cpu, &target_mask);
        errno = 0; pin_status = sched_setaffinity(0, sizeof(target_mask), &target_mask);
        pin_error = pin_status == 0 ? 0 : errno;
        pinned = snapshot();
        if (pin_status != 0 || pinned.status != 0 || !CPU_ISSET(saved_target.cpu, &pinned.mask) || CPU_COUNT(&pinned.mask) != 1) local_bad = 1;
    }
    if (PMPI_Allreduce(&local_bad, &world_errors, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        world_errors = EXPECTED_WORLD; local_bad = 1;
    }
    if (write_init_audit(before, &after, &pinned, pin_status, pin_error, hook_rc, preflight_errors, world_errors, thread_match) != 0) write_error = 1;
    if (PMPI_Allreduce(&write_error, &world_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) world_bad = EXPECTED_WORLD;
    saved_init_errors = world_errors + world_bad;
    if (local != MPI_COMM_NULL) PMPI_Comm_free(&local);
    return saved_init_errors == 0 ? MPI_SUCCESS : MPI_ERR_OTHER;
}

static int begin_init(const char *hook, int requested)
{
    int expected = 0;
    if (!__sync_bool_compare_and_swap(&init_state, expected, 1)) { __sync_lock_test_and_set(&init_reentry_error, 1); return MPI_ERR_OTHER; }
    snprintf(init_hook, sizeof(init_hook), "%s", hook);
    requested_level = requested;
    init_thread = pthread_self();
    saved_process_pid = (long)getpid();
    saved_init_tid = (long)syscall(SYS_gettid);
    return MPI_SUCCESS;
}

int MPI_Init(int *argc, char ***argv)
{
    AffinitySnapshot before = snapshot();
    int rc, provided = -1;
    if (begin_init("MPI_Init", MPI_THREAD_SINGLE) != MPI_SUCCESS) return MPI_ERR_OTHER;
    rc = PMPI_Init(argc, argv);
    if (rc != MPI_SUCCESS) { init_state = 3; return rc; }
    if (PMPI_Query_thread(&provided) != MPI_SUCCESS) provided = -1;
    provided_level = provided;
    init_state = 2;
    rc = prepare_after_init(&before, MPI_SUCCESS);
    return rc;
}

int MPI_Init_thread(int *argc, char ***argv, int required, int *provided)
{
    AffinitySnapshot before = snapshot();
    int rc;
    if (begin_init("MPI_Init_thread", required) != MPI_SUCCESS) return MPI_ERR_OTHER;
    rc = PMPI_Init_thread(argc, argv, required, provided);
    if (rc != MPI_SUCCESS) { init_state = 3; return rc; }
    provided_level = provided ? *provided : -1;
    init_state = 2;
    return prepare_after_init(&before, MPI_SUCCESS);
}

int MPI_Finalize(void)
{
    AffinitySnapshot before;
    int local_error, collective_errors = 0, write_error = 0, write_errors = 0;
    int thread_match, target_present, singleton, rc, expected = 0;
    long finalize_pid = (long)getpid(), finalize_tid = (long)syscall(SYS_gettid);
    if (init_state != 2) return MPI_ERR_OTHER;
    if (!__sync_bool_compare_and_swap(&finalize_state, expected, 1)) return MPI_ERR_OTHER;
    before = snapshot();
    thread_match = pthread_equal(pthread_self(), init_thread) != 0 && finalize_pid == saved_process_pid && finalize_tid == saved_init_tid && finalize_tid == finalize_pid;
    target_present = saved_target.cpu >= 0 && saved_target.cpu < CPU_SETSIZE && before.status == 0 && CPU_ISSET(saved_target.cpu, &before.mask);
    singleton = before.status == 0 && saved_target.cpu >= 0 && CPU_COUNT(&before.mask) == 1 && target_present;
    local_error = saved_init_errors != 0 || init_was_reentered() || !thread_match || !target_present || !singleton || before.status != 0;
    if (PMPI_Allreduce(&local_error, &collective_errors, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) collective_errors = EXPECTED_WORLD;
    if (write_finalize_audit(&before, thread_match, finalize_pid, finalize_tid, target_present, singleton, local_error, collective_errors) != 0) write_error = 1;
    if (PMPI_Allreduce(&write_error, &write_errors, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) write_errors = EXPECTED_WORLD;
    rc = PMPI_Finalize();
    finalize_state = 2;
    /* After PMPI_Finalize, retain only OS-level evidence; no MPI call follows it. */
    if (write_finalize_return(saved_audit_dir, rc, finalize_pid, finalize_tid, collective_errors, write_errors) != 0) {
        fprintf(stderr, "rank %d could not write PMPI_Finalize return audit\n", saved_world_rank);
        write_errors++;
    }
    if (rc != MPI_SUCCESS) return rc;
    return collective_errors == 0 && write_errors == 0 ? MPI_SUCCESS : MPI_ERR_OTHER;
}
