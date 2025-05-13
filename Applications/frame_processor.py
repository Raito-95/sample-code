"""
Thermal Sensor Tool - User Guide

This tool captures thermal imagery from a webcam and processes the data in real time, with support for platform-specific format differences (Linux vs. Windows).

1. SPI Transfer Speed Recommendation:
   - Recommended to set SPI speed to 25MHz. Be cautious of prescaler limits for ABP1/ABP2 chips.

2. System Clock Configuration:
   - Default SYSTEMCLK = 96MHz is suggested to support both SPI and USB image transfer.
   - SYSTEMCLK can be reduced to 54MHz by removing Y16 byte-swapping logic and adjusting SPI prescaling accordingly.

3. Image Processing Logic:
   - Linux: Uses RGB3 format (3 bytes per pixel), processing involves RGB → BGR → swap → RGB.
   - Windows: Most webcams output YUYV format, which requires manual conversion to RGB using OpenCV.
   - This script automatically detects the platform and applies the appropriate conversion process.

4. VLC Note:
   - On Windows, VLC can be set to output RGB3 format. However, this script does not currently support that case. If enabled, manual adjustment to skip the conversion is needed.

5. Image Size:
   - The default processed frame size is 160x120. To support other sizes, modify the reshape line accordingly.
"""

import cv2
import platform
import time

def convert_frame_format(frame):
    # Flatten the frame and perform slicing-based swapping for higher efficiency
    frame = frame.ravel()
    frame[1::2], frame[::2] = frame[::2], frame[1::2]
    return frame.reshape(120, 160, 3)

# Detect the operating system
is_windows = platform.system() == "Windows"

# Capture data from the webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply format conversion for Windows (YUYV to RGB)
    if is_windows:
        frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_YUYV)

    # Apply swapping operation
    converted_frame = convert_frame_format(frame)

    # Display the processed frame
    cv2.imshow('Frame', converted_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        # Save the processed frame with a timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_image_file = f"frame_{timestamp}.png"
        # Directly save using OpenCV to avoid PIL conversion
        cv2.imwrite(output_image_file, converted_frame)
        print(f"Processed frame saved as {output_image_file}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()