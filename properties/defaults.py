import bpy


def _ensure_defaults(scene):
    data = getattr(scene, "bakery_data", None)
    if not data:
        return
    if not data.texture_sets:
        tex_set = data.texture_sets.add()
        tex_set.name = "texture"
        data.active_texture_index = 0
    if not data.global_bake_passes:
        bake_pass = data.global_bake_passes.add()
        bake_pass.pass_type = "normal"
        bake_pass.name = "normal"
        data.active_global_bake_pass_index = 0


def _ensure_defaults_all():
    scenes = getattr(bpy.data, "scenes", None)
    if not scenes:
        return False
    for scene in scenes:
        _ensure_defaults(scene)
    return True


def _deferred_defaults():
    if _ensure_defaults_all():
        return None
    return 1.0


def _on_load(_bakery):
    if not _ensure_defaults_all():
        if not bpy.app.timers.is_registered(_deferred_defaults):
            bpy.app.timers.register(_deferred_defaults, first_interval=0.1)
