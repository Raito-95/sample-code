import os
import cv2


def crop_image(input_image, start_x, start_y, end_x, end_y):
    """
    Crop the image from (start_x, start_y) to (end_x, end_y),
    ensuring the crop box is within the image bounds.
    """
    height, width = input_image.shape[:2]
    
    start_x = max(0, min(start_x, width))
    end_x = max(0, min(end_x, width))
    start_y = max(0, min(start_y, height))
    end_y = max(0, min(end_y, height))

    if end_x <= start_x or end_y <= start_y:
        raise ValueError("Invalid crop dimensions: width or height is zero or negative.")

    return input_image[start_y:end_y, start_x:end_x]


def save_image(output_path, image):
    """
    Save the image to the specified path.
    Handles potential write errors.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        success = cv2.imwrite(output_path, image)
        if not success:
            raise IOError("cv2.imwrite returned False.")
    except Exception as e:
        print(f"Failed to save image {output_path}: {e}")


def get_image_files(folder_path, extensions=(".jpg", ".jpeg", ".png")):
    """
    Get a list of image files in the specified folder with the given extensions.
    """
    return [
        file for file in os.listdir(folder_path) if file.lower().endswith(extensions)
    ]


def main():
    image_folder_path = "."  # Path to the folder containing input images
    output_folder_path = os.path.join(image_folder_path, "crop")  # Output folder

    start_x, start_y = 0, 0
    end_x, end_y = 1920, 1080  # Target crop size

    image_files = get_image_files(image_folder_path)

    if not image_files:
        print("No images found in the specified folder.")
        return

    for image_file in image_files:
        input_image_path = os.path.join(image_folder_path, image_file)

        try:
            input_image = cv2.imread(input_image_path)
            if input_image is None:
                raise IOError("cv2.imread returned None (file not a valid image?)")

            cropped_image = crop_image(input_image, start_x, start_y, end_x, end_y)
            output_image_path = os.path.join(output_folder_path, f"cropped_{image_file}")
            save_image(output_image_path, cropped_image)

            print(f"Cropped and saved image: {output_image_path}")

        except Exception as e:
            print(f"Error processing {image_file}: {e}")

    print("All images processed.")


if __name__ == "__main__":
    main()
