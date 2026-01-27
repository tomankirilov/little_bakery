import bpy

from .bake_utils import _GEOMETRY_SKIP_TYPES


class DUMMYBAKE_OT_texture_set_add(bpy.types.Operator):
    bl_idname = "bakery.texture_set_add"
    bl_label = "Add Texture Set"
    bl_description = "Add a new texture set"

    # add a new texture set.
    def execute(self, context):
        # add a new texture set and make it active.
        data = context.scene.bakery_data
        item = data.texture_sets.add()
        item.name = f"texture_set_{len(data.texture_sets)}"
        data.active_texture_index = len(data.texture_sets) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_texture_set_remove(bpy.types.Operator):
    bl_idname = "bakery.texture_set_remove"
    bl_label = "Remove Texture Set"
    bl_description = "Remove the selected texture set"

    # remove the active texture set.
    def execute(self, context):
        # remove the active texture set safely.
        data = context.scene.bakery_data
        index = data.active_texture_index
        if 0 <= index < len(data.texture_sets):
            data.texture_sets.remove(index)
            if data.texture_sets:
                data.active_texture_index = min(index, len(data.texture_sets) - 1)
            else:
                data.active_texture_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_low_poly_add(bpy.types.Operator):
    bl_idname = "bakery.low_poly_add"
    bl_label = "Add Low Poly"
    bl_description = "Add a low poly entry to the selected texture set"

    # add selected objects to the low poly list.
    def execute(self, context):
        # add selected objects as low polys.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
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
    bl_idname = "bakery.low_poly_remove"
    bl_label = "Remove Low Poly"
    bl_description = "Remove the selected low poly entry"

    # remove the active low poly entry.
    def execute(self, context):
        # remove the active low poly entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_low_index
        if 0 <= index < len(tex_set.low_polys):
            tex_set.low_polys.remove(index)
            if tex_set.low_polys:
                tex_set.active_low_index = min(index, len(tex_set.low_polys) - 1)
            else:
                tex_set.active_low_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_high_poly_add(bpy.types.Operator):
    bl_idname = "bakery.high_poly_add"
    bl_label = "Add High Poly"
    bl_description = "Add a high poly entry to the selected low poly"

    # add selected objects to the high poly list.
    def execute(self, context):
        # add selected objects as high polys.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys or tex_set.active_low_index < 0:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
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
    bl_idname = "bakery.high_poly_remove"
    bl_label = "Remove High Poly"
    bl_description = "Remove the selected high poly entry"

    # remove the active high poly entry.
    def execute(self, context):
        # remove the active high poly entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys or tex_set.active_low_index < 0:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        index = low_item.active_high_index
        if 0 <= index < len(low_item.high_polys):
            low_item.high_polys.remove(index)
            if low_item.high_polys:
                low_item.active_high_index = min(index, len(low_item.high_polys) - 1)
            else:
                low_item.active_high_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_select_object(bpy.types.Operator):
    bl_idname = "bakery.select_object"
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

    # sync list selection with the scene selection.
    def invoke(self, context, event):
        # sync list selection and optionally select the object in the scene.
        data = context.scene.bakery_data
        if self.list_kind == "LOW":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_low_index = self.item_index
        elif self.list_kind == "HIGH":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.low_polys or tex_set.active_low_index < 0:
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


class DUMMYBAKE_OT_clear_selection(bpy.types.Operator):
    bl_idname = "bakery.clear_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear the active list selection"

    list_kind: bpy.props.EnumProperty(
        items=[
            ("TEXTURE", "Texture Sets", ""),
            ("LOW", "Low Poly", ""),
            ("HIGH", "High Poly", ""),
        ]
    )

    # clear list selections.
    def execute(self, context):
        # clear list selections without touching the objects.
        data = context.scene.bakery_data
        if self.list_kind == "TEXTURE":
            data.active_texture_index = -1
            return {"FINISHED"}
        if self.list_kind == "LOW":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_low_index = -1
            return {"FINISHED"}
        if self.list_kind == "HIGH":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.low_polys or tex_set.active_low_index < 0:
                return {"CANCELLED"}
            low_item = tex_set.low_polys[tex_set.active_low_index]
            low_item.active_high_index = -1
            return {"FINISHED"}
        return {"CANCELLED"}


