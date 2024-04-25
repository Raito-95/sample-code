import os
import time

import cv2
import numpy as np
import requests
from PIL import Image, ImageGrab
from translate import Translator

import pytesseract


# API key for Google Cloud Translation
API_KEY = os.getenv('TOKEN')

# Google Cloud Translation API URL
TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'

# Image preprocessing to enhance OCR accuracy
def preprocess_image(image, show_images=False):
    # Convert PIL image to an OpenCV format
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)

    # Enhance contrast by CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(1, 1))
    image_cv = clahe.apply(image_cv)

    # Invert colors if the text and background are both light
    image_cv = cv2.bitwise_not(image_cv)

    # # Adaptive thresholding to handle varying background
    # image_cv = cv2.adaptiveThreshold(
    #     image_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Convert back to PIL image for Tesseract
    image = Image.fromarray(image_cv)

    # Show the preprocessed image if required
    if show_images:
        image.show(title="Preprocessed Image")

    return image

# Define a function to recognize and translate text in an image
def translate_image_text(image, show_images=False):
    # Preprocess the image to improve OCR accuracy
    image = preprocess_image(image, show_images)
    # Use Tesseract OCR to recognize text in the image
    extracted_text = pytesseract.image_to_string(image)
    # Clean and format the extracted text
    extracted_text = extracted_text.replace('\n', ' ')
    return extracted_text

def translate_text_free(text, target_language='zh-TW'):
    translator = Translator(to_lang=target_language)
    try:
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        return f"An error occurred during translation: {e}"

# Translate text using Google Cloud Translation API
def translate_text(text, target_language='zh-TW'):
    params = {
        'q': text,
        'target': target_language,
        'key': API_KEY
    }
    try:
        response = requests.post(TRANSLATE_URL, params=params, timeout=10)
        result = response.json()
        return result['data']['translations'][0]['translatedText']
    except requests.Timeout:
        return "Translation request timed out"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# Monitor clipboard changes and perform OCR and translation
def monitor_clipboard(show_images=False):
    previous_image = None  # Used to store the previous image to avoid re-processing

    while True:
        try:
            image = ImageGrab.grabclipboard()
            if image is not None:
                # Convert image to bytes to compare images directly
                image_bytes = image.tobytes()
                if image_bytes != previous_image:
                    # Perform OCR on the image
                    extracted_text = translate_image_text(image, show_images)

                    # If OCR results are empty or just whitespace, skip translation
                    if not extracted_text.strip():
                        print("No text detected in the image.")
                        print("--------------------------------------------------")
                    else:
                        # Translate the text and print it
                        translated_text = translate_text(extracted_text)
                        translated_text_free = translate_text_free(extracted_text)
                        print(translated_text)
                        print('**********')
                        print(translated_text_free)
                        print("--------------------------------------------------")

                    # Update previous_image to avoid processing the same image again
                    previous_image = image_bytes
        except Exception as e:
            print("Error processing clipboard content:", e)

        time.sleep(0.1)  # Sleep for 100 milliseconds


# Start monitoring clipboard changes
monitor_clipboard(show_images=False)
