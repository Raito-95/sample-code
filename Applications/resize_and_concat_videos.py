# -*- coding: utf-8 -*-
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.resize import resize


def resize_and_pad(video, target_size=(640, 640), bg_color=(0, 0, 0)):
    # Determine if resizing is needed
    if video.size[0] > target_size[0] or video.size[1] > target_size[1]:
        # Resize video, keeping aspect ratio
        if video.size[0] / target_size[0] > video.size[1] / target_size[1]:
            video_resized = resize(video, width=target_size[0])
        else:
            video_resized = resize(video, height=target_size[1])
    else:
        video_resized = video

    # Create a black background and overlay the resized video onto it
    video_padded = CompositeVideoClip(
        [video_resized.set_position(("center", "center"))], size=target_size
    ).on_color(color=bg_color, col_opacity=1)

    return video_padded


def process_videos(
    video_files,
    target_size=(640, 640),
    output_file="output.avi",
    fps=15,
    bg_color=(0, 0, 0),
):
    video_clips = []
    for video_file in video_files:
        if not os.path.exists(video_file):
            print(f"Error: File {video_file} does not exist.")
            continue
        try:
            video_clip = VideoFileClip(video_file)
            video_clips.append(resize_and_pad(video_clip, target_size, bg_color))
        except Exception as e:
            print(f"Error processing file {video_file}: {e}")
            continue

    if not video_clips:
        print("No valid video files to process.")
        return

    final_video = concatenate_videoclips(video_clips)

    final_video.write_videofile(output_file, codec="libx264", fps=fps)

    print(f"Video has been successfully created and saved as {output_file}")


# Example usage
video_files = ["test.avi", "test1.avi"]  # Add more video files as needed
process_videos(
    video_files,
    target_size=(450, 450),
    output_file="output.mp4",
    fps=15,
    bg_color=(0, 0, 0),
)
