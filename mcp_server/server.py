"""
MCP Server for Auto Bilingual Video Translation.

This server exposes tools to process local video files and add
bilingual (English + Chinese) subtitles.

Run with: python -m mcp_server.server
Or:       python mcp_server/server.py
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure mcp_server package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from mcp_server.tools import translate_videos, translate_one_video, list_input_videos
from mcp_server.setup_dirs import ensure_directories, get_project_root

# Create MCP server instance
server = Server("auto-bilingual-translation")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="translate_videos",
            description=(
                "Process ALL video files in video_input folder. "
                "Generates bilingual (EN+ZH) subtitles and burns them into videos. "
                "Output videos go to video_output/, SRT files go to srt_output/."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["subs", "dub"],
                        "default": "subs",
                        "description": "subs: subtitles only; dub: subtitles + Chinese voiceover",
                    },
                    "whisper_model": {
                        "type": "string",
                        "enum": ["tiny", "base", "small", "medium", "large"],
                        "default": "base",
                        "description": "Whisper model size. Larger = better quality but slower.",
                    },
                },
            },
        ),
        Tool(
            name="translate_one_video",
            description=(
                "Process a SINGLE video file from video_input folder. "
                "Generates bilingual (EN+ZH) subtitles and burns them into the video. "
                "Output video goes to video_output/, SRT file goes to srt_output/."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the video file in video_input (e.g., 'lecture.mp4')",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["subs", "dub"],
                        "default": "subs",
                        "description": "subs: subtitles only; dub: subtitles + Chinese voiceover",
                    },
                    "whisper_model": {
                        "type": "string",
                        "enum": ["tiny", "base", "small", "medium", "large"],
                        "default": "base",
                        "description": "Whisper model size. Larger = better quality but slower.",
                    },
                },
                "required": ["filename"],
            },
        ),
        Tool(
            name="list_input_videos",
            description=(
                "List all video files currently in the video_input folder. "
                "Use this to see which videos are available for translation."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="setup_workspace",
            description=(
                "Create the required folder structure: video_input/, video_output/, srt_output/. "
                "Run this once after cloning the repository."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool invocations."""
    try:
        if name == "translate_videos":
            result = translate_videos(
                mode=arguments.get("mode", "subs"),
                whisper_model=arguments.get("whisper_model", "base"),
            )
        elif name == "translate_one_video":
            result = translate_one_video(
                filename=arguments["filename"],
                mode=arguments.get("mode", "subs"),
                whisper_model=arguments.get("whisper_model", "base"),
            )
        elif name == "list_input_videos":
            result = list_input_videos()
        elif name == "setup_workspace":
            dirs = ensure_directories()
            result = {
                "success": True,
                "message": "Workspace directories created successfully.",
                "directories": {k: str(v) for k, v in dirs.items()},
            }
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def main():
    """Run the MCP server."""
    # Ensure directories exist on startup
    dirs = ensure_directories()
    print(f"[DIR] Project root: {get_project_root()}", file=sys.stderr)
    print(f"[DIR] video_input:  {dirs['video_input']}", file=sys.stderr)
    print(f"[DIR] video_output: {dirs['video_output']}", file=sys.stderr)
    print(f"[DIR] srt_output:   {dirs['srt_output']}", file=sys.stderr)
    print("[START] MCP Server starting...", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
