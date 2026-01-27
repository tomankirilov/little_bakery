import bpy

from .items import (
    BakeryHighPolyItem,
    BakeryLowPolyItem,
    BakeryBakeTargetItem,
    BakeryTextureSet,
)
from .settings import BakeryData
from .defaults import _deferred_defaults, _on_load


classes = (
    BakeryHighPolyItem,
    BakeryLowPolyItem,
    BakeryBakeTargetItem,
    BakeryTextureSet,
    BakeryData,
)


# register property groups and attach them to the Scene.
def register():
    # register the property groups and attach them to the Scene.
    for cls in classes:
        if getattr(bpy.types, cls.__name__, None) is None:
            bpy.utils.register_class(cls)
    bpy.types.Scene.bakery_data = bpy.props.PointerProperty(type=BakeryData)
    if not bpy.app.timers.is_registered(_deferred_defaults):
        bpy.app.timers.register(_deferred_defaults, first_interval=0.1)
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


# unregister property groups and remove the Scene pointer.
def unregister():
    # remove the Scene pointer and unregister classes in reverse.
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    if bpy.app.timers.is_registered(_deferred_defaults):
        bpy.app.timers.unregister(_deferred_defaults)
    del bpy.types.Scene.bakery_data
    for cls in reversed(classes):
        if getattr(bpy.types, cls.__name__, None) is not None:
            bpy.utils.unregister_class(cls)
