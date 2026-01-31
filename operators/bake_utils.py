import os
import time
import bpy



_GEOMETRY_SKIP_TYPES = {"CAMERA", "LIGHT", "EMPTY", "ARMATURE", "SPEAKER"}
_HIGH_MATERIAL_NAME = "_bakery_material"
_HIGH_MATERIAL_NODE_NAME = "_bakery_node_group"
_BAKE_MODE_INPUT_INDEX = 0
_TEMP_COLLECTION_NAME = "Bakery_Temp"
_BAKE_MODE_MAP = {
    "ambient_occlusion": "ambient_occlusion",
    "curvature": "curvature",
    "thickness": "thickness",
    "random_island": "random_island",
    "color_attribute": "color_attribute",
    "bakery_position": "bakery_position",
}
_BAKE_PASS_LABELS = {
    "normal": "normal",
    "ambient_occlusion": "ambient_occlusion",
    "curvature": "curvature",
    "thickness": "thickness",
    "position": "position",
    "bakery_position": "bakery_position",
    "custom": "custom",
    "color_attribute": "color_attribute",
    "random_island": "random_island",
}

# Grab addon preferences if they exist (read debug)
def _get_addon_prefs(context):
    # Check for debug logging.
    if context is None:
        return None
    prefs = getattr(context, "preferences", None)
    if not prefs:
        return None
    root_package = __package__.split(".")[0] if __package__ else ""
    candidates = [root_package, "bakery"]
    for key in candidates:
        if not key:
            continue
        addon = prefs.addons.get(key)
        if addon and addon.preferences:
            return addon.preferences
    for addon in prefs.addons.values():
        prefs_obj = getattr(addon, "preferences", None)
        if not prefs_obj:
            continue
        if hasattr(prefs_obj, "name_separator") and hasattr(prefs_obj, "debug_logging"):
            return prefs_obj
    return None

# Print debug messages only when logging is enabled.
def _debug_log(context, message):
    # Global debug log bool:
    prefs = _get_addon_prefs(context)
    if prefs and getattr(prefs, "debug_logging", False):
        print(f"Bakery: {message}")

# Force the UI to redraw so the panel updates while baking.
def _tag_redraw(context):
    # refresh the 3D View sidebar while we bake.
    wm = getattr(context, "window_manager", None)
    if not wm:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
    try:
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
    except RuntimeError:
        pass


# Show progress text and log it.
def _progress(operator, context, message):
    # progress notification in Blender;s status bar.
    operator.report({"INFO"}, message)
    _debug_log(context, message)
    _tag_redraw(context)


# Ask for a saved blend file before baking.
def _ensure_saved_blend(operator, context):
    if bpy.data.is_saved:
        return True
    _popup_error(context, "Please save the .blend file before baking")
    operator.report({"WARNING"}, "Please save the .blend file before baking")
    return False


# Show an error popup in the 3D View area.
def _popup_error(context, message):
    def draw(self, _context):
        self.layout.label(text=message, icon="ERROR")

    wm = getattr(context, "window_manager", None)
    if wm:
        wm.popup_menu(draw, title="Bakery")

# Load the source material from the blend file.
def _load_highpoly_material():
    # Load once and reuse for all bakes.
    material = bpy.data.materials.get(_HIGH_MATERIAL_NAME)
    if material:
        return material
    base_dir = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(base_dir, "data", "bakery_data.blend"),
    ]
    for path in candidates:
        blend_path = os.path.normpath(path)
        if not os.path.exists(blend_path):
            continue
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            if _HIGH_MATERIAL_NAME in data_from.materials:
                data_to.materials = [_HIGH_MATERIAL_NAME]
                break
    return bpy.data.materials.get(_HIGH_MATERIAL_NAME)

# Set the source material to the needed bake mode.
def _set_highpoly_material_mode(material, mode):
    # Switch the material's bake mode by writing into the node input.
    if not material or not material.node_tree:
        return
    node = material.node_tree.nodes.get(_HIGH_MATERIAL_NODE_NAME)
    if not node or not node.inputs:
        return
    node.inputs[_BAKE_MODE_INPUT_INDEX].default_value = mode

# Set AO/curvature/thickness values into the material nodes.
def _set_highpoly_material_settings(material, ao_samples, ao_occlusion_mode, ao_distance,
                                    ao_contrast, curvature_exponent, curvature_contrast,
                                    thickness_samples, thickness_distance):
    # Push all AO/Curvature/Thickness sliders into the shared node group.
    if not material:
        return
    node_group = bpy.data.node_groups.get(_HIGH_MATERIAL_NODE_NAME)
    if node_group:
        ao_node = node_group.nodes.get("Ambient Occlusion")
        if ao_node:
            ao_node.samples = ao_samples
            ao_node.only_local = ao_occlusion_mode == "ISOLATED"
        thickness_node = node_group.nodes.get("BAKER_THICKNESS_SAMPLES")
        if thickness_node:
            thickness_node.samples = thickness_samples
    if material.node_tree:
        node = material.node_tree.nodes.get(_HIGH_MATERIAL_NODE_NAME)
        if node and len(node.inputs) >= 6:
            node.inputs[1].default_value = ao_distance
            node.inputs[2].default_value = ao_contrast
            node.inputs[3].default_value = curvature_contrast
            node.inputs[4].default_value = curvature_exponent
            node.inputs[5].default_value = thickness_distance

# search the layer collection tree to find a specific collection.
def _find_layer_collection(layer_collection, target_collection):
    if layer_collection.collection == target_collection:
        return layer_collection
    for child in layer_collection.children:
        found = _find_layer_collection(child, target_collection)
        if found:
            return found
    return None

# make sure the temp collection exists and is visible.
def _ensure_temp_collection(scene, view_layer):
    # use a temp collection to link objects into the view layer if needed.
    collection = bpy.data.collections.get(_TEMP_COLLECTION_NAME)
    if not collection:
        collection = bpy.data.collections.new(_TEMP_COLLECTION_NAME)
    if collection.name not in scene.collection.children:
        scene.collection.children.link(collection)
    layer_collection = _find_layer_collection(view_layer.layer_collection, collection)
    if layer_collection:
        layer_collection.exclude = False
        layer_collection.hide_viewport = False
    return collection

# find a View3D override so bake operators have a valid context.
def _get_view3d_override(scene, view_layer, active, selected):
    # find a View3D context override so bake ops can run safely.
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for region in area.regions:
                if region.type == "WINDOW":
                    return {
                        "window": window,
                        "screen": window.screen,
                        "area": area,
                        "region": region,
                        "scene": scene,
                        "view_layer": view_layer,
                        "active_object": active,
                        "selected_objects": selected,
                        "selected_editable_objects": selected,
                    }
    return {}

# make sure the first material slot is set on the object.
def _ensure_material_slot(obj, material):
    # force the first material slot so baking always targets the same slot.
    data = getattr(obj, "data", None)
    if not data or not hasattr(data, "materials"):
        return False
    if len(data.materials) == 0:
        data.materials.append(material)
    else:
        data.materials[0] = material
    return True

# create a basic low-poly material if the object has none.
def _ensure_low_material(obj):
# make sure the target has a nodes-enabled material to host the bake.
    data = getattr(obj, "data", None)
    if not data or not hasattr(data, "materials"):
        return None
    if len(data.materials) == 0 or data.materials[0] is None:
        material = bpy.data.materials.new(name="Bakery_Low")
        material.use_nodes = True
        data.materials.append(material)
        return material
    material = data.materials[0]
    material.use_nodes = True
    return material

# store current materials so I can restore them later.
def _capture_materials(obj):
    # stash existing materials so I can restore them after baking.
    data = getattr(obj, "data", None)
    if not data or not hasattr(data, "materials"):
        return None
    return list(data.materials)

# put materials back the way they were before baking.
def _restore_materials(obj, materials):
    # restore the exact material list we had before baking.
    if materials is None:
        return
    data = getattr(obj, "data", None)
    if not data or not hasattr(data, "materials"):
        return
    data.materials.clear()
    for mat in materials:
        data.materials.append(mat)

# set selection and active object for baking.
def _set_selection(scene, view_layer, objects, active=None):
    # control selection to satisfy Blender's bake requirements.
    for obj in view_layer.objects:
        obj.select_set(False)

    temp_collection = _ensure_temp_collection(scene, view_layer)
    temp_links = []
    for obj in objects:
        if obj.name not in view_layer.objects:
            try:
                if obj.name not in temp_collection.objects:
                    temp_collection.objects.link(obj)
                temp_links.append(obj)
            except RuntimeError:
                continue

    selectable = [obj for obj in objects if obj.name in view_layer.objects]
    for obj in selectable:
        obj.hide_select = False
        obj.hide_set(False)
        obj.select_set(True)
    if active and active.name in view_layer.objects:
        view_layer.objects.active = active
    return selectable, temp_links, temp_collection

# create a new image to bake into.
def _make_image(name, width, height):
    # Reuse existing images by name to avoid duplicates.
    image = bpy.data.images.get(name)
    if image:
        image.source = "GENERATED"
        if image.size[0] != width or image.size[1] != height:
            try:
                image.scale(width, height)
            except RuntimeError:
                pass
        image.alpha_mode = "STRAIGHT"
        return image
    image = bpy.data.images.new(name=name, width=width, height=height, alpha=True)
    image.generated_color = (0.0, 0.0, 0.0, 0.0)
    image.alpha_mode = "STRAIGHT"
    return image

# clear the image pixels so the bake starts empty.
def _clear_image(image):
    # clear pixels manually to avoid baking over old data.
    image.source = "GENERATED"
    pixel_count = image.size[0] * image.size[1] * 4
    try:
        image.pixels.foreach_set([0.0] * pixel_count)
        image.update()
    except RuntimeError:
        try:
            image.scale(image.size[0], image.size[1])
            image.pixels.foreach_set([0.0] * pixel_count)
            image.update()
        except RuntimeError:
            pass

from .dilation import _dilate_image

# save the baked image using the chosen output settings.
def _save_image(image, output_dir, filename, settings, scene=None, context=None):
    # Use render image settings because Image doesn't expose color format fields.
    scene = scene or bpy.context.scene
    output_dir = _resolve_output_dir(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    image.filepath_raw = filepath

    image_settings = scene.render.image_settings
    saved_settings = {
        "file_format": image_settings.file_format,
        "color_mode": image_settings.color_mode,
        "color_depth": image_settings.color_depth,
        "compression": image_settings.compression,
    }
    try:
        image_settings.file_format = settings["output_format"]
        image_settings.color_mode = settings["output_color_mode"]
        if settings["output_format"] == "PNG":
            image_settings.color_depth = settings["output_color_depth"]
            image_settings.compression = settings["output_png_compression"]
        image.save_render(filepath, scene=scene)
    finally:
        image_settings.file_format = saved_settings["file_format"]
        image_settings.color_mode = saved_settings["color_mode"]
        image_settings.color_depth = saved_settings["color_depth"]
        image_settings.compression = saved_settings["compression"]
    _debug_log(context, f"Saved image to {filepath}")

# turn the output string into a real folder path.
def _resolve_output_dir(output_dir):
    # Convert user input into a path relative to the current blend file.
    value = (output_dir or "").strip()
    base_dir = bpy.path.abspath("//")
    if not value:
        return base_dir
    if value.startswith("//"):
        value = value[2:]
    if value.startswith("/"):
        value = value[1:]
    value = value.lstrip("\\/")
    return os.path.join(base_dir, value)

# convert an absolute path to a blend-relative folder name.
def _relative_to_blend(path):
    # Collapse absolute paths under the blend directory to a relative subfolder.
    base_dir = bpy.path.abspath("//")
    normalized = bpy.path.abspath(path)
    try:
        relative = os.path.relpath(normalized, base_dir)
    except ValueError:
        return os.path.basename(normalized)
    if relative.startswith(".."):
        return os.path.basename(normalized)
    relative = relative.lstrip("\\/")
    return f"/{relative}" if relative else ""

# list bake passes in the order to process them.
def _collect_bake_passes(data, tex_set):
    # build the final target list (global + optional set override).
    global_targets = [item for item in data.global_bake_passes if item.enabled]
    set_targets = [item for item in tex_set.bake_passes if item.enabled] if tex_set else []
    if set_targets:
        if tex_set.bake_pass_mode == "REPLACE":
            return set_targets
        return global_targets + set_targets
    return global_targets


# choose a display name for a target item.
def _pass_display_name(item):
    name = (item.name or "").strip()
    if name:
        return name
    return _BAKE_PASS_LABELS.get(item.pass_type, item.pass_type)


# build the final texture name from set + target name.
def _pass_texture_name(tex_set, item):
    target_name = _pass_display_name(item)
    if not target_name:
        return tex_set.name
    prefs = _get_addon_prefs(bpy.context)
    separator = getattr(prefs, "name_separator", "_") if prefs else "_"
    separator = separator if separator else "_"
    _debug_log(bpy.context, f"Name separator in use: '{separator}'")
    return f"{tex_set.name}{separator}{target_name}"

# convert the MSAA choice into a numeric scale factor.
def _msaa_factor(value):
    # Parse UI enum values into a numeric scale factor.
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1

# clone materials so each source can use its own color attribute name.
def _copy_color_attribute_material(base_material, attribute_name, cache, created_materials, created_node_groups):
    # Create a per-attribute material + node-group copy so each source can
    # point to a different color attribute without stomping shared state.
    key = attribute_name or ""
    if key in cache:
        return cache[key]

    material_copy = base_material.copy()
    node = material_copy.node_tree.nodes.get(_HIGH_MATERIAL_NODE_NAME)
    if not node or not hasattr(node, "node_tree") or not node.node_tree:
        cache[key] = material_copy
        created_materials.append(material_copy)
        return material_copy

    node_group_copy = node.node_tree.copy()
    node.node_tree = node_group_copy
    node.inputs[_BAKE_MODE_INPUT_INDEX].default_value = "color_attribute"
    color_node = node_group_copy.nodes.get("Color Attribute")
    if color_node:
        color_node.layer_name = attribute_name or ""

    created_materials.append(material_copy)
    created_node_groups.append(node_group_copy)
    cache[key] = material_copy
    return material_copy

# set bake mode and samples for the current target.
def _prepare_bake_pass(item, material, cycles, bake):
    # configure Cycles bake settings and the shared material for the target.
    target_name = item.pass_type
    if target_name == "normal":
        cycles.samples = 1
        cycles.bake_type = "NORMAL"
        bake.normal_space = item.normal_space
        bake.normal_r = item.normal_r
        bake.normal_g = item.normal_g
        bake.normal_b = item.normal_b
        return False
    if target_name == "position":
        cycles.samples = 1
        cycles.bake_type = "POSITION"
        return False
    if target_name == "custom":
        cycles.samples = 1
        cycles.bake_type = item.custom_bake_type
        return False
    cycles.bake_type = "EMIT"
    if target_name == "ambient_occlusion":
        cycles.samples = item.ao_render_samples
        _set_highpoly_material_mode(material, "ambient_occlusion")
        return True
    if target_name == "thickness":
        cycles.samples = item.thickness_render_samples
        _set_highpoly_material_mode(material, "thickness")
        return True
    if target_name == "color_attribute":
        cycles.samples = 1
        return False

    cycles.samples = 1
    mode = _BAKE_MODE_MAP.get(target_name)
    if mode:
        _set_highpoly_material_mode(material, mode)
    return True

# merge global settings with per-texture-set overrides.
def _effective_settings(data, tex_set):
    # keep only shared settings here (targets are separate now).
    if tex_set.override_resolution:
        resolution = tex_set.size
    else:
        resolution = data.global_resolution
    if tex_set.override_dilation:
        dilation = tex_set.set_dilation
    else:
        dilation = data.global_dilation
    if tex_set.override_msaa:
        msaa = tex_set.set_msaa
    else:
        msaa = data.global_msaa
    return {
        "resolution": resolution,
        "dilation": dilation,
        "dilation_method": data.global_dilation_method,
        "msaa": msaa,
        "output_format": data.output_format,
        "output_color_mode": data.output_color_mode,
        "output_color_depth": data.output_color_depth,
        "output_png_compression": data.output_png_compression,
    }

# capture current render and bake settings before changing them.
def _capture_scene_settings(scene):
    # save scene render and bake settings so I can put everything back.
    cycles = scene.cycles
    bake = scene.render.bake
    view = scene.view_settings
    return {
        "engine": scene.render.engine,
        "device": cycles.device,
        "view_transform": view.view_transform,
        "samples": cycles.samples,
        "diffuse_bounces": cycles.diffuse_bounces,
        "glossy_bounces": cycles.glossy_bounces,
        "transmission_bounces": cycles.transmission_bounces,
        "volume_bounces": cycles.volume_bounces,
        "transparent_max_bounces": cycles.transparent_max_bounces,
        "max_bounces": cycles.max_bounces,
        "use_selected_to_active": bake.use_selected_to_active,
        "margin": bake.margin,
        "use_clear": bake.use_clear,
        "use_cage": bake.use_cage,
        "cage_object": bake.cage_object,
        "cage_extrusion": bake.cage_extrusion,
        "max_ray_distance": bake.max_ray_distance,
        "bake_type": cycles.bake_type,
        "normal_space": bake.normal_space,
        "normal_r": bake.normal_r,
        "normal_g": bake.normal_g,
        "normal_b": bake.normal_b,
    }

# apply a predictable scene setup for baking.
def _apply_scene_settings(scene, data):
    # enforce a predictable bake setup (engine, samples, bounces, etc).
    cycles = scene.cycles
    bake = scene.render.bake
    view = scene.view_settings
    scene.render.engine = "CYCLES"
    cycles.device = data.render_device
    view.view_transform = "Standard"
    cycles.diffuse_bounces = 0
    cycles.glossy_bounces = 0
    cycles.transmission_bounces = 0
    cycles.volume_bounces = 0
    cycles.transparent_max_bounces = 0
    cycles.max_bounces = 0
    bake.margin = 0
    cycles.samples = 1

# restore render and bake settings to what they were.
def _restore_scene_settings(scene, saved):
    # restore every render/bake setting I changed.
    cycles = scene.cycles
    bake = scene.render.bake
    view = scene.view_settings
    scene.render.engine = saved["engine"]
    cycles.device = saved["device"]
    view.view_transform = saved["view_transform"]
    cycles.samples = saved["samples"]
    cycles.diffuse_bounces = saved["diffuse_bounces"]
    cycles.glossy_bounces = saved["glossy_bounces"]
    cycles.transmission_bounces = saved["transmission_bounces"]
    cycles.volume_bounces = saved["volume_bounces"]
    cycles.transparent_max_bounces = saved["transparent_max_bounces"]
    cycles.max_bounces = saved["max_bounces"]
    bake.use_selected_to_active = saved["use_selected_to_active"]
    bake.margin = saved["margin"]
    bake.use_clear = saved["use_clear"]
    bake.use_cage = saved["use_cage"]
    bake.cage_object = saved["cage_object"]
    bake.cage_extrusion = saved["cage_extrusion"]
    bake.max_ray_distance = saved["max_ray_distance"]
    cycles.bake_type = saved["bake_type"]
    bake.normal_space = saved["normal_space"]
    bake.normal_r = saved["normal_r"]
    bake.normal_g = saved["normal_g"]
    bake.normal_b = saved["normal_b"]


def _bake_texture_sets(operator, context, texture_sets, label):
    # Main bake entry point used by both "Bake All" and "Bake Selected Set".
    data = context.scene.bakery_data
    material = _load_highpoly_material()
    if not material:
        _popup_error(context, "Missing source material")
        operator.report({"WARNING"}, "Missing source material")
        return False

    if not any(ts.target_meshes for ts in texture_sets):
        _popup_error(context, "Please add at least one target object")
        operator.report({"WARNING"}, "Please add at least one target object")
        return False

    if not any(_collect_bake_passes(data, ts) for ts in texture_sets):
        _popup_error(context, "Please enable at least one bake pass")
        operator.report({"WARNING"}, "Please enable at least one bake pass")
        return False

    prefs = _get_addon_prefs(context)
    if prefs and getattr(prefs, "save_before_bake", False):
        if bpy.data.is_saved:
            try:
                bpy.ops.wm.save_mainfile()
                _debug_log(context, "Saved blend file before bake")
            except RuntimeError:
                _popup_error(context, "Failed to save .blend before bake")
                operator.report({"WARNING"}, "Failed to save .blend before bake")
        else:
            _popup_error(context, "Please save the .blend file before baking")
            operator.report({"WARNING"}, "Please save the .blend file before baking")
            return False

    scene = context.scene
    cycles = scene.cycles
    bake = scene.render.bake
    view_layer = context.view_layer

    saved = _capture_scene_settings(scene)
    data.is_baking = True
    data.baking_set_name = ""
    data.baking_pass_name = ""
    data.baking_progress = 0.0
    data.last_bake_duration = ""
    data.show_last_bake = False
    _tag_redraw(context)
    created_materials = []
    created_node_groups = []
    baked_texture_names = set()
    start_time = time.perf_counter()
    cleared_images = set()
    _debug_log(context, f"{label} started for {len(texture_sets)} texture set(s)")

    # Pre-calculate total target count for a simple progress bar.
    total_targets = 0
    for tex_set in texture_sets:
        total_targets += len(_collect_bake_passes(data, tex_set))
    progress_value = 0
    progress_total = max(1, total_targets)
    wm = getattr(context, "window_manager", None)
    if wm:
        wm.progress_begin(0, progress_total)
    try:
        _apply_scene_settings(scene, data)

        for tex_set in texture_sets:
            settings = _effective_settings(data, tex_set)
            _debug_log(context, f"Preparing texture set '{tex_set.name}'")
            if not tex_set.target_meshes:
                _debug_log(context, f"Skipping texture set '{tex_set.name}' (no targets)")
                continue
            data.baking_set_name = tex_set.name

            saved_materials = {}
            color_attribute_materials = {}
            set_high_objs = []
            for low_item in tex_set.target_meshes:
                low_obj = low_item.object
                if low_obj and low_obj.type == "MESH":
                    saved_materials.setdefault(low_obj, _capture_materials(low_obj))
                for high_item in low_item.source_meshes:
                    high_obj = high_item.object
                    if not high_obj or high_obj.type != "MESH":
                        continue
                    if high_obj not in set_high_objs:
                        set_high_objs.append(high_obj)
                    if high_obj not in saved_materials:
                        saved_materials[high_obj] = _capture_materials(high_obj)

            # MSAA is implemented by baking at a higher resolution and downscaling.
            scale_factor = _msaa_factor(settings["msaa"])
            target_resolution = settings["resolution"]
            bake_resolution = (
                target_resolution[0] * scale_factor,
                target_resolution[1] * scale_factor,
            )
            targets = _collect_bake_passes(data, tex_set)
            for item in targets:
                target_name = item.pass_type

                progress_value += 1
                if wm:
                    wm.progress_update(progress_value)
                target_label = _pass_display_name(item)
                data.baking_pass_name = target_label
                data.baking_progress = progress_value / progress_total
                _progress(operator, context, f"{label}: {tex_set.name} - {target_label}")

                if target_name == "custom" and not item.custom_material:
                    _popup_error(context, "Custom bake pass needs a material")
                    operator.report({"WARNING"}, "Custom bake pass needs a material")
                    continue

                texture_name = _pass_texture_name(tex_set, item)
                image = _make_image(texture_name, bake_resolution[0], bake_resolution[1])
                if image.name not in cleared_images:
                    _clear_image(image)
                    cleared_images.add(image.name)
                bake.use_clear = False
                baked_texture_names.add(texture_name)

                needs_material_settings = _prepare_bake_pass(
                    item,
                    material,
                    cycles,
                    bake,
                )
                # Keep bake margin off so padding is handled only by dilation.
                bake.margin = 0
                if needs_material_settings:
                    _set_highpoly_material_settings(
                        material,
                        item.ao_samples,
                        item.ao_occlusion_mode,
                        item.ao_distance,
                        item.ao_contrast,
                        item.curvature_exponent,
                        item.curvature_contrast,
                        item.thickness_samples,
                        item.thickness_distance,
                    )

                use_bakery_material = target_name in {
                    "ambient_occlusion",
                    "curvature",
                    "thickness",
                    "random_island",
                    "bakery_position",
                }
                if use_bakery_material:
                    for high_obj in set_high_objs:
                        _ensure_material_slot(high_obj, material)
                if target_name == "custom":
                    for high_obj in set_high_objs:
                        _ensure_material_slot(high_obj, item.custom_material)

                for low_item in tex_set.target_meshes:
                    low_obj = low_item.object
                    if not low_obj or low_obj.type != "MESH":
                        continue

                    high_items = [
                        item for item in low_item.source_meshes
                        if item.object and item.object.type == "MESH"
                    ]
                    high_objs = [item.object for item in high_items]
                    if not high_objs:
                        # If there is no source, bake the target with the target material.
                        if use_bakery_material:
                            _ensure_material_slot(low_obj, material)
                        elif target_name == "custom":
                            _ensure_material_slot(low_obj, item.custom_material)
                    if target_name == "color_attribute":
                        # Override the source material per-object to inject the attribute name.
                        for item in high_items:
                            attr_name = (item.color_attribute or "").strip()
                            if not attr_name:
                                attr_name = "Color"
                            mat = _copy_color_attribute_material(
                                material,
                                attr_name,
                                color_attribute_materials,
                                created_materials,
                                created_node_groups,
                            )
                            _ensure_material_slot(item.object, mat)
                    _debug_log(
                        context,
                        f"Baking {target_label} for target '{low_obj.name}' "
                        f"with {len(high_objs)} source object(s)",
                    )
                    restore_hide_render = None
                    if target_name == "ambient_occlusion":
                        occlusion_mode = item.ao_occlusion_mode
                        if occlusion_mode in {"SET", "LOCAL"}:
                            restore_hide_render = {obj: obj.hide_render for obj in scene.objects}
                            for obj in scene.objects:
                                obj.hide_render = True
                            visible = set_high_objs if occlusion_mode == "SET" else high_objs
                            for obj in visible + [low_obj]:
                                obj.hide_render = False
                    for obj in high_objs + [low_obj]:
                        obj.hide_viewport = False
                        obj.hide_render = False

                    if context.mode != "OBJECT":
                        bpy.ops.object.mode_set(mode="OBJECT")

                    selected, temp_links, temp_collection = _set_selection(
                        scene,
                        view_layer,
                        high_objs + [low_obj],
                        active=low_obj,
                    )
                    if (not selected or low_obj not in selected
                            or context.view_layer.objects.active != low_obj):
                        for obj in temp_links:
                            if obj.name in temp_collection.objects:
                                temp_collection.objects.unlink(obj)
                        continue
                    bake.use_selected_to_active = len(selected) > 1
                    if bake.use_selected_to_active and len(selected) < 2:
                        for obj in temp_links:
                            if obj.name in temp_collection.objects:
                                temp_collection.objects.unlink(obj)
                        continue

                    bake.use_cage = low_item.use_cage
                    bake.cage_object = low_item.cage_object if low_item.use_cage else None
                    if low_item.override_cage_extrusion:
                        bake.cage_extrusion = low_item.cage_extrusion
                    else:
                        bake.cage_extrusion = data.global_extrusion
                    if low_item.override_cage_max_ray_distance:
                        bake.max_ray_distance = low_item.cage_max_ray_distance
                    else:
                        bake.max_ray_distance = data.global_max_ray_distance

                    material_slot = _ensure_low_material(low_obj)
                    if not material_slot or not material_slot.node_tree:
                        continue
                    nodes = material_slot.node_tree.nodes
                    image_node = nodes.new("ShaderNodeTexImage")
                    image_node.image = image
                    material_slot.node_tree.nodes.active = image_node
                    try:
                        override = _get_view3d_override(
                            scene,
                            view_layer,
                            low_obj,
                            selected,
                        )
                        if override:
                            with bpy.context.temp_override(**override):
                                bpy.ops.object.bake(type=cycles.bake_type)
                        else:
                            bpy.ops.object.bake(type=cycles.bake_type)
                    finally:
                        nodes.remove(image_node)
                        for obj in temp_links:
                            if obj.name in temp_collection.objects:
                                temp_collection.objects.unlink(obj)
                        if restore_hide_render is not None:
                            for obj, state in restore_hide_render.items():
                                obj.hide_render = state
                    bake.use_clear = False
                    if target_name == "color_attribute":
                        # Restore the shared material after the color-attribute bake.
                        for item in high_items:
                            _ensure_material_slot(item.object, material)

                # Hard padding pass (old behavior) before downscaling.
                dilation = settings["dilation"] * scale_factor
                if dilation > 0:
                    _dilate_image(image, dilation, settings["dilation_method"])
                    _debug_log(context, f"Applied dilation of {dilation}px")
                if scale_factor > 1:
                    image.scale(target_resolution[0], target_resolution[1])
                    _debug_log(
                        context,
                        f"Downscaled from {bake_resolution[0]}x{bake_resolution[1]} "
                        f"to {target_resolution[0]}x{target_resolution[1]}",
                    )
                extension = "png" if settings["output_format"] == "PNG" else "tga"
                _save_image(
                    image,
                    data.output_dir,
                    f"{texture_name}.{extension}",
                    settings,
                    scene=scene,
                    context=context,
                )

            for obj, mats in saved_materials.items():
                _restore_materials(obj, mats)
    finally:
        data.is_baking = False
        data.baking_set_name = ""
        data.baking_pass_name = ""
        data.baking_progress = 0.0
        _tag_redraw(context)
        # always clean up progress bars and any temporary data.
        if wm:
            wm.progress_end()
        _restore_scene_settings(scene, saved)
        for mat in created_materials:
            try:
                bpy.data.materials.remove(mat, do_unlink=True)
            except RuntimeError:
                pass
        for group in created_node_groups:
            try:
                bpy.data.node_groups.remove(group, do_unlink=True)
            except RuntimeError:
                pass
        temp_collection = bpy.data.collections.get(_TEMP_COLLECTION_NAME)
        if temp_collection:
            for obj in list(temp_collection.objects):
                try:
                    temp_collection.objects.unlink(obj)
                except RuntimeError:
                    pass
            if temp_collection.name in scene.collection.children:
                try:
                    scene.collection.children.unlink(temp_collection)
                except RuntimeError:
                    pass
            if temp_collection.users == 0:
                try:
                    bpy.data.collections.remove(temp_collection)
                except RuntimeError:
                    pass
        if material and material.name == _HIGH_MATERIAL_NAME:
            try:
                bpy.data.materials.remove(material, do_unlink=True)
            except RuntimeError:
                pass

    elapsed = time.perf_counter() - start_time
    minutes, seconds = divmod(int(elapsed), 60)
    data.last_bake_duration = f"{minutes}m {seconds}s"
    data.show_last_bake = True
    data.last_bake_textures.clear()
    for name in sorted(baked_texture_names):
        entry = data.last_bake_textures.add()
        entry.value = name
    message = f"{label} finished in {elapsed:.2f}s"
    print(f"Bakery: {message}")
    operator.report({"INFO"}, message)
    return True






