# SPDX-License-Identifier: GPL-2.0-or-later
# Dummy Bake Tools addon skeleton.

import bpy

bl_info = {
    "name": "Dummy Bake Tools",
    "author": "tomanov",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Dummy Bake",
    "description": "bake automation",
    "category": "Object",
}

from . import operators, properties, ui

_ADDON_ID = __name__


class DummyBakePreferences(bpy.types.AddonPreferences):
    bl_idname = _ADDON_ID

    debug_logging: bpy.props.BoolProperty(
        name="Debug Logging",
        description="Print detailed bake progress to the console",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="GitHub").url = "https://tomanov.art/"
        row.operator("wm.url_open", text="Author").url = "https://tomanov.art/"
        layout.prop(self, "debug_logging")

_modules = (properties, operators, ui)


def register():
    bpy.utils.register_class(DummyBakePreferences)
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
    bpy.utils.unregister_class(DummyBakePreferences)


if __name__ == "__main__":
    register()
