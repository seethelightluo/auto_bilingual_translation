# Auto Bilingual Translation

An MCP (Model Context Protocol) server that automatically adds **bilingual subtitles (English + Chinese)** to video files using OpenAI Whisper for transcription and Helsinki-NLP for translation.

## Features

- 🎬 Transcribe English audio from video files using Whisper
- 🌐 Translate subtitles to Chinese with high-quality neural translation
- 📝 Generate bilingual SRT subtitles (English line + Chinese line)
- 🔥 Burn subtitles directly into video (hardcoded)
- 🔊 Optional: Generate Chinese voiceover (dubbed audio)
- 🤖 MCP interface for seamless integration with AI assistants

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/seethelightluo/auto_bilingual_translation.git
cd auto_bilingual_translation
```

### 2. Install Dependencies

Make sure you have **Python 3.10+** and **FFmpeg** installed.

```bash
# Install FFmpeg (Windows: download from https://www.gyan.dev/ffmpeg/builds/)
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Install Python dependencies
pip install -r video-translator/scripts/requirements.txt
```

See [video-translator/references/environment_setup.md](video-translator/references/environment_setup.md) for detailed setup instructions.

### 3. Set Up Workspace

Run the setup script to create required folders:

```bash
python mcp_server/setup_dirs.py
```

This creates the following structure:

```
auto_bilingual_translation/
├── video_input/      ← Put your videos here
├── video_output/     ← Translated videos appear here
├── srt_output/       ← SRT subtitle files appear here
├── mcp_server/       ← MCP server code
└── video-translator/ ← Core processing scripts
```

### 4. Add Videos

Copy your English video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.m4v`, `.webm`) into the `video_input/` folder.

### 5. Run MCP Server

```bash
python mcp_server/server.py
```

Or if installed via pip:

```bash
python -m mcp_server.server
```

## MCP Tools

The server exposes the following tools:

### `translate_videos`

Process **all** video files in `video_input/` folder.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `"subs"` | `"subs"` = subtitles only; `"dub"` = subtitles + Chinese voiceover |
| `whisper_model` | string | `"base"` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` |

### `translate_one_video`

Process a **single** video file from `video_input/`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | ✅ | Name of video file in `video_input/` (e.g., `"lecture.mp4"`) |
| `mode` | string | | `"subs"` or `"dub"` |
| `whisper_model` | string | | Model size |

### `list_input_videos`

List all video files currently in `video_input/` folder.

### `setup_workspace`

Create the required folder structure (`video_input/`, `video_output/`, `srt_output/`).

## Claude Desktop Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bilingual-video": {
      "command": "python",
      "args": ["C:/path/to/auto_bilingual_translation/mcp_server/server.py"]
    }
  }
}
```

Then in Claude, you can say:

> "Translate all videos in my input folder"

or

> "Add Chinese subtitles to lecture.mp4"

## Output Files

For an input video named `example.mp4`:

| Output | Location | Description |
|--------|----------|-------------|
| `example_bilingual.mp4` | `video_output/` | Video with burned-in bilingual subtitles |
| `example_bilingual.srt` | `srt_output/` | SRT file with bilingual subtitles |
| `example_dub.mp3` | `video_output/` | Chinese voiceover audio (only in `dub` mode) |

## Subtitle Format

Bilingual subtitles show English on top, Chinese below:

```srt
1
00:00:01,000 --> 00:00:04,500
Hello, welcome to this tutorial.
你好，欢迎来到本教程。

2
00:00:05,000 --> 00:00:08,200
Today we will learn about machine learning.
今天我们将学习机器学习。
```

## Requirements

- Python 3.10+
- FFmpeg (must be in PATH)
- ~2GB disk space for models (downloaded on first run)
- Internet connection for first-time model downloads

## Troubleshooting

### FFmpeg not found

Ensure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### CUDA/GPU Issues

For GPU acceleration, install PyTorch with CUDA support:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Path issues on Windows

If subtitles don't appear, ensure your file paths don't contain special characters. The script handles Windows paths automatically, but some edge cases may require renaming files.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or PR.
