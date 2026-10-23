#define _GNU_SOURCE
#include <glob.h>
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
    cpu_set_t affinity;

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
    if (sched_getaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_getaffinity");
        MPI_Abort(MPI_COMM_WORLD, 13);
        return 13;
    }
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (CPU_ISSET(cpu, &affinity)) {
            selected_cpu = cpu;
            ++selected_count;
        }
    }
    if (selected_count != 1 || read_physical_core(selected_cpu, &package, &core) != 0 ||
        read_numa_node(selected_cpu, &numa_node) != 0) {
        fprintf(stderr, "rank %d could not prove single-CPU package/core/NUMA topology\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 14);
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
