import os
import bpy

from .items import BakeryBakeTargetItem, BakeryTextureSet


# normalize the output folder name to a safe relative form.
def _normalize_output_dir(self, context):
    # normalize the output folder so it stays relative to the blend file.
    # Store output as a blend-relative subfolder name.
    current = (self.output_dir or "")
    value = current.strip()
    if not value:
        return
    value = value.replace("\\", "/")
    if value.startswith("//"):
        value = value[2:]
    if value.startswith("/"):
        value = value[1:]
    base_dir = bpy.path.abspath("//")
    if os.path.isabs(value):
        try:
            value = os.path.relpath(value, base_dir)
        except ValueError:
            value = os.path.basename(value)
    value = value.strip().lstrip("\\/")
    if value:
        value = f"/{value}"
    if value == current:
        return
    self.output_dir = value


class BakeryData(bpy.types.PropertyGroup):
    # centralize global settings here so the UI and bake logic share data.
    texture_sets: bpy.props.CollectionProperty(type=BakeryTextureSet)
    active_texture_index: bpy.props.IntProperty(default=-1)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=False)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=False)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=False)
    show_global_settings: bpy.props.BoolProperty(name="Show Global Settings", default=False)
    show_render_settings: bpy.props.BoolProperty(name="Show Rendering", default=False)
    show_render_image: bpy.props.BoolProperty(name="Show Image", default=False)
    show_render_padding: bpy.props.BoolProperty(name="Show Padding", default=False)
    show_render_cage: bpy.props.BoolProperty(name="Show Cage", default=False)
    show_bake_targets: bpy.props.BoolProperty(name="Show Bake Targets", default=False)
    show_output: bpy.props.BoolProperty(name="Show Output", default=False)
    show_about: bpy.props.BoolProperty(name="Show About", default=False)
    is_baking: bpy.props.BoolProperty(name="Is Baking", default=False)
    baking_set_name: bpy.props.StringProperty(name="Baking Set", default="")
    baking_target_name: bpy.props.StringProperty(name="Baking Target", default="")
    baking_progress: bpy.props.FloatProperty(name="Baking Progress", default=0.0, min=0.0, max=1.0)
    last_bake_duration: bpy.props.StringProperty(name="Last Bake Duration", default="")
    show_last_bake: bpy.props.BoolProperty(name="Show Last Bake", default=True)
    render_device: bpy.props.EnumProperty(
        name="Render Device",
        items=[
            ("CPU", "CPU", ""),
            ("GPU", "GPU", ""),
        ],
        default="CPU",
    )
    global_msaa: bpy.props.EnumProperty(
        name="MSAA",
        items=[
            ("NONE", "None", ""),
            ("2", "x2", ""),
            ("4", "x4", ""),
            ("8", "x8", ""),
        ],
        default="NONE",
    )
    output_dir: bpy.props.StringProperty(
        name="Output",
        subtype="NONE",
        default="/bakes",
        update=_normalize_output_dir,
    )
    output_format: bpy.props.EnumProperty(
        name="File Format",
        items=[
            ("PNG", "PNG", ""),
            ("TARGA", "TGA", ""),
        ],
        default="PNG",
    )
    output_color_mode: bpy.props.EnumProperty(
        name="Color",
        items=[
            ("RGB", "RGB", ""),
            ("RGBA", "RGBA", ""),
        ],
        default="RGBA",
    )
    output_color_depth: bpy.props.EnumProperty(
        name="Color Depth",
        items=[
            ("8", "8", ""),
            ("16", "16", ""),
        ],
        default="8",
    )
    output_png_compression: bpy.props.IntProperty(
        name="Compression",
        default=15,
        min=0,
        max=100,
        subtype="PERCENTAGE",
    )
    global_resolution: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    global_bake_targets: bpy.props.CollectionProperty(type=BakeryBakeTargetItem)
    active_global_bake_target_index: bpy.props.IntProperty(default=-1)
    global_extrusion: bpy.props.FloatProperty(name="Cage Extrusion", default=0.0, min=0.0)
    global_max_ray_distance: bpy.props.FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
    )
    global_dilation: bpy.props.IntProperty(name="Padding (px)", default=4, min=0)
    global_dilation_method: bpy.props.EnumProperty(
        name="Padding Method",
        items=[
            ("FAST", "Fast", "Original fast padding"),
            ("RADIAL", "Radial", "Smoother radial spread"),
        ],
        default="FAST",
    )
