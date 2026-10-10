#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ad Description Generator.
Generates multimodal visual and narrative descriptions for candidate advertisement videos
using Hugging Face Serverless Inference API (or legacy hosted Video-LLaVA fallback).
Saves output ONLY to the Ads/ folder (Ads/ads_description.csv).
"""

import os
import sys
import glob
import re
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

# Ensure src/ is importable
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from hf_video_captioning import describe_video

load_dotenv()

DEFAULT_HOSTED_URL = os.getenv("VIDEO_LLAVA_URL", "http://[IP_ADDRESS]/describe_video")


def read_ads(video_path: str, model_name: str = None, num_frames: int = None) -> str:
    """
    Generates description for a single ad video file using Hugging Face free models.
    """
    try:
        desc = describe_video(
            video_path=video_path,
            model_name=model_name,
            num_frames=num_frames,
            hosted_url=DEFAULT_HOSTED_URL if os.getenv("VIDEO_LLAVA_URL") else None
        )
        # Strip legacy ASSISTANT tag if present in older microservice responses
        match = re.search(r'ASSISTANT:\s*', desc)
        if match:
            desc = desc[match.end():].strip()
        return desc
    except Exception as e:
        print(f"  [Error] Failed to describe {video_path}: {e}")
        return "error"


def generate_ads_desc(
    ads_dir: str = None,
    model_name: str = None,
    num_frames: int = None,
    force: bool = False
) -> pd.DataFrame:
    """
    Scans ad directories for video files, generates multimodal descriptions,
    and saves ads_description.csv ONLY in the Ads/ folder.
    """
    # Candidate ad directories in order of preference
    candidate_dirs = []
    if ads_dir:
        candidate_dirs.append(ads_dir)
    candidate_dirs.extend([
        os.path.join(os.getcwd(), "Ads"),
        os.path.join(os.getcwd(), "Movie", "Ads"),
    ])

    ads_files_path = []
    for c_dir in candidate_dirs:
        if os.path.exists(c_dir):
            found = glob.glob(os.path.join(c_dir, "**", "*.mp4"), recursive=True)
            if found:
                ads_files_path.extend(found)

    # Deduplicate video paths
    ads_files_path = sorted(list(set(ads_files_path)))

    # Save ONLY to Ads/ads_description.csv
    ads_save_path = os.path.join(os.getcwd(), "Ads", "ads_description.csv")

    if os.path.exists(ads_save_path) and not force and not ads_files_path:
        print(f"Found existing ads description file: {ads_save_path}")
        return pd.read_csv(ads_save_path)

    if not ads_files_path:
        if os.path.exists(ads_save_path):
            print(f"No new video files found to process, loaded existing: {ads_save_path}")
            return pd.read_csv(ads_save_path)
        raise FileNotFoundError(
            f"No advertisement video files (.mp4) found in candidate directories: {candidate_dirs}"
        )

    print(f"\n[Ad Captioning] Discovered {len(ads_files_path)} ad video(s) to process...")
    data = []

    for idx, file_path in enumerate(tqdm(ads_files_path, desc="Processing Ads")):
        if os.path.isfile(file_path):
            ads_description = read_ads(file_path, model_name=model_name, num_frames=num_frames)
            if ads_description == "error":
                continue
            tqdm.write(f"  Ad #{idx+1} ({os.path.basename(file_path)}): {ads_description}")
            data.append({"video_path": str(file_path), "description": ads_description})

    df = pd.DataFrame(data, columns=["video_path", "description"])
    print(f"\nSuccessfully generated descriptions for {df.shape[0]} advertisements.")

    # Save strictly to Ads folder
    os.makedirs(os.path.dirname(os.path.abspath(ads_save_path)), exist_ok=True)
    df.to_csv(ads_save_path, index=False)
    print(f"  Saved ads description exclusively to: {ads_save_path}")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate multimodal descriptions for ad videos.")
    parser.add_argument("--ads-dir", type=str, default=None, help="Directory containing ad videos")
    parser.add_argument("--model", type=str, default=None, help="Hugging Face model ID")
    parser.add_argument("--frames", type=int, default=3, help="Keyframes to sample per ad")
    parser.add_argument("--force", action="store_true", help="Overwrite existing descriptions")
    args = parser.parse_args()

    generate_ads_desc(
        ads_dir=args.ads_dir,
        model_name=args.model,
        num_frames=args.frames,
        force=args.force
    )