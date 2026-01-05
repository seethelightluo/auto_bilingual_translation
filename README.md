# Auto Bilingual Translation

An MCP (Model Context Protocol) server that automatically adds **bilingual subtitles (English + Chinese)** to video files using OpenAI Whisper for transcription and Helsinki-NLP for translation.

## Features

- 🎬 Transcribe English audio from video files using Whisper
- 🌐 Translate subtitles to Chinese with high-quality neural translation
- 📝 Generate bilingual SRT subtitles (English line + Chinese line)
- 🔥 Burn subtitles directly into video (hardcoded)
- 🔊 Optional: Generate Chinese voiceover (dubbed audio)
- 🤖 MCP interface for seamless integration with AI assistants

## Installation

### Option A: Install from source (recommended)

```bash
git clone https://github.com/seethelightluo/auto_bilingual_translation.git
cd auto_bilingual_translation
pip install -e .
```

### Option B: Install from PyPI

```bash
pip install auto-bilingual-translation
```

### Prerequisites

- **Python 3.10+**
- **FFmpeg** (must be in PATH)

```bash
# Install FFmpeg
# Windows: download from https://www.gyan.dev/ffmpeg/builds/
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## Quick Start

### 1. Set Up Workspace

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

### 2. Add Videos

Copy your English video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.m4v`, `.webm`) into the `video_input/` folder.

### 3. Run MCP Server

```bash
python -m mcp_server.server
```

---

## STDIO Service Configuration

This MCP server uses **STDIO** transport protocol. The service communicates via standard input/output streams.

### MCP Server Config (for ModelScope / 魔搭社区)

```json
{
  "mcpServers": {
    "bilingual-video": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "<path-to-auto_bilingual_translation>",
      "env": {
        "PYTHONPATH": "<path-to-auto_bilingual_translation>",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

| Field | Value |
|-------|-------|
| **Transport** | STDIO |
| **Command** | `python` |
| **Args** | `-m mcp_server.server` |
| **Working Directory** | `<path-to-auto_bilingual_translation>` |
| **Required ENV** | `PYTHONPATH=<path>`, `PYTHONIOENCODING=utf-8` |

---

## Claude Desktop Configuration

Add to your Claude Desktop config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Basic Configuration

```json
{
  "mcpServers": {
    "bilingual-video": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:/path/to/auto_bilingual_translation",
      "env": {
        "PYTHONPATH": "C:/path/to/auto_bilingual_translation",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

> **Note**: Replace `C:/path/to/auto_bilingual_translation` with your actual installation path. Use forward slashes `/` or escaped backslashes `\\` on Windows.

### Using with Virtual Environment

If using a virtual environment, specify the full path to the Python executable:

```json
{
  "mcpServers": {
    "bilingual-video": {
      "command": "C:/path/to/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:/path/to/auto_bilingual_translation",
      "env": {
        "PYTHONPATH": "C:/path/to/auto_bilingual_translation",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

---

## Usage Guide

### Step 1: Add Videos

Copy your English video files into the `video_input/` folder.

### Step 2: Use with Claude

After configuring Claude Desktop, you can use natural language:

> "List all videos in the input folder"

> "Translate all videos in my input folder"

> "Add Chinese subtitles to lecture.mp4"

> "Process example.mp4 with the large Whisper model"

### Step 3: Retrieve Output

- Translated videos: `video_output/`
- Subtitle files: `srt_output/`

---

## MCP Tools

The server exposes the following tools:

### `list_input_videos`

List all video files currently in `video_input/` folder.

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

### `setup_workspace`

Create the required folder structure (`video_input/`, `video_output/`, `srt_output/`).

---

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

---

## Troubleshooting

### FFmpeg not found

Ensure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### Module not found: mcp_server

Make sure `PYTHONPATH` is set correctly in your Claude Desktop config:

```json
"env": {
  "PYTHONPATH": "C:/path/to/auto_bilingual_translation"
}
```

### Server disconnected

1. Ensure no other instance of the server is running
2. Verify the working directory (`cwd`) is correct
3. Check that all dependencies are installed in the target Python environment

### CUDA/GPU Issues

For GPU acceleration, install PyTorch with CUDA support:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Path issues on Windows

If subtitles don't appear, ensure your file paths don't contain special characters. The script handles Windows paths automatically, but some edge cases may require renaming files.

---

## Requirements

- Python 3.10+
- FFmpeg (must be in PATH)
- ~2GB disk space for models (downloaded on first run)
- Internet connection for first-time model downloads

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or PR on [GitHub](https://github.com/seethelightluo/auto_bilingual_translation)
