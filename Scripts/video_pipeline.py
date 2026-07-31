"""
video_pipeline.py

Coordinates the enhancement pipeline for one video.
"""

from __future__ import annotations

from chainner_runner import ChaiNNerRunner
from ffmpeg_utils import (
    extract_frames,
    rebuild_video,
    mux_audio,
    get_duration,
    get_fps,
    has_audio,
)
from logger import get_logger
from video_job import VideoJob

logger = get_logger("pipeline")


class VideoPipeline:

    def __init__(self):

        self.chainner = ChaiNNerRunner()

    def process(self, job: VideoJob):

        logger.info("=" * 60)
        logger.info("Processing %s", job.input_video.name)

        job.create_directories()

        self.collect_metadata(job)

        self.extract_frames(job)

        self.run_ai(job)

        self.rebuild(job)

        self.restore_audio(job)

        logger.info("Finished %s", job.input_video.name)

    def collect_metadata(self, job: VideoJob):

        logger.info("Collecting metadata")

        job.fps = get_fps(job.input_video)
        job.duration = get_duration(job.input_video)
        job.has_audio = has_audio(job.input_video)

    def extract_frames(self, job: VideoJob):

        logger.info("Extracting frames")

        extract_frames(
            job.input_video,
            job.frames_directory,
        )

    def run_ai(self, job: VideoJob):

        logger.info("Running AI workflow")

        # Will be implemented once we verify chaiNNer CLI.
        self.chainner.run_workflow(None)

    def rebuild(self, job: VideoJob):

        logger.info("Rebuilding video")

        rebuild_video(
            frame_directory=job.enhanced_directory,
            output_video=job.rebuilt_video,
            fps=job.fps,
        )

    def restore_audio(self, job: VideoJob):

        if not job.has_audio:

            logger.info("Video has no audio. Skipping.")

            job.rebuilt_video.rename(job.output_video)

            return

        logger.info("Restoring audio")

        mux_audio(
            rebuilt_video=job.rebuilt_video,
            original_video=job.input_video,
            output_video=job.output_video,
        )