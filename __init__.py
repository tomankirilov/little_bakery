# SPDX-License-Identifier: GPL-2.0-or-later
# Dummy Bake Tools addon skeleton.

bl_info = {
    "name": "Dummy Bake Tools",
    "author": "Toman",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Dummy Bake",
    "description": "UI scaffolding for bake automation",
    "category": "Object",
}

from . import operators, properties, ui

_modules = (properties, operators, ui)


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()


if __name__ == "__main__":
    register()
