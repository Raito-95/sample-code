import cv2
from PIL import ImageGrab
import numpy as np


def capture_screen_frame():
    """Capture the current screen and return it as a BGR image."""
    img_rgb = ImageGrab.grab()
    img_bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    return img_bgr


def initialize_video_writer(output_filename, frame_size, frame_rate=30, codec="XVID"):
    """Initialize and return a video writer object."""
    fourcc = cv2.VideoWriter_fourcc(*codec)
    return cv2.VideoWriter(output_filename, fourcc, frame_rate, frame_size)


def main():
    try:
        # Define output video parameters
        output_filename = "screen_capture.avi"
        frame_rate = 30

        # Capture an initial frame to get screen dimensions
        initial_frame = capture_screen_frame()
        height, width, _ = initial_frame.shape
        frame_size = (width, height)

        # Initialize video writer
        video_writer = initialize_video_writer(output_filename, frame_size, frame_rate)

        print("Starting screen capture. Press 'Ctrl+C' to stop.")

        while True:
            frame = capture_screen_frame()
            video_writer.write(frame)

    except KeyboardInterrupt:
        print("Screen capture stopped by user.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Release the video writer
        video_writer.release()
        print(f"Video saved as {output_filename}")


if __name__ == "__main__":
    main()
