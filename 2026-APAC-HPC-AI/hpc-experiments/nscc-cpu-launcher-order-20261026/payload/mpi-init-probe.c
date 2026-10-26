#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int snapshot(cpu_set_t *set, int *err)
{
    CPU_ZERO(set);
    if (sched_getaffinity(0, sizeof(*set), set) == 0) return 0;
    *err = errno;
    return -1;
}

static void cpus_json(FILE *f, const cpu_set_t *set)
{
    int i, first = 1;
    fputc('[', f);
    for (i = 0; i < CPU_SETSIZE; ++i) if (CPU_ISSET(i, set)) {
        fprintf(f, "%s%d", first ? "" : ",", i);
        first = 0;
    }
    fputc(']', f);
}

static int write_record(const char *dir, const char *phase, int rank,
                        int pmi_valid, long pmi_rank, const char *host,
                        int status, int err, const cpu_set_t *set)
{
    char path[1024], body[65536];
    int n, fd, written;
    FILE *f = fmemopen(body, sizeof(body), "w");
    if (!f) return -1;
    fprintf(f, "{\"phase\":\"%s\",\"rank\":%d,\"pmi_rank\":", phase, rank);
    if (pmi_valid) fprintf(f, "%ld", pmi_rank); else fputs("null", f);
    fprintf(f, ",\"host\":\"%s\",\"affinity_status\":%d,\"errno\":%d,\"cpus\":", host, status, err);
    cpus_json(f, set);
    fputs("}\n", f);
    if (ferror(f)) { fclose(f); return -1; }
    n = (int)ftell(f);
    fclose(f);
    if (n < 0 || n >= (int)sizeof(body)) return -1;
    if (snprintf(path, sizeof(path), "%s/rank-%04d.json", dir, rank) >= (int)sizeof(path)) return -1;
    fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return -1;
    written = (int)write(fd, body, (size_t)n);
    if (close(fd) != 0 || written != n) return -1;
    return 0;
}

int main(int argc, char **argv)
{
    const char *dir, *pmi = getenv("PMI_RANK");
    char *end = NULL, host[MPI_MAX_PROCESSOR_NAME + 1], pre_host[MPI_MAX_PROCESSOR_NAME + 1];
    long pmi_rank = -1;
    int pmi_valid = 0, pre_err = 0, post_err = 0;
    int provided = -1, post_status, rank = -1, size = -1, name_len = 0;
    int local_error, total_errors = 0, init_rc, capture_error = 0;
    cpu_set_t pre_set, post_set;
    int pre_rc = snapshot(&pre_set, &pre_err);
    dir = argc > 1 ? argv[1] : ".";
    if (pmi && *pmi) {
        errno = 0;
        pmi_rank = strtol(pmi, &end, 10);
        pmi_valid = errno == 0 && end && *end == '\0' && end != pmi;
    }
    if (gethostname(pre_host, sizeof(pre_host)) != 0) strcpy(pre_host, "gethostname_error");
    pre_host[sizeof(pre_host) - 1] = '\0';
    /* Retain entry evidence even when a later MPI initialization hangs. */
    if (pmi_valid && pmi_rank >= 0 && pmi_rank < 512) {
        char pre_dir[1024];
        if (snprintf(pre_dir, sizeof(pre_dir), "%s/pre", dir) >= (int)sizeof(pre_dir)
            || write_record(pre_dir, "before_mpi_init_thread", (int)pmi_rank,
                            pmi_valid, pmi_rank, pre_host, pre_rc, pre_err, &pre_set) != 0)
            capture_error = 1;
    } else capture_error = 1;
    init_rc = MPI_Init_thread(&argc, &argv, MPI_THREAD_SINGLE, &provided);
    if (init_rc != MPI_SUCCESS) {
        fprintf(stderr, "MPI_Init_thread failed rc=%d pre_affinity_status=%d errno=%d\n", init_rc, pre_rc, pre_err);
        return 10;
    }
    if (MPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS) rank = -1;
    if (MPI_Comm_size(MPI_COMM_WORLD, &size) != MPI_SUCCESS) size = -1;
    if (MPI_Get_processor_name(host, &name_len) != MPI_SUCCESS) {
        strcpy(host, "MPI_Get_processor_name_error");
    } else host[name_len < MPI_MAX_PROCESSOR_NAME ? name_len : MPI_MAX_PROCESSOR_NAME] = '\0';
    post_status = snapshot(&post_set, &post_err);
    if (rank >= 0) {
        if (write_record(dir, "after_mpi_init_thread", rank, pmi_valid,
                         pmi_rank, host, post_status, post_err, &post_set) != 0) {
            fprintf(stderr, "rank %d could not write post-init record: %s\n", rank, strerror(errno));
            capture_error = 1;
        }
    }
    local_error = rank < 0 || size != 512 || pre_rc != 0 || post_status != 0 || !pmi_valid || capture_error;
    if (MPI_Allreduce(&local_error, &total_errors, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD) != MPI_SUCCESS)
        total_errors = -1;
    if (rank == 0) printf("MPI_SUMMARY_JSON {\"world_size\":%d,\"ranks_with_capture_or_identity_errors\":%d}\n", size, total_errors);
    fflush(stdout);
    return MPI_Finalize() == MPI_SUCCESS && total_errors == 0 && provided >= MPI_THREAD_SINGLE ? 0 : 11;
}
