#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugging Face-based Video Captioning and Multimodal Description Module.
Extracts representative keyframes from video files and uses free Hugging Face
Serverless Inference API models (such as Salesforce/blip-image-captioning-large)
to generate rich natural language descriptions without requiring self-hosted servers.
"""

import os
import time
import json
import re
from typing import List, Optional
import cv2
import requests
from dotenv import load_dotenv

# Automatically load environment variables from .env
load_dotenv()

DEFAULT_HF_MODEL = os.getenv("HF_MODEL", "Salesforce/blip-image-captioning-large")
ROUTER_API_URL = "https://router.huggingface.co/hf-inference/models/{model_id}"
LEGACY_API_URL = "https://api-inference.huggingface.co/models/{model_id}"


def get_hf_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Hugging Face API key from argument or environment variables."""
    if api_key:
        return api_key.strip()
    for env_var in ("HUGGINGFACE_API_KEY", "HF_TOKEN", "HF_API_KEY"):
        val = os.getenv(env_var)
        if val and val.strip():
            return val.strip()
    return None


def extract_keyframes_from_video(
    video_path: str,
    num_frames: int = 3,
    max_dimension: int = 1024,
    jpeg_quality: int = 85
) -> List[bytes]:
    """
    Extracts representative keyframes evenly spaced across the video duration.
    Returns a list of JPEG-encoded byte arrays.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"OpenCV could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        raise ValueError(f"Video file has 0 frames or invalid stream: {video_path}")

    # Determine frame indices
    if num_frames <= 1:
        frame_indices = [total_frames // 2]
    else:
        step = total_frames / (num_frames + 1)
        frame_indices = [max(0, min(total_frames - 1, int(step * (i + 1)))) for i in range(num_frames)]

    frame_bytes_list: List[bytes] = []

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        # Resize if dimensions exceed max_dimension to keep request fast and within payload limits
        h, w = frame.shape[:2]
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        success, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        if success:
            frame_bytes_list.append(encoded.tobytes())

    cap.release()

    if not frame_bytes_list:
        raise RuntimeError(f"Failed to extract any readable frames from video: {video_path}")

    return frame_bytes_list


def query_hf_image_caption(
    image_bytes: bytes,
    api_key: str,
    model_name: str = DEFAULT_HF_MODEL,
    max_retries: int = 4
) -> str:
    """
    Queries Hugging Face Serverless Inference API for an image caption.
    Handles model cold-starts (HTTP 503) and API rate limits automatically.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "x-wait-for-model": "true"
    }

    endpoints = [
        ROUTER_API_URL.format(model_id=model_name),
        LEGACY_API_URL.format(model_id=model_name)
    ]

    last_error = None

    for endpoint in endpoints:
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, headers=headers, data=image_bytes, timeout=60)

                # Cold-start handling: Hugging Face models spin up on demand
                if response.status_code == 503:
                    try:
                        err_info = response.json()
                        estimated_time = float(err_info.get("estimated_time", 15.0))
                    except Exception:
                        estimated_time = 15.0
                    wait_sec = min(30.0, max(5.0, estimated_time))
                    print(f"    [HF Model Loading] Waiting {wait_sec:.1f}s for '{model_name}' to initialize...")
                    time.sleep(wait_sec)
                    continue

                # Rate limit handling
                if response.status_code == 429:
                    wait_sec = 5.0 * (attempt + 1)
                    print(f"    [HF Rate Limit] Backing off {wait_sec:.1f}s...")
                    time.sleep(wait_sec)
                    continue

                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                        return data[0]["generated_text"].strip()
                    elif isinstance(data, dict) and "generated_text" in data:
                        return data["generated_text"].strip()
                    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                        return data[0].strip()
                    elif isinstance(data, str):
                        return data.strip()
                    else:
                        return str(data)

                # If 404 or 410 on this endpoint, break and try alternative endpoint
                if response.status_code in (404, 410):
                    last_error = f"HTTP {response.status_code} at {endpoint}"
                    break

                last_error = f"HTTP {response.status_code}: {response.text}"

            except requests.RequestException as e:
                last_error = str(e)
                time.sleep(2.0)

    raise RuntimeError(f"Hugging Face Inference API failed for model '{model_name}': {last_error}")


def synthesize_frame_captions(captions: List[str]) -> str:
    """
    Synthesizes multiple frame-level captions into a cohesive video scene description.
    """
    cleaned: List[str] = []
    seen = set()

    for c in captions:
        c_clean = c.strip().rstrip(".")
        if c_clean and c_clean.lower() not in seen:
            seen.add(c_clean.lower())
            cleaned.append(c_clean)

    if not cleaned:
        return "The video displays a movie scene."

    if len(cleaned) == 1:
        desc = f"The video shows {cleaned[0]}."
    elif len(cleaned) == 2:
        desc = f"The video begins with {cleaned[0]}. Later in the scene, it shows {cleaned[1]}."
    else:
        desc = (
            f"The video starts with {cleaned[0]}. "
            f"As the scene progresses, {cleaned[1]}. "
            f"Towards the conclusion, it displays {cleaned[2]}."
        )

    # Normalize punctuation and casing
    desc = desc.strip()
    if desc and not desc.endswith("."):
        desc += "."
    return desc


def describe_video(
    video_path: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    num_frames: Optional[int] = None,
    hosted_url: Optional[str] = None
) -> str:
    """
    Generates a natural language description for a given video file.

    Priority:
    1. If HUGGINGFACE_API_KEY is available: extracts keyframes and queries free Hugging Face model.
    2. Fallback: If a legacy hosted URL (like self-hosted Video-LLaVA) is provided/configured, calls it.
    """
    hf_key = get_hf_api_key(api_key)
    target_model = model_name or os.getenv("HF_MODEL", DEFAULT_HF_MODEL)

    if num_frames is None:
        try:
            num_frames = int(os.getenv("HF_NUM_FRAMES", "3"))
        except ValueError:
            num_frames = 3

    # Check for legacy hosted microservice fallback if no HF key is present
    url = hosted_url or os.getenv("VIDEO_LLAVA_URL")
    if not hf_key and url:
        print(f"  [Fallback] No Hugging Face API key found, querying legacy hosted URL: {url}")
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            resp = requests.post(url, files=files, timeout=120)
            data = resp.json()
            return data.get("description", str(data))

    if not hf_key:
        raise ValueError(
            "Hugging Face API key is missing!\n"
            "Please obtain a free API token from https://huggingface.co/settings/tokens\n"
            "and add it to your .env file:\n"
            "    HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxx\n"
            "or set the HUGGINGFACE_API_KEY environment variable."
        )

    # Extract keyframes and query Hugging Face Inference API
    keyframes = extract_keyframes_from_video(video_path, num_frames=num_frames)
    frame_captions: List[str] = []

    for i, img_bytes in enumerate(keyframes):
        caption = query_hf_image_caption(
            image_bytes=img_bytes,
            api_key=hf_key,
            model_name=target_model
        )
        frame_captions.append(caption)

    description = synthesize_frame_captions(frame_captions)
    return description
