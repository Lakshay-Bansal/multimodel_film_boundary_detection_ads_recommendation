import cv2
import os
import pandas as pd

def cut_clip(video_path, frame_number, output_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    start_frame = max(0, int(frame_number - (30 * fps)))
    end_frame = min(cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1, int(frame_number + (30 * fps)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Change codec to 'mp4v' for MP4 format
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened() and start_frame <= frame_number:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        start_frame += 1

    cap.release()
    out.release()

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_30s_back_scene_clips(movie_name: str):
    # movie_name = "Kung Fu Panda (2008).mp4"
    video_path = os.path.join(os.getcwd(), f'Movie/{movie_name}')
    if not os.path.exists(video_path):
        movie_stem = os.path.splitext(movie_name)[0]
        alt_video = os.path.join(os.getcwd(), f'Movie/{movie_stem}/{movie_name}')
        if os.path.exists(alt_video):
            video_path = alt_video

    fileName = os.path.join(os.getcwd(), f'Movie/{movie_name}.theshold_scenes_final.txt')
    if not os.path.exists(fileName):
        movie_stem = os.path.splitext(movie_name)[0]
        alt_file = os.path.join(os.getcwd(), f'Movie/{movie_stem}/{movie_name}.theshold_scenes_final.txt')
        if os.path.exists(alt_file):
            fileName = alt_file

    df = pd.read_csv(fileName, sep=' ', header=None)
    df.columns = ['start', 'end']

    # Output path where clip is stored
    output_path = os.path.join(os.getcwd(), f'result/{movie_name}_scene_clips')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for clip_num, start_frame in enumerate(df["start"]):
        output_clip_path = os.path.join(output_path, f"{clip_num+1}_{start_frame}.mp4")
        cut_clip(video_path, start_frame, output_clip_path)
