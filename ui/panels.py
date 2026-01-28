from pathlib import Path

import bpy

from .draw_helpers import _indent_column, _draw_resolution_row, _draw_bake_target_settings


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
        ).url = "https://github.com/tomankirilov/dummy_bake_tools"
        # buttons_col.operator(
        #     "wm.url_open",
        #     text="Documentation",
        #     icon="HELP",
        # ).url = "https://tomanov.art/"
        buttons_col.operator(
            "wm.url_open",
            text="About",
            icon="USER",
        ).url = "https://tomanov.art/"

        about_col.separator(factor=0.5)


class DUMMYBAKE_PT_completed(bpy.types.Panel):
    bl_label = ""
    bl_idname = "DUMMYBAKE_PT_completed"
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

        completed_box = layout.box()
        title_row = completed_box.row()
        title_row.alignment = "CENTER"
        title_row.label(text="BAKE COMPLETED", icon="CHECKMARK")

        textures = [item.value for item in data.last_bake_textures]
        if textures:
            list_box = layout.box()
            list_header = list_box.row()

            # list_header.label(text="Baked Textures", icon="IMAGE")
            list_header.label(text="Baked Textures")
            for name in textures:
                row = list_box.split(factor=0.08, align=True)
                row.label(text="")
                row.column(align=True).label(text=f"- {name}")

        buttons_col = layout.column(align=True)
        buttons_col.scale_y = 1.6
        buttons_col.operator("bakery.open_output_dir", text="Open Bake Directory", icon="FILE_FOLDER")
        buttons_col.operator("bakery.hide_last_bake", text="Continue Baking", icon="PLAY")

        _draw_about(layout, data, force_expand=True)


class DUMMYBAKE_PT_tools(bpy.types.Panel):
    bl_label = "Little Bakery"
    bl_idname = "DUMMYBAKE_PT_tools"
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
        if data and (not data.texture_sets or not data.global_bake_targets):
            try:
                from ..properties.defaults import _ensure_defaults
                _ensure_defaults(context.scene)
            except Exception:
                pass
        def _draw_about_inner(section_layout, force_expand=False):
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
                ).url = "https://github.com/tomankirilov/dummy_bake_tools"
                # buttons_col.operator(
                #     "wm.url_open",
                #     text="Documentation",
                #     icon="HELP",
                # ).url = "https://tomanov.art/"
                buttons_col.operator(
                    "wm.url_open",
                    text="About",
                    icon="USER",
                ).url = "https://tomanov.art/"

                about_col.separator(factor=0.5)

        # only show baking progress and about while baking.
        if data.is_baking:
            progress_box = layout.box()
            title_row = progress_box.row()
            
            
            #title_row.alert = True #make the text red
            title_row.alignment = "CENTER"
            title_row.label(text="BAKING IN PROGRESS", icon="ERROR")

            info_col = progress_box.column(align=True)
            info_col.label(text=f"- Set: {data.baking_set_name}")
            info_col.label(text=f"- Target: {data.baking_target_name}")

            
            progress_box.prop(data, "baking_progress", text="Progress", slider=True)
            _draw_about(layout, data, force_expand=True)
            return

        _draw_about(layout, data)

        if data.show_last_bake and data.last_bake_duration:
            completed_box = layout.box()
            title_row = completed_box.row()
            title_row.alignment = "CENTER"
            title_row.label(text="BAKE COMPLETED", icon="CHECKMARK")

            info_col = completed_box.column(align=True)
            info_col.label(text=f"- Completed in {data.last_bake_duration}")

            buttons_col = layout.column(align=True)
            buttons_col.scale_y = 1.6
            buttons_col.operator("bakery.open_output_dir", text="Open Bake Directory", icon="FILE_FOLDER")
            buttons_col.operator("bakery.hide_last_bake", text="Continue Baking", icon="PLAY")

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
        header.label(text="Global Settings", icon="TOOL_SETTINGS")
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
                device_col = _indent_column(render_col)
                row = device_col.split(factor=0.4, align=True)
                row.label(text="Render Device")
                row.prop(data, "render_device", text="")

            sections.separator(factor=0.4)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_image",
                icon="TRIA_DOWN" if data.show_render_image else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Image")
            if data.show_render_image:
                image_col = _indent_column(sections)
                _draw_resolution_row(image_col, data, "global_resolution")
                image_col.separator(factor=0.3)
                row = image_col.split(factor=0.4, align=True)
                row.label(text="MSAA")
                row.prop(data, "global_msaa", text="")

            sections.separator(factor=0.4)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_padding",
                icon="TRIA_DOWN" if data.show_render_padding else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Padding")
            if data.show_render_padding:
                pad_col = _indent_column(sections)
                pad_col.separator(factor=0.2)
                row = pad_col.split(factor=0.4, align=True)
                row.label(text="Method")
                row.prop(data, "global_dilation_method", text="")
                pad_col.prop(data, "global_dilation")

            sections.separator(factor=0.4)

            header = sections.row(align=True)
            header.prop(
                data,
                "show_render_cage",
                icon="TRIA_DOWN" if data.show_render_cage else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            header.label(text="Cage")
            if data.show_render_cage:
                cage_col = _indent_column(sections)
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
            "show_bake_targets",
            icon="TRIA_DOWN" if data.show_bake_targets else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Bake Targets", icon="IMAGE")
        if data.show_bake_targets:
            bake_col = bake_box.column(align=True)
            row = bake_col.row()
            row.template_list(
                "BAKERY_UL_bake_targets",
                "",
                data,
                "global_bake_targets",
                data,
                "active_global_bake_target_index",
                rows=4,
            )
            col = row.column(align=True)
            col.operator("bakery.bake_target_add_global", icon="ADD", text="")
            col.operator("bakery.bake_target_remove_global", icon="REMOVE", text="")
            col.separator()
            col.operator("bakery.bake_target_move_global_up", icon="TRIA_UP", text="")
            col.operator("bakery.bake_target_move_global_down", icon="TRIA_DOWN", text="")

            if data.global_bake_targets and 0 <= data.active_global_bake_target_index < len(data.global_bake_targets):
                item = data.global_bake_targets[data.active_global_bake_target_index]
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
                header.label(text="Target Settings")
                if item.show_settings:
                    _draw_bake_target_settings(settings_col, item)

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
                "DUMMYBAKE_UL_texture_sets",
                "",
                data,
                "texture_sets",
                data,
                "active_texture_index",
                rows=2,
            )
            col = row.column(align=True)
            col.operator("bakery.texture_set_add", icon="ADD", text="")
            col.operator("bakery.texture_set_remove", icon="REMOVE", text="")
            clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "TEXTURE"

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
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_dilation", text="")
                    dilation_row = row.row(align=True)
                    dilation_row.enabled = tex_set.override_dilation
                    dilation_row.prop(tex_set, "set_dilation", text="Padding (px)")
                    row = set_col.row(align=True)
                    row.prop(tex_set, "override_msaa", text="")
                    msaa_row = row.row(align=True)
                    msaa_row.enabled = tex_set.override_msaa
                    msaa_split = msaa_row.split(factor=0.4, align=True)
                    msaa_split.label(text="MSAA")
                    msaa_split.prop(tex_set, "set_msaa", text="")

                row = box.row(align=True)
                row.prop(
                    tex_set,
                    "override_bake_targets",
                    icon="TRIA_DOWN" if tex_set.override_bake_targets else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Bake Targets")
                if tex_set.override_bake_targets:
                    row = _indent_column(box)
                    row.prop(tex_set, "bake_target_mode")
                    list_row = row.row()
                    list_row.template_list(
                        "BAKERY_UL_bake_targets",
                        "",
                        tex_set,
                        "bake_targets",
                        tex_set,
                        "active_bake_target_index",
                        rows=4,
                    )
                    col = list_row.column(align=True)
                    col.operator("bakery.bake_target_add_set", icon="ADD", text="")
                    col.operator("bakery.bake_target_remove_set", icon="REMOVE", text="")
                    col.separator()
                    col.operator("bakery.bake_target_move_set_up", icon="TRIA_UP", text="")
                    col.operator("bakery.bake_target_move_set_down", icon="TRIA_DOWN", text="")
                    if tex_set.bake_targets and 0 <= tex_set.active_bake_target_index < len(tex_set.bake_targets):
                        item = tex_set.bake_targets[tex_set.active_bake_target_index]
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
                        header.label(text="Target Settings")
                        if item.show_settings:
                            _draw_bake_target_settings(settings_col, item)

        if not tex_set:
            return

        low_box = layout.box()
        header = low_box.row(align=True)
        header.scale_y = 1.4
        header.prop(
            data,
            "show_low_polys",
            icon="TRIA_DOWN" if data.show_low_polys else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        header.label(text="Low Poly", icon="MESH_ICOSPHERE")
        if data.show_low_polys:
            row = low_box.row()
            row.template_list(
                "DUMMYBAKE_UL_low_polys",
                "",
                tex_set,
                "low_polys",
                tex_set,
                "active_low_index",
                rows=2,
            )
            col = row.column(align=True)
            col.operator("bakery.low_poly_add", icon="ADD", text="")
            col.operator("bakery.low_poly_remove", icon="REMOVE", text="")
            clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
            clear_op.list_kind = "LOW"

            if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
                low_item = tex_set.low_polys[tex_set.active_low_index]
                row = low_box.row(align=True)
                row.prop(
                    low_item,
                    "override_global_settings",
                    icon="TRIA_DOWN" if low_item.override_global_settings else "TRIA_RIGHT",
                    icon_only=True,
                    emboss=False,
                )
                row.label(text="Override Global Settings")
                if low_item.override_global_settings:
                    cage_col = low_box.column(align=True)
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

        if tex_set.low_polys and 0 <= tex_set.active_low_index < len(tex_set.low_polys):
            low_item = tex_set.low_polys[tex_set.active_low_index]
            high_box = layout.box()
            high_header = high_box.row(align=True)
            high_header.scale_y = 1.4
            high_header.prop(
                data,
                "show_high_polys",
                icon="TRIA_DOWN" if data.show_high_polys else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            high_header.label(text="High Poly", icon="MESH_UVSPHERE")
            if data.show_high_polys:
                row = high_box.row()
                row.template_list(
                    "DUMMYBAKE_UL_high_polys",
                    "",
                    low_item,
                    "high_polys",
                    low_item,
                    "active_high_index",
                    rows=2,
                )
                col = row.column(align=True)
                col.operator("bakery.high_poly_add", icon="ADD", text="")
                col.operator("bakery.high_poly_remove", icon="REMOVE", text="")
                clear_op = col.operator("bakery.clear_selection", icon="PANEL_CLOSE", text="")
                clear_op.list_kind = "HIGH"
                if low_item.high_polys and 0 <= low_item.active_high_index < len(low_item.high_polys):
                    high_item = low_item.high_polys[low_item.active_high_index]
                    high_box.prop(high_item, "color_attribute")

        if data.is_baking:
            return
