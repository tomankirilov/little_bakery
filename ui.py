import bpy


## NOTE: https://docs.blender.org/manual/en/latest/contribute/manual/guides/icons.html
## Blender icons ^^ 


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


# draw custom suffix toggles and inputs.
def _draw_custom_suffix(layout, obj, prefix, base):
    # show suffix fields only when the custom toggle is on.
    # only show suffix fields when the custom flag is enabled.
    flag_name = f"{prefix}{base}_custom_suffix"
    value_name = f"{prefix}{base}_suffix"
    layout.prop(obj, flag_name)
    if getattr(obj, flag_name):
        layout.prop(obj, value_name)


# draw all ambient occlusion settings.
def _draw_ao_options(layout, obj, prefix):
    # group all AO settings under the AO toggle.
    # place AO details under the AO toggle so they stay compact.
    row = layout.split(factor=0.4, align=True)
    row.label(text="Mode")
    row.prop(obj, f"{prefix}ao_occlusion_mode", text="")
    layout.prop(obj, f"{prefix}ao_samples")
    layout.prop(obj, f"{prefix}ao_render_samples")
    layout.prop(obj, f"{prefix}ao_distance")
    layout.prop(obj, f"{prefix}ao_contrast")
    _draw_custom_suffix(layout, obj, prefix, "ao")


# draw all curvature settings.
def _draw_curvature_options(layout, obj, prefix):
    # group curvature sliders together.
    # Curvature needs two sliders, so I group them here.
    layout.prop(obj, f"{prefix}curvature_exponent")
    layout.prop(obj, f"{prefix}curvature_contrast")
    _draw_custom_suffix(layout, obj, prefix, "curvature")


# draw all thickness settings.
def _draw_thickness_options(layout, obj, prefix):
    # group thickness sliders together.
    # Thickness also has multiple fields, so I wrap them in this helper.
    layout.prop(obj, f"{prefix}thickness_samples")
    layout.prop(obj, f"{prefix}thickness_render_samples")
    layout.prop(obj, f"{prefix}thickness_distance")
    _draw_custom_suffix(layout, obj, prefix, "thickness")


# draw settings for a single bake target item.
def _draw_bake_target_settings(layout, item):
    if item.target_type == "ambient_occlusion":
        row = layout.split(factor=0.4, align=True)
        row.label(text="Mode")
        row.prop(item, "ao_occlusion_mode", text="")
        layout.prop(item, "ao_samples")
        layout.prop(item, "ao_render_samples")
        layout.prop(item, "ao_distance")
        layout.prop(item, "ao_contrast")
    elif item.target_type == "curvature":
        layout.prop(item, "curvature_exponent")
        layout.prop(item, "curvature_contrast")
    elif item.target_type == "thickness":
        layout.prop(item, "thickness_samples")
        layout.prop(item, "thickness_render_samples")
        layout.prop(item, "thickness_distance")
    elif item.target_type == "color_attribute":
        layout.prop(item, "color_attribute_name")

    layout.prop(item, "custom_suffix")
    if item.custom_suffix:
        layout.prop(item, "suffix")


class DUMMYBAKE_UL_texture_sets(bpy.types.UIList):
    # draw each texture set row.
    # keep list rows compact: icon + name.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        row.label(icon="IMAGE_DATA")
        row.prop(item, "name", text="", emboss=False)


class DUMMYBAKE_UL_low_polys(bpy.types.UIList):
    # draw each low poly row.
    # expose a quick select button and an object search per row.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("bakery.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "LOW"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class DUMMYBAKE_UL_high_polys(bpy.types.UIList):
    # draw each high poly row.
    # High polys mirror the low poly list layout for consistency.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("bakery.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "HIGH"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class BAKERY_UL_bake_targets(bpy.types.UIList):
    # draw each bake target row.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        row.label(icon="IMAGE_PLANE")
        row.prop(item, "target_type", text="")


class DUMMYBAKE_PT_tools(bpy.types.Panel):
    bl_label = "Bakery"
    bl_idname = "DUMMYBAKE_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bakery"

    # draw the main sidebar UI.
    def draw(self, context):
        # build the sidebar layout from top to bottom.
        # build the whole sidebar here, starting with About and then Bake.
        layout = self.layout
        data = context.scene.bakery_data

        if data.is_baking:
            progress_box = layout.box()
            title_row = progress_box.row()
            title_row.alignment = "CENTER"
            title_row.label(text="BAKING IN PROGRESS", icon="ERROR")
            info_col = progress_box.column(align=True)
            info_col.label(text=f"- Set: {data.baking_set_name}")
            info_col.label(text=f"- Target: {data.baking_target_name}")
            progress_box.prop(data, "baking_progress", text="Progress", slider=True)

            about_box = layout.box()
            header = about_box.row(align=True)
            header.label(text="About")
            about_col = about_box.column(align=True)
            label_row = about_col.row()
            label_row.alignment = "CENTER"
            label_row.label(text="Baked with love for everybody!")
            row = about_col.row(align=True)
            row.operator("wm.url_open", text="GitHub").url = "https://tomanov.art/"
            row.operator("wm.url_open", text="Author").url = "https://tomanov.art/"
            return

        about_box = layout.box()
        header = about_box.row(align=True)
        header.prop(
            data,
            "show_about",
            icon="TRIA_DOWN" if data.show_about else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        #header.label(text="About", icon="USER")
        header.label(text="About")
        if data.show_about:
            about_col = about_box.column(align=True)
            label_row = about_col.row()
            label_row.alignment = "CENTER"
            label_row.label(text="Baked with love for everybody!")
            row = about_col.row(align=True)
            row.operator("wm.url_open", text="GitHub").url = "https://tomanov.art/"
            row.operator("wm.url_open", text="Author").url = "https://tomanov.art/"

        if data.last_bake_duration and data.show_last_bake:
            last_box = layout.box()
            row = last_box.row()
            row.alignment = "CENTER"
            row.operator(
                "bakery.hide_last_bake",
                text=f"Bake Completed in {data.last_bake_duration}",
                emboss=False,
            )

        buttons_col = layout.column(align=True)
        buttons_col.scale_y = 2.0


        #buttons_col.operator("bakery.bake_all", text="Bake", icon="SEQUENCE")
        buttons_col.operator("bakery.bake_all", text="Bake")
        global_box = layout.box()
        header = global_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_global_settings",
            icon="TRIA_DOWN" if data.show_global_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Global Settings", icon="TOOL_SETTINGS")
        if data.show_global_settings:
            sections = global_box.column(align=True)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_bake_targets",
                icon="TRIA_DOWN" if data.show_bake_targets else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Bake Targets")
            if data.show_bake_targets:
                bake_col = _indent_column(sections)
                row = bake_col.row()
                row.template_list(
                    "BAKERY_UL_bake_targets",
                    "",
                    data,
                    "global_bake_targets",
                    data,
                    "active_global_bake_target_index",
                    rows=4,
                )
                col = row.column(align=True)
                col.operator("bakery.bake_target_add_global", icon="ADD", text="")
                col.operator("bakery.bake_target_remove_global", icon="REMOVE", text="")
                col.separator()
                col.operator("bakery.bake_target_move_global_up", icon="TRIA_UP", text="")
                col.operator("bakery.bake_target_move_global_down", icon="TRIA_DOWN", text="")

                if data.global_bake_targets and 0 <= data.active_global_bake_target_index < len(data.global_bake_targets):
                    item = data.global_bake_targets[data.active_global_bake_target_index]
                    settings_col = bake_col.column(align=True)
                    settings_col.separator()
                    settings_col.label(text="Target Settings:")
                    _draw_bake_target_settings(settings_col, item)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_settings",
                icon="TRIA_DOWN" if data.show_render_settings else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Rendering")
            if data.show_render_settings:
                render_col = _indent_column(sections)
                row = render_col.split(factor=0.4, align=True)
                row.label(text="Render Device")
                row.prop(data, "render_device", text="")
                row = render_col.split(factor=0.4, align=True)
                row.label(text="MSAA")
                row.prop(data, "global_msaa", text="")
                _draw_resolution_row(render_col, data, "global_resolution")
                render_col.prop(data, "global_dilation")
                render_col.prop(data, "global_extrusion")
                render_col.prop(data, "global_max_ray_distance", text="Max Ray Distance")

            header = sections.row(align=True)
            header.prop(
                data,
                "show_output",
                icon="TRIA_DOWN" if data.show_output else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Output")
            if data.show_output:
                output_col = _indent_column(sections)
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Output")
                output_row = row.row(align=True)
                output_row.prop(data, "output_dir", text="")
                output_row.operator("bakery.pick_output_dir", text="", icon="FILE_FOLDER")
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Format")
                row.prop(data, "output_format", text="")
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Color")
                row.prop(data, "output_color_mode", text="")
                if data.output_format == "PNG":
                    row = output_col.split(factor=0.4, align=True)
                    row.label(text="Color Depth")
                    row.prop(data, "output_color_depth", text="")
                    row = output_col.split(factor=0.4, align=True)
                    row.label(text="Compression")
                    row.prop(data, "output_png_compression", text="")

        box = layout.box()
        header = box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_texture_sets",
            icon="TRIA_DOWN" if data.show_texture_sets else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Texture Sets", icon="RENDER_RESULT")
        tex_set = None
        if data.texture_sets and 0 <= data.active_texture_index < len(data.texture_sets):
            tex_set = data.texture_sets[data.active_texture_index]

        if data.show_texture_sets:
            row = box.row()
            row.template_list(
                "DUMMYBAKE_UL_texture_sets",
                "",
                data,
                "texture_sets",
                data,
                "active_texture_index",
                rows=2,
            )
            col = row.column(align=True)
            col.operator("bakery.texture_set_add", icon="ADD", text="")
            col.operator("bakery.texture_set_remove", icon="REMOVE", text="")
            clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "TEXTURE"

            if tex_set:
                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_global_settings",
                    icon="TRIA_DOWN" if tex_set.override_global_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Render Settings")
                if tex_set.override_global_settings:
                    set_col = _indent_column(box)
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_resolution", text="")
                    res_row = row.row(align=True)
                    res_row.enabled = tex_set.override_resolution
                    res_split = res_row.split(factor=0.4, align=True)
                    res_split.label(text="Resolution")
                    res_split.prop(tex_set, "size", text="")
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_dilation", text="")
                    dilation_row = row.row(align=True)
                    dilation_row.enabled = tex_set.override_dilation
                    dilation_row.prop(tex_set, "set_dilation", text="Dilation (px)")
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_msaa", text="")
                    msaa_row = row.row(align=True)
                    msaa_row.enabled = tex_set.override_msaa
                    msaa_split = msaa_row.split(factor=0.4, align=True)
                    msaa_split.label(text="MSAA")
                    msaa_split.prop(tex_set, "set_msaa", text="")

                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_bake_targets",
                    icon="TRIA_DOWN" if tex_set.override_bake_targets else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Bake Targets")
                if tex_set.override_bake_targets:
                    row = _indent_column(box)
                    row.prop(tex_set, "bake_target_mode")
                    list_row = row.row()
                    list_row.template_list(
                        "BAKERY_UL_bake_targets",
                        "",
                        tex_set,
                        "bake_targets",
                        tex_set,
                        "active_bake_target_index",
                        rows=4,
                    )
                    col = list_row.column(align=True)
                    col.operator("bakery.bake_target_add_set", icon="ADD", text="")
                    col.operator("bakery.bake_target_remove_set", icon="REMOVE", text="")
                    col.separator()
                    col.operator("bakery.bake_target_move_set_up", icon="TRIA_UP", text="")
                    col.operator("bakery.bake_target_move_set_down", icon="TRIA_DOWN", text="")
                    if tex_set.bake_targets and 0 <= tex_set.active_bake_target_index < len(tex_set.bake_targets):
                        item = tex_set.bake_targets[tex_set.active_bake_target_index]
                        settings_col = row.column(align=True)
                        settings_col.separator()
                        settings_col.label(text="Target Settings:")
                        _draw_bake_target_settings(settings_col, item)

        if not tex_set:
            return

        low_box = layout.box()
        header = low_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_low_polys",
            icon="TRIA_DOWN" if data.show_low_polys else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Low Poly", icon="MESH_ICOSPHERE")
        if data.show_low_polys:
            row = low_box.row()
            row.template_list(
                "DUMMYBAKE_UL_low_polys",
                "",
                tex_set,
                "low_polys",
                tex_set,
                "active_low_index",
                rows=2,
            )
            col = row.column(align=True)
            col.operator("bakery.low_poly_add", icon="ADD", text="")
            col.operator("bakery.low_poly_remove", icon="REMOVE", text="")
            clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "LOW"

            if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
                low_item = tex_set.low_polys[tex_set.active_low_index]
                low_box.label(text="Low Poly Settings")
                row = low_box.row(align=True)
                row.prop(
                    low_item,
                    "override_global_settings",
                    icon="TRIA_DOWN" if low_item.override_global_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Global Settings")
                if low_item.override_global_settings:
                    cage_col = low_box.column(align=True)
                    cage_row = cage_col.row(align=True)
                    cage_row.prop(low_item, "use_cage", text="")
                    cage_row.label(text="Cage")
                    picker_row = cage_row.row(align=True)
                    picker_row.scale_x = 1.6
                    picker_row.enabled = low_item.use_cage
                    picker_row.prop_search(
                        low_item,
                        "cage_object",
                        context.scene,
                        "objects",
                        text="",
                        icon="VIEWZOOM",
                    )
                    row = cage_col.row(align=True)
                    row.prop(low_item, "override_cage_extrusion", text="")
                    extrusion_row = row.row(align=True)
                    extrusion_row.enabled = low_item.override_cage_extrusion
                    extrusion_row.prop(low_item, "cage_extrusion", text="Cage Extrusion")
                    row = cage_col.row(align=True)
                    row.prop(low_item, "override_cage_max_ray_distance", text="")
                    ray_row = row.row(align=True)
                    ray_row.enabled = low_item.override_cage_max_ray_distance
                    ray_row.prop(low_item, "cage_max_ray_distance")

        if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
            low_item = tex_set.low_polys[tex_set.active_low_index]
            high_box = layout.box()
            high_header = high_box.row(align=True)
            high_header.scale_y = 1.4
            high_header.prop(
                data,
                "show_high_polys",
                icon="TRIA_DOWN" if data.show_high_polys else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            high_header.label(text="High Poly", icon="MESH_UVSPHERE")
            if data.show_high_polys:
                row = high_box.row()
                row.template_list(
                    "DUMMYBAKE_UL_high_polys",
                    "",
                    low_item,
                    "high_polys",
                    low_item,
                    "active_high_index",
                    rows=2,
                )
                col = row.column(align=True)
                col.operator("bakery.high_poly_add", icon="ADD", text="")
                col.operator("bakery.high_poly_remove", icon="REMOVE", text="")
                clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
                clear_op.list_kind = "HIGH"
                if low_item.high_polys and 0 <= low_item.active_high_index < len(low_item.high_polys):
                    high_item = low_item.high_polys[low_item.active_high_index]
                    high_box.prop(high_item, "color_attribute")

        if data.is_baking:
            return


classes = (
    DUMMYBAKE_UL_texture_sets,
    DUMMYBAKE_UL_low_polys,
    DUMMYBAKE_UL_high_polys,
    BAKERY_UL_bake_targets,
    DUMMYBAKE_PT_tools,
)


# register all UI classes.
def register():
    # register all UI classes.
    for cls in classes:
        bpy.utils.register_class(cls)


# unregister all UI classes.
def unregister():
    # unregister UI classes in reverse order.
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
