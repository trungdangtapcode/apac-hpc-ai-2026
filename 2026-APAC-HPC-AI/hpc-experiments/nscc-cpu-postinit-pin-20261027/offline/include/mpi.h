#ifndef OFFLINE_MPI_H
#define OFFLINE_MPI_H
typedef int MPI_Comm;
typedef int MPI_Info;
typedef int MPI_Datatype;
typedef int MPI_Op;
#define MPI_MAX_PROCESSOR_NAME 255
#define MPI_COMM_WORLD 1
#define MPI_COMM_NULL 0
#define MPI_COMM_TYPE_SHARED 1
#define MPI_INFO_NULL 0
#define MPI_THREAD_SINGLE 0
#define MPI_SUCCESS 0
#define MPI_INT 1
#define MPI_CHAR 2
#define MPI_MIN 1
#define MPI_SUM 2
int MPI_Init_thread(int *, char ***, int, int *);
int MPI_Comm_rank(MPI_Comm, int *);
int MPI_Comm_size(MPI_Comm, int *);
int MPI_Get_processor_name(char *, int *);
int MPI_Comm_split_type(MPI_Comm, int, int, MPI_Info, MPI_Comm *);
int MPI_Allgather(const void *, int, MPI_Datatype, void *, int, MPI_Datatype, MPI_Comm);
int MPI_Bcast(void *, int, MPI_Datatype, int, MPI_Comm);
int MPI_Allreduce(const void *, void *, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Abort(MPI_Comm, int);
int MPI_Comm_free(MPI_Comm *);
int MPI_Finalize(void);
#endif
