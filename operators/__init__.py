import bpy

from .list_ops import (
    DUMMYBAKE_OT_texture_set_add,
    DUMMYBAKE_OT_texture_set_remove,
    DUMMYBAKE_OT_low_poly_add,
    DUMMYBAKE_OT_low_poly_remove,
    DUMMYBAKE_OT_high_poly_add,
    DUMMYBAKE_OT_high_poly_remove,
    DUMMYBAKE_OT_select_object,
    DUMMYBAKE_OT_clear_selection,
)
from .bake_ops import (
    DUMMYBAKE_OT_bake_all,
    DUMMYBAKE_OT_bake_selected_set,
)
from .io_ops import DUMMYBAKE_OT_pick_output_dir
from .target_ops import (
    Bakery_OT_bake_target_add_global,
    Bakery_OT_bake_target_remove_global,
    Bakery_OT_bake_target_move_global_up,
    Bakery_OT_bake_target_move_global_down,
    Bakery_OT_bake_target_add_set,
    Bakery_OT_bake_target_remove_set,
    Bakery_OT_bake_target_move_set_up,
    Bakery_OT_bake_target_move_set_down,
    DUMMYBAKE_OT_hide_last_bake,
)


classes = (
    DUMMYBAKE_OT_texture_set_add,
    DUMMYBAKE_OT_texture_set_remove,
    DUMMYBAKE_OT_low_poly_add,
    DUMMYBAKE_OT_low_poly_remove,
    DUMMYBAKE_OT_high_poly_add,
    DUMMYBAKE_OT_high_poly_remove,
    DUMMYBAKE_OT_select_object,
    DUMMYBAKE_OT_clear_selection,
    DUMMYBAKE_OT_bake_all,
    DUMMYBAKE_OT_bake_selected_set,
    DUMMYBAKE_OT_pick_output_dir,
    Bakery_OT_bake_target_add_global,
    Bakery_OT_bake_target_remove_global,
    Bakery_OT_bake_target_move_global_up,
    Bakery_OT_bake_target_move_global_down,
    Bakery_OT_bake_target_add_set,
    Bakery_OT_bake_target_remove_set,
    Bakery_OT_bake_target_move_set_up,
    Bakery_OT_bake_target_move_set_down,
    DUMMYBAKE_OT_hide_last_bake,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
