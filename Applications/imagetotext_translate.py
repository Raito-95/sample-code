import os
import time
import cv2
import numpy as np
from PIL import Image, ImageGrab
from translate import Translator
import pytesseract

def preprocess_image(image, show_images=False):
    """
    Preprocess the image to enhance OCR accuracy.
    """
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(1, 1))
    image_cv = clahe.apply(image_cv)
    image_cv = cv2.bitwise_not(image_cv)
    image = Image.fromarray(image_cv)

    if show_images:
        image.show(title="Preprocessed Image")

    return image

def translate_image_text(image, show_images=False):
    """
    Recognize text in the image using Tesseract OCR.
    """
    image = preprocess_image(image, show_images)
    extracted_text = pytesseract.image_to_string(image)
    extracted_text = extracted_text.replace("\n", " ").strip()
    return extracted_text

def translate_text_free(text, target_language="zh-TW"):
    """
    Translate text using a free translator.
    """
    translator = Translator(to_lang=target_language)
    try:
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        return f"An error occurred during translation: {e}"

def monitor_clipboard(show_images=False):
    """
    Monitor clipboard changes and perform OCR and translation.
    """
    previous_image = None

    while True:
        try:
            image = ImageGrab.grabclipboard()
            if image is not None and isinstance(image, Image.Image):
                image_bytes = image.tobytes()
                if image_bytes != previous_image:
                    extracted_text = translate_image_text(image, show_images)
                    if extracted_text:
                        translated_text_free = translate_text_free(extracted_text)
                        print(f"Extracted Text: {extracted_text}")
                        print("**********")
                        print(f"Translated: {translated_text_free}")
                        print("--------------------------------------------------")
                    else:
                        print("No text detected in the image.")
                        print("--------------------------------------------------")
                    previous_image = image_bytes
        except Exception as e:
            print(f"Error processing clipboard content: {e}")

        time.sleep(0.1)  # Sleep for 100 milliseconds

# Start monitoring clipboard changes
if __name__ == "__main__":
    monitor_clipboard()
