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
            row = col.split(factor=0.6, align=True)
            row.label(text="Render Device")
            row.prop(data, "render_device", text="")
            col.prop(data, "render_samples", text="Render Samples")
            col.prop(data, "output_dir", text="Output")
            col.prop(data, "global_size", text="Size")
            col.prop(data, "global_bake_normals_ws")
            col.prop(data, "global_bake_ambient_occlusion")
            col.prop(data, "global_bake_curvature")
            col.prop(data, "global_bake_thickness")
            col.prop(data, "global_bake_position")
            col.prop(data, "global_bake_random_island")
            col.prop(data, "global_extrusion", text="Extrusion")
            col.prop(data, "global_max_ray_distance", text="Max Ray Distance")

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
            set_box = layout.box()
            header = set_box.row(align=True)
            header.prop(
                tex_set,
                "show_set_settings",
                icon="TRIA_DOWN" if tex_set.show_set_settings else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Set Settings")
            if tex_set.show_set_settings:
                col = set_box.column(align=True)
                col.prop(tex_set, "override_global_settings")
                if tex_set.override_global_settings:
                    col.prop(tex_set, "size")
                    col.prop(tex_set, "bake_normals_ws")
                    col.prop(tex_set, "bake_ambient_occlusion")
                    col.prop(tex_set, "bake_curvature")
                    col.prop(tex_set, "bake_thickness")
                    col.prop(tex_set, "bake_position")
                    col.prop(tex_set, "bake_random_island")

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
                cage_box = layout.box()
                cage_box.label(text="Low Poly Settings")
                cage_box.prop(low_item, "use_cage")
                cage_box.prop(low_item, "override_global_settings")
                if low_item.override_global_settings:
                    cage_box.prop(low_item, "cage_extrusion")
                    cage_box.prop(low_item, "cage_max_ray_distance")
                if low_item.use_cage:
                    cage_box.prop_search(
                        low_item,
                        "cage_object",
                        context.scene,
                        "objects",
                        text="",
                        icon="VIEWZOOM",
                    )

                high_box = layout.box()
                header = high_box.row(align=True)
                header.prop(
                    data,
                    "show_high_polys",
                    icon="TRIA_DOWN" if data.show_high_polys else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                header.label(text="High Poly")
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
