import re
from pathlib import Path

import bpy

try:
    import tomllib
except Exception:
    tomllib = None


def _load_manifest_version():
    manifest_path = Path(__file__).with_name("blender_manifest.toml")
    try:
        if tomllib:
            with manifest_path.open("rb") as handle:
                data = tomllib.load(handle)
            version_str = data.get("version")
        else:
            version_str = None
            for line in manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version"):
                    match = re.search(r"\"([^\"]+)\"", line)
                    if match:
                        version_str = match.group(1)
                        break
        if not version_str:
            return None, None
        parts = [int(p) for p in re.findall(r"\d+", version_str)]
        if not parts:
            return version_str, None
        return version_str, tuple(parts)
    except Exception:
        return None, None


__version__, _version_tuple = _load_manifest_version()
if _version_tuple is None:
    _version_tuple = (0, 0, 0)
    if __version__ is None:
        __version__ = "0.0.0"

bl_info = {
    "name": "Little Bakery",
    "author": "tomanov",
    "version": _version_tuple,
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Little Bakery",
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
    name_separator: bpy.props.StringProperty(
        name="Name Separator",
        description="Separator between texture set and bake pass names",
        default="_",
    )

    # Draw Preferences UI:
    def draw(self, context):

        layout = self.layout
        layout.prop(self, "name_separator")
        layout.prop(self, "save_before_bake")
        layout.prop(self, "debug_logging")

        # Links:
        #row = layout.row(align=True)
        #row.operator("wm.url_open", text="GitHub").url = "https://tomanov.art/"
        #row.operator("wm.url_open", text="Author").url = "https://tomanov.art/"

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
