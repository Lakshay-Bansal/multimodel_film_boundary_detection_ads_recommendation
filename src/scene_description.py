import os
import glob
import requests
import pandas as pd
import tqdm as tqdm

def read_scene(video_path):
    with open(video_path, 'rb') as video_file:
        # Define the files to be uploaded
        files = {'video': video_file}
        # Send the POST request
        response = requests.post(url, files=files)
    return response.json()['description']

url = 'http://localhost/describe_video'

def generate_scene_desc(movie_name: str):
    # movie_name = "Kung Fu Panda (2008).mp4"
    # Output will be saved in ./result/{movie_name}_scene_clips path
    # Path for reading video clips
    scene_dir = os.path.join(os.getcwd(), f'result/{movie_name}_scene_clips')
    file_pattern = os.path.join(scene_dir, '**', '*.mp4')
    scene_files_path = glob.glob(file_pattern, recursive=True)

    # Save a scene description to a file
    save_scene_description_path = os.path.join(os.getcwd(), f'result/{movie_name}_scene_clips/scene_description.csv')

    data = []

    # for idx, file_path in tqdm(enumerate(list(scene_files_path)), total=len(scene_files_path), desc="Processing files"):
    for idx, file_path in enumerate(scene_files_path):    
        if os.path.isfile(file_path):
            scene_desciption = read_scene(file_path)
            print(f"Scene {idx+1} - Path: {file_path} - {scene_desciption}")
            new_entry = {'video_path': str(file_path), 'description': scene_desciption}
            data.append(new_entry)

    
    df = pd.DataFrame(data, columns=['video_path', 'description'])
    print(f"Stored a description for {df.shape[0]}")
    df.to_csv(save_scene_description_path, index=False)