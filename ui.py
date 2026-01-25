# SPDX-License-Identifier: GPL-2.0-or-later

import bpy


def _indent_column(layout):
    row = layout.row()
    row.separator()
    return row.column(align=True)


def _draw_resolution_row(layout, obj, prop_name):
    row = layout.split(factor=0.4, align=True)
    row.label(text="Resolution")
    row.prop(obj, prop_name, text="")


def _draw_custom_suffix(layout, obj, prefix, base):
    flag_name = f"{prefix}{base}_custom_suffix"
    value_name = f"{prefix}{base}_suffix"
    layout.prop(obj, flag_name)
    if getattr(obj, flag_name):
        layout.prop(obj, value_name)


def _draw_ao_options(layout, obj, prefix):
    layout.prop(obj, f"{prefix}ao_local_only")
    layout.prop(obj, f"{prefix}ao_samples")
    layout.prop(obj, f"{prefix}ao_render_samples")
    layout.prop(obj, f"{prefix}ao_distance")
    _draw_custom_suffix(layout, obj, prefix, "ao")


def _draw_curvature_options(layout, obj, prefix):
    layout.prop(obj, f"{prefix}curvature_exponent")
    _draw_custom_suffix(layout, obj, prefix, "curvature")


def _draw_thickness_options(layout, obj, prefix):
    layout.prop(obj, f"{prefix}thickness_samples")
    layout.prop(obj, f"{prefix}thickness_render_samples")
    layout.prop(obj, f"{prefix}thickness_distance")
    _draw_custom_suffix(layout, obj, prefix, "thickness")


class DUMMYBAKE_UL_texture_sets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(icon="IMAGE_DATA")
        row.prop(item, "name", text="", emboss=False)


class DUMMYBAKE_UL_low_polys(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("dummybake.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "LOW"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class DUMMYBAKE_UL_high_polys(bpy.types.UIList):
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

    def draw(self, context):
        layout = self.layout
        data = context.scene.dummy_bake_data

        bake_box = layout.box()
        col = bake_box.column(align=True)
        col.operator("dummybake.bake_all", text="Bake All")
        col.operator("dummybake.bake_selected_set", text="Bake Selected Set")
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
        header.label(text="Rendering")
        if data.show_render_settings:
            render_col = _indent_column(sections)
            row = render_col.split(factor=0.4, align=True)
            row.label(text="Render Device")
            row.prop(data, "render_device", text="")
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
        header.label(text="Output")
        if data.show_global_settings:
            output_col = _indent_column(sections)
            row = output_col.split(factor=0.4, align=True)
            row.label(text="Output")
            row.prop(data, "output_dir", text="")
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
        if data.show_texture_sets:
            row = box.row()
            row.template_list(
                "DUMMYBAKE_UL_texture_sets",
                "",
                data,
                "texture_sets",
                data,
                "active_texture_index",
            )
            col = row.column(align=True)
            col.operator("dummybake.texture_set_add", icon="ADD", text="")
            col.operator("dummybake.texture_set_remove", icon="REMOVE", text="")
            clear_op = col.operator("dummybake.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "TEXTURE"

            if data.texture_sets and 0 <= data.active_texture_index < len(data.texture_sets):
                tex_set = data.texture_sets[data.active_texture_index]
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
                    set_col.prop(tex_set, "bake_random_island")
                    if tex_set.bake_random_island:
                        rand_col = _indent_column(set_col)
                        _draw_custom_suffix(rand_col, tex_set, "", "random_island")

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
                    )
                    col = row.column(align=True)
                    col.operator("dummybake.high_poly_add", icon="ADD", text="")
                    col.operator("dummybake.high_poly_remove", icon="REMOVE", text="")
                    clear_op = col.operator("dummybake.clear_selection", icon="PANEL_CLOSE", text="")
                    clear_op.list_kind = "HIGH"


classes = (
    DUMMYBAKE_UL_texture_sets,
    DUMMYBAKE_UL_low_polys,
    DUMMYBAKE_UL_high_polys,
    DUMMYBAKE_PT_tools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
