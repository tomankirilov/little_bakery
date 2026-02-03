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


#threshold of 0.1 is good for most cases.
#blend of 0.5 gives seems ok for most images. can go slightly lower 
# on high fine detail images.

# IMPORTANT: Apply after dilation, before MSAA!

def _apply_fxaa(image, threshold=0.1, blend=0.5):
    # Very basic FXAA-style pass: detect high-contrast edges and blend neighbor pixels.
    # Currently takes about 1s for a 4k texture.

    width, height = image.size
    if width < 3 or height < 3:
        return

    if np is not None and _use_numpy_filters():
        _apply_fxaa_numpy(image, threshold=threshold, blend=blend)
        return

    total = width * height * 4
    pixels = array("f", [0.0]) * total
    image.pixels.foreach_get(pixels)
    out_pixels = array("f", pixels)

    def _luma(i):
        return (
            pixels[i] * 0.299
            + pixels[i + 1] * 0.587
            + pixels[i + 2] * 0.114
        )

    w = width
    for y in range(1, height - 1):
        row = y * w
        row_n = (y - 1) * w
        row_s = (y + 1) * w
        for x in range(1, width - 1):
            idx = (row + x) * 4
            idx_n = (row_n + x) * 4
            idx_s = (row_s + x) * 4
            idx_w = (row + x - 1) * 4
            idx_e = (row + x + 1) * 4

            lum = _luma(idx)
            lum_n = _luma(idx_n)
            lum_s = _luma(idx_s)
            lum_w = _luma(idx_w)
            lum_e = _luma(idx_e)

            lum_min = min(lum, lum_n, lum_s, lum_w, lum_e)
            lum_max = max(lum, lum_n, lum_s, lum_w, lum_e)
            if lum_max - lum_min < threshold:
                continue

            r = (pixels[idx_n] + pixels[idx_s] + pixels[idx_w] + pixels[idx_e]) * 0.25
            g = (pixels[idx_n + 1] + pixels[idx_s + 1] + pixels[idx_w + 1] + pixels[idx_e + 1]) * 0.25
            b = (pixels[idx_n + 2] + pixels[idx_s + 2] + pixels[idx_w + 2] + pixels[idx_e + 2]) * 0.25
            a = (pixels[idx_n + 3] + pixels[idx_s + 3] + pixels[idx_w + 3] + pixels[idx_e + 3]) * 0.25

            out_pixels[idx] = pixels[idx] * (1.0 - blend) + r * blend
            out_pixels[idx + 1] = pixels[idx + 1] * (1.0 - blend) + g * blend
            out_pixels[idx + 2] = pixels[idx + 2] * (1.0 - blend) + b * blend
            out_pixels[idx + 3] = pixels[idx + 3] * (1.0 - blend) + a * blend

    image.pixels.foreach_set(out_pixels)
    image.update()


def _apply_fxaa_numpy(image, threshold=0.1, blend=0.5):
    width, height = image.size
    pixels = np.empty((height, width, 4), dtype=np.float32)
    image.pixels.foreach_get(pixels.ravel())

    center = pixels
    padded = np.pad(center, ((1, 1), (1, 1), (0, 0)), mode="edge")
    n = padded[:-2, 1:-1, :]
    s = padded[2:, 1:-1, :]
    w = padded[1:-1, :-2, :]
    e = padded[1:-1, 2:, :]

    lum = center[:, :, 0] * 0.299 + center[:, :, 1] * 0.587 + center[:, :, 2] * 0.114
    lum_n = n[:, :, 0] * 0.299 + n[:, :, 1] * 0.587 + n[:, :, 2] * 0.114
    lum_s = s[:, :, 0] * 0.299 + s[:, :, 1] * 0.587 + s[:, :, 2] * 0.114
    lum_w = w[:, :, 0] * 0.299 + w[:, :, 1] * 0.587 + w[:, :, 2] * 0.114
    lum_e = e[:, :, 0] * 0.299 + e[:, :, 1] * 0.587 + e[:, :, 2] * 0.114

    lum_min = np.minimum.reduce([lum, lum_n, lum_s, lum_w, lum_e])
    lum_max = np.maximum.reduce([lum, lum_n, lum_s, lum_w, lum_e])
    mask = (lum_max - lum_min) >= threshold

    avg = (n + s + w + e) * 0.25
    out = center.copy()
    if mask.any():
        mask3 = mask[:, :, None]
        out = np.where(mask3, center * (1.0 - blend) + avg * blend, center)

    pixels[:, :, :] = out
    image.pixels.foreach_set(pixels.ravel())
    image.update()
