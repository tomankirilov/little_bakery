# SPDX-License-Identifier: GPL-2.0-or-later

import bpy


class DummyBakeHighPolyItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    color_attribute: bpy.props.StringProperty(name="Color Attribute", default="")


class DummyBakeLowPolyItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    high_polys: bpy.props.CollectionProperty(type=DummyBakeHighPolyItem)
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


class DummyBakeTextureSet(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    low_polys: bpy.props.CollectionProperty(type=DummyBakeLowPolyItem)
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
    ao_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    ao_suffix: bpy.props.StringProperty(name="Suffix", default="_ambient_occlusion")
    bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
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


class DummyBakeData(bpy.types.PropertyGroup):
    texture_sets: bpy.props.CollectionProperty(type=DummyBakeTextureSet)
    active_texture_index: bpy.props.IntProperty(default=-1)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=False)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=False)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=False)
    show_global_settings: bpy.props.BoolProperty(name="Show Global Settings", default=False)
    show_render_settings: bpy.props.BoolProperty(name="Show Rendering", default=False)
    show_bake_targets: bpy.props.BoolProperty(name="Show Bake Targets", default=False)
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
        subtype="DIR_PATH",
        default="",
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
    global_ao_custom_suffix: bpy.props.BoolProperty(name="Custom Suffix", default=False)
    global_ao_suffix: bpy.props.StringProperty(name="Suffix", default="_ambient_occlusion")
    global_bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    global_curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
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
    DummyBakeHighPolyItem,
    DummyBakeLowPolyItem,
    DummyBakeTextureSet,
    DummyBakeData,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dummy_bake_data = bpy.props.PointerProperty(type=DummyBakeData)


def unregister():
    del bpy.types.Scene.dummy_bake_data
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
