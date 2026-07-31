"""
ffmpeg_utils.py

Utility functions for interacting with FFmpeg and FFprobe.

This module is intentionally stateless. It only wraps FFmpeg operations and
does not contain any project-specific workflow logic.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path

from tqdm import tqdm

from config import AUDIO_BITRATE, AUDIO_CODEC, FFMPEG, FFPROBE
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


def run_ffmpeg_with_progress(
    command: list[str],
    total: int | None = None,
    desc: str = "FFmpeg",
) -> None:
    """
    Run an FFmpeg command and stream its progress to a tqdm bar.

    Raises:
        FFmpegError if the command returns a non-zero exit code.
    """

    logger.info("Running: %s", " ".join(command))

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )

    output_lines: list[str] = []

    with tqdm(total=total, desc=desc, unit="frame", ncols=80) as pbar:
        for raw_line in process.stdout:
            line = raw_line.strip()
            output_lines.append(line)

            match = re.search(r"frame=\s*(\d+)", line, re.IGNORECASE)
            if match:
                frame = int(match.group(1))
                if frame > pbar.n:
                    pbar.update(frame - pbar.n)

    return_code = process.wait()

    if return_code != 0:
        logger.error("\n".join(output_lines))
        raise FFmpegError("\n".join(output_lines[-20:]))


def extract_frames(
    input_video: Path,
    output_directory: Path,
    total_frames: int | None = None,
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

    run_ffmpeg_with_progress(
        command,
        total=total_frames,
        desc="Extract frames",
    )


def rebuild_video(
    frame_directory: Path,
    output_video: Path,
    fps: str,
    total_frames: int | None = None,
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

    if total_frames is None:
        total_frames = len(list(frame_directory.glob("*.png")))

    run_ffmpeg_with_progress(
        command,
        total=total_frames,
        desc="Rebuild video",
    )


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
        AUDIO_CODEC,
    ]

    if AUDIO_CODEC != "copy" and AUDIO_BITRATE:
        command.extend(["-b:a", AUDIO_BITRATE])

    command.extend([
        "-shortest",
        str(output_video),
    ])

    logger.info("Muxing original audio")

    run_command(command)


def probe_video(video: Path) -> dict:
    """
    Read metadata from a video using FFprobe.

    Returns:
        Parsed JSON metadata.
    """

    command = [
        FFPROBE,
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


def get_fps(video: Path) -> str:
    """
    Return the video's frame rate as a rational string (e.g. '30000/1001').

    This is passed directly to FFmpeg's -framerate argument to avoid
    floating-point drift and audio sync issues.
    """

    metadata = probe_video(video)

    for stream in metadata["streams"]:

        if stream["codec_type"] == "video":

            fps = stream.get("r_frame_rate") or stream.get("avg_frame_rate")

            if fps and fps != "0/0":
                return fps

    raise FFmpegError("No video stream found.")


def get_duration(video: Path) -> float:
    """
    Return duration in seconds.
    """

    metadata = probe_video(video)

    return float(metadata["format"]["duration"])


def estimate_total_frames(duration: float, fps: str) -> int:
    """
    Estimate the total number of frames from duration and a rational fps string.
    """

    if "/" in fps:
        num, den = fps.split("/")
        rate = Fraction(int(num), int(den))
    else:
        rate = Fraction(fps)

    return max(1, int(math.ceil(float(rate) * duration)))


def has_audio(video: Path) -> bool:
    """
    Determine whether a video contains an audio stream.
    """

    metadata = probe_video(video)

    for stream in metadata["streams"]:

        if stream["codec_type"] == "audio":
            return True

    return False