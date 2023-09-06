import cv2
import os


def crop_image(input_image, start_x, start_y, end_x, end_y):
    cropped_image = input_image[start_y:end_y, start_x:end_x]
    return cropped_image


def save_image(output_path, image):
    cv2.imwrite(output_path, image)


def main():
    image_folder_path = '.'
    image_files = [file for file in os.listdir(image_folder_path) if file.endswith('.jpg')]

    start_x, start_y = 1900, 2000
    end_x, end_y = 2000, 2100

    for image_file in image_files:
        input_image_path = os.path.join(image_folder_path, image_file)
        input_image = cv2.imread(input_image_path)
        cropped_image = crop_image(input_image, start_x, start_y, end_x, end_y)
        output_image_path = os.path.join(image_folder_path, f"crop/cropped_{image_file}")
        save_image(output_image_path, cropped_image)
    print("所有圖片擷取和儲存完成！")


if __name__ == "__main__":
    main() 