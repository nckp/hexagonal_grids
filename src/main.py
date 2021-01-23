
from PIL import Image, ImageDraw
import math

img = Image.new('RGB', (800, 800), (0xff, 0xff, 0xff))
draw = ImageDraw.Draw(img)

###
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
###

def draw_hex(hex, color = 128):
    draw.line((hex[0], hex[1]), fill = color)
    draw.line((hex[1], hex[2]), fill = color)
    draw.line((hex[2], hex[3]), fill = color)
    draw.line((hex[3], hex[4]), fill = color)
    draw.line((hex[4], hex[5]), fill = color)
    draw.line((hex[5], hex[0]), fill = color)

def main():
    t_hex = (300, 620) # position
    draw_hex( get_corners(t_hex, 12) )
    img.show()
    
# program entry
main()