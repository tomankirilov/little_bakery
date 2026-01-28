import bpy


# create a slightly indented column for nested UI sections.
def _indent_column(layout):
    # indent groups so nested options are easier to scan.
    # use this to visually nest settings under foldouts.
    row = layout.row()
    row.separator()
    return row.column(align=True)


# draw a resolution row with a label and a field.
def _draw_resolution_row(layout, obj, prop_name):
    # draw the resolution in a consistent label/value layout.
    # keep resolution rows consistent across global and per-set UI.
    row = layout.split(factor=0.4, align=True)
    row.label(text="Resolution")
    row.prop(obj, prop_name, text="")


# draw settings for a single bake target item.
def _draw_bake_target_settings(layout, item):
    row = layout.split(factor=0.4, align=True)
    row.label(text="Target")
    row.prop(item, "target_type", text="")
    if item.target_type == "ambient_occlusion":
        row = layout.split(factor=0.4, align=True)
        row.label(text="Mode")
        row.prop(item, "ao_occlusion_mode", text="")
        layout.prop(item, "ao_samples")
        layout.prop(item, "ao_render_samples")
        layout.prop(item, "ao_distance")
        layout.prop(item, "ao_contrast")
    elif item.target_type == "normal":
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
    elif item.target_type == "curvature":
        layout.prop(item, "curvature_exponent")
        layout.prop(item, "curvature_contrast")
    elif item.target_type == "thickness":
        layout.prop(item, "thickness_samples")
        layout.prop(item, "thickness_render_samples")
        layout.prop(item, "thickness_distance")
    elif item.target_type == "color_attribute":
        layout.prop(item, "color_attribute_name")
    elif item.target_type == "custom":
        layout.prop(item, "custom_material")
        layout.prop(item, "custom_bake_type")
