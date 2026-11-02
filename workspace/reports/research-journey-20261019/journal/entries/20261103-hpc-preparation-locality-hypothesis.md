# A deeper hypothesis from the first in-solver samples

The owner asked again to think about improvements. We retained a partial running-job snapshot rather than treating it as a full result. In-solver MemAvailable reaches about 40 GiB, much lower than prior endpoints; reclaim and allocation counters do not consistently explain timing. We therefore qualify preparation-driven page-cache placement across NUMA nodes and MPI busy waiting before assuming fewer ranks or a malloc parameter will help.

The tempting fixed 1 MiB glibc trim setting was rejected as an unqualified recommendation: the effective default is adaptive and unknown. No extra job or budget reservation is made while 2294671 occupies the one-allocation cap. Full question, evidence, controls, limits, references and falsifiers are in the [mechanism review](/home/apacsc42/workspace/reports/hpc-next-directions-20261103/MECHANISMS.md).
