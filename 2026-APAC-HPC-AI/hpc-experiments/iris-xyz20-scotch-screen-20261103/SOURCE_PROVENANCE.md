# XYZ source lineage

`accepted-xyz-source-manifest.json` is copied byte-for-byte from the retained `source-before.json` of job 2294262, not renamed from the zyx candidate manifest. The corresponding retained `source-after.json` is byte-identical. The inventory has 1,040 regular files and one approved `constant/polyMesh` symlink.

The same job’s source check reports order `xyz`, hierarchical factors `[7, 4, 2]`, and 41 canonical input pins. Its independent time-zero field seal contains 336 fields. The case carried a READY marker for the initialized xyz tree. Reproduction paths: `iris-order56-full150-reverse-20261028/completed-2294262/collected/cases/xyz/{source-before.json,source-after.json,copy-field-seal.json,READY}` and `.../runs/2294262/xyz-source-check.json`. The earlier 2294234 collection independently confirms the same xyz source-before/source-after hash.

This preparation does not claim a new remote rehash. Before a new measurement, the runtime must compare the full live xyz source and default Scotch source to their separate manifests, seal all 336 fields, then recheck source and fields after each solver arm. Never substitute the zyx manifest: partitioned meshes and initialized fields are method-specific.
