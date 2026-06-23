import math


def point_in_rect(point, rect):
    px, py = point
    rx, ry, rw, rh = rect
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def rects_overlap(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def circle_rect_overlap(cx, cy, cr, rx, ry, rw, rh):
    nearest_x = max(rx, min(cx, rx + rw))
    nearest_y = max(ry, min(cy, ry + rh))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return dx * dx + dy * dy <= cr * cr


def car_collision_mtv(car1, car2):
    corners1 = car1.get_corners()
    corners2 = car2.get_corners()

    mtv_axis = None
    min_overlap = float("inf")

    for corners in (corners1, corners2):
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            ax = -(p2[1] - p1[1])
            ay = p2[0] - p1[0]
            axis_len = math.hypot(ax, ay)
            if axis_len < 0.001:
                continue
            ax /= axis_len
            ay /= axis_len

            proj1 = [p[0] * ax + p[1] * ay for p in corners1]
            proj2 = [p[0] * ax + p[1] * ay for p in corners2]
            max1, min1 = max(proj1), min(proj1)
            max2, min2 = max(proj2), min(proj2)

            if max1 < min2 or max2 < min1:
                return None

            overlap = min(max1, max2) - max(min1, min2)
            if overlap < min_overlap:
                min_overlap = overlap
                mtv_axis = (ax, ay)

    if mtv_axis is None:
        return None

    dx = car2.x - car1.x
    dy = car2.y - car1.y
    if dx * mtv_axis[0] + dy * mtv_axis[1] < 0:
        mtv_axis = (-mtv_axis[0], -mtv_axis[1])

    return (mtv_axis[0], mtv_axis[1], min_overlap)
