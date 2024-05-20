import os
import cv2


def crop_image(input_image, start_x, start_y, end_x, end_y):
    """
    Crop the image from (start_x, start_y) to (end_x, end_y).
    """
    return input_image[start_y:end_y, start_x:end_x]


def save_image(output_path, image):
    """
    Save the image to the specified path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, image)


def get_image_files(folder_path, extensions=(".jpg", ".jpeg", ".png")):
    """
    Get a list of image files in the specified folder with the given extensions.
    """
    return [
        file for file in os.listdir(folder_path) if file.lower().endswith(extensions)
    ]


def main():
    image_folder_path = "."  # Path to the folder containing input images
    # Output folder for cropped images
    output_folder_path = os.path.join(image_folder_path, "crop")

    start_x, start_y = 0, 0  # Starting coordinates of the top-left corner for cropping
    end_x, end_y = (
        1920,
        1080,
    )  # Ending coordinates of the bottom-right corner for cropping

    image_files = get_image_files(image_folder_path)

    if not image_files:
        print("No images found in the specified folder.")
        return

    for image_file in image_files:
        input_image_path = os.path.join(image_folder_path, image_file)
        input_image = cv2.imread(input_image_path)

        if input_image is None:
            print(f"Failed to load image: {input_image_path}")
            continue

        cropped_image = crop_image(input_image, start_x, start_y, end_x, end_y)
        output_image_path = os.path.join(output_folder_path, f"cropped_{image_file}")

        save_image(output_image_path, cropped_image)
        print(f"Cropped and saved image: {output_image_path}")

    print("All images cropped and saved!")


if __name__ == "__main__":
    main()
