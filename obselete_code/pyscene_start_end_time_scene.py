from moviepy.editor import VideoFileClip
import scenedetect
from scenedetect import VideoManager, SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import AdaptiveDetector
from scenedetect.video_splitter import split_video_ffmpeg
from scenedetect.frame_timecode import FrameTimecode
import json

def calculate_time_ranges(video_path, start_offset=25, end_offset = 30):
    video = VideoFileClip(video_path)
    
    # Get the total duration of the video in seconds
    duration = video.duration
    # print(duration)
    
    # Convert 25 minutes and 30 minutes to seconds
    start_offset = start_offset * 60
    end_offset = end_offset * 60
    
    # Calculate start and end times
    start_time = start_offset
    end_time = duration - end_offset
    
    # Ensure the start and end times are within the video duration
    if start_time < 0:
        start_time = 0
    if end_time > duration:
        end_time = duration
    
    # Convert times from seconds to HH:MM:SS format
    start_time_formatted = format_time(start_time)
    end_time_formatted = format_time(end_time)

    print(f"Start time: {start_time_formatted}")
    print(f"End time: {end_time_formatted}")
    
    return start_time_formatted, end_time_formatted

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# video_path = r"C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\Netflix Poc\Inception_720p.mp4"
# start_time, end_time = calculate_time_ranges(video_path)
# print(f"Start time: {start_time}")
# print(f"End time: {end_time}")

from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def detect_and_split_scenes(video_path, start_time, end_time, frame_skip, min_scene_len, frame_window):
    # Create a video manager for the video file
    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    fps=video_manager.get_framerate()
    
    # Set the start and end times for the video manager
    start_time_s = FrameTimecode(timecode=start_time, fps=video_manager.get_framerate()).get_seconds()
    end_time_s = FrameTimecode(timecode=end_time, fps=video_manager.get_framerate()).get_seconds()
    
    # Set the scene manager and add the adaptive scene detector
    scene_manager.add_detector(AdaptiveDetector(min_scene_len=min_scene_len, window_width=frame_window))
    
    # Set downscale factor to 3 and start the video manager
    video_manager.set_downscale_factor(frame_skip)
    video_manager.start()

    # Seek the video to the start time
    start_frame = FrameTimecode(timecode=start_time, fps=video_manager.get_framerate())
    video_manager.seek(start_frame)
    
    # Perform scene detection
    scene_manager.detect_scenes(frame_source=video_manager)
    
    # Obtain list of detected scenes
    scene_list = scene_manager.get_scene_list()
    
    # Filter scenes to only include those within the start and end time
    filtered_scene_list = [(scene[0], scene[1]) for scene in scene_list if scene[0].get_seconds() >= start_time_s and scene[1].get_seconds() <= end_time_s]

    print(f"Detected {len(filtered_scene_list)} scenes.")

    # Get the frame numbers for each scene
    frame_ranges = [(scene[0].get_frames(), scene[1].get_frames()) for scene in filtered_scene_list]
    
    # split_times = {0: ['00:25:00', 35964], 1: ['00:40:59', 58972], 2: ['00:57:09', 82222], 3: ['01:13:10', 105275], 4: ['01:29:20', 128532]}
    # Print the frame ranges
    for i, (start_frame, end_frame) in enumerate(frame_ranges):
        print(f"Scene {i+1}: Start Frame = {format_time(start_frame/fps)}, End Frame = {format_time(end_frame/fps)}")
        split_times[i] = [format_time(start_frame/fps), start_frame]
    
    print(split_times)
    # Save the split_scene json
    # Save the dictionary as a JSON file
    current_path = os.path.dirname(os.path.abspath(__file__))
    split_times_fileName = f"{os.path.basename(video_path)}_split_scene.json"
    
    split_times_file_path = os.path.join(current_path, split_times_fileName)

    with open(split_times_file_path, 'w') as json_file:
        json.dump(split_times, json_file, indent=4)

    print(f"Dictionary saved to {split_times_file_path}")
    
    # Split video into scenes using FFmpeg
    # split_video_ffmpeg(video_path, scene_list, output_dir='output_scenes')

    # video_manager.release()

# Example usage
video_path = r"C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\Netflix Poc\Inception_720p.mp4"
start_time, end_time = calculate_time_ranges(video_path)
frame_skip = 3          # Skipping three frames - It increases the processing speed
min_scene_len = 23000   # Equivalent to atleast 16 min clip
frame_window = 5        # To match the content in 5 frames

detect_and_split_scenes(video_path, start_time, end_time, frame_skip, min_scene_len, frame_window)
