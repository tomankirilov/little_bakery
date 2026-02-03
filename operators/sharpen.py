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


def _sharpen_image(image, amount=0.5, per_channel=False):
    # Simple unsharp mask: original + amount * (original - blurred).
    width, height = image.size
    if width < 3 or height < 3 or amount <= 0.0:
        return

    if np is not None and _use_numpy_filters():
        _sharpen_image_numpy(image, amount=amount, per_channel=per_channel)
        return

    total = width * height * 4
    pixels = array("f", [0.0]) * total
    image.pixels.foreach_get(pixels)
    out_pixels = array("f", pixels)

    def _idx(x, y):
        return (y * width + x) * 4

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            i = _idx(x, y)
            if per_channel:
                for c in range(3):
                    c0 = pixels[i + c]
                    blur = (
                        pixels[_idx(x - 1, y) + c]
                        + pixels[_idx(x + 1, y) + c]
                        + pixels[_idx(x, y - 1) + c]
                        + pixels[_idx(x, y + 1) + c]
                        + c0
                    ) / 5.0
                    val = c0 + amount * (c0 - blur)
                    out_pixels[i + c] = max(0.0, min(1.0, val))
            else:
                l = (
                    pixels[i] * 0.299
                    + pixels[i + 1] * 0.587
                    + pixels[i + 2] * 0.114
                )
                blur_l = (
                    (pixels[_idx(x - 1, y)] * 0.299 + pixels[_idx(x - 1, y) + 1] * 0.587 + pixels[_idx(x - 1, y) + 2] * 0.114)
                    + (pixels[_idx(x + 1, y)] * 0.299 + pixels[_idx(x + 1, y) + 1] * 0.587 + pixels[_idx(x + 1, y) + 2] * 0.114)
                    + (pixels[_idx(x, y - 1)] * 0.299 + pixels[_idx(x, y - 1) + 1] * 0.587 + pixels[_idx(x, y - 1) + 2] * 0.114)
                    + (pixels[_idx(x, y + 1)] * 0.299 + pixels[_idx(x, y + 1) + 1] * 0.587 + pixels[_idx(x, y + 1) + 2] * 0.114)
                    + l
                ) / 5.0
                delta = amount * (l - blur_l)
                for c in range(3):
                    val = pixels[i + c] + delta
                    out_pixels[i + c] = max(0.0, min(1.0, val))
            out_pixels[i + 3] = pixels[i + 3]

    image.pixels.foreach_set(out_pixels)
    image.update()


def _sharpen_image_numpy(image, amount=0.5, per_channel=False):
    width, height = image.size
    pixels = np.empty((height, width, 4), dtype=np.float32)
    image.pixels.foreach_get(pixels.ravel())

    padded = np.pad(pixels, ((1, 1), (1, 1), (0, 0)), mode="edge")
    center = pixels
    left = padded[1:-1, :-2, :]
    right = padded[1:-1, 2:, :]
    up = padded[:-2, 1:-1, :]
    down = padded[2:, 1:-1, :]

    if per_channel:
        blur = (left + right + up + down + center) / 5.0
        out = center + amount * (center - blur)
        out[:, :, :3] = np.clip(out[:, :, :3], 0.0, 1.0)
        out[:, :, 3] = center[:, :, 3]
    else:
        luma = center[:, :, 0] * 0.299 + center[:, :, 1] * 0.587 + center[:, :, 2] * 0.114
        blur_l = (
            left[:, :, 0] * 0.299 + left[:, :, 1] * 0.587 + left[:, :, 2] * 0.114
            + right[:, :, 0] * 0.299 + right[:, :, 1] * 0.587 + right[:, :, 2] * 0.114
            + up[:, :, 0] * 0.299 + up[:, :, 1] * 0.587 + up[:, :, 2] * 0.114
            + down[:, :, 0] * 0.299 + down[:, :, 1] * 0.587 + down[:, :, 2] * 0.114
            + luma
        ) / 5.0
        delta = amount * (luma - blur_l)
        out = center.copy()
        out[:, :, 0] = np.clip(center[:, :, 0] + delta, 0.0, 1.0)
        out[:, :, 1] = np.clip(center[:, :, 1] + delta, 0.0, 1.0)
        out[:, :, 2] = np.clip(center[:, :, 2] + delta, 0.0, 1.0)
        out[:, :, 3] = center[:, :, 3]

    image.pixels.foreach_set(out.ravel())
    image.update()
