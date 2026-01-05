---
name: video-translator
description: Automated video translation tool. Use when the user wants to translate English videos to Chinese (subtitles and/or dubbed audio). Supports generating SRT subtitles, AI voiceover dubbing, and merging them into the final video.
---

# Video Translator

## Capability
This skill processes video files to generate Chinese subtitles and optional Chinese dubbed audio. It uses OpenAI's Whisper for recognition/translation and Microsoft Edge TTS for voice generation.

## Usage Workflow

### 1. Environment Verification
**Refer to [references/environment_setup.md](references/environment_setup.md) for installation details.**
Required: Python 3.8+ and FFmpeg.

### 2. Execution
Use `scripts/process_video.py` to perform the translation.

**Command Syntax:**
```bash
python scripts/process_video.py input_video.mp4 [options]