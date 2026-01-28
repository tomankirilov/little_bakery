from collections import deque
from array import array


# expand edge colors into transparent pixels (fast hard expansion).
def _dilate_image(image, iterations):
    # Expand colors into transparent pixels using a fast BFS over a float buffer.
    if iterations <= 0:
        return

    width, height = image.size
    total = width * height

    pixels = array("f", [0.0]) * (total * 4)
    image.pixels.foreach_get(pixels)

    owner = array("i", [-1]) * total
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

    while queue:
        idx = queue.popleft()
        current_dist = dist[idx]
        if current_dist >= iterations:
            continue
        x = idx % width
        nd = current_dist + 1
        base_owner = owner[idx]

        if idx >= width:
            up = idx - width
            if x > 0:
                n = up - 1
                if owner[n] == -1:
                    owner[n] = base_owner
                    dist[n] = nd
                    queue.append(n)
            n = up
            if owner[n] == -1:
                owner[n] = base_owner
                dist[n] = nd
                queue.append(n)
            if x < w1:
                n = up + 1
                if owner[n] == -1:
                    owner[n] = base_owner
                    dist[n] = nd
                    queue.append(n)

        if x > 0:
            n = idx - 1
            if owner[n] == -1:
                owner[n] = base_owner
                dist[n] = nd
                queue.append(n)
        if x < w1:
            n = idx + 1
            if owner[n] == -1:
                owner[n] = base_owner
                dist[n] = nd
                queue.append(n)

        dn = idx + width
        if dn < total:
            if x > 0:
                n = dn - 1
                if owner[n] == -1:
                    owner[n] = base_owner
                    dist[n] = nd
                    queue.append(n)
            n = dn
            if owner[n] == -1:
                owner[n] = base_owner
                dist[n] = nd
                queue.append(n)
            if x < w1:
                n = dn + 1
                if owner[n] == -1:
                    owner[n] = base_owner
                    dist[n] = nd
                    queue.append(n)

    for idx in transparent:
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
