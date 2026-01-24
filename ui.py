# SPDX-License-Identifier: GPL-2.0-or-later

import bpy


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
        bake_box.label(text="Bake")
        col = bake_box.column(align=True)
        col.operator("dummybake.bake_all", text="Bake All")
        col.operator("dummybake.bake_selected_set", text="Bake Selected Set")
        col.prop(data, "output_dir", text="Output")

        global_box = layout.box()
        header = global_box.row(align=True)
        header.prop(
            data,
            "show_global_settings",
            icon="TRIA_DOWN" if data.show_global_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Global Settings")
        if data.show_global_settings:
            col = global_box.column(align=True)
            col.label(text="General")
            row = col.row()
            row.separator()
            general_col = row.column(align=True)
            row = general_col.split(factor=0.4, align=True)
            row.label(text="Render Device")
            row.prop(data, "render_device", text="")
            general_col.prop(data, "render_samples", text="Render Samples")
            general_col.prop(data, "global_extrusion")
            general_col.prop(data, "global_max_ray_distance", text="Max Ray Distance")
            col.separator()
            col.label(text="Bake Targets")
            row = col.row()
            row.separator()
            bake_col = row.column(align=True)
            row = bake_col.split(factor=0.4, align=True)
            row.label(text="Resolution")
            row.prop(data, "global_resolution", text="")
            bake_col.prop(data, "global_bake_normals_ws")
            if data.global_bake_normals_ws:
                row = bake_col.row()
                row.separator()
                normals_col = row.column(align=True)
                normals_col.prop(data, "global_normals_custom_prefix")
                if data.global_normals_custom_prefix:
                    normals_col.prop(data, "global_normals_prefix")
            bake_col.prop(data, "global_bake_ambient_occlusion")
            if data.global_bake_ambient_occlusion:
                row = bake_col.row()
                row.separator()
                ao_col = row.column(align=True)
                ao_col.prop(data, "global_ao_local_only")
                ao_col.prop(data, "global_ao_samples")
                ao_col.prop(data, "global_ao_distance")
                ao_col.prop(data, "global_ao_custom_prefix")
                if data.global_ao_custom_prefix:
                    ao_col.prop(data, "global_ao_prefix")
            bake_col.prop(data, "global_bake_curvature")
            if data.global_bake_curvature:
                row = bake_col.row()
                row.separator()
                curv_col = row.column(align=True)
                curv_col.prop(data, "global_curvature_exponent")
                curv_col.prop(data, "global_curvature_custom_prefix")
                if data.global_curvature_custom_prefix:
                    curv_col.prop(data, "global_curvature_prefix")
            bake_col.prop(data, "global_bake_thickness")
            if data.global_bake_thickness:
                row = bake_col.row()
                row.separator()
                thick_col = row.column(align=True)
                thick_col.prop(data, "global_thickness_samples")
                thick_col.prop(data, "global_thickness_distance")
                thick_col.prop(data, "global_thickness_custom_prefix")
                if data.global_thickness_custom_prefix:
                    thick_col.prop(data, "global_thickness_prefix")
            bake_col.prop(data, "global_bake_position")
            if data.global_bake_position:
                row = bake_col.row()
                row.separator()
                pos_col = row.column(align=True)
                pos_col.prop(data, "global_position_custom_prefix")
                if data.global_position_custom_prefix:
                    pos_col.prop(data, "global_position_prefix")
            bake_col.prop(data, "global_bake_random_island")
            if data.global_bake_random_island:
                row = bake_col.row()
                row.separator()
                rand_col = row.column(align=True)
                rand_col.prop(data, "global_random_island_custom_prefix")
                if data.global_random_island_custom_prefix:
                    rand_col.prop(data, "global_random_island_prefix")

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
                row = box.row()
                row.separator()
                set_col = row.column(align=True)
                row = set_col.split(factor=0.4, align=True)
                row.label(text="Resolution")
                row.prop(tex_set, "size", text="")
                set_col.prop(tex_set, "bake_normals_ws")
                if tex_set.bake_normals_ws:
                    row = set_col.row()
                    row.separator()
                    normals_col = row.column(align=True)
                    normals_col.prop(tex_set, "normals_custom_prefix")
                    if tex_set.normals_custom_prefix:
                        normals_col.prop(tex_set, "normals_prefix")
                set_col.prop(tex_set, "bake_ambient_occlusion")
                if tex_set.bake_ambient_occlusion:
                    row = set_col.row()
                    row.separator()
                    ao_col = row.column(align=True)
                    ao_col.prop(tex_set, "ao_local_only")
                    ao_col.prop(tex_set, "ao_samples")
                    ao_col.prop(tex_set, "ao_distance")
                    ao_col.prop(tex_set, "ao_custom_prefix")
                    if tex_set.ao_custom_prefix:
                        ao_col.prop(tex_set, "ao_prefix")
                set_col.prop(tex_set, "bake_curvature")
                if tex_set.bake_curvature:
                    row = set_col.row()
                    row.separator()
                    curv_col = row.column(align=True)
                    curv_col.prop(tex_set, "curvature_exponent")
                    curv_col.prop(tex_set, "curvature_custom_prefix")
                    if tex_set.curvature_custom_prefix:
                        curv_col.prop(tex_set, "curvature_prefix")
                set_col.prop(tex_set, "bake_thickness")
                if tex_set.bake_thickness:
                    row = set_col.row()
                    row.separator()
                    thick_col = row.column(align=True)
                    thick_col.prop(tex_set, "thickness_samples")
                    thick_col.prop(tex_set, "thickness_distance")
                    thick_col.prop(tex_set, "thickness_custom_prefix")
                    if tex_set.thickness_custom_prefix:
                        thick_col.prop(tex_set, "thickness_prefix")
                set_col.prop(tex_set, "bake_position")
                if tex_set.bake_position:
                    row = set_col.row()
                    row.separator()
                    pos_col = row.column(align=True)
                    pos_col.prop(tex_set, "position_custom_prefix")
                    if tex_set.position_custom_prefix:
                        pos_col.prop(tex_set, "position_prefix")
                set_col.prop(tex_set, "bake_random_island")
                if tex_set.bake_random_island:
                    row = set_col.row()
                    row.separator()
                    rand_col = row.column(align=True)
                    rand_col.prop(tex_set, "random_island_custom_prefix")
                    if tex_set.random_island_custom_prefix:
                        rand_col.prop(tex_set, "random_island_prefix")

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

                    high_header = low_box.row(align=True)
                    high_header.prop(
                        data,
                        "show_high_polys",
                        icon="TRIA_DOWN" if data.show_high_polys else "TRIA_RIGHT",
                        icon_only=True,
                        emboss=False,
                    )
                    high_header.label(text="High Poly")
                    if data.show_high_polys:
                        row = low_box.row()
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
