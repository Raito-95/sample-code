import time
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pytesseract
from deep_translator import GoogleTranslator

def preprocess_image(image, show_images=False):
    """
    Convert image to grayscale, apply CLAHE, and invert colors to improve OCR.
    """
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(1, 1))
    image_cv = clahe.apply(image_cv)
    image_cv = cv2.bitwise_not(image_cv)
    processed_image = Image.fromarray(image_cv)

    if show_images:
        processed_image.show(title="Preprocessed Image")

    return processed_image

def extract_text_from_image(image, show_images=False):
    """
    Use Tesseract to extract text from a preprocessed image.
    """
    image = preprocess_image(image, show_images)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text.replace("\n", " ").strip()

def translate_text(text, target_language="zh-TW"):
    """
    Translate text using deep-translator's GoogleTranslator.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        return translator.translate(text)
    except Exception as e:
        return f"[Translation Error] {e}"

def is_supported_image(image):
    """
    Check if the clipboard image is a valid PIL image with supported mode.
    """
    return isinstance(image, Image.Image) and image.mode in ("RGB", "RGBA", "L")

def monitor_clipboard(show_images=False):
    """
    Monitor clipboard and perform OCR + translation when image content is detected.
    """
    previous_image_bytes = None

    print("Monitoring clipboard... Press Ctrl+C to stop.")
    while True:
        try:
            clipboard_content = ImageGrab.grabclipboard()
            if is_supported_image(clipboard_content):
                image_bytes = clipboard_content.tobytes()
                if image_bytes != previous_image_bytes:
                    text = extract_text_from_image(clipboard_content, show_images)
                    if text:
                        translation = translate_text(text)
                        print(f"\nExtracted: {text}")
                        print("Translated:", translation)
                        print("-" * 50)
                    else:
                        print("No text detected.")
                        print("-" * 50)
                    previous_image_bytes = image_bytes
        except Exception as e:
            print(f"[Error] {e}")

        time.sleep(0.1)  # 100ms delay

if __name__ == "__main__":
    monitor_clipboard(show_images=False)
