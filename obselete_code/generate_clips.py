import moviepy.editor as mp
import os

def read_frames_from_file(txt_file_path):
    frames = []
    with open(txt_file_path, 'r') as file:
        for line in file:
            start_end = line.strip().split()
            if len(start_end) == 2:
                start_frame, end_frame = map(int, start_end)
                frames.append((start_frame, end_frame))
    return frames

def generate_clips(video_file_path, frames, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    video = mp.VideoFileClip(video_file_path)
    fps = video.fps

    for i, (start_frame, end_frame) in enumerate(frames):
        start_time = start_frame / fps
        end_time = end_frame / fps
        clip = video.subclip(start_time, end_time)
        output_path = os.path.join(output_dir, f'clip_{i+1}.mp4')
        clip.write_videofile(output_path, codec='libx264')

# Example usage
folder = r'C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\TransNetV2\inference'
movie_name = 'Inception_720p_2min'
video_file_path = os.path.join(folder, f'{movie_name}.mp4')
txt_file_path = os.path.join(folder, f'{movie_name}.mp4.scenes.txt')
output_dir = os.path.join(folder, f'Clips_{movie_name}')
if not os.path.exists(output_dir):
        os.makedirs(output_dir)

frames = read_frames_from_file(txt_file_path)
print(frames)
generate_clips(video_file_path, frames, output_dir)

