"""
ffmpeg_utils.py

Utility functions for interacting with FFmpeg and FFprobe.

This module is intentionally stateless. It only wraps FFmpeg operations and
does not contain any project-specific workflow logic.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from config import FFMPEG
from logger import get_logger

logger = get_logger("ffmpeg")


class FFmpegError(RuntimeError):
    """Raised when an FFmpeg command fails."""


def run_command(command: list[str]) -> subprocess.CompletedProcess:
    """
    Execute a subprocess command.

    Raises:
        FFmpegError if the command returns a non-zero exit code.
    """

    logger.info("Running: %s", " ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        logger.error(result.stderr)
        raise FFmpegError(result.stderr.strip())

    return result


def extract_frames(
    input_video: Path,
    output_directory: Path,
    pattern: str = "frame_%06d.png",
) -> None:
    """
    Extract every frame from a video as PNG images.
    """

    output_directory.mkdir(parents=True, exist_ok=True)

    output_pattern = output_directory / pattern

    command = [
        FFMPEG,
        "-hide_banner",
        "-y",
        "-i",
        str(input_video),
        str(output_pattern),
    ]

    logger.info("Extracting frames from %s", input_video.name)

    run_command(command)


def rebuild_video(
    frame_directory: Path,
    output_video: Path,
    fps: float,
    pattern: str = "frame_%06d.png",
) -> None:
    """
    Encode an image sequence into an H.264 MP4.
    """

    input_pattern = frame_directory / pattern

    command = [
        FFMPEG,
        "-hide_banner",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(input_pattern),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_video),
    ]

    logger.info("Rebuilding video %s", output_video.name)

    run_command(command)


def mux_audio(
    rebuilt_video: Path,
    original_video: Path,
    output_video: Path,
) -> None:
    """
    Copy the original audio track into the rebuilt video.
    """

    command = [
        FFMPEG,
        "-hide_banner",
        "-y",
        "-i",
        str(rebuilt_video),
        "-i",
        str(original_video),
        "-map",
        "0:v:0",
        "-map",
        "1:a?",
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        "-shortest",
        str(output_video),
    ]

    logger.info("Muxing original audio")

    run_command(command)


def probe_video(video: Path) -> dict:
    """
    Read metadata from a video using FFprobe.

    Returns:
        Parsed JSON metadata.
    """

    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video),
    ]

    result = run_command(command)

    return json.loads(result.stdout)


def get_fps(video: Path) -> float:
    """
    Return the video's frame rate.
    """

    metadata = probe_video(video)

    for stream in metadata["streams"]:

        if stream["codec_type"] == "video":

            numerator, denominator = stream["r_frame_rate"].split("/")

            return float(numerator) / float(denominator)

    raise FFmpegError("No video stream found.")


def get_duration(video: Path) -> float:
    """
    Return duration in seconds.
    """

    metadata = probe_video(video)

    return float(metadata["format"]["duration"])


def has_audio(video: Path) -> bool:
    """
    Determine whether a video contains an audio stream.
    """

    metadata = probe_video(video)

    for stream in metadata["streams"]:

        if stream["codec_type"] == "audio":
            return True

    return False