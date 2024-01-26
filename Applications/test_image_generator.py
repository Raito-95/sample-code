from PIL import Image, ImageDraw
import random

width, height = 1920, 1080

image = Image.new("RGB", (width, height), "black")

draw = ImageDraw.Draw(image)

edge_width = 1

grid_spacing = 120
for x in range(0, width, grid_spacing):
    draw.line([(x, 0), (x, height)], fill="white", width=edge_width)
for y in range(0, height, grid_spacing):
    draw.line([(0, y), (width, y)], fill="white", width=edge_width)

noise_intensity = 20
for x in range(width):
    for y in range(height):
        noise = random.randint(-noise_intensity, noise_intensity)
        r, g, b = image.getpixel((x, y))
        r += noise
        g += noise
        b += noise
        image.putpixel((x, y), (r, g, b))

draw.rectangle([(0, 0), (width, edge_width)], fill=(255, 0, 0))
draw.rectangle([(0, height - edge_width), (width, height)], fill=(0, 255, 0))
draw.rectangle([(0, 0), (edge_width, height)], fill=(0, 0, 255))
draw.rectangle([(width - edge_width, 0), (width, height)], fill=(255, 255, 0))

image.save("panel_test.png")
