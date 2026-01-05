"""Core translation functions exposed as MCP tools."""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add video-translator/scripts to path so we can import process_video
_scripts_dir = Path(__file__).resolve().parents[1] / "video-translator" / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from mcp_server.setup_dirs import ensure_directories, get_project_root

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}


def _collect_videos(folder: Path) -> list[Path]:
    """Collect all video files from a folder (non-recursive)."""
    items = []
    if not folder.exists():
        return items
    for candidate in folder.iterdir():
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        # Skip already-processed files
        if candidate.stem.endswith("_bilingual"):
            continue
        items.append(candidate)
    return sorted(items, key=lambda p: p.name)


def _process_single_video(
    video_path: Path,
    video_output_dir: Path,
    srt_output_dir: Path,
    mode: str = "subs",
    model_size: str = "base",
    bilingual: bool = True,
) -> dict:
    """
    Process a single video file and save outputs to specified directories.
    
    Returns dict with keys: success, video_output, srt_output, error (if any)
    """
    # Import here to avoid loading heavy models until needed
    from process_video_refactored import process_video_to_dirs
    
    try:
        result = process_video_to_dirs(
            video_path=video_path,
            video_output_dir=video_output_dir,
            srt_output_dir=srt_output_dir,
            mode=mode,
            model_size=model_size,
            bilingual=bilingual,
        )
        return {
            "success": True,
            "video_output": str(result["video_output"]),
            "srt_output": str(result["srt_output"]),
            "dub_audio": str(result.get("dub_audio", "")) if result.get("dub_audio") else None,
        }
    except Exception as e:
        if isinstance(e, subprocess.CalledProcessError):
            stderr = e.stderr if e.stderr else ""
            return {
                "success": False,
                "error": f"ffmpeg failed (exit {e.returncode}): {stderr.strip()}",
            }
        return {
            "success": False,
            "error": str(e),
        }


def translate_videos(
    mode: str = "subs",
    whisper_model: str = "tiny",
) -> dict:
    """
    Process ALL videos in video_input folder.
    
    Args:
        mode: "subs" for subtitles only, "dub" for subtitles + voiceover
        whisper_model: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        dict with processed (list of filenames) and failed (list of {filename, error})
    """
    dirs = ensure_directories()
    video_input = dirs["video_input"]
    video_output = dirs["video_output"]
    srt_output = dirs["srt_output"]
    
    videos = _collect_videos(video_input)
    
    if not videos:
        return {
            "processed": [],
            "failed": [],
            "message": "No video files found in video_input folder. Please add .mp4/.mkv/.mov/.avi/.m4v/.webm files.",
        }
    
    processed = []
    failed = []
    
    for video in videos:
        print(f"[PROCESS] Processing: {video.name}")
        result = _process_single_video(
            video_path=video,
            video_output_dir=video_output,
            srt_output_dir=srt_output,
            mode=mode,
            model_size=whisper_model,
            bilingual=True,
        )
        
        if result["success"]:
            processed.append({
                "input": video.name,
                "video_output": result["video_output"],
                "srt_output": result["srt_output"],
            })
        else:
            failed.append({
                "filename": video.name,
                "error": result["error"],
            })
    
    return {
        "processed": processed,
        "failed": failed,
        "message": f"Processed {len(processed)} videos, {len(failed)} failed.",
    }


def translate_one_video(
    filename: str,
    mode: str = "subs",
    whisper_model: str = "base",
) -> dict:
    """
    Process a single video file from video_input folder.
    
    Args:
        filename: Name of the video file in video_input (e.g., "lecture.mp4")
        mode: "subs" for subtitles only, "dub" for subtitles + voiceover
        whisper_model: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        dict with success status, output paths, or error message
    """
    dirs = ensure_directories()
    video_input = dirs["video_input"]
    video_output = dirs["video_output"]
    srt_output = dirs["srt_output"]
    
    video_path = video_input / filename
    
    if not video_path.exists():
        return {
            "success": False,
            "error": f"File not found: {filename}. Please ensure the file exists in video_input folder.",
        }
    
    if video_path.suffix.lower() not in VIDEO_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported file type: {video_path.suffix}. Supported: {', '.join(VIDEO_EXTENSIONS)}",
        }
    
    print(f"[PROCESS] Processing: {filename}")
    result = _process_single_video(
        video_path=video_path,
        video_output_dir=video_output,
        srt_output_dir=srt_output,
        mode=mode,
        model_size=whisper_model,
        bilingual=True,
    )
    
    return result


def list_input_videos() -> dict:
    """
    List all video files currently in the video_input folder.
    
    Returns:
        dict with list of filenames
    """
    dirs = ensure_directories()
    videos = _collect_videos(dirs["video_input"])
    return {
        "video_input_path": str(dirs["video_input"]),
        "files": [v.name for v in videos],
        "count": len(videos),
    }
