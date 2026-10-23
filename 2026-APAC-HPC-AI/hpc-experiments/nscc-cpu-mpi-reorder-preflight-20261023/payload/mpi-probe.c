#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void json_string(const char *s)
{
    const unsigned char *p = (const unsigned char *)(s ? s : "");
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

int main(int argc, char **argv)
{
    int rank = -1, size = -1, name_len = 0, cpu, first = 1;
    char processor[MPI_MAX_PROCESSOR_NAME + 1];
    const char *pmi_rank = getenv("PMI_RANK");
    cpu_set_t affinity;

    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) return 10;
    if (MPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS ||
        MPI_Comm_size(MPI_COMM_WORLD, &size) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 11);
        return 11;
    }
    if (MPI_Get_processor_name(processor, &name_len) != MPI_SUCCESS) {
        MPI_Abort(MPI_COMM_WORLD, 12);
        return 12;
    }
    processor[name_len < MPI_MAX_PROCESSOR_NAME ? name_len : MPI_MAX_PROCESSOR_NAME] = '\0';
    CPU_ZERO(&affinity);
    if (sched_getaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_getaffinity");
        MPI_Abort(MPI_COMM_WORLD, 13);
        return 13;
    }

    /* Prefix makes probe records distinguishable from PALS/MPICH diagnostics. */
    fputs("PROBE_JSON\t{\"rank\":", stdout);
    printf("%d,\"world_size\":%d,\"processor_name\":", rank, size);
    json_string(processor);
    fputs(",\"pmi_rank\":", stdout);
    if (pmi_rank) json_string(pmi_rank); else fputs("null", stdout);
    fputs(",\"affinity_cpus\":[", stdout);
    for (cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (CPU_ISSET(cpu, &affinity)) {
            if (!first) putchar(',');
            printf("%d", cpu);
            first = 0;
        }
    }
    fputs("]}\n", stdout);
    fflush(stdout);
    return MPI_Finalize() == MPI_SUCCESS ? 0 : 14;
}
