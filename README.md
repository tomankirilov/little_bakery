# Little Bakery
## What is Little Bakery?
Little Bakery is a Blender addon that automates baking workflows for texturing.
It supports both low to high poly bakes and low poly only bakes.

## What makes it special?
Little Bakery allows for grouping many objects and baking them all with a single click. Settings are saved and rebaking is easy. Bake multiple texture types, multiple objects, combine, mix and match them as you wish.

## What it does
- Manages texture sets with low poly + high poly lists.
- Bakes multiple targets in one pass (per texture set or all sets).
- Adds configurable padding to remove UV seams.
- Supports MSAA-style supersampling by baking at a higher resolution and
  downscaling before saving.
- Lets you bake vertex color attributes by name, per high poly.

## Addon "Jargon"
- Texture Sets - refers to a set of low poly/high poly/cage files baked into a signle image set. Multiple low poly objects can be baked on the same image set, each with corresponding high poly.
- Global Settings
- Local Settings
- MSAA


## Bake targets
Bake targets can be also described as specific baked images. Each one has the option for a custom suffix when the file is saved. There are also some specific options per target.
- Tangent Space Normal
- Object Space Normal
- Ambient Occlusion
  - Local Only
  - Ray Count
  - Render Samples
  - Distance
  - Contrast
- Curvature
  - Exponent (Default = 2.2) - makes the curvature mid-level perfect mid gray. 
  - Contrast (Default = 0) - allows for adjusting the contrast of the curvature.
- Thickness
  - Ray Count
  - Render Samples
  - Distance
- Position
- Color Attribute
  - Color Attribute (Default = 'Color') - allows for baking of vertex color information. Can be overriten per set or high poly object.
- Random Island (ID Mask)

## Output settings
Currently only PNG and TGA are supported as output files.
- Format: PNG or TGA
- Color: RGB or RGBA
- TGA file format
- PNG file format: Color Depth (8/16), Compression (percentage)
Images are saved in the project (blend file) directory or a custom subdirectory.

## Rendering settings
Rendering settings:
- Render Device: CPU or GPU
- Resolution
- MSAA (None/x2/x4/x8)
- Padding (px)
- Cage Extrusion / Max Ray Distance

## Notes
- Only AO and Thickness use render samples; other targets render at 1 sample.
- Padding is done externally via OIIO.
- MSAA is achieved by rendering the texture at a higher resolution and scaling it down.

## About
- This addon was created by [Toman Tomanov (tomanov)](https://www.tomanov.art/)
- The addon is distributed under the [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://www.gnu.org/licenses/gpl-3.0.en.html)
