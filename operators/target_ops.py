import bpy

from .bake_utils import _TARGET_LABELS


class Bakery_OT_bake_target_add_global(bpy.types.Operator):
    bl_idname = "bakery.bake_target_add_global"
    bl_label = "Add Bake Target"
    bl_description = "Add a global bake target"

    target_type: bpy.props.EnumProperty(
        name="Target",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
            ("custom", "Custom", ""),
        ],
        default="normal",
    )

    # show a popup to pick the target type.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # draw the popup UI.
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_type", text="")

    # add a new global bake target entry.
    def execute(self, context):
        data = context.scene.bakery_data
        item = data.global_bake_targets.add()
        data.active_global_bake_target_index = len(data.global_bake_targets) - 1
        item.target_type = self.target_type
        item.name = _TARGET_LABELS.get(item.target_type, item.target_type)
        return {"FINISHED"}


class Bakery_OT_bake_target_remove_global(bpy.types.Operator):
    bl_idname = "bakery.bake_target_remove_global"
    bl_label = "Remove Bake Target"
    bl_description = "Remove the selected global bake target"

    # remove the active global bake target entry.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_target_index
        if 0 <= index < len(data.global_bake_targets):
            data.global_bake_targets.remove(index)
            data.active_global_bake_target_index = min(index, len(data.global_bake_targets) - 1)
        return {"FINISHED"}


class Bakery_OT_bake_target_move_global_up(bpy.types.Operator):
    bl_idname = "bakery.bake_target_move_global_up"
    bl_label = "Move Bake Target Up"
    bl_description = "Move the selected global bake target up"

    # move the active global bake target up in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_target_index
        if index > 0:
            data.global_bake_targets.move(index, index - 1)
            data.active_global_bake_target_index = index - 1
        return {"FINISHED"}


class Bakery_OT_bake_target_move_global_down(bpy.types.Operator):
    bl_idname = "bakery.bake_target_move_global_down"
    bl_label = "Move Bake Target Down"
    bl_description = "Move the selected global bake target down"

    # move the active global bake target down in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_target_index
        if 0 <= index < len(data.global_bake_targets) - 1:
            data.global_bake_targets.move(index, index + 1)
            data.active_global_bake_target_index = index + 1
        return {"FINISHED"}


class Bakery_OT_bake_target_add_set(bpy.types.Operator):
    bl_idname = "bakery.bake_target_add_set"
    bl_label = "Add Bake Target"
    bl_description = "Add a bake target to the active texture set"

    target_type: bpy.props.EnumProperty(
        name="Target",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
            ("custom", "Custom", ""),
        ],
        default="normal",
    )

    # show a popup to pick the target type.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # draw the popup UI.
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_type", text="")

    # add a new bake target entry to the active set.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        item = tex_set.bake_targets.add()
        tex_set.active_bake_target_index = len(tex_set.bake_targets) - 1
        item.target_type = self.target_type
        item.name = _TARGET_LABELS.get(item.target_type, item.target_type)
        return {"FINISHED"}


class Bakery_OT_bake_target_remove_set(bpy.types.Operator):
    bl_idname = "bakery.bake_target_remove_set"
    bl_label = "Remove Bake Target"
    bl_description = "Remove the selected bake target from the active texture set"

    # remove the active bake target from the set.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_target_index
        if 0 <= target_index < len(tex_set.bake_targets):
            tex_set.bake_targets.remove(target_index)
            tex_set.active_bake_target_index = min(target_index, len(tex_set.bake_targets) - 1)
        return {"FINISHED"}


class Bakery_OT_bake_target_move_set_up(bpy.types.Operator):
    bl_idname = "bakery.bake_target_move_set_up"
    bl_label = "Move Bake Target Up"
    bl_description = "Move the selected bake target up in the active set"

    # move the active set bake target up in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_target_index
        if target_index > 0:
            tex_set.bake_targets.move(target_index, target_index - 1)
            tex_set.active_bake_target_index = target_index - 1
        return {"FINISHED"}


class Bakery_OT_bake_target_move_set_down(bpy.types.Operator):
    bl_idname = "bakery.bake_target_move_set_down"
    bl_label = "Move Bake Target Down"
    bl_description = "Move the selected bake target down in the active set"

    # move the active set bake target down in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_target_index
        if 0 <= target_index < len(tex_set.bake_targets) - 1:
            tex_set.bake_targets.move(target_index, target_index + 1)
            tex_set.active_bake_target_index = target_index + 1
        return {"FINISHED"}


# hide the last-bake banner when the user dismisses it.
class BAKERY_OT_hide_last_bake(bpy.types.Operator):
    bl_idname = "bakery.hide_last_bake"
    bl_label = "Hide Last Bake"
    bl_description = "Hide the last bake message"

    # toggle off the last-bake banner.
    def execute(self, context):
        data = context.scene.bakery_data
        data.show_last_bake = False
        return {"FINISHED"}


# run the full bake pipeline for one or more texture sets.
