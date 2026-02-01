import bpy


_BAKE_PASS_LABELS = {
    "normal": "normal",
    "ambient_occlusion": "ambient_occlusion",
    "curvature": "curvature",
    "curvature_from_normal": "curvature_from_normal",
    "thickness": "thickness",
    "position": "position",
    "bakery_position": "bakery_position",
    "custom": "custom",
    "color_attribute": "color_attribute",
    "random_island": "random_island",
}


def _update_pass_type(self, context):
    # keep the name in sync when the user hasn't typed a custom one.
    if not (self.name or "").strip():
        self.name = _BAKE_PASS_LABELS.get(self.pass_type, self.pass_type)
    if self.pass_type == "normal":
        self.normal_space = "TANGENT"


class BakerySourceMeshItem(bpy.types.PropertyGroup):
    # keep source entries lightweight; color_attribute is optional.
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    color_attribute: bpy.props.StringProperty(name="Color Attribute", default="")


class BakeryTargetMeshItem(bpy.types.PropertyGroup):
    # store per-target mesh cage settings here so each target can override.
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    source_meshes: bpy.props.CollectionProperty(type=BakerySourceMeshItem)
    active_source_index: bpy.props.IntProperty(default=-1)
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


class BakeryBakePassItem(bpy.types.PropertyGroup):
    # one bake pass entry with its own settings.
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    name: bpy.props.StringProperty(name="Name", default="")
    show_settings: bpy.props.BoolProperty(name="Show Pass Settings", default=True)
    pass_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("curvature_from_normal", "Curvature (Normal)", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
            ("custom", "Custom", ""),
        ],
        default="ambient_occlusion",
        update=_update_pass_type,
    )
    ao_samples: bpy.props.IntProperty(name="Ray Count", default=32, min=1)
    ao_render_samples: bpy.props.IntProperty(name="Render Samples", default=8, min=1)
    ao_normalize: bpy.props.BoolProperty(name="Normalize", default=False)
    ao_occlusion_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("SET", "Set", "Occlusion from only the sources in this texture set"),
            ("LOCAL", "Local", "Occlusion from only the sources linked to each target"),
            ("ISOLATED", "Isolated", "Occlusion per source mesh."),
        ],
        default="SET",
    )
    ao_distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.0)
    ao_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)

    curvature_exponent: bpy.props.FloatProperty(name="Exponent", default=2.2, min=0.0)
    curvature_contrast: bpy.props.FloatProperty(name="Contrast", default=0.0, min=0.0)
    normal_curv_radius: bpy.props.IntProperty(name="Radius (px)", default=2, min=1, max=8)
    normal_curv_strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0, max=4.0)
    normal_curv_contrast: bpy.props.FloatProperty(name="Contrast", default=0.2, min=0.0, max=1.0)
    normal_curv_invert: bpy.props.BoolProperty(name="Invert", default=False)

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
    sharpen: bpy.props.BoolProperty(name="Sharpen", default=False)
    sharpen_amount: bpy.props.FloatProperty(name="Amount", default=0.5, min=0.0, max=2.0)
    sharpen_per_channel: bpy.props.BoolProperty(name="Per Channel", default=False)


class BakeryTextureSet(bpy.types.PropertyGroup):
    # group bake passes and their settings per texture set for overrides.
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    target_meshes: bpy.props.CollectionProperty(type=BakeryTargetMeshItem)
    active_target_index: bpy.props.IntProperty(default=-1)
    override_global_settings: bpy.props.BoolProperty(name="Override Global Settings", default=False)
    override_resolution: bpy.props.BoolProperty(name="Resolution", default=False)
    override_dilation: bpy.props.BoolProperty(name="Padding", default=False)
    override_fxaa: bpy.props.BoolProperty(name="FXAA", default=False)
    override_msaa: bpy.props.BoolProperty(name="MSAA", default=False)
    size: bpy.props.IntVectorProperty(
        name="Resolution",
        size=2,
        default=(1024, 1024),
        min=1,
        subtype="NONE",
    )
    set_dilation: bpy.props.IntProperty(name="Padding (px)", default=4, min=0)
    set_fxaa_enabled: bpy.props.BoolProperty(name="FXAA", default=False)
    set_fxaa_threshold: bpy.props.FloatProperty(
        name="Threshold",
        default=0.1,
        min=0.0,
        max=1.0,
    )
    set_fxaa_blend: bpy.props.FloatProperty(
        name="Blend",
        default=0.5,
        min=0.0,
        max=1.0,
    )
    set_msaa: bpy.props.EnumProperty(
        name="MSAA",
        items=[
            ("NONE", "None", ""),
            ("2", "MSAA x2", ""),
            ("4", "MSAA x4", ""),
            ("8", "MSAA x8", ""),
        ],
        default="NONE",
    )
    override_bake_passes: bpy.props.BoolProperty(name="Override Bake Passes", default=False)
    bake_pass_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("ADD", "Add", ""),
            ("REPLACE", "Replace", ""),
        ],
        default="ADD",
    )
    bake_passes: bpy.props.CollectionProperty(type=BakeryBakePassItem)
    active_bake_pass_index: bpy.props.IntProperty(default=-1)


class BakeryStringItem(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(name="Value", default="")
