#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene Description Module.
Generates multimodal visual and narrative descriptions for candidate scene clips
using Hugging Face Serverless Inference API (or legacy hosted Video-LLaVA fallback).
Saves and reads scene descriptions from the Movie sub-folder of the given movie name
(e.g., Movie/<movie_name>/scene_description.csv).
"""

import os
import sys
import glob
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

# Ensure src/ is importable
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from hf_video_captioning import describe_video

load_dotenv()

# Legacy URL fallback if user has hosted microservice
DEFAULT_HOSTED_URL = os.getenv("VIDEO_LLAVA_URL", "http://localhost/describe_video")


def read_scene(video_path: str, model_name: str = None, num_frames: int = None) -> str:
    """
    Generates description for a single scene clip using Hugging Face free models
    (with fallback to hosted microservice if configured).
    """
    return describe_video(
        video_path=video_path,
        model_name=model_name,
        num_frames=num_frames,
        hosted_url=DEFAULT_HOSTED_URL if os.getenv("VIDEO_LLAVA_URL") else None
    )


def get_movie_subfolder(movie_name: str) -> str:
    """
    Resolves the movie subfolder under Movie/ for a given movie filename or path.
    Example: 'Spiderman 1.mkv' -> 'Movie/Spiderman 1'
    """
    movie_stem = os.path.splitext(os.path.basename(movie_name))[0]
    return os.path.join(os.getcwd(), "Movie", movie_stem)


def generate_scene_desc(
    movie_name: str,
    model_name: str = None,
    num_frames: int = None,
    force: bool = False
) -> pd.DataFrame:
    """
    Scans scene clips for a movie, generates multimodal scene descriptions,
    and saves scene_description.csv in the Movie sub-folder of the movie name
    (e.g., Movie/<movie_name>/scene_description.csv).
    """
    movie_stem = os.path.splitext(os.path.basename(movie_name))[0]
    movie_subfolder = get_movie_subfolder(movie_name)
    os.makedirs(movie_subfolder, exist_ok=True)

    save_scene_description_path = os.path.join(movie_subfolder, "scene_description.csv")

    # If already generated in Movie sub-folder, read and return
    if os.path.exists(save_scene_description_path) and not force:
        print(f"Reading existing scene descriptions from Movie sub-folder: {save_scene_description_path}")
        return pd.read_csv(save_scene_description_path)

    # Locate directory containing scene clips
    candidate_clip_dirs = [
        os.path.join(os.getcwd(), f"result/{movie_name}_scene_clips"),
        os.path.join(os.getcwd(), f"result/{movie_stem}_scene_clips"),
        os.path.join(movie_subfolder, "scene_clips"),
        movie_subfolder,
    ]

    scene_files = []
    found_clip_dir = None
    for c_dir in candidate_clip_dirs:
        if os.path.exists(c_dir):
            files = sorted(glob.glob(os.path.join(c_dir, "*.mp4")))
            if files:
                scene_files = files
                found_clip_dir = c_dir
                break

    if not scene_files:
        raise FileNotFoundError(
            f"No .mp4 scene clips found in candidate directories: {candidate_clip_dirs}\n"
            f"Please run Step 2 (extract_30s_back_clip.py) first to generate context clips."
        )

    print(f"\n[Scene Captioning] Found {len(scene_files)} scene clip(s) in: {found_clip_dir}")
    print(f"[Scene Captioning] Target save location: {save_scene_description_path}")
    data = []

    for idx, file_path in enumerate(tqdm(scene_files, desc=f"Captioning '{movie_stem}' clips")):
        try:
            scene_desc = read_scene(file_path, model_name=model_name, num_frames=num_frames)
            tqdm.write(f"  Clip #{idx+1} ({os.path.basename(file_path)}): {scene_desc}")
            data.append({"video_path": str(file_path), "description": scene_desc})
        except Exception as e:
            tqdm.write(f"  [Warning] Failed to describe clip #{idx+1} ({file_path}): {e}")
            data.append({"video_path": str(file_path), "description": f"Scene context clip #{idx+1}."})

    df = pd.DataFrame(data, columns=["video_path", "description"])
    df.to_csv(save_scene_description_path, index=False)
    print(f"[Success] Saved {df.shape[0]} scene descriptions to: {save_scene_description_path}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate multimodal descriptions for scene clips.")
    parser.add_argument("movie_name", type=str, nargs="?", default="Spiderman 1.mkv", help="Movie filename")
    parser.add_argument("--model", type=str, default=None, help="Hugging Face model ID")
    parser.add_argument("--frames", type=int, default=3, help="Number of keyframes to sample per clip")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scene_description.csv")
    args = parser.parse_args()

    generate_scene_desc(
        movie_name=args.movie_name,
        model_name=args.model,
        num_frames=args.frames,
        force=args.force
    )