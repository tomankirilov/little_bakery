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
    cage_extrusion: bpy.props.FloatProperty(name="Extrusion", default=0.0, min=0.0)
    cage_max_ray_distance: bpy.props.FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
    )


class BakeryTextureSet(bpy.types.PropertyGroup):
    # group bake targets and their settings per texture set for overrides.
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    low_polys: bpy.props.CollectionProperty(type=BakeryLowPolyItem)
    active_low_index: bpy.props.IntProperty(default=-1)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    size: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    bake_normals_ws: bpy.props.BoolProperty(name="Object Space Normal", default=False)
    bake_tangent_normal: bpy.props.BoolProperty(name="Tangent Space Normal", default=False)
    normals_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    normals_suffix: bpy.props.StringProperty(name="Suffix", default="_normals_ws")
    tangent_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    tangent_suffix: bpy.props.StringProperty(name="Suffix", default="_tangent_normal")
    bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    ao_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    ao_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    ao_local_only: bpy.props.BoolProperty(name="Local Only", default=False)
    ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    ao_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)
    ao_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    ao_suffix: bpy.props.StringProperty(name="Suffix", default="_ambient_occlusion")
    bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    curvature_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)
    curvature_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    curvature_suffix: bpy.props.StringProperty(name="Suffix", default="_curvature")
    bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    thickness_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    thickness_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    thickness_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    thickness_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    thickness_suffix: bpy.props.StringProperty(name="Suffix", default="_thickness")
    bake_position: bpy.props.BoolProperty(name="Position", default=False)
    bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)
    bake_color_attribute: bpy.props.BoolProperty(name="Color Attribute", default=False)
    position_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    position_suffix: bpy.props.StringProperty(name="Suffix", default="_position")
    random_island_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    random_island_suffix: bpy.props.StringProperty(name="Suffix", default="_random_island")
    color_attribute_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    color_attribute_suffix: bpy.props.StringProperty(name="Suffix", default="_color_attribute")
    color_attribute_name: bpy.props.StringProperty(name="Color Attribute", default="Color")


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
    global_bake_normals_ws: bpy.props.BoolProperty(name="Object Space Normal", default=False)
    global_bake_tangent_normal: bpy.props.BoolProperty(name="Tangent Space Normal", default=False)
    global_normals_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_normals_suffix: bpy.props.StringProperty(name="Suffix", default="_normals_ws")
    global_tangent_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_tangent_suffix: bpy.props.StringProperty(name="Suffix", default="_tangent_normal")
    global_bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    global_ao_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    global_ao_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    global_ao_local_only: bpy.props.BoolProperty(name="Local Only", default=False)
    global_ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    global_ao_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)
    global_ao_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_ao_suffix: bpy.props.StringProperty(name="Suffix", default="_ambient_occlusion")
    global_bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    global_curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    global_curvature_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)
    global_curvature_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_curvature_suffix: bpy.props.StringProperty(name="Suffix", default="_curvature")
    global_bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    global_thickness_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    global_thickness_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    global_thickness_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    global_thickness_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_thickness_suffix: bpy.props.StringProperty(name="Suffix", default="_thickness")
    global_bake_position: bpy.props.BoolProperty(name="Position", default=False)
    global_bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)
    global_bake_color_attribute: bpy.props.BoolProperty(name="Color Attribute", default=False)
    global_position_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_position_suffix: bpy.props.StringProperty(name="Suffix", default="_position")
    global_random_island_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_random_island_suffix: bpy.props.StringProperty(name="Suffix", default="_random_island")
    global_color_attribute_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_color_attribute_suffix: bpy.props.StringProperty(name="Suffix", default="_color_attribute")
    global_color_attribute_name: bpy.props.StringProperty(name="Color Attribute", default="Color")
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
