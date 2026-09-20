# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 17:09:21 2024

@author: NH3183
# Generate clips and convert the mp4 to mp3 functions

"""
import os
from moviepy.editor import VideoFileClip
from moviepy.editor import AudioFileClip

def create_clip(input_file, output_file, clip_duration=120):
    try:
        # Load the video file
        video = VideoFileClip(input_file)
        
        # Extract the first 2 minutes (120 seconds)
        clip = video.subclip(0, clip_duration)
        
        # Write the clip to a new file
        clip.write_videofile(output_file, codec="libx264")
        
        print(f"Clip created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Specify the input file path and output file path
# video_path = r"C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\Netflix Poc"
# input_file_path = os.path.join(video_path, "Inception_720p.mp4")  # Replace with your input file path
# output_file_path = os.path.join(video_path, "Inception_720p_2min.mp4")  # Replace with your desired output file path

# # Create the clip
# create_clip(input_file_path, output_file_path)

#%%

from moviepy.editor import *

# Load the mp4 file
movie_name = "Kung Fu Panda (2008).mp4"
movie_name = f"Movie\{movie_name}"
video_path =  os.path.join(os.getcwd(), movie_name)
audio_file_path = movie_name[:-1] + "3" 
# print(audio_file_path)

# input_file_path = video_path
# video = VideoFileClip(input_file_path)

# # Extract audio from video
# video.audio.write_audiofile(audio_file_path)


# Load the MP3 file
clip = AudioFileClip(audio_file_path)

# Write the audio to a WAV file
print(f"{audio_file_path[:-4]}.wav")
clip.write_audiofile(f"{audio_file_path[:-4]}.wav")

# Close the clip
clip.close()
