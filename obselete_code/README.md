# Obsolete & Experimental Codebase

This directory contains legacy prototypes, proof-of-concept (PoC) scripts, and early experiments developed during the initial phases of the **Multimodal Film Boundary Detection & Advertisement Recommendation** project.

---

## 📌 Overview of the Codebase

The goal of the overarching project is to:
1. Detect natural film break points and scene transitions suitable for ad insertion.
2. Extract scene clips leading up to candidate ad break locations.
3. Automatically describe scene and advertisement content using multimodal vision-language models (e.g., Video-LLaVA, LLaMA).
4. Contextually match and recommend the most relevant advertisements to detected film scenes using text embeddings and cosine similarity.

Before converging on the standardized pipeline now organized at the repository root, these scripts served as iterative experiments across:
- **Rule-based & Adaptive Scene Detection** (using `PySceneDetect` and frame analysis).
- **Video & Audio Processing / Trimming** (using `MoviePy` and `OpenCV`).
- **Multimodal Video Captioning API Integration** (connecting to a hosted Video-LLaVA service).
- **Text Generation & Semantic Ad Matching Exploration** (testing local and cloud LLMs like Hugging Face LLaMA-3 and Ollama).

---

## 📂 File Breakdown & Functionality

### 1. Scene Detection & Boundary Extraction

#### [`scene_detect.py`](./scene_detect.py)
- **Purpose**: Rapid PoC for adaptive scene transition detection and keyframe visualization.
- **Workflow**:
  - Uses `scenedetect.detect` with `AdaptiveDetector` on sample video files (e.g., `Inception_720p_2min.mp4`).
  - Uses OpenCV (`cv2.VideoCapture`) to compute the midpoint frame of each detected scene.
  - Generates a visual contact sheet grid using `matplotlib.pyplot` showing start/end timestamps.
  - Extracts and saves individual scene keyframe images to a `frames/` directory.

#### [`pyscene_start_end_time_scene.py`](./pyscene_start_end_time_scene.py)
- **Purpose**: Structured boundary detection over long videos with exclusion buffers.
- **Workflow**:
  - Defines an offset window (ignoring initial ~25 minutes and trailing ~30 minutes of a movie to avoid intro/credits).
  - Configures `VideoManager`, `StatsManager`, and `SceneManager` with `AdaptiveDetector` (frame skipping, minimum scene length thresholds).
  - Outputs detected scene boundary timestamps and frame indices into a JSON file (`<video_name>_split_scene.json`).
  - *Superseded by*: The neural TransNetV2-based detection pipeline in the project root (`threshold_scenes_transnetv2.py`).

---

### 2. Video Clipping & Audio Preparation

#### [`extract_clip.py`](./extract_clip.py)
- **Purpose**: Generates context clips leading up to candidate break timestamps.
- **Workflow**:
  - Reads timestamp cut points from the JSON split file produced by `pyscene_start_end_time_scene.py`.
  - For each cut point, extracts the preceding 30-second subclip (`[t - 30s, t]`) using `moviepy.video.io.VideoFileClip`.
  - Saves the resulting MP4 clips into an output directory for multimodal description.
  - *Superseded by*: [`../extract_30s_back_clip.py`](../extract_30s_back_clip.py).

#### [`generate_clips.py`](./generate_clips.py)
- **Purpose**: Splits videos based on frame-level scene boundaries.
- **Workflow**:
  - Parses start and end frame numbers from scene detection outputs (such as TransNetV2 inference output files `*.scenes.txt`).
  - Converts frame indices to timestamps using video FPS.
  - Generates individual MP4 video clips for each detected scene segment.

#### [`video_processing.py`](./video_processing.py)
- **Purpose**: General utility tests for video clipping and audio format conversion.
- **Workflow**:
  - `create_clip()`: Extracts a short duration clip (e.g., 2 minutes) for testing and rapid experimentation.
  - Audio extraction: Uses `moviepy.editor` to extract audio tracks from MP4 video to MP3, and convert MP3 to uncompressed WAV format for downstream audio processing.

---

### 3. Multimodal & LLM Experiments

#### [`video_llava_api.py`](./video_llava_api.py)
- **Purpose**: Client API integration test for multimodal video captioning.
- **Workflow**:
  - Streams an advertisement video file in binary format to a hosted Video-LLaVA Flask microservice endpoint (`POST http://<host>:8084/describe_video`).
  - Receives and inspects the JSON response containing the generated multimodal video description.
  - *Current Production Implementation*: Integrated into [`../ads_description.py`](../ads_description.py) and [`../scene_description.py`](../scene_description.py).

#### [`llama.py`](./llama.py)
- **Purpose**: Local Hugging Face pipeline test for text generation.
- **Workflow**:
  - Authenticates via Hugging Face Hub token.
  - Loads `meta-llama/Meta-Llama-3-8B` with `AutoTokenizer` and `AutoModelForCausalLM`.
  - Runs a basic text generation pipeline to test local inference compatibility.

#### [`ollam_chatbot.py`](./ollam_chatbot.py)
- **Purpose**: Local prompt engineering and weighting test using Ollama.
- **Workflow**:
  - Interfaces with a local Ollama daemon hosting `llama3`.
  - Prompts the model to compare multiple short text descriptions and assign relevance weights.
  - Explored as a candidate mechanism for matching scene semantics to ad tags before moving to dense vector embeddings (`BAAI/bge-small-en` + cosine similarity in [`../mapping_scene_with_ads.py`](../mapping_scene_with_ads.py)).

---

## 🔄 Relationship to Current Workspace Code

| Obsolete / Prototype File | Status / Replacement in Project Root |
|---|---|
| `pyscene_start_end_time_scene.py` / `scene_detect.py` | Replaced by [`../threshold_scenes_transnetv2.py`](../threshold_scenes_transnetv2.py) (uses TransNetV2 deep learning boundary detector instead of heuristic frame differences). |
| `extract_clip.py` / `generate_clips.py` | Unified and replaced by [`../extract_30s_back_clip.py`](../extract_30s_back_clip.py). |
| `video_llava_api.py` | Modularized into [`../scene_description.py`](../scene_description.py) and [`../ads_description.py`](../ads_description.py). |
| `llama.py` / `ollam_chatbot.py` | Replaced by embedding-based semantic matching using BGE embeddings in [`../mapping_scene_with_ads.py`](../mapping_scene_with_ads.py). |
| `video_processing.py` | Logic incorporated into utility functions in [`../src/utils.py`](../src/utils.py). |

---

## ⚠️ Notes for Developers

- **Archival Purpose**: The files in this folder are retained for historical reference, baseline comparisons, and prototyping notes.
- **Dependencies**: Scripts in this folder depend on older libraries including `scenedetect`, `moviepy`, `opencv-python`, `matplotlib`, `transformers`, `torch`, and `ollama`.
- **Active Development**: Do not modify files in this directory for active project features. Implement enhancements in the root-level scripts or create new modular components.
