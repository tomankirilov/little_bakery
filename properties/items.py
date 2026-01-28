import bpy


_BAKE_TARGET_LABELS = {
    "normal": "normal",
    "ambient_occlusion": "ambient_occlusion",
    "curvature": "curvature",
    "thickness": "thickness",
    "position": "position",
    "bakery_position": "bakery_position",
    "custom": "custom",
    "color_attribute": "color_attribute",
    "random_island": "random_island",
}


def _update_target_type(self, context):
    # keep the name in sync when the user hasn't typed a custom one.
    if not (self.name or "").strip():
        self.name = _BAKE_TARGET_LABELS.get(self.target_type, self.target_type)
    if self.target_type == "normal":
        self.normal_space = "TANGENT"


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
    override_cage_extrusion: bpy.props.BoolProperty(name="Cage Extrusion", default=False)
    override_cage_max_ray_distance: bpy.props.BoolProperty(name="Max Ray Distance", default=False)
    cage_extrusion: bpy.props.FloatProperty(name="Extrusion", default=0.0, min=0.0)
    cage_max_ray_distance: bpy.props.FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
    )


class BakeryBakeTargetItem(bpy.types.PropertyGroup):
    # one bake target entry with its own settings.
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    name: bpy.props.StringProperty(name="Name", default="")
    show_settings: bpy.props.BoolProperty(name="Show Target Settings", default=True)
    target_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("custom", "Custom", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
        ],
        default="ambient_occlusion",
        update=_update_target_type,
    )
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
    custom_material: bpy.props.PointerProperty(name="Material", type=bpy.types.Material)
    custom_bake_type: bpy.props.EnumProperty(
        name="Bake Type",
        items=[
            ("COMBINED", "Combined", ""),
            ("AO", "Ambient Occlusion", ""),
            ("SHADOW", "Shadow", ""),
            ("POSITION", "Position", ""),
            ("NORMAL", "Normal", ""),
            ("UV", "UV", ""),
            ("ROUGHNESS", "Roughness", ""),
            ("EMIT", "Emission", ""),
            ("ENVIRONMENT", "Environment", ""),
            ("DIFFUSE", "Diffuse", ""),
            ("GLOSSY", "Glossy", ""),
            ("TRANSMISSION", "Transmission", ""),
        ],
        default="EMIT",
    )

    normal_space: bpy.props.EnumProperty(
        name="Space",
        items=[
            ("TANGENT", "Tangent", ""),
            ("OBJECT", "Object", ""),
        ],
        default="TANGENT",
    )
    normal_r: bpy.props.EnumProperty(
        name="Swizzle R",
        items=[
            ("POS_X", "+X", ""),
            ("POS_Y", "+Y", ""),
            ("POS_Z", "+Z", ""),
            ("NEG_X", "-X", ""),
            ("NEG_Y", "-Y", ""),
            ("NEG_Z", "-Z", ""),
        ],
        default="POS_X",
    )
    normal_g: bpy.props.EnumProperty(
        name="Swizzle G",
        items=[
            ("POS_X", "+X", ""),
            ("POS_Y", "+Y", ""),
            ("POS_Z", "+Z", ""),
            ("NEG_X", "-X", ""),
            ("NEG_Y", "-Y", ""),
            ("NEG_Z", "-Z", ""),
        ],
        default="POS_Y",
    )
    normal_b: bpy.props.EnumProperty(
        name="Swizzle B",
        items=[
            ("POS_X", "+X", ""),
            ("POS_Y", "+Y", ""),
            ("POS_Z", "+Z", ""),
            ("NEG_X", "-X", ""),
            ("NEG_Y", "-Y", ""),
            ("NEG_Z", "-Z", ""),
        ],
        default="POS_Z",
    )


class BakeryTextureSet(bpy.types.PropertyGroup):
    # group bake targets and their settings per texture set for overrides.
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    low_polys: bpy.props.CollectionProperty(type=BakeryLowPolyItem)
    active_low_index: bpy.props.IntProperty(default=-1)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    override_resolution: bpy.props.BoolProperty(name="Resolution", default=False)
    override_dilation: bpy.props.BoolProperty(name="Padding", default=False)
    override_msaa: bpy.props.BoolProperty(name="MSAA", default=False)
    size: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    set_dilation: bpy.props.IntProperty(name="Padding (px)", default=4, min=0)
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
