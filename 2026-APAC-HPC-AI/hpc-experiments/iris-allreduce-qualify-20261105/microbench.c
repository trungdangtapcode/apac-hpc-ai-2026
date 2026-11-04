#define _POSIX_C_SOURCE 200809L
#include <mpi.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WARMUPS 100
#define ITERATIONS 1000
#define BLOCKS 2
#define MAX_COUNT 8

static int compare_double(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}
static double percentile(const double *values, int n, double p) {
    double copy[ITERATIONS];
    memcpy(copy, values, (size_t)n * sizeof(double));
    qsort(copy, (size_t)n, sizeof(double), compare_double);
    int index = (int)ceil(p * n) - 1;
    if (index < 0) index = 0;
    if (index >= n) index = n - 1;
    return copy[index];
}
static int run_bench(const char *path) {
    int rank, size, failed = 0;
    char library[MPI_MAX_LIBRARY_VERSION_STRING];
    int library_len = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Get_library_version(library, &library_len);
    library[library_len] = '\0';
    if (size != 56) failed = 1;
    double send[MAX_COUNT], recv[MAX_COUNT];
    for (int i = 0; i < MAX_COUNT; ++i) send[i] = (double)(rank + 1) * (double)(i + 1);
    const int counts[2] = {1, 8};
    double local[ITERATIONS], worst[ITERATIONS];
    FILE *out = NULL;
    if (rank == 0) {
        out = fopen(path, "w");
        if (!out) failed = 1;
    }
    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (any_failed) { if (out) fclose(out); return 2; }
    if (rank == 0) {
        fprintf(out, "{\"ranks\":%d,\"warmup_calls_per_count\":%d,\"iterations_per_block\":%d,\"blocks\":%d,\"library_version\":\"", size, WARMUPS, ITERATIONS, BLOCKS);
        for (int i = 0; i < library_len; ++i) {
            unsigned char c = (unsigned char)library[i];
            if (c == '"' || c == '\\') fputc('\\', out);
            if (c >= 32) fputc(c, out);
        }
        fprintf(out, "\",\"payloads\":[");
    }
    for (int ci = 0; ci < 2; ++ci) {
        int count = counts[ci];
        double expected[MAX_COUNT];
        for (int i = 0; i < count; ++i) expected[i] = (double)(size * (size + 1) / 2) * (double)(i + 1);
        for (int i = 0; i < WARMUPS; ++i) MPI_Allreduce(send, recv, count, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        for (int i = 0; i < count; ++i) if (fabs(recv[i] - expected[i]) > 1e-9) failed = 1;
        if (rank == 0) fprintf(out, "%s{\"count\":%d,\"bytes\":%d,\"blocks\":[", ci ? "," : "", count, count * (int)sizeof(double));
        for (int block = 0; block < BLOCKS; ++block) {
            MPI_Barrier(MPI_COMM_WORLD);
            for (int iter = 0; iter < ITERATIONS; ++iter) {
                double start = MPI_Wtime();
                MPI_Allreduce(send, recv, count, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
                local[iter] = MPI_Wtime() - start;
                for (int i = 0; i < count; ++i) if (fabs(recv[i] - expected[i]) > 1e-9) failed = 1;
            }
            MPI_Allreduce(local, worst, ITERATIONS, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
            int block_failed = 0;
            MPI_Allreduce(&failed, &block_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
            failed = block_failed;
            if (rank == 0) {
                fprintf(out, "%s{\"median_worst_rank_seconds\":%.12g,\"p95_worst_rank_seconds\":%.12g,\"raw_worst_rank_seconds\":[", block ? "," : "", percentile(worst, ITERATIONS, 0.50), percentile(worst, ITERATIONS, 0.95));
                for (int i = 0; i < ITERATIONS; ++i) fprintf(out, "%s%.12g", i ? "," : "", worst[i]);
                fprintf(out, "]}");
            }
        }
        if (rank == 0) fprintf(out, "]}");
    }
    if (rank == 0) { fprintf(out, "],\"correctness\":\"%s\"}\n", failed ? "FAIL" : "PASS"); fclose(out); }
    int global_failed = 0;
    MPI_Allreduce(&failed, &global_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    return global_failed ? 3 : 0;
}
static int run_probe(void) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    double value = (double)(rank + 1), sum = 0.0;
    MPI_Allreduce(&value, &sum, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
    int ok = size == 56 && fabs(sum - (double)(size * (size + 1) / 2)) < 1e-9;
    if (rank == 0) printf("probe ranks=%d allreduce_sum=%.0f correctness=%s\n", size, sum, ok ? "PASS" : "FAIL");
    return ok ? 0 : 3;
}
int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, rc = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    if (argc == 2 && strcmp(argv[1], "--probe") == 0) rc = run_probe();
    else if (argc == 3 && strcmp(argv[1], "--output") == 0) rc = run_bench(argv[2]);
    else { if (rank == 0) fprintf(stderr, "usage: %s --probe | --output FILE\n", argv[0]); rc = 64; }
    int max_rc = 0;
    MPI_Allreduce(&rc, &max_rc, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    MPI_Finalize();
    return max_rc;
}
