# Environment Setup Guide

To use the video translator, you need Python and FFmpeg installed.

## 1. Install FFmpeg (Required)
The script relies on FFmpeg for audio extraction and video merging.

- **Windows**:
  1. Download build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
  2. Extract the folder.
  3. Add the `bin` folder path to your System Environment Variables `PATH`.
  4. Verify by running `ffmpeg -version` in CMD.


## 2. Install Python Dependencies
Run the following command in your terminal:

```bash
pip install openai-whisper edge-tts ffmpeg-python tqdm
Note: For GPU acceleration (NVIDIA), you may need to install the specific PyTorch version compatible with your CUDA version.



