"""
Multimodal Film Boundary Detection & Advertisement Recommendation - Source Package
"""

from .hf_video_captioning import describe_video, extract_keyframes_from_video
from .scene_description import generate_scene_desc
from .mapping_scene_with_ads import map_scene_desc_ads, get_embeddings
from .threshold_scenes_transnetv2 import generate_threshold_scenes
from .extract_30s_back_clip import generate_30s_back_scene_clips
from .utils import frame_to_time, timestamp_to_frame_number

__all__ = [
    "describe_video",
    "extract_keyframes_from_video",
    "generate_scene_desc",
    "map_scene_desc_ads",
    "get_embeddings",
    "generate_threshold_scenes",
    "generate_30s_back_scene_clips",
    "frame_to_time",
    "timestamp_to_frame_number",
]
