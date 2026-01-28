from collections import deque
from array import array


_OFFSETS_FAST = (
    (0, -1),
    (-1, 0), (1, 0),
    (0, 1),
)


_OFFSETS_16 = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1),
    (-2, 1),  (-1, 2),  (1, 2),  (2, 1),
)

_OFFSETS_RADIAL = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
    (-2, 0), (2, 0), (0, -2), (0, 2),
    (-2, -1), (-1, -2), (1, -2), (2, -1),
    (-2, 1),  (-1, 2),  (1, 2),  (2, 1),
)


_OFFSETS_JITTER = _OFFSETS_RADIAL

# expand edge colors into transparent pixels (fast hard expansion).
def _dilate_buffer(pixels, width, height, iterations, offsets):
    if iterations <= 0:
        return

    total = width * height
    owner = array("i", [-1]) * total
    if iterations < 32767:
        dist = array("h", [-1]) * total
    else:
        dist = array("i", [-1]) * total
    queue = deque()
    transparent = array("i")

    p4 = 0
    for idx in range(total):
        if pixels[p4 + 3] > 0.0:
            owner[idx] = idx
            dist[idx] = 0
            queue.append(idx)
        else:
            transparent.append(idx)
        p4 += 4

    if not queue:
        return

    remaining = len(transparent)
    w1 = width - 1
    h1 = height - 1

    while queue:
        idx = queue.popleft()
        current_dist = dist[idx]
        if current_dist >= iterations:
            continue
        x = idx % width
        y = idx // width
        nd = current_dist + 1
        base_owner = owner[idx]
        for ox, oy in offsets:
            nx = x + ox
            ny = y + oy
            if nx < 0 or nx > w1 or ny < 0 or ny > h1:
                continue
            n = ny * width + nx
            if owner[n] != -1:
                continue
            owner[n] = base_owner
            dist[n] = nd
            queue.append(n)
            remaining -= 1
            if remaining <= 0:
                queue.clear()
                break

    for idx in transparent:
        oi = owner[idx]
        if oi == -1:
            continue
        dst = idx * 4
        src = oi * 4
        if pixels[dst + 3] > 0.0:
            pixels[dst] = (pixels[dst] + pixels[src]) * 0.5
            pixels[dst + 1] = (pixels[dst + 1] + pixels[src + 1]) * 0.5
            pixels[dst + 2] = (pixels[dst + 2] + pixels[src + 2]) * 0.5
            pixels[dst + 3] = 1.0
            continue
        pixels[dst] = pixels[src]
        pixels[dst + 1] = pixels[src + 1]
        pixels[dst + 2] = pixels[src + 2]
        pixels[dst + 3] = 1.0


# expand edge colors into transparent pixels (fast hard expansion).
def _dilate_image_fast(image, iterations):
    # Fast 4-neighbor dilation with a light downsample pass after 16px.
    if iterations <= 0:
        return

    width, height = image.size
    pixels = array("f", [0.0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)

    if iterations <= 16:
        _dilate_buffer(pixels, width, height, iterations, _OFFSETS_FAST)
        image.pixels.foreach_set(pixels)
        image.update()
        return

    _dilate_buffer(pixels, width, height, 16, _OFFSETS_FAST)
    remaining = iterations - 16

    def _downscale(src, src_w, src_h, factor):
        dst_w = max(1, src_w // factor)
        dst_h = max(1, src_h // factor)
        dst = array("f", [0.0]) * (dst_w * dst_h * 4)
        for y in range(dst_h):
            sy = min(src_h - 1, y * factor)
            for x in range(dst_w):
                sx = min(src_w - 1, x * factor)
                src_i = (sy * src_w + sx) * 4
                dst_i = (y * dst_w + x) * 4
                dst[dst_i] = src[src_i]
                dst[dst_i + 1] = src[src_i + 1]
                dst[dst_i + 2] = src[src_i + 2]
                dst[dst_i + 3] = src[src_i + 3]
        return dst, dst_w, dst_h

    def _upsample_fill(dst, dst_w, dst_h, src, src_w, src_h, factor):
        for y in range(dst_h):
            sy = min(src_h - 1, y // factor)
            for x in range(dst_w):
                dst_i = (y * dst_w + x) * 4
                if dst[dst_i + 3] > 0.0:
                    continue
                sx = min(src_w - 1, x // factor)
                src_i = (sy * src_w + sx) * 4
                if src[src_i + 3] <= 0.0:
                    continue
                dst[dst_i] = src[src_i]
                dst[dst_i + 1] = src[src_i + 1]
                dst[dst_i + 2] = src[src_i + 2]
                dst[dst_i + 3] = 1.0

    if remaining <= 48:
        half, half_w, half_h = _downscale(pixels, width, height, 2)
        _dilate_buffer(half, half_w, half_h, (remaining + 1) // 2, _OFFSETS_FAST)
        _upsample_fill(pixels, width, height, half, half_w, half_h, 2)
    else:
        half, half_w, half_h = _downscale(pixels, width, height, 2)
        _dilate_buffer(half, half_w, half_h, 24, _OFFSETS_FAST)
        _upsample_fill(pixels, width, height, half, half_w, half_h, 2)

        quarter, quarter_w, quarter_h = _downscale(pixels, width, height, 4)
        _dilate_buffer(quarter, quarter_w, quarter_h, (remaining - 48 + 3) // 4, _OFFSETS_FAST)
        _upsample_fill(pixels, width, height, quarter, quarter_w, quarter_h, 4)

    image.pixels.foreach_set(pixels)
    image.update()




# expand edge colors into transparent pixels (16-direction expansion).
def _dilate_image_wide(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    pixels = array("f", [0.0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)
    _dilate_buffer(pixels, width, height, iterations, _OFFSETS_16)
    image.pixels.foreach_set(pixels)
    image.update()




# expand edge colors into transparent pixels (jittered neighbor order).
def _dilate_image_jitter(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    pixels = array("f", [0.0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)

    total = width * height
    owner = array("i", [-1]) * total
    if iterations < 32767:
        dist = array("h", [-1]) * total
    else:
        dist = array("i", [-1]) * total
    queue = deque()
    transparent = array("i")

    p4 = 0
    for idx in range(total):
        if pixels[p4 + 3] > 0.0:
            owner[idx] = idx
            dist[idx] = 0
            queue.append(idx)
        else:
            transparent.append(idx)
        p4 += 4

    if not queue:
        return

    w1 = width - 1
    h1 = height - 1
    offsets = _OFFSETS_JITTER
    offset_count = len(offsets)

    while queue:
        idx = queue.popleft()
        current_dist = dist[idx]
        if current_dist >= iterations:
            continue
        x = idx % width
        y = idx // width
        nd = current_dist + 1
        base_owner = owner[idx]
        start = idx % offset_count
        for i in range(offset_count):
            ox, oy = offsets[(start + i) % offset_count]
            nx = x + ox
            ny = y + oy
            if nx < 0 or nx > w1 or ny < 0 or ny > h1:
                continue
            n = ny * width + nx
            if owner[n] != -1:
                continue
            owner[n] = base_owner
            dist[n] = nd
            queue.append(n)
            remaining -= 1
            if remaining <= 0:
                queue.clear()
                break

    for idx in transparent:
        oi = owner[idx]
        if oi == -1:
            continue
        dst = idx * 4
        src = oi * 4
        if pixels[dst + 3] > 0.0:
            pixels[dst] = (pixels[dst] + pixels[src]) * 0.5
            pixels[dst + 1] = (pixels[dst + 1] + pixels[src + 1]) * 0.5
            pixels[dst + 2] = (pixels[dst + 2] + pixels[src + 2]) * 0.5
            pixels[dst + 3] = 1.0
            continue
        pixels[dst] = pixels[src]
        pixels[dst + 1] = pixels[src + 1]
        pixels[dst + 2] = pixels[src + 2]
        pixels[dst + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()

# expand edge colors into transparent pixels (radial-ish expansion).
def _dilate_image_radial(image, iterations):
    # Slightly larger neighbor ring for a more radial-looking spread.
    if iterations <= 0:
        return

    width, height = image.size
    pixels = array("f", [0.0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)
    _dilate_buffer(pixels, width, height, iterations, _OFFSETS_RADIAL)
    image.pixels.foreach_set(pixels)
    image.update()




# expand edge colors into transparent pixels (euclidean distance).
def _dilate_image_euclidean(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    total = width * height

    pixels = array("f", [0.0]) * (total * 4)
    image.pixels.foreach_get(pixels)

    owner = array("i", [-1]) * total
    dist = array("f", [1e9]) * total
    transparent = array("i")

    import heapq
    heap = []

    p4 = 0
    for idx in range(total):
        if pixels[p4 + 3] > 0.0:
            owner[idx] = idx
            dist[idx] = 0.0
            heapq.heappush(heap, (0.0, idx))
        else:
            transparent.append(idx)
        p4 += 4

    if not heap:
        return

    w1 = width - 1
    h1 = height - 1
    neighbors = (
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, 1.4142136), (1, -1, 1.4142136),
        (-1, 1, 1.4142136),  (1, 1, 1.4142136),
    )

    while heap:
        d, idx = heapq.heappop(heap)
        if d != dist[idx]:
            continue
        if d >= iterations:
            continue
        x = idx % width
        y = idx // width
        base_owner = owner[idx]
        for ox, oy, cost in neighbors:
            nx = x + ox
            ny = y + oy
            if nx < 0 or nx > w1 or ny < 0 or ny > h1:
                continue
            n = ny * width + nx
            nd = d + cost
            if nd >= dist[n] or nd > iterations:
                continue
            dist[n] = nd
            owner[n] = base_owner
            heapq.heappush(heap, (nd, n))

    for idx in transparent:
        oi = owner[idx]
        if oi == -1:
            continue
        dst = idx * 4
        src = oi * 4
        if pixels[dst + 3] > 0.0:
            pixels[dst] = (pixels[dst] + pixels[src]) * 0.5
            pixels[dst + 1] = (pixels[dst + 1] + pixels[src + 1]) * 0.5
            pixels[dst + 2] = (pixels[dst + 2] + pixels[src + 2]) * 0.5
            pixels[dst + 3] = 1.0
            continue
        pixels[dst] = pixels[src]
        pixels[dst + 1] = pixels[src + 1]
        pixels[dst + 2] = pixels[src + 2]
        pixels[dst + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()



# expand edge colors into transparent pixels (chamfer distance transform).
def _dilate_image_chamfer(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    total = width * height
    pixels = array("f", [0.0]) * (total * 4)
    image.pixels.foreach_get(pixels)

    # 3-4 chamfer weights (orth=3, diag=4)
    INF = 1 << 30
    dist = array("i", [INF]) * total
    owner = array("i", [-1]) * total

    p4 = 0
    for idx in range(total):
        if pixels[p4 + 3] > 0.0:
            dist[idx] = 0
            owner[idx] = idx
        p4 += 4

    # Forward pass
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            best = dist[idx]
            best_owner = owner[idx]
            if x > 0:
                n = idx - 1
                d = dist[n] + 3
                if d < best:
                    best = d
                    best_owner = owner[n]
            if y > 0:
                n = idx - width
                d = dist[n] + 3
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x > 0:
                    n = idx - width - 1
                    d = dist[n] + 4
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x < width - 1:
                    n = idx - width + 1
                    d = dist[n] + 4
                    if d < best:
                        best = d
                        best_owner = owner[n]
            dist[idx] = best
            owner[idx] = best_owner

    # Backward pass
    for y in range(height - 1, -1, -1):
        row = y * width
        for x in range(width - 1, -1, -1):
            idx = row + x
            best = dist[idx]
            best_owner = owner[idx]
            if x < width - 1:
                n = idx + 1
                d = dist[n] + 3
                if d < best:
                    best = d
                    best_owner = owner[n]
            if y < height - 1:
                n = idx + width
                d = dist[n] + 3
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x < width - 1:
                    n = idx + width + 1
                    d = dist[n] + 4
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x > 0:
                    n = idx + width - 1
                    d = dist[n] + 4
                    if d < best:
                        best = d
                        best_owner = owner[n]
            dist[idx] = best
            owner[idx] = best_owner

    # Map iterations to chamfer units (orth step == 3)
    max_dist = iterations * 3

    for idx in range(total):
        if dist[idx] == 0:
            continue
        if dist[idx] > max_dist:
            continue
        oi = owner[idx]
        if oi == -1:
            continue
        dst = idx * 4
        src = oi * 4
        if pixels[dst + 3] > 0.0:
            pixels[dst] = (pixels[dst] + pixels[src]) * 0.5
            pixels[dst + 1] = (pixels[dst + 1] + pixels[src + 1]) * 0.5
            pixels[dst + 2] = (pixels[dst + 2] + pixels[src + 2]) * 0.5
            pixels[dst + 3] = 1.0
            continue
        pixels[dst] = pixels[src]
        pixels[dst + 1] = pixels[src + 1]
        pixels[dst + 2] = pixels[src + 2]
        pixels[dst + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()



# expand edge colors into transparent pixels (5x5 chamfer transform).
def _dilate_image_chamfer5(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    total = width * height
    pixels = array("f", [0.0]) * (total * 4)
    image.pixels.foreach_get(pixels)

    INF = 1 << 30
    dist = array("i", [INF]) * total
    owner = array("i", [-1]) * total

    p4 = 0
    for idx in range(total):
        if pixels[p4 + 3] > 0.0:
            dist[idx] = 0
            owner[idx] = idx
        p4 += 4

    w1 = width - 1
    h1 = height - 1

    # Forward pass (5x5 mask)
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            best = dist[idx]
            best_owner = owner[idx]
            # left and up neighbors
            if x > 0:
                n = idx - 1
                d = dist[n] + 5
                if d < best:
                    best = d
                    best_owner = owner[n]
            if x > 1:
                n = idx - 2
                d = dist[n] + 10
                if d < best:
                    best = d
                    best_owner = owner[n]
            if y > 0:
                n = idx - width
                d = dist[n] + 5
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x > 0:
                    n = idx - width - 1
                    d = dist[n] + 7
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x < w1:
                    n = idx - width + 1
                    d = dist[n] + 7
                    if d < best:
                        best = d
                        best_owner = owner[n]
            if y > 1:
                n = idx - 2 * width
                d = dist[n] + 10
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x > 0:
                    n = idx - 2 * width - 1
                    d = dist[n] + 11
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x < w1:
                    n = idx - 2 * width + 1
                    d = dist[n] + 11
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x > 1:
                    n = idx - 2 * width - 2
                    d = dist[n] + 14
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x < w1 - 1:
                    n = idx - 2 * width + 2
                    d = dist[n] + 14
                    if d < best:
                        best = d
                        best_owner = owner[n]
            dist[idx] = best
            owner[idx] = best_owner

    # Backward pass
    for y in range(height - 1, -1, -1):
        row = y * width
        for x in range(width - 1, -1, -1):
            idx = row + x
            best = dist[idx]
            best_owner = owner[idx]
            if x < w1:
                n = idx + 1
                d = dist[n] + 5
                if d < best:
                    best = d
                    best_owner = owner[n]
            if x < w1 - 1:
                n = idx + 2
                d = dist[n] + 10
                if d < best:
                    best = d
                    best_owner = owner[n]
            if y < h1:
                n = idx + width
                d = dist[n] + 5
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x < w1:
                    n = idx + width + 1
                    d = dist[n] + 7
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x > 0:
                    n = idx + width - 1
                    d = dist[n] + 7
                    if d < best:
                        best = d
                        best_owner = owner[n]
            if y < h1 - 1:
                n = idx + 2 * width
                d = dist[n] + 10
                if d < best:
                    best = d
                    best_owner = owner[n]
                if x < w1:
                    n = idx + 2 * width + 1
                    d = dist[n] + 11
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x > 0:
                    n = idx + 2 * width - 1
                    d = dist[n] + 11
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x < w1 - 1:
                    n = idx + 2 * width + 2
                    d = dist[n] + 14
                    if d < best:
                        best = d
                        best_owner = owner[n]
                if x > 1:
                    n = idx + 2 * width - 2
                    d = dist[n] + 14
                    if d < best:
                        best = d
                        best_owner = owner[n]
            dist[idx] = best
            owner[idx] = best_owner

    max_dist = iterations * 5
    for idx in range(total):
        if dist[idx] == 0:
            continue
        if dist[idx] > max_dist:
            continue
        oi = owner[idx]
        if oi == -1:
            continue
        dst = idx * 4
        if pixels[dst + 3] > 0.0:
            continue
        src = oi * 4
        pixels[dst] = pixels[src]
        pixels[dst + 1] = pixels[src + 1]
        pixels[dst + 2] = pixels[src + 2]
        pixels[dst + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()


# expand edge colors into transparent pixels (true EDT, 2-pass).
def _dilate_image_edt(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    total = width * height
    pixels = array("f", [0.0]) * (total * 4)
    image.pixels.foreach_get(pixels)

    big = 1.0e20

    def edt_1d(f):
        n = len(f)
        v = [0] * n
        z = [0.0] * (n + 1)
        k = 0
        v[0] = 0
        z[0] = -1.0e30
        z[1] = 1.0e30
        for q in range(1, n):
            while True:
                p = v[k]
                s = ((f[q] + q * q) - (f[p] + p * p)) / (2 * (q - p))
                if s <= z[k]:
                    k -= 1
                    if k < 0:
                        k = 0
                        break
                else:
                    break
            if s <= z[k]:
                continue
            k += 1
            v[k] = q
            z[k] = s
            z[k + 1] = 1.0e30
        d = [0.0] * n
        idx = [0] * n
        k = 0
        for q in range(n):
            while z[k + 1] < q:
                k += 1
            p = v[k]
            d[q] = (q - p) * (q - p) + f[p]
            idx[q] = p
        return d, idx

    # Column pass
    g = [0.0] * total
    nearest_y = array("i", [-1]) * total
    for x in range(width):
        f = [big] * height
        for y in range(height):
            idx = y * width + x
            if pixels[idx * 4 + 3] > 0.0:
                f[y] = 0.0
        d, idxs = edt_1d(f)
        for y in range(height):
            gi = y * width + x
            g[gi] = d[y]
            nearest_y[gi] = idxs[y]

    # Row pass
    max_dist2 = iterations * iterations
    for y in range(height):
        f = [0.0] * width
        for x in range(width):
            f[x] = g[y * width + x]
        d, idxs = edt_1d(f)
        for x in range(width):
            if d[x] > max_dist2:
                continue
            idx = y * width + x
            if pixels[idx * 4 + 3] > 0.0:
                continue
            sx = idxs[x]
            sy = nearest_y[y * width + sx]
            if sy < 0:
                continue
            src = (sy * width + sx) * 4
            dst = idx * 4
            pixels[dst] = pixels[src]
            pixels[dst + 1] = pixels[src + 1]
            pixels[dst + 2] = pixels[src + 2]
            pixels[dst + 3] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()

# expand edge colors with a multi-scale strategy.
def _dilate_image_multiscale(image, iterations):
    if iterations <= 0:
        return

    width, height = image.size
    pixels = array("f", [0.0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)

    full_steps = min(iterations, 16)
    mid_steps = min(max(iterations - 16, 0), 32)
    rest_steps = max(iterations - 16 - 32, 0)

    if full_steps > 0:
        _dilate_buffer(pixels, width, height, full_steps, _OFFSETS_FAST)

    def _downscale(src, src_w, src_h, factor):
        dst_w = max(1, src_w // factor)
        dst_h = max(1, src_h // factor)
        dst = array("f", [0.0]) * (dst_w * dst_h * 4)
        for y in range(dst_h):
            sy = min(src_h - 1, y * factor)
            for x in range(dst_w):
                sx = min(src_w - 1, x * factor)
                src_i = (sy * src_w + sx) * 4
                dst_i = (y * dst_w + x) * 4
                dst[dst_i] = src[src_i]
                dst[dst_i + 1] = src[src_i + 1]
                dst[dst_i + 2] = src[src_i + 2]
                dst[dst_i + 3] = src[src_i + 3]
        return dst, dst_w, dst_h

    def _upsample_fill(dst, dst_w, dst_h, src, src_w, src_h, factor):
        for y in range(dst_h):
            sy = min(src_h - 1, y // factor)
            for x in range(dst_w):
                dst_i = (y * dst_w + x) * 4
                if dst[dst_i + 3] > 0.0:
                    continue
                sx = min(src_w - 1, x // factor)
                src_i = (sy * src_w + sx) * 4
                if src[src_i + 3] <= 0.0:
                    continue
                dst[dst_i] = src[src_i]
                dst[dst_i + 1] = src[src_i + 1]
                dst[dst_i + 2] = src[src_i + 2]
                dst[dst_i + 3] = 1.0

    if mid_steps > 0:
        half, half_w, half_h = _downscale(pixels, width, height, 2)
        _dilate_buffer(half, half_w, half_h, (mid_steps + 1) // 2, _OFFSETS_FAST)
        _upsample_fill(pixels, width, height, half, half_w, half_h, 2)

    if rest_steps > 0:
        quarter, quarter_w, quarter_h = _downscale(pixels, width, height, 4)
        _dilate_buffer(quarter, quarter_w, quarter_h, (rest_steps + 3) // 4, _OFFSETS_FAST)
        _upsample_fill(pixels, width, height, quarter, quarter_w, quarter_h, 4)

    image.pixels.foreach_set(pixels)
    image.update()


def _dilate_image(image, iterations, method="FAST"):
    if method == "RADIAL":
        return _dilate_image_radial(image, iterations)
    if method == "WIDE":
        return _dilate_image_wide(image, iterations)
    if method == "MULTI":
        return _dilate_image_multiscale(image, iterations)
    if method == "JITTER":
        return _dilate_image_jitter(image, iterations)
    if method == "EUCLIDEAN":
        return _dilate_image_euclidean(image, iterations)
    if method == "CHAMFER":
        return _dilate_image_chamfer(image, iterations)
    if method == "CHAMFER5":
        return _dilate_image_chamfer5(image, iterations)
    if method == "EDT":
        return _dilate_image_edt(image, iterations)
    return _dilate_image_fast(image, iterations)
