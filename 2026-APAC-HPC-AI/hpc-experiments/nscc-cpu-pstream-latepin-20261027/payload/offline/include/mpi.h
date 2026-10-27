#ifndef LATEPIN_NARROW_MPI_SYNTAX_SHIM_H
#define LATEPIN_NARROW_MPI_SYNTAX_SHIM_H
typedef int MPI_Comm;
typedef int MPI_Info;
typedef int MPI_Datatype;
typedef int MPI_Op;
#define MPI_MAX_PROCESSOR_NAME 256
#define MPI_COMM_WORLD 1
#define MPI_COMM_NULL 0
#define MPI_INFO_NULL 0
#define MPI_COMM_TYPE_SHARED 1
#define MPI_SUCCESS 0
#define MPI_ERR_OTHER 17
#define MPI_THREAD_SINGLE 0
#define MPI_INT 1
#define MPI_CHAR 2
#define MPI_BYTE 3
#define MPI_SUM 4
int PMPI_Init(int *, char ***);
int PMPI_Init_thread(int *, char ***, int, int *);
int PMPI_Query_thread(int *);
int PMPI_Comm_rank(MPI_Comm, int *);
int PMPI_Comm_size(MPI_Comm, int *);
int PMPI_Get_processor_name(char *, int *);
int PMPI_Allgather(const void *, int, MPI_Datatype, void *, int, MPI_Datatype, MPI_Comm);
int PMPI_Comm_split_type(MPI_Comm, int, int, MPI_Info, MPI_Comm *);
int PMPI_Bcast(void *, int, MPI_Datatype, int, MPI_Comm);
int PMPI_Allreduce(const void *, void *, int, MPI_Datatype, MPI_Op, MPI_Comm);
int PMPI_Comm_free(MPI_Comm *);
int PMPI_Finalize(void);
int MPI_Init(int *, char ***);
int MPI_Init_thread(int *, char ***, int, int *);
int MPI_Comm_rank(MPI_Comm, int *);
int MPI_Comm_size(MPI_Comm, int *);
int MPI_Get_processor_name(char *, int *);
int MPI_Allreduce(const void *, void *, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Finalize(void);
#endif
