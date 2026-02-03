from array import array

try:
    import numpy as np
except Exception:
    np = None


def _normal_to_curvature(image, radius=2, strength=1.0, contrast=0.2, invert=False, edge_clamp=1.0, use_numpy=False):
    # Photoshop-style curvature from RG emboss, multiplied by B.
    if use_numpy and np is not None:
        _normal_to_curvature_numpy(
            image,
            radius=radius,
            strength=strength,
            contrast=contrast,
            invert=invert,
            edge_clamp=edge_clamp,
        )
        return
    _normal_to_curvature_python(
        image,
        radius=radius,
        strength=strength,
        contrast=contrast,
        invert=invert,
        edge_clamp=edge_clamp,
    )


def _normal_to_curvature_python(image, radius=2, strength=1.0, contrast=0.2, invert=False, edge_clamp=1.0):
    width, height = image.size
    if width < 2 or height < 2:
        return

    radius = max(1, int(radius))
    total = width * height * 4
    pixels = array("f", [0.0]) * total
    image.pixels.foreach_get(pixels)
    out_pixels = array("f", pixels)

    def _idx(x, y):
        return (y * width + x) * 4

    def _clamp01(value):
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    clamp = max(0.0, min(1.0, edge_clamp))
    strength = max(0.0, strength)
    for y in range(height):
        y0 = max(0, y - radius)
        y1 = min(height - 1, y + radius)
        for x in range(width):
            x0 = max(0, x - radius)
            x1 = min(width - 1, x + radius)
            i_c = _idx(x, y)
            i_l = _idx(x0, y)
            i_r = _idx(x1, y)
            i_d = _idx(x, y0)
            i_u = _idx(x, y1)

            dx = pixels[i_r] - pixels[i_l]
            dy = pixels[i_u + 1] - pixels[i_d + 1]
            raw = (dx + dy) * 0.5
            if clamp < 1.0:
                if raw > clamp:
                    raw = clamp
                elif raw < -clamp:
                    raw = -clamp
            curv = 0.5 + raw * strength
            curv = _clamp01(curv)
            curv *= _clamp01(pixels[i_c + 2])
            if contrast:
                curv = (curv - 0.5) * (1.0 + contrast) + 0.5
            if invert:
                curv = 1.0 - curv
            curv = _clamp01(curv)

            out_pixels[i_c] = curv
            out_pixels[i_c + 1] = curv
            out_pixels[i_c + 2] = curv
            out_pixels[i_c + 3] = 1.0

    image.pixels.foreach_set(out_pixels)
    image.update()


def _normal_to_curvature_numpy(image, radius=2, strength=1.0, contrast=0.2, invert=False, edge_clamp=1.0):
    width, height = image.size
    if width < 2 or height < 2:
        return

    radius = max(1, int(radius))
    clamp = max(0.0, min(1.0, edge_clamp))
    strength = max(0.0, strength)

    pixels = np.empty((height, width, 4), dtype=np.float32)
    image.pixels.foreach_get(pixels.ravel())

    padded_x = np.pad(pixels, ((0, 0), (radius, radius), (0, 0)), mode="edge")
    left = padded_x[:, 0:width, 0]
    right = padded_x[:, 2 * radius:2 * radius + width, 0]

    padded_y = np.pad(pixels, ((radius, radius), (0, 0), (0, 0)), mode="edge")
    down = padded_y[0:height, :, 1]
    up = padded_y[2 * radius:2 * radius + height, :, 1]

    raw = (right - left + up - down) * 0.5
    if clamp < 1.0:
        raw = np.clip(raw, -clamp, clamp)

    curv = 0.5 + raw * strength
    curv = np.clip(curv, 0.0, 1.0)
    curv *= np.clip(pixels[:, :, 2], 0.0, 1.0)

    if contrast:
        curv = (curv - 0.5) * (1.0 + contrast) + 0.5
    if invert:
        curv = 1.0 - curv
    curv = np.clip(curv, 0.0, 1.0)

    pixels[:, :, 0] = curv
    pixels[:, :, 1] = curv
    pixels[:, :, 2] = curv
    pixels[:, :, 3] = 1.0

    image.pixels.foreach_set(pixels.ravel())
    image.update()

