import os
import time
import cv2
import numpy as np
import requests
from dotenv import load_dotenv
from PIL import Image, ImageGrab
from translate import Translator
import pytesseract

# Load environment variables from .env file
load_dotenv()

# API key for Google Cloud Translation
API_KEY = os.getenv("GCP_TOKEN")

# Google Cloud Translation API URL
TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"


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


def translate_text(text, target_language="zh-TW"):
    """
    Translate text using Google Cloud Translation API.
    """
    params = {"q": text, "target": target_language, "key": API_KEY}
    try:
        response = requests.post(TRANSLATE_URL, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result["data"]["translations"][0]["translatedText"]
    except requests.Timeout:
        return "Translation request timed out"
    except requests.RequestException as e:
        return f"An error occurred: {e}"


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
                        translated_text = translate_text(extracted_text)
                        translated_text_free = translate_text_free(extracted_text)
                        print(f"Extracted Text: {extracted_text}")
                        print("**********")
                        print(f"Paid: {translated_text}")
                        print("**********")
                        print(f"Free: {translated_text_free}")
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
    monitor_clipboard(show_images=True)
