# Little Bakery - 1.1.0 changes:

## Breaking Compatibility with 1.0.0

* Bake Targets are now Bake Passes
* Targets are now Target Meshes
* Sources are now Source Meshes

* Because of renaming all files made with 1.0.0 will have to be rebuilt:
    * Bake Targets will be gone from the Little Bakery list and need to be added again.
    * Source Meshes Will be gone from the Little Bakery list and need to be added again.
    * Target meshes will be gone from the Little Bakery list and need to be added again.



## Anti-Aliasing:

* FXAA-like anti-aliasing option that works together with MSAA.



## New Passes:

* New Curvature mode extracted from the Normals.
* Opacity Pass



## Filters:

* Sharpen Filter added for each Pass as an option.
* Sharpen has a "Per Channel" mode that splits the image channels and sharpens them individually. Works for data passes like Normal Maps.



## UV Select:

* Now you can choose what UVs to bake on.
* If now UVs are set - the active UV Set is used.
* Per Target Mesh override.



## Quality of life:

* Info for baking is now more detailed. You receive bake time for each Target.
* Shortcuts:
    * Ctrl + Click on a Source or Target Mesh selects the mesh.
    * When adding sources the addon automatically populates with selected objects.




