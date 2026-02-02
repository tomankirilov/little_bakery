import bpy

from .bake_utils import _BAKE_PASS_LABELS


class Bakery_OT_bake_pass_add_global(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_add_global"
    bl_label = "Add Bake Pass"
    bl_description = "Add a global bake pass"

    pass_type: bpy.props.EnumProperty(
        name="Pass",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("curvature_from_normal", "Curvature (Normal)", ""),
            ("opacity", "Opacity", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
            ("custom", "Custom", ""),
        ],
        default="normal",
    )

    # show a popup to pick the pass type.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # draw the popup UI.
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pass_type", text="")

    # add a new global bake pass entry.
    def execute(self, context):
        data = context.scene.bakery_data
        item = data.global_bake_passes.add()
        data.active_global_bake_pass_index = len(data.global_bake_passes) - 1
        item.pass_type = self.pass_type
        item.name = _BAKE_PASS_LABELS.get(item.pass_type, item.pass_type)
        return {"FINISHED"}


class Bakery_OT_bake_pass_remove_global(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_remove_global"
    bl_label = "Remove Bake Pass"
    bl_description = "Remove the selected global bake pass"

    # remove the active global bake pass entry.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_pass_index
        if 0 <= index < len(data.global_bake_passes):
            data.global_bake_passes.remove(index)
            data.active_global_bake_pass_index = min(index, len(data.global_bake_passes) - 1)
        return {"FINISHED"}


class Bakery_OT_bake_pass_move_global_up(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_move_global_up"
    bl_label = "Move Bake Pass Up"
    bl_description = "Move the selected global bake pass up"

    # move the active global bake pass up in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_pass_index
        if index > 0:
            data.global_bake_passes.move(index, index - 1)
            data.active_global_bake_pass_index = index - 1
        return {"FINISHED"}


class Bakery_OT_bake_pass_move_global_down(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_move_global_down"
    bl_label = "Move Bake Pass Down"
    bl_description = "Move the selected global bake pass down"

    # move the active global bake pass down in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_global_bake_pass_index
        if 0 <= index < len(data.global_bake_passes) - 1:
            data.global_bake_passes.move(index, index + 1)
            data.active_global_bake_pass_index = index + 1
        return {"FINISHED"}


class Bakery_OT_bake_pass_add_set(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_add_set"
    bl_label = "Add Bake Pass"
    bl_description = "Add a bake pass to the active texture set"

    pass_type: bpy.props.EnumProperty(
        name="Pass",
        items=[
            ("normal", "Normal", ""),
            ("ambient_occlusion", "Ambient Occlusion", ""),
            ("curvature", "Curvature", ""),
            ("curvature_from_normal", "Curvature (Normal)", ""),
            ("opacity", "Opacity", ""),
            ("thickness", "Thickness", ""),
            ("position", "Position", ""),
            ("bakery_position", "Bakery Position", ""),
            ("color_attribute", "Color Attribute", ""),
            ("random_island", "Random Island", ""),
            ("custom", "Custom", ""),
        ],
        default="normal",
    )

    # show a popup to pick the pass type.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # draw the popup UI.
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pass_type", text="")

    # add a new bake pass entry to the active set.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        item = tex_set.bake_passes.add()
        tex_set.active_bake_pass_index = len(tex_set.bake_passes) - 1
        item.pass_type = self.pass_type
        item.name = _BAKE_PASS_LABELS.get(item.pass_type, item.pass_type)
        return {"FINISHED"}


class Bakery_OT_bake_pass_remove_set(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_remove_set"
    bl_label = "Remove Bake Pass"
    bl_description = "Remove the selected bake pass from the active texture set"

    # remove the active bake pass from the set.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_pass_index
        if 0 <= target_index < len(tex_set.bake_passes):
            tex_set.bake_passes.remove(target_index)
            tex_set.active_bake_pass_index = min(target_index, len(tex_set.bake_passes) - 1)
        return {"FINISHED"}


class Bakery_OT_bake_pass_move_set_up(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_move_set_up"
    bl_label = "Move Bake Pass Up"
    bl_description = "Move the selected bake pass up in the active set"

    # move the active set bake pass up in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_pass_index
        if target_index > 0:
            tex_set.bake_passes.move(target_index, target_index - 1)
            tex_set.active_bake_pass_index = target_index - 1
        return {"FINISHED"}


class Bakery_OT_bake_pass_move_set_down(bpy.types.Operator):
    bl_idname = "bakery.bake_pass_move_set_down"
    bl_label = "Move Bake Pass Down"
    bl_description = "Move the selected bake pass down in the active set"

    # move the active set bake pass down in the list.
    def execute(self, context):
        data = context.scene.bakery_data
        index = data.active_texture_index
        if not data.texture_sets or index < 0 or index >= len(data.texture_sets):
            return {"CANCELLED"}
        tex_set = data.texture_sets[index]
        target_index = tex_set.active_bake_pass_index
        if 0 <= target_index < len(tex_set.bake_passes) - 1:
            tex_set.bake_passes.move(target_index, target_index + 1)
            tex_set.active_bake_pass_index = target_index + 1
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


