from moviepy.editor import VideoFileClip
import requests
import os
from transformers import pipeline
import re
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



def classify_genre(description):
    url = 'http://localhost:8084/classify'
    headers = {'Content-Type': 'application/json'}
    data = {'description': description}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['genre']
    else:
        raise Exception(f'Error: {response.status_code}')

# Example usage
# description = 'A new tech startup has been launched.'
# result = classify_genre(description)
# print(result)

# Load the tokenizer and model
model_name = "BAAI/bge-small-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)

    # Get the model output
    with torch.no_grad():
        outputs = model(**inputs)

    # The embeddings are typically the output of the last hidden state
    embeddings = outputs.last_hidden_state
    sentence_embeddings = embeddings.mean(dim=1)

    return sentence_embeddings

def filter_desc(descrption: list):
  desc_filetered = []
  for desc in descrption:
    if isinstance(desc, str):
        desc_filetered.append(desc[re.search(r'ASSISTANT: ',desc).end():])
  return desc_filetered

def map_scene_desc_ads(all_ads_desc, scene_desc):
    all_ads_desc = all_ads_desc.to_list()
    scene_desc = scene_desc.to_list()

    # Filtering the unwanted text from text desciption till Assistant keyword
    # all_ads_desc = filter_desc(all_ads_desc)
    scene_desc = filter_desc(scene_desc)

    ad_embeddings = get_embeddings(all_ads_desc)
    scene_embeddings = get_embeddings(scene_desc)

    map_ads_idx = np.argmax(cosine_similarity(ad_embeddings,scene_embeddings),axis = 0)
    print(f"Scene are mapped to ads {map_ads_idx} idx")
    return map_ads_idx


