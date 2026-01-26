# Dummy Bake Tools
Dummy Bake Tools is a Blender addon that automates multi-target baking workflows
for low/high poly setups. It focuses on predictable results, repeatable output
settings, and quick switching between bake targets.

## What it does
- Manages texture sets with low poly + high poly lists.
- Bakes multiple targets in one pass (per texture set or all sets).
- Adds configurable padding (dilation) to remove UV seams.
- Supports MSAA-style supersampling by baking at a higher resolution and
  downscaling before saving.
- Lets you bake vertex color attributes by name, per high poly.

## Bake targets
Global and per-texture-set targets:
- Tangent Space Normal
- Object Space Normal
- Ambient Occlusion
- Curvature
- Thickness
- Position
- Color Attribute
- Random Island (ID Mask)

## Color Attribute baking
Color Attribute allows baking vertex colors.

- Global setting: `Color Attribute` name (default: "Color").
- Per texture set: override the name if needed.
- Per high poly: optional override. If non-empty, it wins for that object.
- Missing attribute names just bake black.

## Output settings
Output settings:
- Format: PNG or TGA
- Color: RGB or RGBA
- TGA file format
- PNG file format: Color Depth (8/16), Compression (percentage)
- Images are saved in the project (blend file) directory or a custom subdirectory.

## Rendering settings
Rendering settings:
- Render Device: CPU or GPU
- Resolution
- MSAA (None/x2/x4/x8)
- Dilation (px)
- Cage Extrusion / Max Ray Distance

## Baking behavior notes
- Only AO and Thickness use render samples; other targets render at 1 sample.
- Dilation is done externally via OIIO.

## About
- This addon was created by Toman Tomanov (tomanov)
- The addon is distributed under the GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007