from PIL import Image, ImageEnhance
import os

# Function to enhance an image with a given factor and enhancer type
def enhance_image(input_frame, element, enhancer_type, factor, save_path):
    enhance = enhancer_type(input_frame)
    enhanced_image = enhance.enhance(factor)
    enhanced_image.save(save_path)
    print(f'Saved image to {save_path}, Enhancement factor: {factor}')

# Get the current directory of the script
current_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_path, 'data')
enhancement_types = [ImageEnhance.Brightness, ImageEnhance.Color, ImageEnhance.Contrast, ImageEnhance.Sharpness]
enhancement_names = ['bright', 'color', 'contrast', 'sharp']

# Create folders (if they don't exist)
for folder_name in enhancement_names:
    folder_path = os.path.join(data_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

# Filter out image files
images_list = [file for file in os.listdir(current_path) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Apply multiple enhancements to each image
for image_name in images_list:
    image_path = os.path.join(current_path, image_name)
    if os.path.isfile(image_path):
        frame = Image.open(image_path)
        
        for enhancer_type, enhancer_name in zip(enhancement_types, enhancement_names):
            factor = 0.5
            enhancer_folder = os.path.join(data_path, enhancer_name)
            
            for count in range(6):
                save_path = os.path.join(enhancer_folder, f"{os.path.splitext(image_name)[0]}_{enhancer_name}_{count + 1}.png")
                enhance_image(frame, enhancer_type, enhancer_name, factor, save_path)
                factor += 0.3
