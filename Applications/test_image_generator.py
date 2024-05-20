import random
from PIL import Image, ImageDraw

# Define the image dimensions
width, height = 1920, 1080

# Create a new black image
image = Image.new("RGB", (width, height), "black")
draw = ImageDraw.Draw(image)

# Set edge width and grid spacing
edge_width = 1
grid_spacing = 120

# Draw the grid lines
for x in range(0, width, grid_spacing):
    draw.line([(x, 0), (x, height)], fill="white", width=edge_width)
for y in range(0, height, grid_spacing):
    draw.line([(0, y), (width, y)], fill="white", width=edge_width)

# Add noise to the image
noise_intensity = 20
for x in range(width):
    for y in range(height):
        noise = random.randint(-noise_intensity, noise_intensity)
        r, g, b = image.getpixel((x, y))
        r = max(0, min(255, r + noise))
        g = max(0, min(255, g + noise))
        b = max(0, min(255, b + noise))
        image.putpixel((x, y), (r, g, b))

# Draw colored edges on the borders
draw.rectangle((0, 0, width, edge_width), fill=(255, 0, 0))  # Top edge
draw.rectangle((0, height - edge_width, width, height), fill=(0, 255, 0))  # Bottom edge
draw.rectangle((0, 0, edge_width, height), fill=(0, 0, 255))  # Left edge
draw.rectangle((width - edge_width, 0, width, height), fill=(255, 255, 0))  # Right edge

# Save the image
image.save("panel_test.png")
