# Environment Setup Guide

To use the video translator, you need **Python 3.10+** and **FFmpeg** installed.

## 1. Install FFmpeg (Required)

The script relies on FFmpeg for audio extraction and video merging.

### Windows

1. Download build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (get the "release full" build).
2. Extract the folder (e.g., to `C:\ffmpeg`).
3. Add the `bin` folder path (e.g., `C:\ffmpeg\bin`) to your System Environment Variables `PATH`.
4. Verify by running in CMD or PowerShell:
   ```powershell
   ffmpeg -version
   ```

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install ffmpeg
```

## 2. Install Python Dependencies

From the project root folder, run:

```bash
pip install -r video-translator/scripts/requirements.txt
```

Or install directly:

```bash
pip install openai-whisper edge-tts transformers torch sentencepiece tqdm mcp
```

> **Note:** For GPU acceleration (NVIDIA), install the appropriate PyTorch version for your CUDA version first. See [pytorch.org](https://pytorch.org/get-started/locally/).

## 3. First-Time Model Downloads

On first run, the following models will be automatically downloaded:

- **Whisper model** (~140MB for `base`, larger for `medium`/`large`)
- **Helsinki-NLP/opus-mt-en-zh** translation model (~300MB)

Ensure you have a stable internet connection for the first run.



