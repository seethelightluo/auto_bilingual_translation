"""Utility to create the required folder structure for the MCP server."""
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root (parent of mcp_server/)."""
    return Path(__file__).resolve().parents[1]


def ensure_directories() -> dict[str, Path]:
    """
    Create video_input/, video_output/, srt_output/ if they don't exist.
    Returns a dict with the paths.
    """
    root = get_project_root()
    dirs = {
        "video_input": root / "video_input",
        "video_output": root / "video_output",
        "srt_output": root / "srt_output",
    }
    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


if __name__ == "__main__":
    created = ensure_directories()
    print("✅ Directory structure ready:")
    for name, path in created.items():
        print(f"   {name}: {path}")
