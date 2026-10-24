#define _GNU_SOURCE
#include <glob.h>
#include <errno.h>
#include <unistd.h>
#include <mpi.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void json_string(const char *value)
{
    const unsigned char *p = (const unsigned char *)(value ? value : "");
    putchar('"');
    while (*p) {
        if (*p == '"' || *p == '\\') {
            putchar('\\');
            putchar(*p);
        } else if (*p < 0x20) {
            printf("\\u%04x", (unsigned int)*p);
        } else {
            putchar(*p);
        }
        ++p;
    }
    putchar('"');
}

static int read_integer(const char *path, int *value)
{
    FILE *stream = fopen(path, "r");
    int status;
    if (!stream) return -1;
    status = fscanf(stream, "%d", value) == 1 ? 0 : -1;
    fclose(stream);
    return status;
}

static int read_physical_core(int cpu, int *package, int *core)
{
    char path[256];
    snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/topology/physical_package_id", cpu);
    if (read_integer(path, package) != 0) return -1;
    snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/topology/core_id", cpu);
    return read_integer(path, core);
}

static int cpulist_contains(const char *path, int cpu)
{
    FILE *stream = fopen(path, "r");
    char line[8192];
    char *cursor;
    if (!stream) return 0;
    if (!fgets(line, sizeof(line), stream)) {
        fclose(stream);
        return 0;
    }
    fclose(stream);
    cursor = line;
    while (*cursor) {
        char *end;
        long first = strtol(cursor, &end, 10);
        long last = first;
        if (end == cursor) break;
        cursor = end;
        if (*cursor == '-') {
            last = strtol(cursor + 1, &end, 10);
            if (end == cursor + 1) break;
            cursor = end;
        }
        if (cpu >= first && cpu <= last) return 1;
        if (*cursor == ',') ++cursor;
        else if (*cursor == '\n' || *cursor == '\0') break;
        else break;
    }
    return 0;
}

static int read_numa_node(int cpu, int *node)
{
    char pattern[256];
    glob_t paths;
    size_t i;
    int count = 0, glob_status;
    snprintf(pattern, sizeof(pattern), "/sys/devices/system/cpu/cpu%d/node[0-9]*", cpu);
    glob_status = glob(pattern, 0, NULL, &paths);
    if (glob_status != 0 && glob_status != GLOB_NOMATCH) return -1;
    if (glob_status == 0) {
        for (i = 0; i < paths.gl_pathc; ++i) {
            const char *base = strrchr(paths.gl_pathv[i], '/');
            int value;
            if (base && sscanf(base + 1, "node%d", &value) == 1) {
                *node = value;
                ++count;
            }
        }
        globfree(&paths);
    }
    if (count == 1) return 0;
    if (count > 1) return -1;

    /* Fall back to the node cpulist for kernels without per-CPU node symlinks. */
    snprintf(pattern, sizeof(pattern), "/sys/devices/system/node/node[0-9]*");
    if (glob(pattern, 0, NULL, &paths) != 0) return -1;
    for (i = 0; i < paths.gl_pathc; ++i) {
        char cpulist[512];
        const char *base = strrchr(paths.gl_pathv[i], '/');
        int value;
        if (!base || sscanf(base + 1, "node%d", &value) != 1) continue;
        snprintf(cpulist, sizeof(cpulist), "%s/cpulist", paths.gl_pathv[i]);
        if (cpulist_contains(cpulist, cpu)) {
            *node = value;
            ++count;
        }
    }
    globfree(&paths);
    return count == 1 ? 0 : -1;
}

int main(int argc, char **argv)
{
    int rank = -1, world_size = -1, name_length = 0;
    int cpu, selected_cpu = -1, selected_count = 0;
    int package = -1, core = -1, numa_node = -1;
    char processor[MPI_MAX_PROCESSOR_NAME + 1];
    char pmi_rank[128];
    const char *pmi = getenv("PMI_RANK");
    int has_pmi = pmi != NULL;
    cpu_set_t affinity, before_affinity;
    int before_status, affinity_status, core_status = -99, numa_status = -99;
    int core_errno = 0, numa_errno = 0, local_failed, total_failed = 0;
    CPU_ZERO(&before_affinity);
    before_status = sched_getaffinity(0, sizeof(before_affinity), &before_affinity);

    /* Snapshot the launcher diagnostic before MPI may adjust its environment. */
    snprintf(pmi_rank, sizeof(pmi_rank), "%s", pmi ? pmi : "");
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) return 10;
    if (MPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS ||
        MPI_Comm_size(MPI_COMM_WORLD, &world_size) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 11);
        return 11;
    }
    if (MPI_Get_processor_name(processor, &name_length) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 12);
        return 12;
    }
    processor[name_length < MPI_MAX_PROCESSOR_NAME ? name_length : MPI_MAX_PROCESSOR_NAME] = '\0';
    CPU_ZERO(&affinity);
    affinity_status = sched_getaffinity(0, sizeof(affinity), &affinity);
    if (affinity_status == 0) {
        for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
            if (CPU_ISSET(cpu, &affinity)) { selected_cpu = cpu; ++selected_count; }
        }
    }
    if (selected_count == 1) {
        errno = 0;
        core_status = read_physical_core(selected_cpu, &package, &core);
        core_errno = errno;
        errno = 0;
        numa_status = read_numa_node(selected_cpu, &numa_node);
        numa_errno = errno;
    }
    /* Emit one bounded diagnostic line per process before a collective decision.
       No rank aborts before the other ranks can retain their own failing check. */
    {
        char *record = NULL;
        size_t length = 0;
        FILE *stream = open_memstream(&record, &length);
        if (!stream) { MPI_Abort(MPI_COMM_WORLD, 16); return 16; }
        fprintf(stream, "TOPOLOGY_JSON\t{\"rank\":%d,\"pre_init_affinity_status\":%d,\"pre_init_cpus\":[", rank, before_status);
        int first = 1;
        for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, &before_affinity)) {
            fprintf(stream, "%s%d", first ? "" : ",", cpu); first = 0;
        }
        fprintf(stream, "],\"post_init_affinity_status\":%d,\"post_init_cpus\":[", affinity_status);
        first = 1;
        for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, &affinity)) {
            fprintf(stream, "%s%d", first ? "" : ",", cpu); first = 0;
        }
        fprintf(stream, "],\"core_status\":%d,\"core_errno\":%d,\"numa_status\":%d,\"numa_errno\":%d,\"package\":%d,\"core\":%d,\"numa\":%d}\n", core_status, core_errno, numa_status, numa_errno, package, core, numa_node);
        fclose(stream);
        if (length >= 4096 || write(STDOUT_FILENO, record, length) != (ssize_t)length) {
            free(record); MPI_Abort(MPI_COMM_WORLD, 17); return 17;
        }
        free(record);
    }
    local_failed = affinity_status != 0 || selected_count != 1 || core_status != 0 || numa_status != 0;
    if (MPI_Allreduce(&local_failed, &total_failed, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 18); return 18;
    }
    if (total_failed != 0) {
        if (rank == 0) fprintf(stderr, "TOPOLOGY_CHECK_FAILED ranks=%d; inspect TOPOLOGY_JSON records; candidate was not launched\n", total_failed);
        MPI_Finalize();
        return 14;
    }

    fputs("MAP_JSON\t{\"rank\":", stdout);
    printf("%d,\"world_size\":%d,\"processor_name\":", rank, world_size);
    json_string(processor);
    fputs(",\"pmi_rank\":", stdout);
    if (has_pmi) json_string(pmi_rank); else fputs("null", stdout);
    printf(",\"affinity_cpus\":[%d],\"physical_package_id\":%d,\"physical_core_id\":%d,\"numa_node\":%d}\n",
           selected_cpu, package, core, numa_node);
    fflush(stdout);
    return MPI_Finalize() == MPI_SUCCESS ? 0 : 15;
}
