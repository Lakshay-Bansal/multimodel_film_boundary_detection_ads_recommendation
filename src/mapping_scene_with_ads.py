#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene-to-Advertisement Semantic Matching Module.
Computes dense sentence embeddings using BAAI/bge-small-en and performs
cosine similarity matching between scene visual descriptions and ad inventory.
"""

import os
import re
from typing import List, Union
import numpy as np
import pandas as pd
import requests
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Global model cache for lazy loading
_TOKENIZER = None
_MODEL = None
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en"


def get_embedding_model():
    """Lazily loads and caches the embedding model and tokenizer."""
    global _TOKENIZER, _MODEL
    if _MODEL is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        _TOKENIZER = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
        _MODEL = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME)
        _MODEL.eval()
    return _TOKENIZER, _MODEL


def get_embeddings(text: Union[str, List[str]]):
    """
    Generates sentence embeddings for input text or list of texts using mean pooling.
    """
    tokenizer, model = get_embedding_model()

    if isinstance(text, str):
        text = [text]

    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling over token embeddings
    embeddings = outputs.last_hidden_state
    sentence_embeddings = embeddings.mean(dim=1)
    return sentence_embeddings


def filter_desc(description_list: List[Union[str, float]]) -> List[str]:
    """
    Cleans descriptions by stripping legacy ASSISTANT prefixes if present,
    and returns sanitized strings.
    """
    filtered = []
    for desc in description_list:
        if isinstance(desc, str):
            match = re.search(r'ASSISTANT:\s*', desc)
            if match:
                filtered.append(desc[match.end():].strip())
            else:
                filtered.append(desc.strip())
        elif pd.notna(desc):
            filtered.append(str(desc).strip())
        else:
            filtered.append("")
    return filtered


def map_scene_desc_ads(all_ads_desc: Union[pd.Series, List[str]], scene_desc: Union[pd.Series, List[str]]) -> np.ndarray:
    """
    Matches each scene description with the most contextually relevant ad
    based on cosine similarity of dense embeddings.

    Returns:
        numpy.ndarray: Array of ad indices corresponding to each scene.
    """
    if hasattr(all_ads_desc, "to_list"):
        all_ads_desc = all_ads_desc.to_list()
    if hasattr(scene_desc, "to_list"):
        scene_desc = scene_desc.to_list()

    all_ads_desc = filter_desc(all_ads_desc)
    scene_desc = filter_desc(scene_desc)

    if not all_ads_desc:
        raise ValueError("Ad descriptions list is empty.")
    if not scene_desc:
        raise ValueError("Scene descriptions list is empty.")

    ad_embeddings = get_embeddings(all_ads_desc)
    scene_embeddings = get_embeddings(scene_desc)

    similarity_matrix = cosine_similarity(ad_embeddings.numpy(), scene_embeddings.numpy())
    map_ads_idx = np.argmax(similarity_matrix, axis=0)

    print(f"Scenes successfully mapped to ad indices: {map_ads_idx.tolist()}")
    return map_ads_idx


def classify_genre(description: str) -> str:
    """
    Optional helper to classify scene or ad genre.
    Falls back gracefully if no classification server is reachable.
    """
    url = os.getenv("CLASSIFY_URL", "http://localhost:8084/classify")
    headers = {"Content-Type": "application/json"}
    data = {"description": description}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            return response.json().get("genre", "General")
    except Exception:
        pass
    return "General"


if __name__ == "__main__":
    # Test execution with sample descriptions
    test_ads = pd.Series([
        "A fast red sports car driving down a high-speed highway at night.",
        "A family enjoying lunch with fresh juice and snacks in a sunny park.",
        "A luxury Swiss wristwatch displayed with elegant diamond styling."
    ])
    test_scenes = pd.Series([
        "A thrilling vehicle chase scene with race cars speeding through streets.",
        "A peaceful picnic scene with friends laughing together outdoors."
    ])

    matched_indices = map_scene_desc_ads(test_ads, test_scenes)
    for s_i, a_i in enumerate(matched_indices):
        print(f"Scene #{s_i+1} matched to Ad #{a_i+1}: '{test_ads.iloc[a_i]}'")
