# Pinned runtime evidence

The source files are exact retained snapshots from the SGLang image used by the
successful 223091 no-model probe and failed 223055 full integration. The patched
nixl-conn.py is the existing runtime adapter, not a new transport repair.
SHA256 values are recorded in validation.json and verified inside each GPU rank.
The common connection, staging and NIXL API files retain their original licence
headers. Runtime SGLang helpers are extracted from the installed files after
hash verification; the retained copies support CPU tests and recovery.

CPU rehearsal uses an isolated temporary environment with actual NumPy, with
its version reported in numpy-rehearsal.stdout. It exercises the pinned Python
methods without a GPU/network backend. It is not the container NumPy identity.
The runtime image is checked for existence before submission, and both ranks
record the actual NIXL binding/API and PyTorch identities after startup.
