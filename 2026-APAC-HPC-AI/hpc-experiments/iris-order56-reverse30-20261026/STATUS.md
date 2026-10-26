# Reverse-order screen admitted

**2294132** was submitted once at **16:30:14 UTC on 26 October 2026**. A fresh Slurm query at 16:30:35 UTC reports RUNNING on iris001. The own queue was empty at admission.

The frozen job runs zyx then xyz, 30 steps and 29 timed intervals per arm. Both use independent copies of the same initialized source cases as parent 2294099. Maximum is 45 minutes on 56 allocated CPUs: **42 allocated CPU-hours**. Solver caps are 1,150 seconds per arm; source/copy/numerical validation and global deadline guards remain required. Memory/VM snapshots run outside native solver timing and record their collection duration. No cache flush or system tuning is performed.

After reservation the existing shared Iris ledger commits **211 of 224 allocated CPU-hours**: 169 consumed conservative allowance plus 42 reserved, leaving 13 until terminal reconciliation. No NSCC SU is used by Iris. The parent apparent 26.94% improvement is still provisional; this is a reverse-order short control, not a full-length or official score. Do not modify this submitted payload in place.
