#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main pipeline runner for Multimodal Film Boundary Detection & Advertisement Recommendation.
Executes the workflow for a single movie file using existing modular logic in src/.
"""

import os
import sys
import argparse

# Add src directory to path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def run(movie_name: str, shot_size: int = 50, threshold: float = 0.7, play: bool = False):
    import pandas as pd
    from threshold_scenes_transnetv2 import generate_threshold_scenes
    from extract_30s_back_clip import generate_30s_back_scene_clips
    from scene_description import generate_scene_desc
    from mapping_scene_with_ads import map_scene_desc_ads

    print("=" * 65)
    print(f"  Processing Movie: {movie_name}")
    print("=" * 65)

    # 1. Scene Boundary Detection
    threshold_file = os.path.join(os.getcwd(), f'Movie/{movie_name}.theshold_scenes_final.txt')
    if not os.path.exists(threshold_file):
        movie_stem = os.path.splitext(movie_name)[0]
        alt = os.path.join(os.getcwd(), f'Movie/{movie_stem}/{movie_name}.theshold_scenes_final.txt')
        if os.path.exists(alt):
            threshold_file = alt

    if not os.path.exists(threshold_file):
        print("\n[Step 1] Detecting scene boundaries from TransNetV2 predictions...")
        generate_threshold_scenes(movie_name, shot_size=shot_size, threshold=threshold)
    else:
        print(f"\n[Step 1] Found existing scene boundary file: {threshold_file}")

    # 2. Extract 30-sec Context Clips
    scene_clips_dir = os.path.join(os.getcwd(), f'result/{movie_name}_scene_clips')
    if not os.path.exists(scene_clips_dir):
        print(f"\n[Step 2] Generating 30s pre-roll scene clips in: {scene_clips_dir}...")
        generate_30s_back_scene_clips(movie_name)
    else:
        print(f"\n[Step 2] Found existing scene clips directory: {scene_clips_dir}")

    # 3. Generate Scene Descriptions via Video-LLaVA
    scene_desc_csv = os.path.join(scene_clips_dir, 'scene_description.csv')
    if not os.path.exists(scene_desc_csv):
        print(f"\n[Step 3] Querying Video-LLaVA to describe scene clips...")
        generate_scene_desc(movie_name)
    else:
        print(f"\n[Step 3] Found existing scene descriptions: {scene_desc_csv}")

    # 4. Map Scenes to Ads via Semantic Similarity
    ads_desc_csv = os.path.join(os.getcwd(), 'Ads/ads_description.csv')
    if not os.path.exists(ads_desc_csv):
        ads_desc_csv = os.path.join(os.getcwd(), 'ads_description.csv')

    print(f"\n[Step 4] Matching scene context with ad inventory...")
    scene_description = pd.read_csv(scene_desc_csv)
    ads_description = pd.read_csv(ads_desc_csv)
    map_ads_idx = map_scene_desc_ads(ads_description["description"], scene_description["description"])

    print("\n" + "-" * 65)
    print("  Scene-to-Ad Mapping Results:")
    print("-" * 65)
    for scene_idx, ad_idx in enumerate(map_ads_idx):
        print(f"  Scene #{scene_idx + 1}  -->  Ad #{ad_idx + 1} ({ads_description['video_path'].iloc[ad_idx]})")
    print("-" * 65)

    # 5. Launch Video Player GUI (Optional)
    if play:
        import tkinter as tk
        from video_player import SimpleVideoPlayer

        print("\n[Step 5] Launching Video Player GUI...")
        scenes_df = pd.read_csv(threshold_file, sep=' ', header=None)
        scene_start_frames = list(scenes_df[0])

        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}")

        player = SimpleVideoPlayer(root, scene_start_frames, scene_description, ads_description)
        root.mainloop()

    print("\nDone! Pipeline execution finished successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Run multimodal boundary detection and ad recommendation for a single movie.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "movie_name",
        type=str,
        nargs="?",
        default="Spiderman 1.mkv",
        help="Target movie filename (e.g. 'Spiderman 1.mkv' or 'Kung Fu Panda (2008).mp4').",
    )
    parser.add_argument(
        "--shot-size",
        type=int,
        default=50,
        help="Minimum shot length in frames.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="TransNetV2 cut probability threshold.",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="Launch the interactive GUI video player after processing.",
    )

    args = parser.parse_args()
    run(
        movie_name=args.movie_name,
        shot_size=args.shot_size,
        threshold=args.threshold,
        play=args.play,
    )


if __name__ == "__main__":
    main()
