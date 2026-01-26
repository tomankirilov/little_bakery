# SPDX-License-Identifier: GPL-2.0-or-later
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
    layout.prop(obj, f"{prefix}ao_local_only")
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


class DUMMYBAKE_UL_texture_sets(bpy.types.UIList):
    # draw each texture set row.
    # keep list rows compact: icon + name.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(icon="IMAGE_DATA")
        row.prop(item, "name", text="", emboss=False)


class DUMMYBAKE_UL_low_polys(bpy.types.UIList):
    # draw each low poly row.
    # expose a quick select button and an object search per row.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("dummybake.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "LOW"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class DUMMYBAKE_UL_high_polys(bpy.types.UIList):
    # draw each high poly row.
    # High polys mirror the low poly list layout for consistency.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("dummybake.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "HIGH"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class DUMMYBAKE_PT_tools(bpy.types.Panel):
    bl_label = "Dummy Bake Tools"
    bl_idname = "DUMMYBAKE_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dummy Bake"

    # draw the main sidebar UI.
    def draw(self, context):
        # build the sidebar layout from top to bottom.
        # build the whole sidebar here, starting with About and then Bake.
        layout = self.layout
        data = context.scene.dummy_bake_data

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
                "dummybake.hide_last_bake",
                text=f"Bake Completed in {data.last_bake_duration}",
                emboss=False,
            )

        bake_box = layout.box()
        col = bake_box.column(align=True)
        col.operator("dummybake.bake_all", text="Bake All", icon='RENDER_RESULT')
        col.operator("dummybake.bake_selected_set", text="Bake Selected Set", icon='FILE_IMAGE')
        bake_box.separator()
        indent_row = bake_box.row()
        indent_row.separator()
        sections = indent_row.column(align=True)

        header = sections.row(align=True)
        header.prop(
            data,
            "show_bake_targets",
            icon="TRIA_DOWN" if data.show_bake_targets else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )


        ### BAKE TARGETS:
        header.label(text="Bake Targets")
        if data.show_bake_targets:
            bake_col = _indent_column(sections)
            bake_col.prop(data, "global_bake_tangent_normal")
            if data.global_bake_tangent_normal:
                tangent_col = _indent_column(bake_col)
                _draw_custom_suffix(tangent_col, data, "global_", "tangent")
            bake_col.prop(data, "global_bake_normals_ws")
            if data.global_bake_normals_ws:
                normals_col = _indent_column(bake_col)
                _draw_custom_suffix(normals_col, data, "global_", "normals")
            bake_col.prop(data, "global_bake_ambient_occlusion")
            if data.global_bake_ambient_occlusion:
                ao_col = _indent_column(bake_col)
                _draw_ao_options(ao_col, data, "global_")
            bake_col.prop(data, "global_bake_curvature")
            if data.global_bake_curvature:
                curv_col = _indent_column(bake_col)
                _draw_curvature_options(curv_col, data, "global_")
            bake_col.prop(data, "global_bake_thickness")
            if data.global_bake_thickness:
                thick_col = _indent_column(bake_col)
                _draw_thickness_options(thick_col, data, "global_")
            bake_col.prop(data, "global_bake_position")
            if data.global_bake_position:
                pos_col = _indent_column(bake_col)
                _draw_custom_suffix(pos_col, data, "global_", "position")
            bake_col.prop(data, "global_bake_color_attribute")
            if data.global_bake_color_attribute:
                color_col = _indent_column(bake_col)
                color_col.prop(data, "global_color_attribute_name", text="Color Attribute")
                _draw_custom_suffix(color_col, data, "global_", "color_attribute")
            bake_col.prop(data, "global_bake_random_island")
            if data.global_bake_random_island:
                rand_col = _indent_column(bake_col)
                _draw_custom_suffix(rand_col, data, "global_", "random_island")

        header = sections.row(align=True)
        header.prop(
            data,
            "show_render_settings",
            icon="TRIA_DOWN" if data.show_render_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )

        ### RENDERING::
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
            "show_global_settings",
            icon="TRIA_DOWN" if data.show_global_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )



        ## OUTPUT:
        header.label(text="Output")
        if data.show_global_settings:
            output_col = _indent_column(sections)
            row = output_col.split(factor=0.4, align=True)
            row.label(text="Output")
            output_row = row.row(align=True)
            output_row.prop(data, "output_dir", text="")
            output_row.operator("dummybake.pick_output_dir", text="", icon="FILE_FOLDER")
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
        header.prop(
            data,
            "show_texture_sets",
            icon="TRIA_DOWN" if data.show_texture_sets else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Texture Sets")
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
            col.operator("dummybake.texture_set_add", icon="ADD", text="")
            col.operator("dummybake.texture_set_remove", icon="REMOVE", text="")
            clear_op = col.operator("dummybake.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "TEXTURE"

            if tex_set:
                box.prop(tex_set, "override_global_settings")
                if tex_set.override_global_settings:
                    set_col = _indent_column(box)
                    _draw_resolution_row(set_col, tex_set, "size")
                    set_col.prop(tex_set, "bake_tangent_normal")
                    if tex_set.bake_tangent_normal:
                        tangent_col = _indent_column(set_col)
                        _draw_custom_suffix(tangent_col, tex_set, "", "tangent")
                    set_col.prop(tex_set, "bake_normals_ws")
                    if tex_set.bake_normals_ws:
                        normals_col = _indent_column(set_col)
                        _draw_custom_suffix(normals_col, tex_set, "", "normals")
                    set_col.prop(tex_set, "bake_ambient_occlusion")
                    if tex_set.bake_ambient_occlusion:
                        ao_col = _indent_column(set_col)
                        _draw_ao_options(ao_col, tex_set, "")
                    set_col.prop(tex_set, "bake_curvature")
                    if tex_set.bake_curvature:
                        curv_col = _indent_column(set_col)
                        _draw_curvature_options(curv_col, tex_set, "")
                    set_col.prop(tex_set, "bake_thickness")
                    if tex_set.bake_thickness:
                        thick_col = _indent_column(set_col)
                        _draw_thickness_options(thick_col, tex_set, "")
                    set_col.prop(tex_set, "bake_position")
                    if tex_set.bake_position:
                        pos_col = _indent_column(set_col)
                        _draw_custom_suffix(pos_col, tex_set, "", "position")
                    set_col.prop(tex_set, "bake_color_attribute")
                    if tex_set.bake_color_attribute:
                        color_col = _indent_column(set_col)
                        color_col.prop(tex_set, "color_attribute_name", text="Color Attribute")
                        _draw_custom_suffix(color_col, tex_set, "", "color_attribute")
                    set_col.prop(tex_set, "bake_random_island")
                    if tex_set.bake_random_island:
                        rand_col = _indent_column(set_col)
                        _draw_custom_suffix(rand_col, tex_set, "", "random_island")

        if not tex_set:
            return

        low_box = layout.box()
        header = low_box.row(align=True)
        header.prop(
            data,
            "show_low_polys",
            icon="TRIA_DOWN" if data.show_low_polys else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Low Poly")
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
            col.operator("dummybake.low_poly_add", icon="ADD", text="")
            col.operator("dummybake.low_poly_remove", icon="REMOVE", text="")
            clear_op = col.operator("dummybake.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "LOW"

            if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
                low_item = tex_set.low_polys[tex_set.active_low_index]
                low_box.label(text="Low Poly Settings")
                low_box.prop(low_item, "use_cage")
                if low_item.use_cage:
                    low_box.prop_search(
                        low_item,
                        "cage_object",
                        context.scene,
                        "objects",
                        text="",
                        icon="VIEWZOOM",
                    )
                low_box.prop(low_item, "override_global_settings")
                if low_item.override_global_settings:
                    cage_col = low_box.column(align=True)
                    cage_col.prop(low_item, "cage_extrusion", text="Cage Extrusion")
                    cage_col.prop(low_item, "cage_max_ray_distance")

        if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
            low_item = tex_set.low_polys[tex_set.active_low_index]
            high_box = layout.box()
            high_header = high_box.row(align=True)
            high_header.prop(
                data,
                "show_high_polys",
                icon="TRIA_DOWN" if data.show_high_polys else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            high_header.label(text="High Poly")
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
                col.operator("dummybake.high_poly_add", icon="ADD", text="")
                col.operator("dummybake.high_poly_remove", icon="REMOVE", text="")
                clear_op = col.operator("dummybake.clear_selection", icon="PANEL_CLOSE", text="")
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
