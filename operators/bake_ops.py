import bpy

from .bake_utils import _ensure_saved_blend, _popup_error, _bake_texture_sets


class BAKERY_OT_bake_all(bpy.types.Operator):
    bl_idname = "bakery.bake_all"
    bl_label = "Bake"
    bl_description = "Bake the checked texture sets"

    # bake the checked texture sets.
    def execute(self, context):
        # bake the checked texture sets in order.
        # route to the shared bake pipeline for checked sets.
        if not _ensure_saved_blend(self, context):
            return {"CANCELLED"}
        data = context.scene.bakery_data
        if not data.texture_sets:
            self.report({"WARNING"}, "No texture sets to bake")
            return {"CANCELLED"}

        selected_sets = [tex_set for tex_set in data.texture_sets if tex_set.enabled]
        if not selected_sets:
            _popup_error(context, "Please check at least one texture set")
            self.report({"WARNING"}, "Please check at least one texture set")
            return {"CANCELLED"}
        result = _bake_texture_sets(self, context, selected_sets, "Bake")
        return {"FINISHED"} if result else {"CANCELLED"}


class BAKERY_OT_bake_selected_set(bpy.types.Operator):
    bl_idname = "bakery.bake_selected_set"
    bl_label = "Bake Selected Sets"
    bl_description = "Deprecated"

    # deprecated entry point (kept for safety if wired elsewhere).
    def execute(self, context):
        _popup_error(context, "Use the Bake button instead")
        self.report({"WARNING"}, "Use the Bake button instead")
        return {"CANCELLED"}


