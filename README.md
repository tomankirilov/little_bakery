# Dummy Bake Tools

Dummy Bake Tools is a Blender addon that automates multi-target baking workflows
for low/high poly setups. It focuses on predictable results, repeatable output
settings, and quick switching between bake targets.

## What it does

- Manages texture sets with low poly + high poly lists.
- Bakes multiple targets in one pass (per texture set or all sets).
- Adds configurable padding (dilation) to reduce UV seams.
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
- Random Island

## Typical workflow

1. Create a Texture Set.
2. Add one or more Low Poly objects to the set.
3. For each Low Poly, add one or more High Poly objects.
4. Choose bake targets in Global Settings or override per texture set.
5. Set output format and resolution.
6. Run Bake All or Bake Selected Set.

## Color Attribute baking

Color Attribute allows baking vertex colors (or other named attributes).

- Global setting: `Color Attribute` name (default: "Color").
- Per texture set: override the name if needed.
- Per high poly: optional override. If non-empty, it wins for that object.
- Missing attribute names just bake black (acceptable fallback).

Internally, the addon creates a temporary copy of the high poly material and
node group per attribute name to avoid shared state conflicts. These copies are
removed after the bake finishes to keep the file clean.

## Output settings

Output settings live under the Output foldout:

- Format: PNG or TGA
- Color: RGB or RGBA
- PNG only: Color Depth (8/16), Compression (percentage)

The addon saves images with the chosen format and settings by temporarily
adjusting Blender's render image settings for each save.

## Rendering settings

Rendering settings live under the Rendering foldout:

- Render Device: CPU or GPU
- Resolution
- MSAA (None/x2/x4/x8)
- Dilation (px)
- Cage Extrusion / Max Ray Distance

MSAA is implemented by baking at a higher resolution and downscaling before
dilation is applied. Dilation is scaled with MSAA so padding stays consistent.

## Baking behavior notes

- Only AO and Thickness use render samples; other targets render at 1 sample.
- Dilation expands colors into transparent pixels to reduce edge seams.
- Baking uses temporary selection overrides so the right objects are active.

## Debug logging and progress

Enable Debug Logging in addon preferences to get detailed console output:

- Which texture set and target are being baked
- Per-object bake operations
- Dilation and downscaling steps
- Saved file paths

During baking, progress messages appear in Blender's status bar (e.g.
"Bake All: Texture Set 1 - Object Space Normal"), and a progress bar is shown.

## Tips

- Use Bake Selected Set to iterate quickly on one texture set.
- Keep MSAA at None or x2 for large sets to reduce memory usage.
- If output looks black for Color Attribute, verify the attribute name.

