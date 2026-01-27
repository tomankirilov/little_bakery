import bpy

from .lists import (
    DUMMYBAKE_UL_texture_sets,
    DUMMYBAKE_UL_low_polys,
    DUMMYBAKE_UL_high_polys,
    BAKERY_UL_bake_targets,
)
from .panels import DUMMYBAKE_PT_tools


classes = (
    DUMMYBAKE_UL_texture_sets,
    DUMMYBAKE_UL_low_polys,
    DUMMYBAKE_UL_high_polys,
    BAKERY_UL_bake_targets,
    DUMMYBAKE_PT_tools,
)


# register all UI classes.
def register():
    # register all UI classes.
    for cls in classes:
        bpy.utils.register_class(cls)


# unregister all UI classes.
def unregister():
    # unregister UI classes in reverse order.
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
