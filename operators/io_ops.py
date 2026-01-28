import os
import bpy

from .bake_utils import _resolve_output_dir, _relative_to_blend


class BAKERY_OT_pick_output_dir(bpy.types.Operator):
    bl_idname = "bakery.pick_output_dir"
    bl_label = "Pick Output Folder"
    bl_description = "Choose a subfolder relative to the current blend file"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    # open the file picker at the current output folder.
    def invoke(self, context, event):
        # open the folder picker at the current output location.
        data = context.scene.bakery_data
        base_dir = bpy.path.abspath("//")
        current = _resolve_output_dir(data.output_dir)
        target = current if current else base_dir
        if target and not os.path.isdir(target):
            try:
                os.makedirs(target, exist_ok=True)
            except OSError:
                target = base_dir
        self.directory = target
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    # store the chosen folder as a relative path.
    def execute(self, context):
        # store the picked folder as a blend-relative path.
        data = context.scene.bakery_data
        if self.directory:
            data.output_dir = _relative_to_blend(self.directory)
        return {"FINISHED"}


class BAKERY_OT_open_output_dir(bpy.types.Operator):
    bl_idname = "bakery.open_output_dir"
    bl_label = "Open Bake Folder"
    bl_description = "Open the current bake output folder"

    # open the output directory in the OS file browser.
    def execute(self, context):
        data = context.scene.bakery_data
        target = _resolve_output_dir(data.output_dir)
        if not target:
            self.report({"WARNING"}, "Output directory is empty")
            return {"CANCELLED"}
        try:
            os.makedirs(target, exist_ok=True)
        except OSError:
            self.report({"WARNING"}, "Failed to create output directory")
            return {"CANCELLED"}
        try:
            bpy.ops.wm.path_open(filepath=target)
        except RuntimeError:
            self.report({"WARNING"}, "Failed to open output directory")
            return {"CANCELLED"}
        return {"FINISHED"}


