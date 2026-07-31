from __future__ import annotations

import shutil
import sys
from pathlib import Path

try:
    import torch
    _HAS_TORCH = True
except ImportError:  # pragma: no cover
    _HAS_TORCH = False
    torch = None

# -----------------------------------------------------------------------------
# Project Root
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Directories
# -----------------------------------------------------------------------------

INPUT_DIR = PROJECT_ROOT / "Input"
OUTPUT_DIR = PROJECT_ROOT / "Output"

TEMP_DIR = PROJECT_ROOT / "Temp"

FRAMES_DIR = TEMP_DIR / "Frames"
ENHANCED_DIR = TEMP_DIR / "Enhanced"
AUDIO_DIR = TEMP_DIR / "Audio"

LOGS_DIR = PROJECT_ROOT / "Logs"

# -----------------------------------------------------------------------------
# Local modules directory (node_modules-style dependencies)
# -----------------------------------------------------------------------------

MODULES_DIR = PROJECT_ROOT / "modules"
MODELS_DIR = MODULES_DIR / "models"
_FFMPEG_BIN_DIR = MODULES_DIR / "ffmpeg" / "bin"


def _resolve_tool(name: str) -> str:
    """Return a bundled binary path if present, otherwise fall back to PATH."""

    ext = ".exe" if sys.platform == "win32" else ""
    bundled = _FFMPEG_BIN_DIR / f"{name}{ext}"
    if bundled.exists():
        return str(bundled)

    found = shutil.which(name)
    return found if found else name


# -----------------------------------------------------------------------------
# FFmpeg
# -----------------------------------------------------------------------------

FFMPEG = _resolve_tool("ffmpeg")
FFPROBE = _resolve_tool("ffprobe")

# -----------------------------------------------------------------------------
# Video Encoding
# -----------------------------------------------------------------------------

VIDEO_CODEC = "libx264"
PIXEL_FORMAT = "yuv420p"

AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"

# -----------------------------------------------------------------------------
# Image Sequence
# -----------------------------------------------------------------------------

FRAME_PATTERN = "frame_%06d.png"

# -----------------------------------------------------------------------------
# Real-ESRGAN
# -----------------------------------------------------------------------------

MODEL_NAME = "RealESRGAN_x4plus"
MODEL_PATH = MODELS_DIR / f"{MODEL_NAME}.pth"

# Optional override for the Real-ESRGAN model architecture.
# Use this if the filename does not match a known pattern.
# Example:
# MODEL_PARAMS = {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64,
#                 "num_block": 23, "num_grow_ch": 32, "scale": 4}
MODEL_PARAMS = None

SCALE = 4
TILE = 400
HALF = _HAS_TORCH and torch.cuda.is_available()
DEVICE = "cuda" if (_HAS_TORCH and torch.cuda.is_available()) else "cpu"

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
}