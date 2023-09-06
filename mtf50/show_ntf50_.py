import argparse
import cv2
import os
from compute_mtf50 import ImageProcessor

class MTF50Processor:
    def __init__(self):
        self.selected_roi = None
        self.roi_selected = False
        self.start_x, self.start_y = -1, -1
        self.end_x, self.end_y = -1, -1
        self.current_x, self.current_y = -1, -1
        self.scale_factor = 0.5

    def select_roi(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_x, self.start_y = x, y
            self.current_x, self.current_y = x, y
            self.roi_selected = False
        elif event == cv2.EVENT_MOUSEMOVE:
            self.current_x, self.current_y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.end_x, self.end_y = x, y
            orig_start_x = int(min(self.start_x, self.current_x) / self.scale_factor)
            orig_start_y = int(min(self.start_y, self.current_y) / self.scale_factor)
            orig_end_x = int(max(self.start_x, self.current_x) / self.scale_factor)
            orig_end_y = int(max(self.start_y, self.current_y) / self.scale_factor)
            self.selected_roi = (orig_start_x, orig_start_y, orig_end_x, orig_end_y)
            self.roi_selected = True

    def process_frame(self, frame):
        window_width = frame.shape[1] // 2
        window_height = frame.shape[0] // 2
        resized_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        cv2.resizeWindow('Camera', window_width, window_height)
        if self.roi_selected:
            if self.selected_roi:
                roi = frame[self.selected_roi[1]:self.selected_roi[3], self.selected_roi[0]:self.selected_roi[2]]
                if roi.size == 0:
                    print("Invalid ROI selection. Skipping...")
                    self.roi_selected = False
                    return resized_frame
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                mtf_computer = ImageProcessor(gray, show=False)
                mtf50 = mtf_computer.MTF()
                mtf50_rounded = round(mtf50, 3) if mtf50 is not None else None
                text_x = resized_frame.shape[1] - 200
                text_y = resized_frame.shape[0] - 30
                cv2.rectangle(resized_frame, (int(self.start_x), int(self.start_y)), (int(self.end_x), int(self.end_y)), (0, 255, 0), 1)
                cv2.putText(resized_frame, f'MTF50: {mtf50_rounded}', (int(text_x), int(text_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
        elif self.start_x != -1 and self.start_y != -1:
            cv2.rectangle(resized_frame, (self.start_x, self.start_y), (self.current_x, self.current_y), (0, 255, 0), 1)
        return resized_frame
    
    def process_from_camera(self):
        cv2.namedWindow('Camera')
        cv2.setMouseCallback('Camera', self.select_roi)
        cap = cv2.VideoCapture(0)
        auto_focus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
        auto_exposure = cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        auto_wb = cap.get(cv2.CAP_PROP_AUTO_WB)
        print(f"Auto Focus: {auto_focus}")
        print(f"Auto Exposure: {auto_exposure}")
        print(f"Auto White Balance: {auto_wb}")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0)
        cap.set(cv2.CAP_PROP_CONTRAST, 10)
        cap.set(cv2.CAP_PROP_SATURATION, 10)
        show_properties = False

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                break
            processed_frame = self.process_frame(frame)
            cv2.imshow('Camera', processed_frame)
            if show_properties:
                properties = [
                    "CAP_PROP_POS_MSEC",
                    "CAP_PROP_POS_FRAMES",
                    "CAP_PROP_FRAME_WIDTH",
                    "CAP_PROP_FRAME_HEIGHT",
                    "CAP_PROP_FPS",
                    "CAP_PROP_BRIGHTNESS",
                    "CAP_PROP_CONTRAST",
                    "CAP_PROP_SATURATION",
                    "CAP_PROP_HUE",
                    "CAP_PROP_GAIN",
                    "CAP_PROP_EXPOSURE",
                ]
                for prop in properties:
                    value = cap.get(getattr(cv2, prop))
                    print(f"{prop}: {value}")
                show_properties = False
            key = cv2.waitKey(1) & 0xFF
            if key == ord('p'):
                show_properties = True
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def process_from_image(self, folder_path):
        image_files = [file for file in os.listdir(folder_path) if file.endswith('.jpg')]
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            frame = cv2.imread(image_path)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mtf_computer = ImageProcessor(gray, show=True)
            mtf50 = mtf_computer.MTF()
            mtf50_rounded = round(mtf50, 3) if mtf50 is not None else None
            print(f'Image: {image_file}, MTF50: {mtf50_rounded}')

    def main(self):
        parser = argparse.ArgumentParser(description='MTF50 Calculator.')
        parser.add_argument('--camera', action='store_true', help='Read from camera.')
        parser.add_argument('--folder', type=str, help='Read from image folder.')
        args = parser.parse_args()
        if args.camera:
            self.process_from_camera()
        elif args.folder:
            self.process_from_image(args.folder)
        else:
            print("You must provide either --camera or --folder argument.")
            exit(1)


if __name__ == "__main__":
    mtf50_processor = MTF50Processor()
    mtf50_processor.main()