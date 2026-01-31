import bpy

from .lists import (
    BAKERY_UL_texture_sets,
    BAKERY_UL_target_meshes,
    BAKERY_UL_source_meshes,
    BAKERY_UL_bake_passes,
)
from .panels import BAKERY_PT_tools, BAKERY_PT_completed


classes = (
    BAKERY_UL_texture_sets,
    BAKERY_UL_target_meshes,
    BAKERY_UL_source_meshes,
    BAKERY_UL_bake_passes,
    BAKERY_PT_completed,
    BAKERY_PT_tools,
)


# register all UI classes.
def register():
    # register all UI classes.
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


# unregister all UI classes.
def unregister():
    # unregister UI classes in reverse order.
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
