from array import array


def _normal_to_curvature(image, radius=2, strength=1.0, contrast=0.2, invert=False):
    # Photoshop-style curvature from RG emboss, multiplied by B.
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

    def _normal_at(x, y):
        i = _idx(x, y)
        nx = pixels[i] * 2.0 - 1.0
        ny = pixels[i + 1] * 2.0 - 1.0
        nz = pixels[i + 2] * 2.0 - 1.0
        return nx, ny, nz

    def _clamp01(value):
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

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
            curv = 0.5 + (dx + dy) * 0.5 * max(0.0, strength)
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
