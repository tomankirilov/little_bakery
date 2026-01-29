import bpy

from .list_ops import (
    BAKERY_OT_texture_set_add,
    BAKERY_OT_texture_set_remove,
    BAKERY_OT_texture_set_move_up,
    BAKERY_OT_texture_set_move_down,
    BAKERY_OT_low_poly_add,
    BAKERY_OT_low_poly_remove,
    BAKERY_OT_low_poly_move_up,
    BAKERY_OT_low_poly_move_down,
    BAKERY_OT_high_poly_add,
    BAKERY_OT_high_poly_remove,
    BAKERY_OT_high_poly_move_up,
    BAKERY_OT_high_poly_move_down,
    BAKERY_OT_select_object,
    BAKERY_OT_clear_selection,
)
from .bake_ops import (
    BAKERY_OT_bake_all,
    BAKERY_OT_bake_selected_set,
)
from .io_ops import BAKERY_OT_pick_output_dir, BAKERY_OT_open_output_dir
from .target_ops import (
    Bakery_OT_bake_target_add_global,
    Bakery_OT_bake_target_remove_global,
    Bakery_OT_bake_target_move_global_up,
    Bakery_OT_bake_target_move_global_down,
    Bakery_OT_bake_target_add_set,
    Bakery_OT_bake_target_remove_set,
    Bakery_OT_bake_target_move_set_up,
    Bakery_OT_bake_target_move_set_down,
    BAKERY_OT_hide_last_bake,
)


classes = (
    BAKERY_OT_texture_set_add,
    BAKERY_OT_texture_set_remove,
    BAKERY_OT_texture_set_move_up,
    BAKERY_OT_texture_set_move_down,
    BAKERY_OT_low_poly_add,
    BAKERY_OT_low_poly_remove,
    BAKERY_OT_low_poly_move_up,
    BAKERY_OT_low_poly_move_down,
    BAKERY_OT_high_poly_add,
    BAKERY_OT_high_poly_remove,
    BAKERY_OT_high_poly_move_up,
    BAKERY_OT_high_poly_move_down,
    BAKERY_OT_select_object,
    BAKERY_OT_clear_selection,
    BAKERY_OT_bake_all,
    BAKERY_OT_bake_selected_set,
    BAKERY_OT_pick_output_dir,
    BAKERY_OT_open_output_dir,
    Bakery_OT_bake_target_add_global,
    Bakery_OT_bake_target_remove_global,
    Bakery_OT_bake_target_move_global_up,
    Bakery_OT_bake_target_move_global_down,
    Bakery_OT_bake_target_add_set,
    Bakery_OT_bake_target_remove_set,
    Bakery_OT_bake_target_move_set_up,
    Bakery_OT_bake_target_move_set_down,
    BAKERY_OT_hide_last_bake,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
