from PIL import Image, ImageEnhance
import os


def enhance_image(input_frame, enhancer_class, factor, save_path):
    """
    Enhance an image with a given factor using a specific PIL enhancer class and save it.
    """
    enhancer = enhancer_class(input_frame)
    enhanced_image = enhancer.enhance(factor)
    enhanced_image.save(save_path)
    print(f'Saved image to {save_path}, Enhancement factor: {factor}')


def get_images_list(directory, extensions):
    """
    Filter out image files based on specified extensions in the given directory.
    """
    return [file for file in os.listdir(directory) if file.lower().endswith(extensions)]


def create_folder(path):
    """
    Create a folder if it doesn't already exist.
    """
    os.makedirs(path, exist_ok=True)


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_path, 'data')

# Enhancements setup
enhancement_types = {
    'brightness': ImageEnhance.Brightness,
    'color': ImageEnhance.Color,
    'contrast': ImageEnhance.Contrast,
    'sharpness': ImageEnhance.Sharpness
}
image_extensions = ('.png', '.jpg', '.jpeg')

# Create enhancement folders
for name in enhancement_types.keys():
    create_folder(os.path.join(data_path, name))

# Process images
images_list = get_images_list(current_path, image_extensions)
for image_name in images_list:
    image_path = os.path.join(current_path, image_name)
    frame = Image.open(image_path)

    for enhancer_name, enhancer_class in enhancement_types.items():
        enhancer_folder = os.path.join(data_path, enhancer_name)
        factor = 0.5

        for count in range(6):
            save_path = os.path.join(
                enhancer_folder, f"{os.path.splitext(image_name)[0]}_{enhancer_name}_{count + 1}.png")
            enhance_image(frame, enhancer_class, factor, save_path)
            factor += 0.3
