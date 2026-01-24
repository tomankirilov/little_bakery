# SPDX-License-Identifier: GPL-2.0-or-later

import bpy


class DummyBakeHighPolyItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)


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
    show_set_settings: bpy.props.BoolProperty(name="Show Set Settings", default=False)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    size: bpy.props.IntVectorProperty(
        name="Size",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    bake_normals_ws: bpy.props.BoolProperty(name="Normals WS", default=False)
    normals_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    normals_prefix: bpy.props.StringProperty(name="Prefix", default="_normals_ws")
    bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    ao_samples: bpy.props.IntProperty(name="Samples", default=32, min=1)
    ao_local_only: bpy.props.BoolProperty(name="Local Only", default=False)
    ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    ao_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    ao_prefix: bpy.props.StringProperty(name="Prefix", default="_ambient_occlusion")
    bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    curvature_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    curvature_prefix: bpy.props.StringProperty(name="Prefix", default="_curvature")
    bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    thickness_samples: bpy.props.IntProperty(name="Samples", default=32, min=1)
    thickness_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    thickness_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    thickness_prefix: bpy.props.StringProperty(name="Prefix", default="_thickness")
    bake_position: bpy.props.BoolProperty(name="Position", default=False)
    bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)
    position_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    position_prefix: bpy.props.StringProperty(name="Prefix", default="_position")
    random_island_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    random_island_prefix: bpy.props.StringProperty(name="Prefix", default="_random_island")


class DummyBakeData(bpy.types.PropertyGroup):
    texture_sets: bpy.props.CollectionProperty(type=DummyBakeTextureSet)
    active_texture_index: bpy.props.IntProperty(default=-1)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=False)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=False)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=False)
    show_global_settings: bpy.props.BoolProperty(name="Show Global Settings", default=False)
    render_device: bpy.props.EnumProperty(
        name="Render Device",
        items=[
            ("CPU", "CPU", ""),
            ("GPU", "GPU", ""),
        ],
        default="GPU",
    )
    render_samples: bpy.props.IntProperty(
        name="Render Samples",
        default=1024,
        min=1,
    )
    output_dir: bpy.props.StringProperty(
        name="Output",
        subtype="DIR_PATH",
        default="//",
    )
    global_resolution: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    global_bake_normals_ws: bpy.props.BoolProperty(name="Normals WS", default=False)
    global_normals_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_normals_prefix: bpy.props.StringProperty(name="Prefix", default="_normals_ws")
    global_bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    global_ao_samples: bpy.props.IntProperty(name="Samples", default=32, min=1)
    global_ao_local_only: bpy.props.BoolProperty(name="Local Only", default=False)
    global_ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    global_ao_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_ao_prefix: bpy.props.StringProperty(name="Prefix", default="_ambient_occlusion")
    global_bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    global_curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    global_curvature_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_curvature_prefix: bpy.props.StringProperty(name="Prefix", default="_curvature")
    global_bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    global_thickness_samples: bpy.props.IntProperty(name="Samples", default=32, min=1)
    global_thickness_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    global_thickness_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_thickness_prefix: bpy.props.StringProperty(name="Prefix", default="_thickness")
    global_bake_position: bpy.props.BoolProperty(name="Position", default=False)
    global_bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)
    global_position_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_position_prefix: bpy.props.StringProperty(name="Prefix", default="_position")
    global_random_island_custom_prefix: bpy.props.BoolProperty(name="Custom Prefix", default=False)
    global_random_island_prefix: bpy.props.StringProperty(name="Prefix", default="_random_island")
    global_extrusion: bpy.props.FloatProperty(name="Cage Extrusion", default=0.0, min=0.0)
    global_max_ray_distance: bpy.props.FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
    )


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
