from array import array
import bpy

try:
    import numpy as np
except Exception:
    np = None


def _use_numpy_filters():
    prefs = getattr(bpy.context, "preferences", None)
    if not prefs:
        return False
    root_package = __package__.split(".")[0] if __package__ else ""
    addon = prefs.addons.get(root_package) if root_package else None
    if addon and addon.preferences:
        return bool(getattr(addon.preferences, "use_numpy_filters", False))
    return False


def _normalize_image_luma(image):
    # Normalize image luminance to 0..1 across all pixels.
    width, height = image.size
    if width < 1 or height < 1:
        return

    if np is not None and _use_numpy_filters():
        _normalize_image_luma_numpy(image)
        return

    total = width * height * 4
    pixels = array("f", [0.0]) * total
    image.pixels.foreach_get(pixels)

    l_min = 1.0
    l_max = 0.0
    for i in range(0, total, 4):
        l = (
            pixels[i] * 0.299
            + pixels[i + 1] * 0.587
            + pixels[i + 2] * 0.114
        )
        if l < l_min:
            l_min = l
        if l > l_max:
            l_max = l

    if l_max <= l_min:
        return
    scale = 1.0 / (l_max - l_min)

    for i in range(0, total, 4):
        l = (
            pixels[i] * 0.299
            + pixels[i + 1] * 0.587
            + pixels[i + 2] * 0.114
        )
        n = (l - l_min) * scale
        if l > 0.0:
            ratio = n / l
            pixels[i] = max(0.0, min(1.0, pixels[i] * ratio))
            pixels[i + 1] = max(0.0, min(1.0, pixels[i + 1] * ratio))
            pixels[i + 2] = max(0.0, min(1.0, pixels[i + 2] * ratio))
        else:
            pixels[i] = n
            pixels[i + 1] = n
            pixels[i + 2] = n
        pixels[i + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()


def _normalize_image_luma_numpy(image):
    width, height = image.size
    pixels = np.empty((height, width, 4), dtype=np.float32)
    image.pixels.foreach_get(pixels.ravel())

    luma = pixels[:, :, 0] * 0.299 + pixels[:, :, 1] * 0.587 + pixels[:, :, 2] * 0.114
    l_min = float(luma.min(initial=1.0))
    l_max = float(luma.max(initial=0.0))
    if l_max <= l_min:
        return
    scale = 1.0 / (l_max - l_min)
    n = (luma - l_min) * scale

    nonzero = luma > 0.0
    ratio = np.zeros_like(luma)
    ratio[nonzero] = n[nonzero] / luma[nonzero]

    pixels[:, :, 0] = np.clip(pixels[:, :, 0] * ratio + (~nonzero) * n, 0.0, 1.0)
    pixels[:, :, 1] = np.clip(pixels[:, :, 1] * ratio + (~nonzero) * n, 0.0, 1.0)
    pixels[:, :, 2] = np.clip(pixels[:, :, 2] * ratio + (~nonzero) * n, 0.0, 1.0)
    pixels[:, :, 3] = 1.0

    image.pixels.foreach_set(pixels.ravel())
    image.update()
