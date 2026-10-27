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
                                 const cpu_set_t *allowed, const CoreSlot rows[CPU_SETSIZE],
                                 int row_count, const CoreSlot slots[LOCAL_RANKS])
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

static int write_record(const char *dir, int rank, int pmi_rank, const char *host,
                        int local_rank, int world_size, int local_size,
                        const AffinitySnapshot *pre, const AffinitySnapshot *post,
                        int topology_status, const CoreSlot *target,
                        int pin_status, int pin_error,
                        const AffinitySnapshot *immediate,
                        const AffinitySnapshot *after_allreduce,
                        const AffinitySnapshot *after_2s,
                        const AffinitySnapshot *after_final_allreduce,
                        int immediate_global_errors, int final_global_errors,
                        int preflight_global_errors, int sleep_status, long long sleep_elapsed_ns)
{
    char path[PATH_SIZE];
    FILE *stream;
    if (snprintf(path, sizeof(path), "%s/rank-%04d.json", dir, rank) >= (int)sizeof(path)) return -1;
    stream = fopen(path, "wx");
    if (!stream) return -1;
    fprintf(stream, "{\"world_rank\":%d,\"pmi_rank\":%d,\"host\":", rank, pmi_rank);
    write_json_string(stream, host);
    fprintf(stream, ",\"local_rank\":%d,\"world_size\":%d,\"local_size\":%d,", local_rank, world_size, local_size);
    fprintf(stream, "\"pre_init_status\":%d,\"pre_init_errno\":%d,\"pre_init_allowed\":", pre->status, pre->error);
    write_mask(stream, &pre->mask);
    fprintf(stream, ",\"post_init_status\":%d,\"post_init_errno\":%d,\"post_init_allowed\":", post->status, post->error);
    write_mask(stream, &post->mask);
    fprintf(stream, ",\"topology_status\":%d,\"target_cpu\":%d,\"physical_package_id\":%d,\"physical_core_id\":%d,\"numa_node\":%d,",
            topology_status, target->cpu, target->package_id, target->core_id, target->node_id);
    fprintf(stream, "\"sched_setaffinity_status\":%d,\"sched_setaffinity_errno\":%d,\"immediate_mask_status\":%d,\"immediate_mask_errno\":%d,\"immediate_mask\":",
            pin_status, pin_error, immediate->status, immediate->error);
    write_mask(stream, &immediate->mask);
    fprintf(stream, ",\"after_allreduce_status\":%d,\"after_allreduce_errno\":%d,\"after_allreduce_mask\":", after_allreduce->status, after_allreduce->error);
    write_mask(stream, &after_allreduce->mask);
    fprintf(stream, ",\"after_2s_status\":%d,\"after_2s_errno\":%d,\"after_2s_mask\":", after_2s->status, after_2s->error);
    write_mask(stream, &after_2s->mask);
    fprintf(stream, ",\"after_final_allreduce_status\":%d,\"after_final_allreduce_errno\":%d,\"after_final_allreduce_mask\":",
            after_final_allreduce->status, after_final_allreduce->error);
    write_mask(stream, &after_final_allreduce->mask);
    fprintf(stream, ",\"preflight_global_error_count\":%d,\"immediate_global_error_count\":%d,\"final_global_error_count\":%d,\"sleep_status\":%d,\"sleep_elapsed_ns\":%lld}\n",
            preflight_global_errors, immediate_global_errors, final_global_errors, sleep_status, sleep_elapsed_ns);
    if (fclose(stream) != 0) return -1;
    return 0;
}

static long long timespec_ns(const struct timespec *value)
{
    return (long long)value->tv_sec * 1000000000LL + (long long)value->tv_nsec;
}

static int sleep_until_2s(long long *elapsed_ns)
{
    struct timespec start, deadline, finish;
    int rc;
    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) return -1;
    deadline = start;
    deadline.tv_sec += 2;
    do {
        rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &deadline, NULL);
    } while (rc == EINTR);
    if (clock_gettime(CLOCK_MONOTONIC, &finish) != 0) return -1;
    *elapsed_ns = timespec_ns(&finish) - timespec_ns(&start);
    if (rc != 0 || *elapsed_ns < 1900000000LL || *elapsed_ns > 10000000000LL) return -1;
    return 0;
}

int main(int argc, char **argv)
{
    int rank = -1, world_size = -1, name_length = 0, local_rank = -1, local_size = -1;
    int pmi_rank = -1, local_bad = 0, global_bad = 0, immediate_bad = 0, immediate_global_bad = 0;
    int final_bad = 0, final_global_bad = 0, preflight_global_bad = 0, topology_status = -1, pin_status = -1, pin_error = 0;
    int sleep_status = -1, slot_flat[LOCAL_RANKS * 4] = {0}, i;
    int pmi_ranks[EXPECTED_WORLD];
    int local_world_ranks[LOCAL_RANKS];
    int host_counts[EXPECTED_HOSTS] = {0};
    char host[HOST_SIZE] = {0};
    char unique_hosts[EXPECTED_HOSTS][HOST_SIZE] = {{0}};
    char local_hosts[LOCAL_RANKS][HOST_SIZE] = {{0}};
    char *all_hosts = NULL;
    char output_dir[PATH_SIZE];
    const char *pmi_raw = getenv("PMI_RANK");
    MPI_Comm local_comm = MPI_COMM_NULL;
    CoreSlot slots[LOCAL_RANKS];
    CoreSlot topology_rows[CPU_SETSIZE];
    int topology_count = 0;
    CoreSlot target = {-1, -1, -1, -1};
    AffinitySnapshot pre, post, immediate, after_allreduce, after_2s, after_final_allreduce;
    long long sleep_elapsed_ns = -1;

    pre = snapshot();
    if (argc != 2 || snprintf(output_dir, sizeof(output_dir), "%s", argc > 1 ? argv[1] : "") >= (int)sizeof(output_dir)) return 2;
    if (parse_pmi(pmi_raw, &pmi_rank) != 0) local_bad = 1;
    if (MPI_Init_thread(&argc, &argv, MPI_THREAD_SINGLE, &i) != MPI_SUCCESS) return 10;
    if (i < MPI_THREAD_SINGLE || MPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS ||
        MPI_Comm_size(MPI_COMM_WORLD, &world_size) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 11);
        return 11;
    }
    if (world_size != EXPECTED_WORLD || rank < 0 || rank >= EXPECTED_WORLD) {
        if (rank == 0) fprintf(stderr, "WORLD_SIZE_GATE_FAILED world=%d expected=%d\n", world_size, EXPECTED_WORLD);
        MPI_Abort(MPI_COMM_WORLD, 11);
        return 11;
    }
    if (MPI_Get_processor_name(host, &name_length) != MPI_SUCCESS || name_length < 0 || name_length >= HOST_SIZE) {
        MPI_Abort(MPI_COMM_WORLD, 12);
        return 12;
    }
    host[name_length] = '\0';
    post = snapshot();
    if (post.status != 0 || pre.status != 0 || world_size != EXPECTED_WORLD || rank < 0 || rank >= EXPECTED_WORLD) local_bad = 1;
    if (MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, rank, MPI_INFO_NULL, &local_comm) != MPI_SUCCESS ||
        MPI_Comm_rank(local_comm, &local_rank) != MPI_SUCCESS || MPI_Comm_size(local_comm, &local_size) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 13);
        return 13;
    }
    if (local_size != LOCAL_RANKS || local_rank < 0 || local_rank >= LOCAL_RANKS) local_bad = 1;
    if (local_size == LOCAL_RANKS) {
        if (MPI_Allgather(&rank, 1, MPI_INT, local_world_ranks, 1, MPI_INT, local_comm) != MPI_SUCCESS ||
            MPI_Allgather(host, HOST_SIZE, MPI_CHAR, local_hosts, HOST_SIZE, MPI_CHAR, local_comm) != MPI_SUCCESS) {
            MPI_Abort(MPI_COMM_WORLD, 14);
            return 14;
        }
        for (i = 0; i < LOCAL_RANKS; ++i) {
            if (local_hosts[i][HOST_SIZE - 1] != '\0' || strcmp(local_hosts[i], host) != 0 ||
                (i > 0 && local_world_ranks[i - 1] >= local_world_ranks[i])) local_bad = 1;
        }
        if (local_world_ranks[local_rank] != rank) local_bad = 1;
    }
    if (MPI_Allgather(&pmi_rank, 1, MPI_INT, pmi_ranks, 1, MPI_INT, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 14);
        return 14;
    }
    for (i = 0; i < EXPECTED_WORLD; ++i) {
        int j;
        if (pmi_ranks[i] < 0 || pmi_ranks[i] >= EXPECTED_WORLD) local_bad = 1;
        for (j = 0; j < i; ++j) if (pmi_ranks[j] == pmi_ranks[i]) local_bad = 1;
    }
    all_hosts = (char *)calloc((size_t)EXPECTED_WORLD, HOST_SIZE);
    if (!all_hosts) {
        MPI_Abort(MPI_COMM_WORLD, 14);
        return 14;
    }
    if (MPI_Allgather(host, HOST_SIZE, MPI_CHAR, all_hosts, HOST_SIZE, MPI_CHAR, MPI_COMM_WORLD) != MPI_SUCCESS) {
        free(all_hosts);
        MPI_Abort(MPI_COMM_WORLD, 15);
        return 15;
    }
    if (!all_hosts) local_bad = 1;
    else if (count_hosts(all_hosts, unique_hosts, host_counts) != 0) local_bad = 1;
    for (i = 0; i < LOCAL_RANKS * 4; ++i) slot_flat[i] = -1;
    if (world_size == EXPECTED_WORLD && local_size == LOCAL_RANKS && local_rank == 0 && post.status == 0) {
        topology_status = build_slots(&post.mask, slots, topology_rows, &topology_count);
        if (topology_status == 0 && write_topology_record(output_dir, rank, pmi_rank, host,
                &post.mask, topology_rows, topology_count, slots) != 0) topology_status = -1;
        if (topology_status == 0) {
            for (i = 0; i < LOCAL_RANKS; ++i) {
                slot_flat[i * 4] = slots[i].cpu;
                slot_flat[i * 4 + 1] = slots[i].package_id;
                slot_flat[i * 4 + 2] = slots[i].core_id;
                slot_flat[i * 4 + 3] = slots[i].node_id;
            }
        }
    }
    if (MPI_Bcast(&topology_status, 1, MPI_INT, 0, local_comm) != MPI_SUCCESS ||
        MPI_Bcast(slot_flat, LOCAL_RANKS * 4, MPI_INT, 0, local_comm) != MPI_SUCCESS) {
        free(all_hosts);
        MPI_Abort(MPI_COMM_WORLD, 16);
        return 16;
    }
    if (topology_status != 0 || local_bad) local_bad = 1;
    if (topology_status == 0 && local_rank >= 0 && local_rank < LOCAL_RANKS) {
        target.cpu = slot_flat[local_rank * 4];
        target.package_id = slot_flat[local_rank * 4 + 1];
        target.core_id = slot_flat[local_rank * 4 + 2];
        target.node_id = slot_flat[local_rank * 4 + 3];
        if (target.cpu < 0 || target.cpu >= CPU_SETSIZE || post.status != 0 || !CPU_ISSET(target.cpu, &post.mask) ||
            !cpulist_contains("/sys/devices/system/cpu/online", target.cpu)) local_bad = 1;
    }
    free(all_hosts);
    if (MPI_Allreduce(&local_bad, &global_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 17);
        return 17;
    }
    preflight_global_bad = global_bad;
    if (global_bad == 0) {
        cpu_set_t selected;
        CPU_ZERO(&selected);
        CPU_SET(target.cpu, &selected);
        errno = 0;
        pin_status = sched_setaffinity(0, sizeof(selected), &selected);
        pin_error = pin_status == 0 ? 0 : errno;
        immediate = snapshot();
        immediate_bad = pin_status != 0 || immediate.status != 0 || !CPU_ISSET(target.cpu, &immediate.mask) ||
                        CPU_COUNT(&immediate.mask) != 1 || !CPU_ISSET(target.cpu, &immediate.mask);
    } else {
        pin_status = -1;
        immediate = post;
        immediate_bad = 1;
    }
    if (MPI_Allreduce(&immediate_bad, &immediate_global_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 18);
        return 18;
    }
    after_allreduce = snapshot();
    if (after_allreduce.status != 0 || (global_bad == 0 &&
        (CPU_COUNT(&after_allreduce.mask) != 1 || !CPU_ISSET(target.cpu, &after_allreduce.mask)))) final_bad = 1;
    if (sleep_until_2s(&sleep_elapsed_ns) != 0) sleep_status = -1;
    else sleep_status = 0;
    after_2s = snapshot();
    if (sleep_status != 0 || after_2s.status != 0 || (global_bad == 0 &&
        (CPU_COUNT(&after_2s.mask) != 1 || !CPU_ISSET(target.cpu, &after_2s.mask)))) final_bad = 1;
    if (MPI_Allreduce(&final_bad, &final_global_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 19);
        return 19;
    }
    after_final_allreduce = snapshot();
    if (after_final_allreduce.status != 0 || (global_bad == 0 &&
        (CPU_COUNT(&after_final_allreduce.mask) != 1 || !CPU_ISSET(target.cpu, &after_final_allreduce.mask)))) final_bad = 1;
    if (MPI_Allreduce(&final_bad, &final_global_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 20);
        return 20;
    }
    if (write_record(output_dir, rank, pmi_rank, host, local_rank, world_size, local_size,
                     &pre, &post, topology_status, &target, pin_status, pin_error,
                     &immediate, &after_allreduce, &after_2s, &after_final_allreduce,
                     immediate_global_bad, final_global_bad, preflight_global_bad, sleep_status, sleep_elapsed_ns) != 0) {
        local_bad = 1;
    }
    if (MPI_Allreduce(&local_bad, &global_bad, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 21);
        return 21;
    }
    if (rank == 0) printf("POSTINIT_PIN_SUMMARY {\"world_size\":%d,\"preflight_error_ranks\":%d,\"immediate_audit_error_ranks\":%d,\"postwait_audit_error_ranks\":%d,\"record_write_error_ranks\":%d}\n",
                          world_size, preflight_global_bad, immediate_global_bad,
                          final_global_bad, global_bad);
    fflush(stdout);
    MPI_Comm_free(&local_comm);
    if (MPI_Finalize() != MPI_SUCCESS) return 22;
    return preflight_global_bad == 0 && global_bad == 0 && final_global_bad == 0 && immediate_global_bad == 0 ? 0 : 23;
}
