from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import json


def extract_clip(video_path, time_str, output_path):
    # Convert the input time string (HH:MM:SS) to seconds
    time_parts = list(map(int, time_str.split(':')))
    total_seconds = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]

    # Calculate the start time for the clip (30 seconds prior to the given time)
    clip_start_time = total_seconds - 30
    if clip_start_time < 0:
        raise ValueError("The input time is less than 30 seconds from the start of the video.")

    # Extract the clip using moviepy
    with VideoFileClip(video_path) as video:
        clip = video.subclip(clip_start_time, total_seconds)
        clip.write_videofile(output_path, codec='libx264')

    print(f"Clip saved to {output_path}")


if __name__=='__main__':
    video_file_path = video_path = r".\Movie\Inception_720p.mp4"
    current_path = os.path.dirname(os.path.abspath(__file__))
    clips_path = os.path.join(current_path, f"{os.path.basename(video_file_path)}_clips")
    os.makedirs(clips_path, exist_ok=True)

    # Load scene cuts time
    split_times_fileName = f"{os.path.basename(video_file_path)}_split_scene.json"
    with open(split_times_fileName, 'r') as json_file:
        scene_cut_time = json.load(json_file)

    for idx, (key, val) in enumerate(scene_cut_time.items()):
        extract_clip(video_file_path, val[0], os.path.join(clips_path, f"{idx}.mp4"))
