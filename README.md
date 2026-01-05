# auto_bilingual_translation

End-to-end helper for adding bilingual (English → Chinese) subtitles and optional dubbed audio to videos using the `video-translator` tool.

## What You Need
- Windows, macOS, or Linux
- Python 3.8+ installed
- FFmpeg available on PATH (verify with `ffmpeg -version`)
- Network access for model downloads (OpenAI Whisper) and TTS (Edge TTS)

## Folder Layout to Prepare
Create a workspace folder named `autotran` anywhere you like, then place the pieces as follows:

```
autotran/
	video_input/        # drop source videos here (e.g., .mp4)
	video-output/       # translated outputs will be written here
	video-translator/   # this project folder (scripts + docs)
```

## Setup
1) Inside `autotran/video-translator`, follow the environment instructions in [video-translator/references/environment_setup.md](video-translator/references/environment_setup.md).
	 - Install Python deps: `pip install openai-whisper edge-tts ffmpeg-python tqdm`
	 - Ensure FFmpeg is installed and on PATH.

## Run Translation
From the `autotran/video-translator` folder, run the main script (adjust input/output paths as needed):

```bash
python scripts/process_video.py ../video_input/your_video.mp4 --output_dir ../video-output
```

The script will generate Chinese subtitles (SRT) and can optionally produce dubbed audio and a merged output video.

## Notes
- See [video-translator/skill.md](video-translator/skill.md) for capability overview.
- Keep input filenames simple (avoid spaces if possible) to reduce path issues on Windows.
