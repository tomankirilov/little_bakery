from pathlib import Path

import bpy

from .draw_helpers import _indent_column, _draw_resolution_row, _draw_bake_pass_settings


def _addon_version():
    try:
        import importlib
        import sys

        addon_key = __package__.split(".")[0] if __package__ else None
        addon_mod = sys.modules.get(addon_key) if addon_key else None
        if addon_mod is None and addon_key:
            addon_mod = sys.modules.get(f"{addon_key}.__init__")
        if addon_mod is None and addon_key:
            addon_mod = importlib.import_module(addon_key)
        if addon_mod is None:
            return None
        version_str = getattr(addon_mod, "__version__", None)
        if version_str:
            return version_str
        info = getattr(addon_mod, "bl_info", None) or {}
        version_tuple = info.get("version")
        if version_tuple:
            return ".".join(str(x) for x in version_tuple)
    except Exception:
        return None
    return None


def _manifest_version():
    try:
        here = Path(__file__).resolve()
        for parent in [here.parent, *here.parents]:
            manifest_path = parent / "blender_manifest.toml"
            if not manifest_path.is_file():
                continue
            for line in manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version"):
                    parts = line.split('"')
                    if len(parts) >= 2:
                        return parts[1]
            break
    except Exception:
        return None
    return None


def _version_name():
    try:
        here = Path(__file__).resolve()
        for parent in [here.parent, *here.parents]:
            metadata_path = parent / "metadata.toml"
            if not metadata_path.is_file():
                continue
            for line in metadata_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version_name"):
                    parts = line.split('"')
                    if len(parts) >= 2:
                        return parts[1]
            break
    except Exception:
        return None
    return None


def _draw_about(section_layout, data, force_expand=False):
    about_box = section_layout.box()
    header = about_box.row(align=True)
    header.prop(
        data,
        "show_about",
        icon="TRIA_DOWN" if (data.show_about or force_expand) else "TRIA_RIGHT",
        icon_only=True,
        emboss=False,
    )
    header.label(text="Little Bakery", icon="QUESTION")
    #header.label(text="About", icon="USER")
    if data.show_about or force_expand:
        about_col = about_box.column(align=True)

        label_row = about_col.row()
        label_row.alignment = "CENTER"
        label_row.label(text="BAKED WITH LOVE")

        label_row = about_col.row()
        label_row.alignment = "CENTER"
        label_row.label(text="♥️ for everybody ♥️")

        about_col.separator(factor=1.0)

        version = _addon_version() or _manifest_version()
        version_name = _version_name()
        if version and version_name:
            version_label = f"({version} - {version_name})"
        elif version:
            version_label = f"v{version}"
        elif version_name:
            version_label = f"{version_name}"
        else:
            version_label = "vUNKNOWN"
        label_row = about_col.row()
        label_row.alignment = "CENTER"
        label_row.label(text=version_label)

        about_col.separator(factor=2.0)

        buttons_col = about_col.column(align=True)
        buttons_col.operator(
            "wm.url_open",
            text="GitHub",
            icon="EXPERIMENTAL",
        ).url = "https://github.com/tomankirilov/little_bakery/tree/1.0-pale-buns"
        
        buttons_col.operator(
            "wm.url_open",
            text="Documentation",
            icon="HELP",
        ).url = "https://tomankirilov.github.io/little_bakery_docs/"

        buttons_col.operator(
            "wm.url_open",
            text="About",
            icon="USER",
        ).url = "https://tomanov.art/"

        about_col.separator(factor=0.5)


def _draw_completed(layout, data):
    completed_box = layout.box()
    title_row = completed_box.row()
    title_row.alignment = "CENTER"
    title_row.label(text="BAKE COMPLETED", icon="CHECKMARK")

    info_col = completed_box.column(align=True)
    info_col.label(text=f"- Completed in {data.last_bake_duration}")

    textures = [item.value for item in data.last_bake_textures]
    if textures:
        list_box = layout.box()
        list_header = list_box.row()
        list_header.label(text="Baked Textures")
        for name in textures:
            row = list_box.split(factor=0.08, align=True)
            row.label(text="")
            row.column(align=True).label(text=f"- {name}")

    buttons_col = layout.column(align=True)
    buttons_col.scale_y = 1.6
    buttons_col.operator("bakery.open_output_dir", text="Open Bake Directory", icon="FILE_FOLDER")
    buttons_col.operator("bakery.hide_last_bake", text="Continue Baking", icon="PLAY")


class BAKERY_PT_completed(bpy.types.Panel):
    bl_label = ""
    bl_idname = "BAKERY_PT_completed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Little Bakery"

    @classmethod
    def poll(cls, context):
        data = getattr(getattr(context, "scene", None), "bakery_data", None)
        if not data:
            return False
        if data.is_baking:
            return False
        return bool(data.show_last_bake and data.last_bake_duration)

    def draw(self, context):
        layout = self.layout
        data = context.scene.bakery_data

        _draw_completed(layout, data)
        _draw_about(layout, data, force_expand=True)


class BAKERY_PT_tools(bpy.types.Panel):
    bl_label = "Little Bakery"
    bl_idname = "BAKERY_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Little Bakery"

    @classmethod
    def poll(cls, context):
        data = getattr(getattr(context, "scene", None), "bakery_data", None)
        if not data:
            return True
        if data.is_baking:
            return True
        return not (data.show_last_bake and data.last_bake_duration)

    def draw(self, context):
        layout = self.layout
        data = context.scene.bakery_data
        if data and (not data.texture_sets or not data.global_bake_passes):
            try:
                from ..properties.defaults import _ensure_defaults
                _ensure_defaults(context.scene)
            except Exception:
                pass

        # only show baking progress and about while baking.
        if data.is_baking:
            progress_box = layout.box()
            title_row = progress_box.row()
            
            
            #title_row.alert = True #make the text red
            title_row.alignment = "CENTER"
            title_row.label(text="BAKING IN PROGRESS", icon="ERROR")

            info_col = progress_box.column(align=True)
            info_col.label(text=f"- Set: {data.baking_set_name}")
            info_col.label(text=f"- Pass: {data.baking_pass_name}")

            
            progress_box.prop(data, "baking_progress", text="Progress", slider=True)
            _draw_about(layout, data, force_expand=True)
            return

        _draw_about(layout, data)

        if data.show_last_bake and data.last_bake_duration:
            _draw_completed(layout, data)
            _draw_about(layout, force_expand=True)
            return

        buttons_col = layout.column(align=True)
        buttons_col.scale_y = 2.0
        buttons_col.operator("bakery.bake_all", text="Bake", icon="SEQUENCE")



        global_box = layout.box()
        header = global_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_global_settings",
            icon="TRIA_DOWN" if data.show_global_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Render Settings", icon="RESTRICT_RENDER_OFF")
        if data.show_global_settings:
            sections = global_box.column(align=True)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_settings",
                icon="TRIA_DOWN" if data.show_render_settings else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Rendering")
            if data.show_render_settings:
                render_col = _indent_column(sections)
                row = render_col.split(factor=0.4, align=True)
                row.label(text="Render Device")
                row.prop(data, "render_device", text="")

                render_col.separator(factor=0.3)

                _draw_resolution_row(render_col, data, "global_resolution")
                render_col.separator(factor=0.3)

                pad_label = render_col.row(align=True)
                pad_label.label(text="Padding")
                pad_col = _indent_column(render_col)
                pad_col.separator(factor=0.2)
                row = pad_col.split(factor=0.4, align=True)
                row.label(text="Method")
                row.prop(data, "global_dilation_method", text="")
                pad_col.prop(data, "global_dilation")

                render_col.separator(factor=0.4)

                aa_label = render_col.row(align=True)
                aa_label.label(text="Anti-Aliasing")
                aa_col = _indent_column(render_col)

                fxaa_row = aa_col.row(align=True)
                fxaa_row.prop(data, "global_fxaa_enabled", text="FXAA")
                if data.global_fxaa_enabled:
                    fxaa_opts = _indent_column(aa_col)
                    fxaa_opts.prop(data, "global_fxaa_threshold")
                    fxaa_opts.prop(data, "global_fxaa_blend")

                aa_col.separator(factor=0.3)

                msaa_row = aa_col.split(factor=0.4, align=True)
                msaa_row.label(text="MSAA")
                msaa_row.prop(data, "global_msaa", text="")

            sections.separator(factor=0.4)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_cage",
                icon="TRIA_DOWN" if data.show_render_cage else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Projection")
            if data.show_render_cage:
                cage_col = _indent_column(sections)
                uv_row = cage_col.row(align=True)
                uv_row.prop(data, "override_uv_map", text="")
                uv_map_row = uv_row.row(align=True)
                uv_map_row.enabled = data.override_uv_map
                uv_map_row.prop(data, "uv_map_name", text="UV Map")
                cage_col.separator(factor=0.2)
                cage_col.prop(data, "global_extrusion")
                cage_col.prop(data, "global_max_ray_distance", text="Max Ray Distance")

            sections.separator(factor=0.4)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_output",
                icon="TRIA_DOWN" if data.show_output else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Output")
            if data.show_output:
                output_col = _indent_column(sections)
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Directory")
                output_row = row.row(align=True)
                output_row.prop(data, "output_dir", text="")
                output_row.operator("bakery.pick_output_dir", text="", icon="FILE_FOLDER")
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Format")
                row.prop(data, "output_format", text="")
                row = output_col.split(factor=0.4, align=True)
                row.label(text="Color")
                row.prop(data, "output_color_mode", text="")
                if data.output_format == "PNG":
                    row = output_col.split(factor=0.4, align=True)
                    row.label(text="Color Depth")
                    row.prop(data, "output_color_depth", text="")
                    row = output_col.split(factor=0.4, align=True)
                    row.label(text="Compression")
                    row.prop(data, "output_png_compression", text="")
        bake_box = layout.box()
        header = bake_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_bake_passes",
            icon="TRIA_DOWN" if data.show_bake_passes else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Bake Passes", icon="RESTRICT_COLOR_ON")
        if data.show_bake_passes:
            bake_col = bake_box.column(align=True)
            row = bake_col.row()
            row.template_list(
                "BAKERY_UL_bake_passes",
                "",
                data,
                "global_bake_passes",
                data,
                "active_global_bake_pass_index",
                rows=4,
            )
            col = row.column(align=True)
            col.operator("bakery.bake_pass_add_global", icon="ADD", text="")
            col.operator("bakery.bake_pass_remove_global", icon="REMOVE", text="")
            col.separator()
            col.operator("bakery.bake_pass_move_global_up", icon="TRIA_UP", text="")
            col.operator("bakery.bake_pass_move_global_down", icon="TRIA_DOWN", text="")

            if data.global_bake_passes and 0 <= data.active_global_bake_pass_index < len(data.global_bake_passes):
                item = data.global_bake_passes[data.active_global_bake_pass_index]
                settings_col = bake_col.column(align=True)
                settings_col.separator()
                header = settings_col.row(align=True)
                header.prop(
                    item,
                    "show_settings",
                    icon="TRIA_DOWN" if item.show_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                header.label(text="Pass Settings")
                if item.show_settings:
                    _draw_bake_pass_settings(settings_col, item)

        box = layout.box()
        header = box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_texture_sets",
            icon="TRIA_DOWN" if data.show_texture_sets else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Texture Sets", icon="RENDER_RESULT")
        tex_set = None
        if data.texture_sets and 0 <= data.active_texture_index < len(data.texture_sets):
            tex_set = data.texture_sets[data.active_texture_index]

        if data.show_texture_sets:
            row = box.row()
            row.template_list(
                "BAKERY_UL_texture_sets",
                "",
                data,
                "texture_sets",
                data,
                "active_texture_index",
                rows=4,
            )
            col = row.column(align=True)
            col.operator("bakery.texture_set_add", icon="ADD", text="")
            col.operator("bakery.texture_set_remove", icon="REMOVE", text="")
            col.operator("bakery.texture_set_duplicate", icon="DUPLICATE", text="")
            col.separator()
            col.operator("bakery.texture_set_move_up", icon="TRIA_UP", text="")
            col.operator("bakery.texture_set_move_down", icon="TRIA_DOWN", text="")

            if tex_set:
                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_global_settings",
                    icon="TRIA_DOWN" if tex_set.override_global_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Render Settings")
                if tex_set.override_global_settings:
                    set_col = _indent_column(box)
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_resolution", text="")
                    res_row = row.row(align=True)
                    res_row.enabled = tex_set.override_resolution
                    res_split = res_row.split(factor=0.4, align=True)
                    res_split.label(text="Resolution")
                    res_split.prop(tex_set, "size", text="")
                    set_col.separator(factor=0.3)
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_dilation", text="")
                    dilation_row = row.row(align=True)
                    dilation_row.enabled = tex_set.override_dilation
                    dilation_row.prop(tex_set, "set_dilation", text="Padding (px)")
                    set_col.separator(factor=0.3)
                    row = set_col.row(align=True)
                    row.label(text="Anti-Aliasing")
                    aa_col = _indent_column(set_col)

                    row = aa_col.row(align=True)
                    row.prop(tex_set, "override_fxaa", text="")
                    fxaa_row = row.row(align=True)
                    fxaa_row.enabled = tex_set.override_fxaa
                    fxaa_row.prop(tex_set, "set_fxaa_enabled", text="FXAA")
                    if tex_set.override_fxaa and tex_set.set_fxaa_enabled:
                        fxaa_opts = _indent_column(aa_col)
                        fxaa_opts.prop(tex_set, "set_fxaa_threshold")
                        fxaa_opts.prop(tex_set, "set_fxaa_blend")

                    aa_col.separator(factor=0.3)

                    row = aa_col.row(align=True)
                    row.prop(tex_set, "override_msaa", text="")
                    msaa_row = row.row(align=True)
                    msaa_row.enabled = tex_set.override_msaa
                    msaa_split = msaa_row.split(factor=0.4, align=True)
                    msaa_split.label(text="MSAA")
                    msaa_split.prop(tex_set, "set_msaa", text="")

                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_uv_map",
                    icon="TRIA_DOWN" if tex_set.override_uv_map else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override UV Map")
                if tex_set.override_uv_map:
                    set_uv_col = _indent_column(box)
                    set_uv_col.prop(tex_set, "uv_map_name", text="")

                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_bake_passes",
                    icon="TRIA_DOWN" if tex_set.override_bake_passes else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Bake Passes")
                if tex_set.override_bake_passes:
                    row = _indent_column(box)
                    row.prop(tex_set, "bake_pass_mode")
                    list_row = row.row()
                    list_row.template_list(
                        "BAKERY_UL_bake_passes",
                        "",
                        tex_set,
                        "bake_passes",
                        tex_set,
                        "active_bake_pass_index",
                        rows=4,
                    )
                    col = list_row.column(align=True)
                    col.operator("bakery.bake_pass_add_set", icon="ADD", text="")
                    col.operator("bakery.bake_pass_remove_set", icon="REMOVE", text="")
                    col.separator()
                    col.operator("bakery.bake_pass_move_set_up", icon="TRIA_UP", text="")
                    col.operator("bakery.bake_pass_move_set_down", icon="TRIA_DOWN", text="")
                    if tex_set.bake_passes and 0 <= tex_set.active_bake_pass_index < len(tex_set.bake_passes):
                        item = tex_set.bake_passes[tex_set.active_bake_pass_index]
                        settings_col = row.column(align=True)
                        settings_col.separator()
                        header = settings_col.row(align=True)
                        header.prop(
                            item,
                            "show_settings",
                            icon="TRIA_DOWN" if item.show_settings else "TRIA_RIGHT",
                            icon_only=True,
                            emboss=False,
                        )
                        header.label(text="Pass Settings")
                        if item.show_settings:
                            _draw_bake_pass_settings(settings_col, item)

        if not tex_set:
            return

        low_box = layout.box()
        header = low_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_target_meshes",
            icon="TRIA_DOWN" if data.show_target_meshes else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Target Meshes", icon="MESH_ICOSPHERE")
        if data.show_target_meshes:
            row = low_box.row()
            row.template_list(
                "BAKERY_UL_target_meshes",
                "",
                tex_set,
                "target_meshes",
                tex_set,
                "active_target_index",
                rows=4,
            )
            col = row.column(align=True)
            col.operator("bakery.target_mesh_add", icon="ADD", text="")
            col.operator("bakery.target_mesh_remove", icon="REMOVE", text="")
            col.separator()
            col.operator("bakery.target_mesh_move_up", icon="TRIA_UP", text="")
            col.operator("bakery.target_mesh_move_down", icon="TRIA_DOWN", text="")

            if tex_set.target_meshes and 0 <= tex_set.active_target_index < len(tex_set.target_meshes):
                low_item = tex_set.target_meshes[tex_set.active_target_index]
                row = low_box.row(align=True)
                row.prop(
                    low_item,
                    "override_global_settings",
                    icon="TRIA_DOWN" if low_item.override_global_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Projection Settings")
                if low_item.override_global_settings:
                    cage_col = low_box.column(align=True)
                    uv_row = cage_col.row(align=True)
                    uv_row.prop(low_item, "override_uv_map", text="")
                    uv_map_row = uv_row.row(align=True)
                    uv_map_row.enabled = low_item.override_uv_map
                    uv_map_row.prop(low_item, "uv_map_name", text="UV Map")
                    cage_row = cage_col.row(align=True)
                    cage_row.prop(low_item, "use_cage", text="")
                    cage_row.label(text="Cage")
                    picker_row = cage_row.row(align=True)
                    picker_row.scale_x = 1.6
                    picker_row.enabled = low_item.use_cage
                    picker_row.prop_search(
                        low_item,
                        "cage_object",
                        context.scene,
                        "objects",
                        text="",
                        icon="VIEWZOOM",
                    )
                    row = cage_col.row(align=True)
                    row.prop(low_item, "override_cage_extrusion", text="")
                    extrusion_row = row.row(align=True)
                    extrusion_row.enabled = low_item.override_cage_extrusion
                    extrusion_row.prop(low_item, "cage_extrusion", text="Cage Extrusion")
                    row = cage_col.row(align=True)
                    row.prop(low_item, "override_cage_max_ray_distance", text="")
                    ray_row = row.row(align=True)
                    ray_row.enabled = low_item.override_cage_max_ray_distance
                    ray_row.prop(low_item, "cage_max_ray_distance")

        if tex_set.target_meshes and 0 <= tex_set.active_target_index < len(tex_set.target_meshes):
            low_item = tex_set.target_meshes[tex_set.active_target_index]
            high_box = layout.box()
            high_header = high_box.row(align=True)
            high_header.scale_y = 1.4
            high_header.prop(
                data,
                "show_source_meshes",
                icon="TRIA_DOWN" if data.show_source_meshes else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            high_header.label(text="Source Meshes", icon="MESH_UVSPHERE")
            if data.show_source_meshes:
                row = high_box.row()
                row.template_list(
                "BAKERY_UL_source_meshes",
                    "",
                    low_item,
                    "source_meshes",
                    low_item,
                    "active_source_index",
                    rows=4,
                )
                col = row.column(align=True)
                col.operator("bakery.source_mesh_add", icon="ADD", text="")
                col.operator("bakery.source_mesh_remove", icon="REMOVE", text="")
                col.separator()
                col.operator("bakery.source_mesh_move_up", icon="TRIA_UP", text="")
                col.operator("bakery.source_mesh_move_down", icon="TRIA_DOWN", text="")
                if low_item.source_meshes and 0 <= low_item.active_source_index < len(low_item.source_meshes):
                    high_item = low_item.source_meshes[low_item.active_source_index]
                    high_box.prop(high_item, "color_attribute")

        if data.is_baking:
            return


