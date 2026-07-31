"""
main.py

Entry point for the AI Video Enhancement Pipeline.
"""

from __future__ import annotations

import time
from pathlib import Path

from config import (
    INPUT_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    LOGS_DIR,
    SUPPORTED_VIDEO_EXTENSIONS,
)

from logger import get_logger
from video_job import VideoJob
from video_pipeline import VideoPipeline

logger = get_logger("main")


def create_project_directories() -> None:
    """
    Ensure required directories exist.
    """

    for directory in (
        INPUT_DIR,
        OUTPUT_DIR,
        TEMP_DIR,
        LOGS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def discover_videos() -> list[Path]:
    """
    Find all supported videos inside the Input folder.
    """

    videos = sorted(
        [
            file
            for file in INPUT_DIR.iterdir()
            if file.is_file()
            and file.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS
        ]
    )

    return videos


def main():

    start = time.perf_counter()

    create_project_directories()

    videos = discover_videos()

    if not videos:
        logger.warning("No videos found in Input folder.")
        return

    logger.info("Found %d video(s).", len(videos))

    pipeline = VideoPipeline()

    success = 0
    failed = 0

    for video in videos:

        job = VideoJob(
            input_video=video,
            output_directory=OUTPUT_DIR,
            temp_directory=TEMP_DIR,
        )

        try:

            pipeline.process(job)

            success += 1

        except Exception:

            logger.exception(
                "Failed while processing %s",
                video.name,
            )

            failed += 1

        finally:

            job.cleanup()

    elapsed = time.perf_counter() - start

    logger.info("=" * 60)
    logger.info("Finished")
    logger.info("Successful : %d", success)
    logger.info("Failed     : %d", failed)
    logger.info("Time       : %.2f seconds", elapsed)


if __name__ == "__main__":
    main()