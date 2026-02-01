from array import array


def _normalize_image_luma(image):
    # Normalize image luminance to 0..1 across all pixels.
    width, height = image.size
    if width < 1 or height < 1:
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
