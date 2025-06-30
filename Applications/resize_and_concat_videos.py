import os
import time
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx.resize import resize


def resize_and_pad(video, target_size=(640, 640), bg_color=(0, 0, 0)):
    if video.size[0] > target_size[0] or video.size[1] > target_size[1]:
        if video.size[0] / target_size[0] > video.size[1] / target_size[1]:
            video_resized = resize(video, width=target_size[0])
        else:
            video_resized = resize(video, height=target_size[1])
    else:
        video_resized = video

    return CompositeVideoClip(
        [video_resized.set_position(("center", "center"))],
        size=target_size
    ).on_color(color=bg_color, col_opacity=1)


def get_video_files_from_current_dir(valid_exts={".mp4", ".avi", ".wmv"}):
    return [
        f for f in os.listdir(".")
        if os.path.isfile(f) and os.path.splitext(f)[1].lower() in valid_exts
    ]


def generate_output_filename(base_name, extension):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def process_videos_in_current_dir(
    target_size=(640, 640),
    output_dir="processed_videos",
    fps=15,
    bg_color=(0, 0, 0),
):
    os.makedirs(output_dir, exist_ok=True)
    video_files = get_video_files_from_current_dir()

    if not video_files:
        print("No video files found in the current directory.")
        return

    for video_file in video_files:
        try:
            clip = VideoFileClip(video_file)
            processed_clip = resize_and_pad(clip, target_size, bg_color)

            base_name, ext = os.path.splitext(os.path.basename(video_file))
            output_filename = generate_output_filename(base_name, ext)
            output_path = os.path.join(output_dir, output_filename)

            processed_clip.write_videofile(output_path, codec="libx264", fps=fps)
            print(f"Saved processed video: {output_path}")
        except Exception as e:
            print(f"Error processing {video_file}: {e}")


if __name__ == "__main__":
    process_videos_in_current_dir(
        target_size=(640, 640),
        output_dir="processed_videos",
        fps=15,
        bg_color=(0, 0, 0),
    )
