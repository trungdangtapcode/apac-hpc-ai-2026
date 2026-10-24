# Replace an unexecuted scheduler job, preserve the experiment

R6 job224466 became terminal while the owner-authorized queue order was adjusted to let a5GPU diagnostic fit before the16GPU request. qrls returned35 and qstat-xf showsF with no allocation start, resources_used or Exit_status. The precise PBS transition cause is not established; never describe it as a completed transport experiment. D5R2 job224553 was released and is actually running.

This replacement keeps R6 model/source/runtime arguments, serial-then-concurrent semantic requests and all gates. Only the allocation namespace changes. It must run after224553 to preserve one active AI allocation. Retain the old R6 maximum until terminal/accounting reconciliation. No benchmark or1600-ID stage is added; no transport result exists. Preserve original queued-source payload and partial queue-order audit.
