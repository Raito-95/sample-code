import random


def generate_test_image(width: int = 3840, height: int = 1200, grid_spacing: int = 120, edge_width: int = 1, noise_intensity: int = 20) -> None:
    from PIL import Image, ImageDraw

    # Create a new black image
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    # Draw the grid lines
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill="white", width=edge_width)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill="white", width=edge_width)

    # Add noise to the image
    pixels = image.load()
    for x in range(width):
        for y in range(height):
            noise = random.randint(-noise_intensity, noise_intensity)
            r, g, b = pixels[x, y]
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            pixels[x, y] = (r, g, b)

    # Draw colored edges on the borders
    draw.rectangle((0, 0, width, edge_width), fill=(255, 0, 0))  # Top edge
    draw.rectangle((0, height - edge_width, width, height), fill=(0, 255, 0))  # Bottom edge
    draw.rectangle((0, 0, edge_width, height), fill=(0, 0, 255))  # Left edge
    draw.rectangle((width - edge_width, 0, width, height), fill=(255, 255, 0))  # Right edge

    image.save(f"panel_test_{width}x{height}.png")


if __name__ == "__main__":
    generate_test_image()
