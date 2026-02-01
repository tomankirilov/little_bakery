from array import array


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
