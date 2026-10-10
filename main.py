#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main pipeline runner for Multimodal Film Boundary Detection & Advertisement Recommendation.
Executes the workflow for a single movie file using modular logic in src/.

Data routing specifications:
- Ad inventory descriptions are always saved & read exclusively from: Ads/ads_description.csv
- Scene descriptions are generated & read from the Movie sub-folder: Movie/<movie_name>/scene_description.csv
"""

import os
import sys
import argparse

# Add src directory to path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def run(
    movie_name: str,
    shot_size: int = 50,
    threshold: float = 0.7,
    play: bool = False,
    model: str = None,
    frames: int = 3,
    force_desc: bool = False
):
    import pandas as pd
    from threshold_scenes_transnetv2 import generate_threshold_scenes
    from extract_30s_back_clip import generate_30s_back_scene_clips
    from scene_description import generate_scene_desc, get_movie_subfolder
    from mapping_scene_with_ads import map_scene_desc_ads

    movie_basename = os.path.basename(movie_name)
    movie_stem = os.path.splitext(movie_basename)[0]
    movie_subfolder = get_movie_subfolder(movie_name)

    print("=" * 65)
    print(f"  Processing Movie: {movie_name}")
    print(f"  Movie Sub-folder: {movie_subfolder}")
    print("=" * 65)

    # 1. Scene Boundary Detection
    threshold_file = os.path.join(movie_subfolder, f'{movie_name}.theshold_scenes_final.txt')
    if not os.path.exists(threshold_file):
        alt = os.path.join(os.getcwd(), f'Movie/{movie_name}.theshold_scenes_final.txt')
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
        alt_clips = os.path.join(movie_subfolder, 'scene_clips')
        if os.path.exists(alt_clips):
            scene_clips_dir = alt_clips

    if not os.path.exists(scene_clips_dir):
        print(f"\n[Step 2] Generating 30s pre-roll scene clips in: {scene_clips_dir}...")
        generate_30s_back_scene_clips(movie_name)
    else:
        print(f"\n[Step 2] Found existing scene clips directory: {scene_clips_dir}")

    # 3. Generate / Read Scene Descriptions from Movie sub-folder
    scene_desc_csv = os.path.join(movie_subfolder, 'scene_description.csv')
    if not os.path.exists(scene_desc_csv) or force_desc:
        print(f"\n[Step 3] Generating scene descriptions in Movie sub-folder: {scene_desc_csv}...")
        generate_scene_desc(movie_name, model_name=model, num_frames=frames, force=force_desc)
    else:
        print(f"\n[Step 3] Found existing scene descriptions in Movie sub-folder: {scene_desc_csv}")

    # 4. Map Scenes to Ads via Semantic Similarity
    # Always refer to Ads folder for ad descriptions
    ads_desc_csv = os.path.join(os.getcwd(), 'Ads', 'ads_description.csv')

    # If Ads/ads_description.csv does not exist, generate it
    if not os.path.exists(ads_desc_csv):
        print(f"\n[Step 4a] Ads/ads_description.csv not found. Generating ad descriptions into Ads/...")
        try:
            from ads_description import generate_ads_desc
            generate_ads_desc(model_name=model, num_frames=frames)
        except Exception as e:
            print(f"  [Warning] Could not automatically generate ads descriptions: {e}")

    if not os.path.exists(ads_desc_csv):
        raise FileNotFoundError(f"Missing ad descriptions file at: {ads_desc_csv}")

    print(f"\n[Step 4] Matching scene context with ad inventory...")
    print(f"  Scene descriptions read from: {scene_desc_csv}")
    print(f"  Ad descriptions read from:    {ads_desc_csv}")

    scene_description = pd.read_csv(scene_desc_csv)
    ads_description = pd.read_csv(ads_desc_csv)
    map_ads_idx = map_scene_desc_ads(ads_description["description"], scene_description["description"])

    print("\n" + "-" * 65)
    print("  Scene-to-Ad Mapping Results:")
    print("-" * 65)
    for scene_idx, ad_idx in enumerate(map_ads_idx):
        ad_path = ads_description['video_path'].iloc[ad_idx] if 'video_path' in ads_description.columns else f"Ad #{ad_idx+1}"
        print(f"  Scene #{scene_idx + 1}  -->  Ad #{ad_idx + 1} ({ad_path})")
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
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Hugging Face model ID for video captioning (default from HF_MODEL in .env).",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=3,
        help="Number of keyframes to extract per scene clip.",
    )
    parser.add_argument(
        "--force-desc",
        action="store_true",
        help="Re-generate scene descriptions even if already existing in Movie sub-folder.",
    )

    args = parser.parse_args()
    run(
        movie_name=args.movie_name,
        shot_size=args.shot_size,
        threshold=args.threshold,
        play=args.play,
        model=args.model,
        frames=args.frames,
        force_desc=args.force_desc,
    )


if __name__ == "__main__":
    main()
