import bpy

from .bake_utils import _GEOMETRY_SKIP_TYPES


class BAKERY_OT_texture_set_add(bpy.types.Operator):
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


class BAKERY_OT_texture_set_remove(bpy.types.Operator):
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


class BAKERY_OT_texture_set_move_up(bpy.types.Operator):
    bl_idname = "bakery.texture_set_move_up"
    bl_label = "Move Texture Set Up"
    bl_description = "Move the selected texture set up"

    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if index > 0:
            data.texture_sets.move(index, index - 1)
            data.active_texture_index = index - 1
        return {"FINISHED"}


class BAKERY_OT_texture_set_move_down(bpy.types.Operator):
    bl_idname = "bakery.texture_set_move_down"
    bl_label = "Move Texture Set Down"
    bl_description = "Move the selected texture set down"

    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if 0 <= index < len(data.texture_sets) - 1:
            data.texture_sets.move(index, index + 1)
            data.active_texture_index = index + 1
        return {"FINISHED"}


class BAKERY_OT_target_mesh_add(bpy.types.Operator):
    bl_idname = "bakery.target_mesh_add"
    bl_label = "Add Target Mesh"
    bl_description = "Add a target mesh entry to the selected texture set"

    # add selected objects to the target list.
    def execute(self, context):
        # add selected objects as targets.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
        ]
        if selected:
            existing = {item.object for item in tex_set.target_meshes if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = tex_set.target_meshes.add()
                item.object = obj
            tex_set.active_target_index = max(0, len(tex_set.target_meshes) - 1)
        else:
            tex_set.target_meshes.add()
            tex_set.active_target_index = len(tex_set.target_meshes) - 1
        return {"FINISHED"}


class BAKERY_OT_target_mesh_remove(bpy.types.Operator):
    bl_idname = "bakery.target_mesh_remove"
    bl_label = "Remove Target Mesh"
    bl_description = "Remove the selected target mesh entry"

    # remove the active target entry.
    def execute(self, context):
        # remove the active target entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_target_index
        if 0 <= index < len(tex_set.target_meshes):
            tex_set.target_meshes.remove(index)
            if tex_set.target_meshes:
                tex_set.active_target_index = min(index, len(tex_set.target_meshes) - 1)
            else:
                tex_set.active_target_index = -1
        return {"FINISHED"}


class BAKERY_OT_target_mesh_move_up(bpy.types.Operator):
    bl_idname = "bakery.target_mesh_move_up"
    bl_label = "Move Target Up"
    bl_description = "Move the selected target up"

    def execute(self, context):
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_target_index
        if index > 0:
            tex_set.target_meshes.move(index, index - 1)
            tex_set.active_target_index = index - 1
        return {"FINISHED"}


class BAKERY_OT_target_mesh_move_down(bpy.types.Operator):
    bl_idname = "bakery.target_mesh_move_down"
    bl_label = "Move Target Down"
    bl_description = "Move the selected target down"

    def execute(self, context):
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_target_index
        if 0 <= index < len(tex_set.target_meshes) - 1:
            tex_set.target_meshes.move(index, index + 1)
            tex_set.active_target_index = index + 1
        return {"FINISHED"}


class BAKERY_OT_source_mesh_add(bpy.types.Operator):
    bl_idname = "bakery.source_mesh_add"
    bl_label = "Add Source Mesh"
    bl_description = "Add a source mesh entry to the selected target mesh"

    # add selected objects to the source list.
    def execute(self, context):
        # add selected objects as sources.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.target_meshes or tex_set.active_target_index < 0:
            return {"CANCELLED"}
        target_item = tex_set.target_meshes[tex_set.active_target_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
        ]
        if selected:
            existing = {item.object for item in target_item.source_meshes if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = target_item.source_meshes.add()
                item.object = obj
            target_item.active_source_index = max(0, len(target_item.source_meshes) - 1)
        else:
            target_item.source_meshes.add()
            target_item.active_source_index = len(target_item.source_meshes) - 1
        return {"FINISHED"}


class BAKERY_OT_source_mesh_remove(bpy.types.Operator):
    bl_idname = "bakery.source_mesh_remove"
    bl_label = "Remove Source Mesh"
    bl_description = "Remove the selected source mesh entry"

    # remove the active source entry.
    def execute(self, context):
        # remove the active source entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.target_meshes or tex_set.active_target_index < 0:
            return {"CANCELLED"}
        target_item = tex_set.target_meshes[tex_set.active_target_index]
        index = target_item.active_source_index
        if 0 <= index < len(target_item.source_meshes):
            target_item.source_meshes.remove(index)
            if target_item.source_meshes:
                target_item.active_source_index = min(index, len(target_item.source_meshes) - 1)
            else:
                target_item.active_source_index = -1
        return {"FINISHED"}


class BAKERY_OT_source_mesh_move_up(bpy.types.Operator):
    bl_idname = "bakery.source_mesh_move_up"
    bl_label = "Move Source Up"
    bl_description = "Move the selected source up"

    def execute(self, context):
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.target_meshes or tex_set.active_target_index < 0:
            return {"CANCELLED"}
        target_item = tex_set.target_meshes[tex_set.active_target_index]
        index = target_item.active_source_index
        if index > 0:
            target_item.source_meshes.move(index, index - 1)
            target_item.active_source_index = index - 1
        return {"FINISHED"}


class BAKERY_OT_source_mesh_move_down(bpy.types.Operator):
    bl_idname = "bakery.source_mesh_move_down"
    bl_label = "Move Source Down"
    bl_description = "Move the selected source down"

    def execute(self, context):
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.target_meshes or tex_set.active_target_index < 0:
            return {"CANCELLED"}
        target_item = tex_set.target_meshes[tex_set.active_target_index]
        index = target_item.active_source_index
        if 0 <= index < len(target_item.source_meshes) - 1:
            target_item.source_meshes.move(index, index + 1)
            target_item.active_source_index = index + 1
        return {"FINISHED"}


class BAKERY_OT_select_object(bpy.types.Operator):
    bl_idname = "bakery.select_object"
    bl_label = "Select Object"
    bl_description = "Select the object from this list item"

    object_name: bpy.props.StringProperty()
    list_kind: bpy.props.EnumProperty(
        items=[
            ("TARGET", "Target Mesh", ""),
            ("SOURCE", "Source Mesh", ""),
        ]
    )
    item_index: bpy.props.IntProperty()

    # sync list selection with the scene selection.
    def invoke(self, context, event):
        # sync list selection and optionally select the object in the scene.
        data = context.scene.bakery_data
        if self.list_kind == "TARGET":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_target_index = self.item_index
        elif self.list_kind == "SOURCE":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.target_meshes or tex_set.active_target_index < 0:
                return {"CANCELLED"}
            target_item = tex_set.target_meshes[tex_set.active_target_index]
            target_item.active_source_index = self.item_index

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


class BAKERY_OT_clear_selection(bpy.types.Operator):
    bl_idname = "bakery.clear_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear the active list selection"

    list_kind: bpy.props.EnumProperty(
        items=[
            ("TEXTURE", "Texture Sets", ""),
            ("TARGET", "Target Mesh", ""),
            ("SOURCE", "Source Mesh", ""),
        ]
    )

    # clear list selections.
    def execute(self, context):
        # clear list selections without touching the objects.
        data = context.scene.bakery_data
        if self.list_kind == "TEXTURE":
            data.active_texture_index = -1
            return {"FINISHED"}
        if self.list_kind == "TARGET":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_target_index = -1
            return {"FINISHED"}
        if self.list_kind == "SOURCE":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.target_meshes or tex_set.active_target_index < 0:
                return {"CANCELLED"}
            target_item = tex_set.target_meshes[tex_set.active_target_index]
            target_item.active_source_index = -1
            return {"FINISHED"}
        return {"CANCELLED"}



