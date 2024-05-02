import os
import cv2

def crop_image(input_image, start_x, start_y, end_x, end_y):
    # Crop the image
    cropped_image = input_image[start_y:end_y, start_x:end_x]
    return cropped_image

def save_image(output_path, image):
    # Save the image to the specified path
    cv2.imwrite(output_path, image)

def main():
    image_folder_path = '.'  # Path to the folder containing input images
    image_files = [file for file in os.listdir(image_folder_path) if file.endswith('.jpg')]

    start_x, start_y = 0, 0  # Starting coordinates of the top-left corner for cropping
    end_x, end_y = 1920, 1080  # Ending coordinates of the bottom-right corner for cropping

    for image_file in image_files:
        input_image_path = os.path.join(image_folder_path, image_file)
        input_image = cv2.imread(input_image_path)
        cropped_image = crop_image(input_image, start_x, start_y, end_x, end_y)
        output_image_path = os.path.join(image_folder_path, f"crop/cropped_{image_file}")  # Path to save the cropped image
        save_image(output_image_path, cropped_image)
    print("All images cropped and saved!")

if __name__ == "__main__":
    main()
