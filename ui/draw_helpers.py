import bpy


# create a slightly indented column for nested UI sections.
def _indent_column(layout):
    # indent groups so nested options are easier to scan.
    # use this to visually nest settings under foldouts.
    row = layout.row()
    row.separator()
    return row.column(align=True)


# draw a resolution row with a label and a field.
def _draw_resolution_row(layout, obj, prop_name, target="GLOBAL"):
    # draw the resolution in a consistent label/value layout.
    # keep resolution rows consistent across global and per-set UI.
    label_row = layout.row(align=True)
    label_row.label(text="Resolution")
    field_col = _indent_column(layout)
    res_col = field_col.column(align=True)
    res_col.prop(obj, prop_name, index=0, text="")
    res_col.prop(obj, prop_name, index=1, text="")
    controls = field_col.row(align=True)
    op = controls.operator("bakery.resolution_scale", text="Half", icon="TRIA_DOWN")
    op.target = target
    op.factor = 0.5
    op = controls.operator("bakery.resolution_scale", text="Double", icon="TRIA_UP")
    op.target = target
    op.factor = 2.0


# draw settings for a single bake pass item.
def _draw_bake_pass_settings(layout, item):
    row = layout.split(factor=0.4, align=True)
    row.label(text="Pass")
    row.prop(item, "pass_type", text="")
    if item.pass_type == "ambient_occlusion":
        row = layout.split(factor=0.4, align=True)
        row.label(text="Mode")
        row.prop(item, "ao_occlusion_mode", text="")
        layout.prop(item, "ao_samples")
        layout.prop(item, "ao_render_samples")
        layout.prop(item, "ao_normalize")
        layout.prop(item, "ao_distance")
        layout.prop(item, "ao_contrast")
    elif item.pass_type == "normal":
        row = layout.split(factor=0.4, align=True)
        row.label(text="Space")
        row.prop(item, "normal_space", text="")
        row = layout.split(factor=0.4, align=True)
        row.label(text="Swizzle R")
        row.prop(item, "normal_r", text="")
        row = layout.split(factor=0.4, align=True)
        row.label(text="Swizzle G")
        row.prop(item, "normal_g", text="")
        row = layout.split(factor=0.4, align=True)
        row.label(text="Swizzle B")
        row.prop(item, "normal_b", text="")
    elif item.pass_type == "curvature":
        layout.prop(item, "curvature_mode")
        if item.curvature_mode == "NORMAL":
            layout.prop(item, "normal_curv_radius")
            layout.prop(item, "normal_curv_strength")
            layout.prop(item, "normal_curv_contrast")
            layout.prop(item, "normal_curv_edge_clamp")
            layout.prop(item, "normal_curv_invert")
        else:
            layout.prop(item, "curvature_exponent")
            layout.prop(item, "curvature_contrast")
    elif item.pass_type == "thickness":
        layout.prop(item, "thickness_samples")
        layout.prop(item, "thickness_render_samples")
        layout.prop(item, "thickness_distance")
    elif item.pass_type == "color_attribute":
        layout.prop(item, "color_attribute_name")
    elif item.pass_type == "custom":
        layout.prop(item, "custom_material")
        layout.prop(item, "custom_bake_type")
    layout.separator(factor=0.3)
    layout.prop(item, "sharpen")
    if item.sharpen:
        sharpen_col = layout.column(align=True)
        sharpen_col.prop(item, "sharpen_amount")
        sharpen_col.prop(item, "sharpen_per_channel")
