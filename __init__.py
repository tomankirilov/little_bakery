import bpy

bl_info = {
    "name": "Bakery",
    "author": "tomanov",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Bakery",
    "description": "bake automation",
    "category": "Object",
}

from . import operators, properties, ui

_ADDON_ID = __name__


class BakeryPreferences(bpy.types.AddonPreferences):
    bl_idname = _ADDON_ID

    debug_logging: bpy.props.BoolProperty(
        name="Debug Logging",
        description="Print detailed bake progress to the console",
        default=False,
    )
    save_before_bake: bpy.props.BoolProperty(
        name="Save blend file before bake",
        description="Save the current .blend before starting a bake",
        default=False,
    )

    # Draw Preferences UI.
    def draw(self, context):

        layout = self.layout
        layout.prop(self, "debug_logging")
        layout.prop(self, "save_before_bake")
        row = layout.row(align=True)
        row.operator("wm.url_open", text="GitHub").url = "https://tomanov.art/"
        row.operator("wm.url_open", text="Author").url = "https://tomanov.art/"

_modules = (properties, operators, ui)


def register():
    bpy.utils.register_class(BakeryPreferences)
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
    bpy.utils.unregister_class(BakeryPreferences)


if __name__ == "__main__":
    register()
