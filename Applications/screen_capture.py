import cv2
from PIL import ImageGrab
import numpy as np
import time
import keyboard


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
        delay = 1 / frame_rate

        # Capture an initial frame to get screen dimensions
        initial_frame = capture_screen_frame()
        height, width, _ = initial_frame.shape
        frame_size = (width, height)

        # Initialize video writer
        video_writer = initialize_video_writer(output_filename, frame_size, frame_rate)

        print("Press 'p' to start/pause/resume recording. Press 'Ctrl+C' to stop.")

        is_recording = False

        while True:
            start_time = time.time()

            if keyboard.is_pressed("p"):
                is_recording = not is_recording
                if is_recording:
                    print("Started recording.")
                else:
                    print("Paused recording.")
                time.sleep(0.5)

            if is_recording:
                frame = capture_screen_frame()
                video_writer.write(frame)

            elapsed_time = time.time() - start_time
            sleep_time = max(0, delay - elapsed_time)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Screen capture stopped by user.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if "video_writer" in locals():
            video_writer.release()
        print(f"Video saved as {output_filename}")


if __name__ == "__main__":
    main()
