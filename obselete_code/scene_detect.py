# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 17:24:35 2024

@author: NH3183
"""

from scenedetect import detect, AdaptiveDetector
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import math
import os

video_path = r"C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\Netflix Poc"
input_file_path = os.path.join(video_path, "Inception_720p_2min.mp4")  # Replace with your input file path
 
video_local_path = input_file_path



content_list = detect(video_local_path, AdaptiveDetector())

#%%

video = cv2.VideoCapture(video_local_path)

def get_frame(scene):
    frame_id = (scene[1] - scene[0]).frame_num // 2 + scene[0].frame_num
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
    _, frame = video.read()
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

frame_display_per_row = 5
frame_display_rows = math.ceil(len(content_list) / frame_display_per_row)

frames = []

plt.figure(figsize=(60, 60))
for i, scene in enumerate(content_list):
    frame = get_frame(scene)
    frames.append(frame)
    plt.subplot(frame_display_rows, frame_display_per_row, i+1)
    plt.imshow(frame)
    plt.title(f"scene {i+1}\n{scene[0].get_timecode()}--{scene[1].get_timecode()}", fontsize=50)
    plt.xticks([])
    plt.yticks([])

plt.tight_layout()

save_folder = os.path.join(video_path, "frames")
os.makedirs(save_folder, exist_ok=True)

for i, frame in enumerate(frames):
    frame.save(f"{save_folder}/scene{i+1}.jpg")



