import numpy as np
from PIL import Image

def load_unique_colors(path):
    image = Image.open(path)
    data = np.array(image)
    if image.mode == 'RGBA':
        data = data[:, :, :3]  # Ignore alpha channel
    colors = data.reshape(-1, data.shape[2])
    filtered_colors = colors[(np.all(colors != [0, 0, 0], axis=1)) & (np.all(colors != [255, 255, 255], axis=1))]
    unique = np.unique(filtered_colors, axis=0)
    return unique

def save_colors_to_code_format(unique, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("unique_colors = np.array([\n")
        for color in unique:
            file.write(f"    [{', '.join(map(str, color))}],\n")
        file.write("])")

image_path = 'C:/Users/User/Desktop/result.png'
unique_colors = load_unique_colors(image_path)
save_colors_to_code_format(unique_colors, 'unique_colors.txt')
