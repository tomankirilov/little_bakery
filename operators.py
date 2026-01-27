import os
import time
import bpy


_GEOMETRY_SKIP_TYPES = {"CAMERA", "LIGHT", "EMPTY", "ARMATURE", "SPEAKER"}
_HIGH_MATERIAL_NAME = "_bakery_material"
_HIGH_MATERIAL_NODE_NAME = "_bakery_node_group"
_BAKE_MODE_INPUT_INDEX = 0
_TEMP_COLLECTION_NAME = "Bakery_Temp"
_BAKE_MODE_MAP = {
    "normals_ws": "normalws",
    "ambient_occlusion": "ambient_occlusion",
    "curvature": "curvature",
    "thickness": "thickness",
    "position": "position",
    "random_island": "random_island",
    "color_attribute": "color_attribute",
}
_TARGET_LABELS = {
    "tangent_normal": "Tangent Space Normal",
    "normals_ws": "Object Space Normal",
    "ambient_occlusion": "Ambient Occlusion",
    "curvature": "Curvature",
    "thickness": "Thickness",
    "position": "Position",
    "color_attribute": "Color Attribute",
    "random_island": "Random Island",
}

# Grab addon preferences if they exist (read debug)
def _get_addon_prefs(context):
    # Check for debug logging.
    if context is None:
        return None
    prefs = getattr(context, "preferences", None)
    if not prefs:
        return None
    addon = prefs.addons.get(__package__)
    return addon.preferences if addon else None

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

# Load the high poly material from the blend file.
def _load_highpoly_material():
    # Load once and reuse for all bakes.
    material = bpy.data.materials.get(_HIGH_MATERIAL_NAME)
    if material:
        return material
    blend_path = os.path.join(os.path.dirname(__file__), "bakery_data.blend")
    if os.path.exists(blend_path):
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            if _HIGH_MATERIAL_NAME in data_from.materials:
                data_to.materials = [_HIGH_MATERIAL_NAME]
    return bpy.data.materials.get(_HIGH_MATERIAL_NAME)

# Set the high poly material to the needed bake mode.
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
    # make sure the low poly has a nodes-enabled material to host the bake.
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
    # create a new RGBA image with transparent background.
    image = bpy.data.images.new(name=name, width=width, height=height, alpha=True)
    image.generated_color = (0.0, 0.0, 0.0, 0.0)
    image.alpha_mode = "STRAIGHT"
    return image

# clear the image pixels so the bake starts empty.
def _clear_image(image):
    # clear pixels manually to avoid baking over old data.
    pixel_count = image.size[0] * image.size[1] * 4
    image.pixels.foreach_set([0.0] * pixel_count)
    image.update()

# expand edge colors into transparent pixels.
def _dilate_image(image, iterations):
    # Expand colors into transparent pixels using a multi-source BFS so the
    # padding comes from original opaque pixels instead of iterative smearing.
    width, height = image.size
    if iterations <= 0:
        return

    from collections import deque

    pixels = list(image.pixels)
    total = width * height
    owner = [-1] * total
    dist = [-1] * total
    queue = deque()

    for idx in range(total):
        if pixels[idx * 4 + 3] > 0.0:
            owner[idx] = idx
            dist[idx] = 0
            queue.append(idx)

    if not queue:
        return

    neighbors = (
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1),
    )

    while queue:
        idx = queue.popleft()
        current_dist = dist[idx]
        if current_dist >= iterations:
            continue
        x = idx % width
        y = idx // width
        for ox, oy in neighbors:
            nx = x + ox
            ny = y + oy
            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                continue
            nidx = ny * width + nx
            if owner[nidx] != -1:
                continue
            owner[nidx] = owner[idx]
            dist[nidx] = current_dist + 1
            queue.append(nidx)

    for idx in range(total):
        if owner[idx] == -1:
            continue
        dst_offset = idx * 4
        if pixels[dst_offset + 3] > 0.0:
            continue
        src_offset = owner[idx] * 4
        pixels[dst_offset:dst_offset + 4] = pixels[src_offset:src_offset + 4]

    image.pixels.foreach_set(pixels)
    image.update()

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

# list bake targets in the order I want to process them.
def _bake_targets_from_settings(settings):
    # keep the bake order stable so output naming stays predictable.
    return [
        ("tangent_normal", settings["tangent_normal"], settings["tangent_suffix"]),
        ("normals_ws", settings["normals_ws"], settings["normals_suffix"]),
        ("ambient_occlusion", settings["ambient_occlusion"], settings["ao_suffix"]),
        ("curvature", settings["curvature"], settings["curvature_suffix"]),
        ("thickness", settings["thickness"], settings["thickness_suffix"]),
        ("position", settings["position"], settings["position_suffix"]),
        ("color_attribute", settings["color_attribute"], settings["color_attribute_suffix"]),
        ("random_island", settings["random_island"], settings["random_island_suffix"]),
    ]

# convert the MSAA choice into a numeric scale factor.
def _msaa_factor(value):
    # Parse UI enum values into a numeric scale factor.
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1

# clone materials so each high poly can use its own color attribute name.
def _copy_color_attribute_material(base_material, attribute_name, cache, created_materials, created_node_groups):
    # Create a per-attribute material + node-group copy so each high poly can
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
def _prepare_bake_target(target_name, settings, material, cycles, bake):
    # Configure Cycles bake settings and the shared material for the target.
    if target_name == "tangent_normal":
        cycles.samples = 1
        cycles.bake_type = "NORMAL"
        bake.normal_space = "TANGENT"
        return False

    cycles.bake_type = "EMIT"
    if target_name == "ambient_occlusion":
        cycles.samples = settings["ao_render_samples"]
        _set_highpoly_material_mode(material, "ambient_occlusion")
        return True
    if target_name == "thickness":
        cycles.samples = settings["thickness_render_samples"]
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
    # Merge texture-set overrides with global defaults into a flat settings dict.
    if tex_set.override_global_settings:
        return {
            "resolution": tex_set.size,
            "normals_ws": tex_set.bake_normals_ws,
            "tangent_normal": tex_set.bake_tangent_normal,
            "ambient_occlusion": tex_set.bake_ambient_occlusion,
            "curvature": tex_set.bake_curvature,
            "thickness": tex_set.bake_thickness,
            "position": tex_set.bake_position,
            "random_island": tex_set.bake_random_island,
            "color_attribute": tex_set.bake_color_attribute,
            "ao_samples": tex_set.ao_samples,
            "ao_render_samples": tex_set.ao_render_samples,
            "ao_occlusion_mode": tex_set.ao_occlusion_mode,
            "ao_distance": tex_set.ao_distance,
            "ao_contrast": tex_set.ao_contrast,
            "curvature_exponent": tex_set.curvature_exponent,
            "curvature_contrast": tex_set.curvature_contrast,
            "thickness_samples": tex_set.thickness_samples,
            "thickness_render_samples": tex_set.thickness_render_samples,
            "thickness_distance": tex_set.thickness_distance,
            "normals_suffix": tex_set.normals_suffix,
            "tangent_suffix": tex_set.tangent_suffix,
            "ao_suffix": tex_set.ao_suffix,
            "curvature_suffix": tex_set.curvature_suffix,
            "thickness_suffix": tex_set.thickness_suffix,
            "position_suffix": tex_set.position_suffix,
            "random_island_suffix": tex_set.random_island_suffix,
            "color_attribute_suffix": tex_set.color_attribute_suffix,
            "color_attribute_name": tex_set.color_attribute_name,
            "dilation": data.global_dilation,
            "msaa": data.global_msaa,
            "output_format": data.output_format,
            "output_color_mode": data.output_color_mode,
            "output_color_depth": data.output_color_depth,
            "output_png_compression": data.output_png_compression,
        }
    return {
        "resolution": data.global_resolution,
        "normals_ws": data.global_bake_normals_ws,
        "tangent_normal": data.global_bake_tangent_normal,
        "ambient_occlusion": data.global_bake_ambient_occlusion,
        "curvature": data.global_bake_curvature,
        "thickness": data.global_bake_thickness,
        "position": data.global_bake_position,
        "random_island": data.global_bake_random_island,
        "color_attribute": data.global_bake_color_attribute,
        "ao_samples": data.global_ao_samples,
        "ao_render_samples": data.global_ao_render_samples,
        "ao_occlusion_mode": data.global_ao_occlusion_mode,
        "ao_distance": data.global_ao_distance,
        "ao_contrast": data.global_ao_contrast,
        "curvature_exponent": data.global_curvature_exponent,
        "curvature_contrast": data.global_curvature_contrast,
        "thickness_samples": data.global_thickness_samples,
        "thickness_render_samples": data.global_thickness_render_samples,
        "thickness_distance": data.global_thickness_distance,
        "normals_suffix": data.global_normals_suffix,
        "tangent_suffix": data.global_tangent_suffix,
        "ao_suffix": data.global_ao_suffix,
        "curvature_suffix": data.global_curvature_suffix,
        "thickness_suffix": data.global_thickness_suffix,
        "position_suffix": data.global_position_suffix,
        "random_island_suffix": data.global_random_island_suffix,
        "color_attribute_suffix": data.global_color_attribute_suffix,
        "color_attribute_name": data.global_color_attribute_name,
        "dilation": data.global_dilation,
        "msaa": data.global_msaa,
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


class DUMMYBAKE_OT_texture_set_add(bpy.types.Operator):
    bl_idname = "bakery.texture_set_add"
    bl_label = "Add Texture Set"
    bl_description = "Add a new texture set"

    # add a new texture set.
    def execute(self, context):
        # add a new texture set and make it active.
        data = context.scene.bakery_data
        item = data.texture_sets.add()
        item.name = f"Texture Set {len(data.texture_sets)}"
        data.active_texture_index = len(data.texture_sets) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_texture_set_remove(bpy.types.Operator):
    bl_idname = "bakery.texture_set_remove"
    bl_label = "Remove Texture Set"
    bl_description = "Remove the selected texture set"

    # remove the active texture set.
    def execute(self, context):
        # remove the active texture set safely.
        data = context.scene.bakery_data
        index = data.active_texture_index
        if 0 <= index < len(data.texture_sets):
            data.texture_sets.remove(index)
            if data.texture_sets:
                data.active_texture_index = min(index, len(data.texture_sets) - 1)
            else:
                data.active_texture_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_low_poly_add(bpy.types.Operator):
    bl_idname = "bakery.low_poly_add"
    bl_label = "Add Low Poly"
    bl_description = "Add a low poly entry to the selected texture set"

    # add selected objects to the low poly list.
    def execute(self, context):
        # add selected objects as low polys.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
        ]
        if selected:
            existing = {item.object for item in tex_set.low_polys if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = tex_set.low_polys.add()
                item.object = obj
            tex_set.active_low_index = max(0, len(tex_set.low_polys) - 1)
        else:
            tex_set.low_polys.add()
            tex_set.active_low_index = len(tex_set.low_polys) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_low_poly_remove(bpy.types.Operator):
    bl_idname = "bakery.low_poly_remove"
    bl_label = "Remove Low Poly"
    bl_description = "Remove the selected low poly entry"

    # remove the active low poly entry.
    def execute(self, context):
        # remove the active low poly entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        index = tex_set.active_low_index
        if 0 <= index < len(tex_set.low_polys):
            tex_set.low_polys.remove(index)
            if tex_set.low_polys:
                tex_set.active_low_index = min(index, len(tex_set.low_polys) - 1)
            else:
                tex_set.active_low_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_high_poly_add(bpy.types.Operator):
    bl_idname = "bakery.high_poly_add"
    bl_label = "Add High Poly"
    bl_description = "Add a high poly entry to the selected low poly"

    # add selected objects to the high poly list.
    def execute(self, context):
        # add selected objects as high polys.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys or tex_set.active_low_index < 0:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        selected = [
            obj for obj in context.selected_objects
            if obj.type not in _GEOMETRY_SKIP_TYPES
        ]
        if selected:
            existing = {item.object for item in low_item.high_polys if item.object}
            for obj in selected:
                if obj in existing:
                    continue
                item = low_item.high_polys.add()
                item.object = obj
            low_item.active_high_index = max(0, len(low_item.high_polys) - 1)
        else:
            low_item.high_polys.add()
            low_item.active_high_index = len(low_item.high_polys) - 1
        return {"FINISHED"}


class DUMMYBAKE_OT_high_poly_remove(bpy.types.Operator):
    bl_idname = "bakery.high_poly_remove"
    bl_label = "Remove High Poly"
    bl_description = "Remove the selected high poly entry"

    # remove the active high poly entry.
    def execute(self, context):
        # remove the active high poly entry.
        data = context.scene.bakery_data
        if not data.texture_sets or data.active_texture_index < 0:
            return {"CANCELLED"}
        tex_set = data.texture_sets[data.active_texture_index]
        if not tex_set.low_polys or tex_set.active_low_index < 0:
            return {"CANCELLED"}
        low_item = tex_set.low_polys[tex_set.active_low_index]
        index = low_item.active_high_index
        if 0 <= index < len(low_item.high_polys):
            low_item.high_polys.remove(index)
            if low_item.high_polys:
                low_item.active_high_index = min(index, len(low_item.high_polys) - 1)
            else:
                low_item.active_high_index = -1
        return {"FINISHED"}


class DUMMYBAKE_OT_select_object(bpy.types.Operator):
    bl_idname = "bakery.select_object"
    bl_label = "Select Object"
    bl_description = "Select the object from this list item"

    object_name: bpy.props.StringProperty()
    list_kind: bpy.props.EnumProperty(
        items=[
            ("LOW", "Low Poly", ""),
            ("HIGH", "High Poly", ""),
        ]
    )
    item_index: bpy.props.IntProperty()

    # sync list selection with the scene selection.
    def invoke(self, context, event):
        # sync list selection and optionally select the object in the scene.
        data = context.scene.bakery_data
        if self.list_kind == "LOW":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_low_index = self.item_index
        elif self.list_kind == "HIGH":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.low_polys or tex_set.active_low_index < 0:
                return {"CANCELLED"}
            low_item = tex_set.low_polys[tex_set.active_low_index]
            low_item.active_high_index = self.item_index

        if not event.ctrl:
            return {"FINISHED"}

        obj = context.scene.objects.get(self.object_name)
        if not obj:
            return {"CANCELLED"}
        if event.shift:
            obj.select_set(True)
        else:
            for other in context.view_layer.objects:
                other.select_set(False)
            obj.select_set(True)
        context.view_layer.objects.active = obj
        return {"FINISHED"}


class DUMMYBAKE_OT_clear_selection(bpy.types.Operator):
    bl_idname = "bakery.clear_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear the active list selection"

    list_kind: bpy.props.EnumProperty(
        items=[
            ("TEXTURE", "Texture Sets", ""),
            ("LOW", "Low Poly", ""),
            ("HIGH", "High Poly", ""),
        ]
    )

    # clear list selections.
    def execute(self, context):
        # clear list selections without touching the objects.
        data = context.scene.bakery_data
        if self.list_kind == "TEXTURE":
            data.active_texture_index = -1
            return {"FINISHED"}
        if self.list_kind == "LOW":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            tex_set.active_low_index = -1
            return {"FINISHED"}
        if self.list_kind == "HIGH":
            if not data.texture_sets or data.active_texture_index < 0:
                return {"CANCELLED"}
            tex_set = data.texture_sets[data.active_texture_index]
            if not tex_set.low_polys or tex_set.active_low_index < 0:
                return {"CANCELLED"}
            low_item = tex_set.low_polys[tex_set.active_low_index]
            low_item.active_high_index = -1
            return {"FINISHED"}
        return {"CANCELLED"}


class DUMMYBAKE_OT_bake_all(bpy.types.Operator):
    bl_idname = "bakery.bake_all"
    bl_label = "Bake All"
    bl_description = "Bake all texture sets"

    # bake every texture set.
    def execute(self, context):
        # bake every texture set in order.
        # route to the shared bake pipeline for all texture sets.
        if not _ensure_saved_blend(self, context):
            return {"CANCELLED"}
        data = context.scene.bakery_data
        if not data.texture_sets:
            self.report({"WARNING"}, "No texture sets to bake")
            return {"CANCELLED"}

        result = _bake_texture_sets(self, context, data.texture_sets, "Bake All")
        return {"FINISHED"} if result else {"CANCELLED"}


class DUMMYBAKE_OT_bake_selected_set(bpy.types.Operator):
    bl_idname = "bakery.bake_selected_set"
    bl_label = "Bake Selected Sets"
    bl_description = "Bake the checked texture sets"

    # bake only the active texture set.
    def execute(self, context):
        # bake only the currently active texture set.
        # route to the shared bake pipeline for just the active set.
        if not _ensure_saved_blend(self, context):
            return {"CANCELLED"}
        data = context.scene.bakery_data
        if not data.texture_sets:
            self.report({"WARNING"}, "No texture sets available")
            return {"CANCELLED"}
        selected_sets = [tex_set for tex_set in data.texture_sets if tex_set.enabled]
        if not selected_sets:
            _popup_error(context, "Please check at least one texture set")
            self.report({"WARNING"}, "Please check at least one texture set")
            return {"CANCELLED"}
        result = _bake_texture_sets(
            self,
            context,
            selected_sets,
            "Bake Selected Sets",
        )
        return {"FINISHED"} if result else {"CANCELLED"}


class DUMMYBAKE_OT_pick_output_dir(bpy.types.Operator):
    bl_idname = "bakery.pick_output_dir"
    bl_label = "Pick Output Folder"
    bl_description = "Choose a subfolder relative to the current blend file"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    # open the file picker at the current output folder.
    def invoke(self, context, event):
        # open the folder picker at the current output location.
        data = context.scene.bakery_data
        base_dir = bpy.path.abspath("//")
        current = _resolve_output_dir(data.output_dir)
        target = current if current else base_dir
        if target and not os.path.isdir(target):
            try:
                os.makedirs(target, exist_ok=True)
            except OSError:
                target = base_dir
        self.directory = target
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    # store the chosen folder as a relative path.
    def execute(self, context):
        # store the picked folder as a blend-relative path.
        data = context.scene.bakery_data
        if self.directory:
            data.output_dir = _relative_to_blend(self.directory)
        return {"FINISHED"}


# hide the last-bake banner when the user dismisses it.
class DUMMYBAKE_OT_hide_last_bake(bpy.types.Operator):
    bl_idname = "bakery.hide_last_bake"
    bl_label = "Hide Last Bake"
    bl_description = "Hide the last bake message"

    # toggle off the last-bake banner.
    def execute(self, context):
        data = context.scene.bakery_data
        data.show_last_bake = False
        return {"FINISHED"}


# run the full bake pipeline for one or more texture sets.
# bake one or more texture sets with shared logic.
def _bake_texture_sets(operator, context, texture_sets, label):
    # Main bake entry point used by both "Bake All" and "Bake Selected Set".
    data = context.scene.bakery_data
    material = _load_highpoly_material()
    if not material:
        _popup_error(context, "Missing high poly material")
        operator.report({"WARNING"}, "Missing high poly material")
        return False

    if not any(ts.low_polys for ts in texture_sets):
        _popup_error(context, "Please add at least one low poly object")
        operator.report({"WARNING"}, "Please add at least one low poly object")
        return False

    if not any(
        enabled
        for ts in texture_sets
        for _, enabled, _ in _bake_targets_from_settings(_effective_settings(data, ts))
    ):
        _popup_error(context, "Please enable at least one bake target")
        operator.report({"WARNING"}, "Please enable at least one bake target")
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
    data.baking_target_name = ""
    data.baking_progress = 0.0
    data.last_bake_duration = ""
    data.show_last_bake = False
    _tag_redraw(context)
    created_materials = []
    created_node_groups = []
    start_time = time.perf_counter()
    _debug_log(context, f"{label} started for {len(texture_sets)} texture set(s)")

    # Pre-calculate total target count for a simple progress bar.
    total_targets = 0
    for tex_set in texture_sets:
        settings = _effective_settings(data, tex_set)
        total_targets += sum(1 for _, enabled, _ in _bake_targets_from_settings(settings) if enabled)
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
            if not tex_set.low_polys:
                _debug_log(context, f"Skipping texture set '{tex_set.name}' (no low polys)")
                continue
            data.baking_set_name = tex_set.name

            saved_materials = {}
            color_attribute_materials = {}
            set_high_objs = []
            for low_item in tex_set.low_polys:
                low_obj = low_item.object
                if low_obj and low_obj.type == "MESH":
                    saved_materials.setdefault(low_obj, _capture_materials(low_obj))
                for high_item in low_item.high_polys:
                    high_obj = high_item.object
                    if not high_obj or high_obj.type != "MESH":
                        continue
                    if high_obj not in set_high_objs:
                        set_high_objs.append(high_obj)
                    if high_obj not in saved_materials:
                        saved_materials[high_obj] = _capture_materials(high_obj)
                    _ensure_material_slot(high_obj, material)

            # MSAA is implemented by baking at a higher resolution and downscaling.
            scale_factor = _msaa_factor(settings["msaa"])
            target_resolution = settings["resolution"]
            bake_resolution = (
                target_resolution[0] * scale_factor,
                target_resolution[1] * scale_factor,
            )
            for target_name, enabled, suffix in _bake_targets_from_settings(settings):
                if not enabled:
                    continue

                progress_value += 1
                if wm:
                    wm.progress_update(progress_value)
                target_label = _TARGET_LABELS.get(target_name, target_name)
                data.baking_target_name = target_label
                data.baking_progress = progress_value / progress_total
                _progress(operator, context, f"{label}: {tex_set.name} - {target_label}")

                image = _make_image(f"{tex_set.name}{suffix}", bake_resolution[0], bake_resolution[1])
                _clear_image(image)
                bake.use_clear = False

                needs_material_settings = _prepare_bake_target(
                    target_name,
                    settings,
                    material,
                    cycles,
                    bake,
                )
                if needs_material_settings:
                    _set_highpoly_material_settings(
                        material,
                        settings["ao_samples"],
                        settings["ao_occlusion_mode"],
                        settings["ao_distance"],
                        settings["ao_contrast"],
                        settings["curvature_exponent"],
                        settings["curvature_contrast"],
                        settings["thickness_samples"],
                        settings["thickness_distance"],
                    )

                for low_item in tex_set.low_polys:
                    low_obj = low_item.object
                    if not low_obj or low_obj.type != "MESH":
                        continue

                    high_items = [
                        item for item in low_item.high_polys
                        if item.object and item.object.type == "MESH"
                    ]
                    high_objs = [item.object for item in high_items]
                    if not high_objs:
                        # If there is no high poly, I bake the low poly with the baker material itself.
                        _ensure_material_slot(low_obj, material)
                    if target_name == "color_attribute":
                        # Override the high poly material per-object to inject the attribute name.
                        for item in high_items:
                            attr_name = (item.color_attribute or "").strip()
                            if not attr_name:
                                attr_name = settings["color_attribute_name"]
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
                        f"Baking {target_label} for low poly '{low_obj.name}' "
                        f"with {len(high_objs)} high poly object(s)",
                    )
                    restore_hide_render = None
                    if target_name == "ambient_occlusion":
                        occlusion_mode = settings["ao_occlusion_mode"]
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
                    if low_item.override_global_settings:
                        bake.cage_extrusion = low_item.cage_extrusion
                        bake.max_ray_distance = low_item.cage_max_ray_distance
                    else:
                        bake.cage_extrusion = data.global_extrusion
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

                # Dilation runs before downscaling so the padding survives MSAA.
                dilation = settings["dilation"] * scale_factor
                if dilation > 0:
                    _dilate_image(image, dilation)
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
                    f"{tex_set.name}{suffix}.{extension}",
                    settings,
                    scene=scene,
                    context=context,
                )

            for obj, mats in saved_materials.items():
                _restore_materials(obj, mats)
    finally:
        data.is_baking = False
        data.baking_set_name = ""
        data.baking_target_name = ""
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
        if material and material.name == _HIGH_MATERIAL_NAME:
            try:
                bpy.data.materials.remove(material, do_unlink=True)
            except RuntimeError:
                pass

    elapsed = time.perf_counter() - start_time
    minutes, seconds = divmod(int(elapsed), 60)
    data.last_bake_duration = f"{minutes}m {seconds}s"
    data.show_last_bake = True
    message = f"{label} finished in {elapsed:.2f}s"
    print(f"Bakery: {message}")
    operator.report({"INFO"}, message)
    return True


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
    DUMMYBAKE_OT_hide_last_bake,
)


# register all operator classes.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# unregister operator classes in reverse order.
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
