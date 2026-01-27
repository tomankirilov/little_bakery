import os
import bpy


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


class BakeryHighPolyItem(bpy.types.PropertyGroup):
    # keep high-poly entries lightweight; color_attribute is optional.
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    color_attribute: bpy.props.StringProperty(name="Color Attribute", default="")


class BakeryLowPolyItem(bpy.types.PropertyGroup):
    # store per-low-poly cage settings here so each low poly can override.
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    high_polys: bpy.props.CollectionProperty(type=BakeryHighPolyItem)
    active_high_index: bpy.props.IntProperty(default=-1)
    cage_object: bpy.props.PointerProperty(type=bpy.types.Object)
    use_cage: bpy.props.BoolProperty(name="Cage", default=False)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    override_cage_extrusion: bpy.props.BoolProperty(name="Cage Extrusion", default=True)
    override_cage_max_ray_distance: bpy.props.BoolProperty(name="Max Ray Distance", default=True)
    cage_extrusion: bpy.props.FloatProperty(name="Extrusion", default=0.0, min=0.0)
    cage_max_ray_distance: bpy.props.FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
    )


class BakeryBakeTargetItem(bpy.types.PropertyGroup):
    # one bake target entry with its own settings.
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    target_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("tangent_normal", "Tangent Space Normal", ""),
            ("normals_ws", "Object Space Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
        ],
        default="ambient_occlusion",
    )
    custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    suffix: bpy.props.StringProperty(name="Suffix", default="")

    ao_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    ao_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    ao_occlusion_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("GLOBAL", "Global", "Occlusion from all meshes in the scene"),
            ("SET", "Set", "Occlusion from only the high polys in this texture set"),
            ("LOCAL", "Local", "Occlusion from only the high polys linked to each low poly"),
            ("ISOLATED", "Isolated", "Occlusion per high poly mesh."),
        ],
        default="SET",
    )
    ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    ao_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)

    curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    curvature_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)

    thickness_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    thickness_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    thickness_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)

    color_attribute_name: bpy.props.StringProperty(name="Color Attribute", default="Color")


class BakeryTextureSet(bpy.types.PropertyGroup):
    # group bake targets and their settings per texture set for overrides.
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    low_polys: bpy.props.CollectionProperty(type=BakeryLowPolyItem)
    active_low_index: bpy.props.IntProperty(default=-1)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    override_resolution: bpy.props.BoolProperty(name="Resolution", default=True)
    override_dilation: bpy.props.BoolProperty(name="Dilation", default=False)
    override_msaa: bpy.props.BoolProperty(name="MSAA", default=False)
    size: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    set_dilation: bpy.props.IntProperty(name="Dilation (px)", default=4, min=0)
    set_msaa: bpy.props.EnumProperty(
        name="MSAA",
        items=[
            ("NONE", "None", ""),
            ("2", "x2", ""),
            ("4", "x4", ""),
            ("8", "x8", ""),
        ],
        default="NONE",
    )
    override_bake_targets: bpy.props.BoolProperty(name="Override Bake Targets", default=False)
    bake_target_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("ADD", "Add", ""),
            ("REPLACE", "Replace", ""),
        ],
        default="ADD",
    )
    bake_targets: bpy.props.CollectionProperty(type=BakeryBakeTargetItem)
    active_bake_target_index: bpy.props.IntProperty(default=-1)


class BakeryData(bpy.types.PropertyGroup):
    # centralize global settings here so the UI and bake logic share data.
    texture_sets: bpy.props.CollectionProperty(type=BakeryTextureSet)
    active_texture_index: bpy.props.IntProperty(default=-1)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=False)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=False)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=False)
    show_global_settings: bpy.props.BoolProperty(name="Show Global Settings", default=False)
    show_render_settings: bpy.props.BoolProperty(name="Show Rendering", default=False)
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
        default="",
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
    global_dilation: bpy.props.IntProperty(name="Dilation (px)", default=4, min=0)


classes = (
    BakeryHighPolyItem,
    BakeryLowPolyItem,
    BakeryBakeTargetItem,
    BakeryTextureSet,
    BakeryData,
)


# register property groups and attach them to the Scene.
def register():
    # register the property groups and attach them to the Scene.
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bakery_data = bpy.props.PointerProperty(type=BakeryData)


# unregister property groups and remove the Scene pointer.
def unregister():
    # remove the Scene pointer and unregister classes in reverse.
    del bpy.types.Scene.bakery_data
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
