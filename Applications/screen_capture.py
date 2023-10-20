from PIL import ImageGrab  # Used for capturing screen images
import numpy as np  # Used for image data processing
import cv2  # OpenCV library for video processing

# Capture a screen image
image = ImageGrab.grab()
width, height = image.size  # Get the width and height of the image

# Define a video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Define the video codec
output_filename = 'screen_capture.avi'  # Output video filename
frame_rate = 30  # Frame rate (frames per second)
video = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))  # Create a video writer

# Start capturing the screen
while True:
    img_rgb = ImageGrab.grab()  # Capture a screen image (RGB mode)
    img_bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)  # Convert to BGR mode, which OpenCV uses
    video.write(img_bgr)  # Write the image to the video file
    cv2.imshow('Screen Capture', img_bgr)  # Display the captured image in a window

    # Press 'q' key to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video writer and close the video file
video.release()
cv2.destroyAllWindows()
