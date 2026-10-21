# Pinned API evidence

Selected file extracted on CPU using unsquashfs with two processors from
/scratch/enroot-images/sglang-harbor.sqsh, source member
usr/local/lib/python3.12/dist-packages/nixl_cu13/_api.py.
SHA256: 27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea.
Original NVIDIA Apache-2.0 header is preserved. Runtime probes must match it.

The first local extraction commands used unsupported -cat and then an already
existing destination directory; both failed without GPU activity or source
mutation. The successful extraction used a fresh nonexisting child destination.
The current installed API and the pinned SGLang adapter govern the probe;
public main-branch examples are references, not assumed runtime version proof.
