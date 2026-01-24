# SPDX-License-Identifier: GPL-2.0-or-later
# Dummy Bake Tools addon skeleton.

bl_info = {
    "name": "Dummy Bake Tools",
    "author": "Toman",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Dummy Bake",
    "description": "UI scaffolding for bake automation",
    "category": "Object",
}

import bpy


class DummyBakeHighPolyItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)


class DummyBakeLowPolyItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    high_polys: bpy.props.CollectionProperty(type=DummyBakeHighPolyItem)
    active_high_index: bpy.props.IntProperty(default=0)


class DummyBakeTextureSet(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Texture Set")
    low_polys: bpy.props.CollectionProperty(type=DummyBakeLowPolyItem)
    active_low_index: bpy.props.IntProperty(default=0)


class DummyBakeData(bpy.types.PropertyGroup):
    texture_sets: bpy.props.CollectionProperty(type=DummyBakeTextureSet)
    active_texture_index: bpy.props.IntProperty(default=0)
    show_texture_sets: bpy.props.BoolProperty(name="Show Texture Sets", default=True)
    show_low_polys: bpy.props.BoolProperty(name="Show Low Poly", default=True)
    show_high_polys: bpy.props.BoolProperty(name="Show High Poly", default=True)


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


class DUMMYBAKE_OT_texture_set_add(bpy.types.Operator):
    bl_idname = "dummybake.texture_set_add"
    bl_label = "Add Texture Set"
    bl_description = "Add a new texture set"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        item = data.texture_sets.add()
        item.name = f"Texture Set {len(data.texture_sets)}"
        data.active_texture_index = len(data.texture_sets) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_texture_set_remove(bpy.types.Operator):
    bl_idname = "dummybake.texture_set_remove"
    bl_label = "Remove Texture Set"
    bl_description = "Remove the selected texture set"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        index = data.active_texture_index
        if 0 <= index < len(data.texture_sets):
            data.texture_sets.remove(index)
            data.active_texture_index = max(0, min(index, len(data.texture_sets) - 1))
        return {"FINISHED"}


class DUMMYBAKE_OT_low_poly_add(bpy.types.Operator):
    bl_idname = "dummybake.low_poly_add"
    bl_label = "Add Low Poly"
    bl_description = "Add a low poly entry to the selected texture set"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        if not data.texture_sets:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in {"CAMERA", "LIGHT", "EMPTY", "ARMATURE", "SPEAKER"}
        ]
        if selected:
            existing = {item.object for item in tex_set.low_polys if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = tex_set.low_polys.add()
                item.object = obj
            tex_set.active_low_index = max(0, len(tex_set.low_polys) - 1)
        else:
            tex_set.low_polys.add()
            tex_set.active_low_index = len(tex_set.low_polys) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_low_poly_remove(bpy.types.Operator):
    bl_idname = "dummybake.low_poly_remove"
    bl_label = "Remove Low Poly"
    bl_description = "Remove the selected low poly entry"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        if not data.texture_sets:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_low_index
        if 0 <= index < len(tex_set.low_polys):
            tex_set.low_polys.remove(index)
            tex_set.active_low_index = max(0, min(index, len(tex_set.low_polys) - 1))
        return {"FINISHED"}


class DUMMYBAKE_OT_high_poly_add(bpy.types.Operator):
    bl_idname = "dummybake.high_poly_add"
    bl_label = "Add High Poly"
    bl_description = "Add a high poly entry to the selected low poly"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        if not data.texture_sets:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in {"CAMERA", "LIGHT", "EMPTY", "ARMATURE", "SPEAKER"}
        ]
        if selected:
            existing = {item.object for item in low_item.high_polys if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = low_item.high_polys.add()
                item.object = obj
            low_item.active_high_index = max(0, len(low_item.high_polys) - 1)
        else:
            low_item.high_polys.add()
            low_item.active_high_index = len(low_item.high_polys) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_high_poly_remove(bpy.types.Operator):
    bl_idname = "dummybake.high_poly_remove"
    bl_label = "Remove High Poly"
    bl_description = "Remove the selected high poly entry"

    def execute(self, context):
        data = context.scene.dummy_bake_data
        if not data.texture_sets:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        index = low_item.active_high_index
        if 0 <= index < len(low_item.high_polys):
            low_item.high_polys.remove(index)
            low_item.active_high_index = max(0, min(index, len(low_item.high_polys) - 1))
        return {"FINISHED"}


class DUMMYBAKE_OT_select_object(bpy.types.Operator):
    bl_idname = "dummybake.select_object"
    bl_label = "Select Object"
    bl_description = "Select the object from this list item"

    object_name: bpy.props.StringProperty()
    list_kind: bpy.props.EnumProperty(
        items=[
            ("LOW", "Low Poly", ""),
            ("HIGH", "High Poly", ""),
        ]
    )
    item_index: bpy.props.IntProperty()

    def invoke(self, context, event):
        data = context.scene.dummy_bake_data
        if self.list_kind == "LOW":
            if not data.texture_sets:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_low_index = self.item_index
        elif self.list_kind == "HIGH":
            if not data.texture_sets:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.low_polys:
                return {"CANCELLED"}
            low_item = tex_set.low_polys[tex_set.active_low_index]
            low_item.active_high_index = self.item_index

        if not event.ctrl:
            return {"FINISHED"}

        obj = context.scene.objects.get(self.object_name)
        if not obj:
            return {"CANCELLED"}
        if event.shift:
            obj.select_set(True)
        else:
            for other in context.view_layer.objects:
                other.select_set(False)
            obj.select_set(True)
        context.view_layer.objects.active = obj
        return {"FINISHED"}


class DUMMYBAKE_PT_tools(bpy.types.Panel):
    bl_label = "Dummy Bake Tools"
    bl_idname = "DUMMYBAKE_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dummy Bake"

    def draw(self, context):
        layout = self.layout
        data = context.scene.dummy_bake_data

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

        if data.texture_sets:
            tex_set = data.texture_sets[data.active_texture_index]
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

            if tex_set.low_polys:
                low_item = tex_set.low_polys[tex_set.active_low_index]
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


classes = (
    DummyBakeHighPolyItem,
    DummyBakeLowPolyItem,
    DummyBakeTextureSet,
    DummyBakeData,
    DUMMYBAKE_UL_texture_sets,
    DUMMYBAKE_UL_low_polys,
    DUMMYBAKE_UL_high_polys,
    DUMMYBAKE_OT_texture_set_add,
    DUMMYBAKE_OT_texture_set_remove,
    DUMMYBAKE_OT_low_poly_add,
    DUMMYBAKE_OT_low_poly_remove,
    DUMMYBAKE_OT_high_poly_add,
    DUMMYBAKE_OT_high_poly_remove,
    DUMMYBAKE_OT_select_object,
    DUMMYBAKE_PT_tools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dummy_bake_data = bpy.props.PointerProperty(type=DummyBakeData)


def unregister():
    del bpy.types.Scene.dummy_bake_data
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
