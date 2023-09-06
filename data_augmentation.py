from PIL import Image, ImageEnhance
import os


# 亮度
def brightness_enhancer(input_frame, element):
    enhance = ImageEnhance.Brightness(input_frame)
    enhanced_image = enhance.enhance(element)
    return enhanced_image


# 色度
def color_enhancer(input_frame, element):
    enhance = ImageEnhance.Color(input_frame)
    enhanced_image = enhance.enhance(element)
    return enhanced_image


# 對比度
def contrast_enhancer(input_frame, element):
    enhance = ImageEnhance.Contrast(input_frame)
    enhanced_image = enhance.enhance(element)
    return enhanced_image


# 銳度
def sharpness_enhancer(input_frame, element):
    enhance = ImageEnhance.Sharpness(input_frame)
    enhanced_image = enhance.enhance(element)
    return enhanced_image


current_path = os.path.dirname(os.path.abspath(__file__))
data_path = current_path + '\\data\\'
bright = data_path + 'bright\\'
color = data_path + 'color\\'
contrast = data_path + 'contrast\\'
sharp = data_path + 'sharp\\'


for save_path in [data_path, bright, color, contrast, sharp]:
    if not os.path.exists(save_path):
        os.mkdir(save_path)

images_list = []
for file in os.listdir(current_path):
    if file.endswith('png'):
        images_list.append(file)
    elif file.endswith('jpg'):
        images_list.append(file)
    elif file.endswith('jpeg'):
        images_list.append(file)


for num in range(len(images_list)):
    image_path = os.path.join(current_path, images_list[num])
    if os.path.isfile(image_path):
        frame = Image.open(image_path)
        factor = 0.5
        for count in range(6):

            bright_enhanced = brightness_enhancer(frame, factor)
            color_enhanced = color_enhancer(frame, factor)
            contrast_enhanced = contrast_enhancer(frame, factor)
            sharp_enhanced = sharpness_enhancer(frame, factor)

            save_bright_path = os.path.join(bright, images_list[num][:-4] + '_bright_' + str(count + 1) + '.png')
            save_color_path = os.path.join(color, images_list[num][:-4] + '_color_' + str(count+1) + '.png')
            save_contrast_path = os.path.join(contrast, images_list[num][:-4] + '_contrast_' + str(count+1) + '.png')
            save_sharp_path = os.path.join(sharp, images_list[num][:-4] + '_sharp_' + str(count+1) + '.png')

            bright_enhanced.save(save_bright_path)
            color_enhanced.save(save_color_path)
            contrast_enhanced.save(save_contrast_path)
            sharp_enhanced.save(save_sharp_path)

            print(f'Save image to {save_bright_path}')
            print(f'Save image to {save_color_path}')
            print(f'Save image to {save_contrast_path}')
            print(f'Save image to {save_sharp_path}')
            print(f'factor:{factor}')
            factor += 0.3

