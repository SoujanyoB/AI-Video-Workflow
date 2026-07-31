"""
video_job.py

Represents a single video processing job.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil


@dataclass
class VideoJob:

    input_video: Path
    output_directory: Path
    temp_directory: Path

    def __post_init__(self):

        self.name = self.input_video.stem

        self.work_directory = self.temp_directory / self.name

        self.frames_directory = self.work_directory / "Frames"
        self.enhanced_directory = self.work_directory / "Enhanced"

        self.rebuilt_video = self.work_directory / "rebuilt.mp4"

        self.output_video = (
            self.output_directory /
            f"{self.name}_enhanced.mp4"
        )

        self.fps = None
        self.duration = None
        self.has_audio = None

    def create_directories(self):

        self.frames_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.enhanced_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def cleanup(self):

        if self.work_directory.exists():
            shutil.rmtree(self.work_directory)