from array import array


def _sharpen_image(image, amount=0.5, per_channel=False):
    # Simple unsharp mask: original + amount * (original - blurred).
    width, height = image.size
    if width < 3 or height < 3 or amount <= 0.0:
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
