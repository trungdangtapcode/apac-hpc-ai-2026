#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

#define MAX_CPU CPU_SETSIZE

static int read_mask(int *cpus, int *count) {
    cpu_set_t set;
    CPU_ZERO(&set);
    if (sched_getaffinity(0, sizeof(set), &set) != 0) return errno;
    *count = 0;
    for (int cpu = 0; cpu < MAX_CPU; ++cpu)
        if (CPU_ISSET(cpu, &set)) cpus[(*count)++] = cpu;
    return 0;
}

static int numa_node(int cpu) {
    char path[160];
    for (int node = 0; node < 256; ++node) {
        snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/node%d", cpu, node);
        if (access(path, F_OK) == 0) return node;
    }
    return -1;
}

static void print_ints(FILE *f, const int *values, int count) {
    fputc('[', f);
    for (int i = 0; i < count; ++i) fprintf(f, "%s%d", i ? "," : "", values[i]);
    fputc(']', f);
}

int main(int argc, char **argv) {
    int pre[MAX_CPU], post[MAX_CPU], npre = 0, npost = 0;
    int pre_rc = read_mask(pre, &npre); /* Immediately before MPI_Init. */
    int init_rc = MPI_Init(&argc, &argv);
    if (init_rc != MPI_SUCCESS) return 20;
    int rank = -1, size = -1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    int post_rc = read_mask(post, &npost); /* Main thread, immediately after MPI_Init. */
    const char *mode = argc > 1 ? argv[1] : "unknown";
    const char *out = getenv("PROBE_OUT");
    char host[256] = "unknown";
    gethostname(host, sizeof(host) - 1);
    int local_bad = pre_rc || post_rc || !out || rank < 0 || size < 1;
    char path[1024];
    int fd = -1;
    FILE *f = NULL;
    if (!local_bad) {
        int n = snprintf(path, sizeof(path), "%s/rank-%03d.json", out, rank);
        if (n < 0 || (size_t)n >= sizeof(path)) local_bad = 1;
        else {
            fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
            if (fd < 0) local_bad = 1;
            else if (!(f = fdopen(fd, "w"))) { close(fd); local_bad = 1; }
        }
    }
    if (!local_bad) {
        fprintf(f, "{\"mode\":\"%s\",\"rank\":%d,\"size\":%d,\"host\":\"%s\",", mode, rank, size, host);
        fprintf(f, "\"pre_mpi_init_errno\":%d,\"pre_cpus\":", pre_rc);
        print_ints(f, pre, npre);
        fprintf(f, ",\"post_mpi_init_errno\":%d,\"post_cpus\":", post_rc);
        print_ints(f, post, npost);
        fputs(",\"post_numa_nodes\":[", f);
        for (int i = 0; i < npost; ++i) fprintf(f, "%s%d", i ? "," : "", numa_node(post[i]));
        fputs("]}\n", f);
        if (fclose(f) != 0) local_bad = 1;
    }
    int any_bad = 0;
    MPI_Allreduce(&local_bad, &any_bad, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    MPI_Barrier(MPI_COMM_WORLD);
    MPI_Finalize();
    return any_bad ? 21 : 0;
}
