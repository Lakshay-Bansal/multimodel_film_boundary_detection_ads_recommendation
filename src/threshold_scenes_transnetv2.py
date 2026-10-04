# from utils import frame_to_time

# print(frame_to_time(1290, 25))
import os
import numpy as np
import pandas as pd
from utils import frame_to_time

def predictions_to_scenes(predictions: np.ndarray, shot_size: int = 50, threshold: float = 0.7):
    # shot_size define the minimum number of frame between start and end of frame for a detected shot

        predictions = (predictions > threshold).astype(np.uint8)

        scenes = []
        scenes_timestamp = []
        t, t_prev, start = -1, 0, 0
        for i, t in enumerate(predictions):
            if t_prev == 1 and t == 0:
                start = i
            if t_prev == 0 and t == 1 and i != 0:
                # fps = 24, hence frame difference > 2880 will means for a 2 min continuous scene atleast
                # 43164 = 30 min as ads need to be inserted after that time
                # end i should be less than len(predictions) - 43164
                if int(i-start) >  shot_size and start > 43164 and i < int(len(predictions) - 43164):
                    scenes.append([start, i])
                    scenes_timestamp.append([start, i, str(frame_to_time(start, fps=23.98)), str(frame_to_time(i, fps=23.98))])
                # scenes.append([start, i])
            t_prev = t
        if t == 0:
            if int(i-start) >  2880 and start > 43164 and i < int(len(predictions) - 43164):
                scenes.append([start, i])
                scenes_timestamp.append([start, i, str(frame_to_time(start, fps=23.98)), str(frame_to_time(i, fps=23.98))])
            # scenes.append([start, i])

        # just fix if all predictions are 1
        if len(scenes) == 0:
            return np.array([[0, len(predictions) - 1]], dtype=np.int32)
    
        return np.array(scenes, dtype=np.int32), np.array(scenes_timestamp)


def generate_threshold_scenes(movie_name: str, shot_size: int = 50, threshold: float = 0.7):
    fileName = os.path.join(os.getcwd(), f'Movie/{movie_name}.predictions.txt')
    if not os.path.exists(fileName):
        movie_stem = os.path.splitext(movie_name)[0]
        alt = os.path.join(os.getcwd(), f'Movie/{movie_stem}/{movie_name}.predictions.txt')
        if os.path.exists(alt):
            fileName = alt

    df = pd.read_csv(fileName, sep=' ', header=None)
    df.columns = ['frame_pred', 'all_frame_pred']

    scenes, scenes_timestamp = predictions_to_scenes(df['frame_pred'], shot_size=shot_size, threshold=threshold)
    print("Number of detected scene", len(scenes))
    out_fileName = os.path.join(os.getcwd(), f'Movie/{movie_name}')
    np.savetxt(out_fileName + ".theshold_scenes.txt", scenes, fmt="%d")
    np.savetxt(out_fileName + ".theshold_scenes_final.txt", scenes, fmt="%d")
    pd.DataFrame(scenes_timestamp).to_csv(out_fileName + ".theshold_scenes_timestamp.txt")
    return scenes


if __name__ == "__main__":
    movie_name = "Spiderman 1.mkv"
    generate_threshold_scenes(movie_name)