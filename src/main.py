
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
import math

Img = Image.new('RGB', (800, 800), color = (0xff,0xff,0xff))
Draw = ImageDraw.Draw(Img)

def hex_corner(position, size, i):
    angle_deg = 60 * i 
    angle_rad = math.pi / 180 * angle_deg
    (x, y) = position
    return (x + size * math.cos(angle_rad), y + size * math.sin(angle_rad))

def get_corners(position, size):
    (x, y) = position
    corners = []
    for i in range(6):
        corners.append(hex_corner(position, size, i))
    return corners

def Hex(_q, _r, _s):
    assert (_q + _r + _s == 0), "q + r + s doesn't equal 0"
    return dict(q = _q, r = _r, s = _s)

def eq(a, b):
    return a['q'] == b['q'] and a['r'] == b['r'] and a['s'] == b['s']

def neq(a, b):
    return not (a['q'] == b['q'] and a['r'] == b['r'] and a['s'] == b['s'])

def hex_add(a, b):
    return Hex(a['q'] + b['q'], a['r'] + b['r'], a['s'] + b['s'])

def hex_subtract(a, b):
    return Hex(a['q'] - b['q'], a['r'] - b['r'], a['s'] - b['s'])

def hex_multiply(a, k):
    return Hex(a['q'] * k, a['r'] * k, a['s'] * k)

def hex_length(hex):
    return int((abs(hex['q']) + abs(hex['r']) + abs(hex['s'])) / 2)

def hex_distance(a, b):
    return hex_length(hex_subtract(a, b))

hex_directions = Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1), Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)

def hex_direction(direction): # direction: 0 .. 5
    assert (0 <= direction and direction < 6), "Direction is outside the range of 0..5"
    return hex_directions[direction]

def hex_neighbor(hex, direction):
    return hex_add(hex, hex_direction(direction))

layout_flat = dict(f0 = 3.0/2.0, f1 = 0.0, f2 = math.sqrt(3.0)/2.0, f3 = math.sqrt(3.0), b0 = 2.0/3.0, b1 = 0.0, b2 = -1.0/3.0, b3 = math.sqrt(3.0)/3.0, start_angle = 0.0)

def Point(x_, y_):
    return dict(x = x_, y = y_)

def Layout(orientation_, size_, origin_):
    return dict(orientation = orientation_, size = size_, origin = origin_)

def hex_to_pixel(layout, h):
    M = layout['orientation']
    x = (M['f0'] * h['q'] + M['f1'] * h['r']) * layout['size']['x']
    y = (M['f2'] * h['q'] + M['f3'] * h['r']) * layout['size']['y']
    return Point(x + layout['origin']['x'], y + layout['origin']['y'])

def pixel_to_hex(layout, p):
    M = layout['orientation']
    pt = Point((p['x'] - layout['origin']['x']) / layout['size']['x'], (p['y'] - layout['origin']['y']) / layout['size']['y'])
    q = M['b0'] * pt['x'] + M['b1'] * pt['y']
    r = M['b2'] * pt['x'] + M['b3'] * pt['y']
    return Hex(q, r, -q - r)#FractionalHex(q, r, -q - r)

def hex_corner_offset(layout, corner):
    size = layout['size']
    angle = 2.0 * math.pi * (layout['orientation']['start_angle'] + corner) / 6
    return Point(size['x'] * math.cos(angle), size['y'] * math.sin(angle))

def polygon_corners(layout, h):
    corners = []
    center = hex_to_pixel(layout, h)
    for i in range(6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center['x'] + offset['x'], center['y'] + offset['y']))
    return corners

def hex_round(h):
    q = int(math.round(h['q']))
    r = int(math.round(h['r']))
    s = int(math.round(h['s']))
    q_diff = math.abs(q - h['q'])
    r_diff = math.abs(r - h['r'])
    s_diff = math.abs(s - h['s'])
    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s
    else:
        s = -q - r
    return Hex(q, r, s)

def lerp(a, b, t):
    return a * (1-t) + b * t

def hex_lerp(a, b, t):
    return Hex(lerp(a['q'], b['q'], t), lerp(a['r'], b['r'], t), lerp(a['s'], b['s'], t))

def hex_linedraw(a, b):
    N = hex_distance(a, b)
    a_nudge(a['q'] + 1e-6, a['r'] + 1e-6, a['s'] - 2e-6)
    b_nudge(b['q'] + 1e-6, b['r'] + 1e-6, b['s'] - 2e-6)
    results = []
    step = 1.0 / math.max(N, 1)
    for i in range(N):
        results.append(hex_round(hex_lerp(a_nudge, b_nudge, step * i)))
    return results

def draw_hexagon_from_corners(corn):
    corners = []
    for co in corn:
        corners.append((co['x'], co['y']))
    Draw.line((corners[0], corners[1]), fill = 128)
    Draw.line((corners[1], corners[2]), fill = 128) 
    Draw.line((corners[2], corners[3]), fill = 128)
    Draw.line((corners[3], corners[4]), fill = 128) 
    Draw.line((corners[4], corners[5]), fill = 128)
    Draw.line((corners[5], corners[0]), fill = 128)
    return (corners[3], corners[4])

def render_map(m):
    for h in m:
        corners = polygon_corners(Layout(layout_flat, Point(42, 42), Point(400, 400)), h)
        (text_pos_x, text_pos_y) = draw_hexagon_from_corners(corners)
        Draw.text((text_pos_y[0], text_pos_x[1] - 5),"(" + str(h['q'])+',' + str(h['r']) + ',' + str(h['r']) + ")",(0,0,0))

def populate_hexagonal_map(map_size):
    hex_map = []
    q = -map_size
    while q <= map_size:
        r1 = max(-map_size, -q - map_size)
        r2 = min(map_size, -q + map_size)
        r = r1 
        while r <= r2:
            hex_map.append(Hex(q, r, -q-r))
            r += 1
        q += 1
    return hex_map

def main():
    map_size = 3

    hex_map = populate_hexagonal_map(map_size)

    render_map(hex_map)
    Img.show()
    

if __name__ == "__main__":
    main()