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
    show_set_settings: bpy.props.BoolProperty(name="Show Set Settings", default=True)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    size: bpy.props.IntVectorProperty(
        name="Size",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    bake_normals_ws: bpy.props.BoolProperty(name="Normals WS", default=False)
    bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    bake_position: bpy.props.BoolProperty(name="Position", default=False)
    bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)


class DummyBakeData(bpy.types.PropertyGroup):
    texture_sets: bpy.props.CollectionProperty(type=DummyBakeTextureSet)
    active_texture_index: bpy.props.IntProperty(default=-1)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=True)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=True)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=True)
    show_global_settings: bpy.props.BoolProperty(name="Show Global Settings", default=True)
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
    output_dir: bpy.props.StringProperty(name="Output", subtype="DIR_PATH")
    global_size: bpy.props.IntVectorProperty(
        name="Size",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    global_bake_normals_ws: bpy.props.BoolProperty(name="Normals WS", default=False)
    global_bake_ambient_occlusion: bpy.props.BoolProperty(name="Ambient Occlusion", default=False)
    global_bake_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    global_bake_thickness: bpy.props.BoolProperty(name="Thickness", default=False)
    global_bake_position: bpy.props.BoolProperty(name="Position", default=False)
    global_bake_random_island: bpy.props.BoolProperty(name="Random Island", default=False)
    global_extrusion: bpy.props.FloatProperty(name="Extrusion", default=0.0, min=0.0)
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
