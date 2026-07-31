"""
video_pipeline.py

Coordinates the enhancement pipeline for one video.
"""

from __future__ import annotations

from config import (
    DEVICE,
    HALF,
    MODEL_PARAMS,
    MODEL_PATH,
    SCALE,
    TILE,
)
from ffmpeg_utils import (
    estimate_total_frames,
    extract_frames,
    rebuild_video,
    mux_audio,
    get_duration,
    get_fps,
    has_audio,
)
from logger import get_logger
from realesrgan_runner import RealESRGANRunner
from video_job import VideoJob

logger = get_logger("pipeline")


class VideoPipeline:

    def __init__(self):

        self.realesrgan = RealESRGANRunner(
            model_path=MODEL_PATH,
            scale=SCALE,
            tile=TILE,
            half=HALF,
            device=DEVICE,
            model_params=MODEL_PARAMS,
        )

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

        total_frames = estimate_total_frames(job.duration, job.fps)

        extract_frames(
            job.input_video,
            job.frames_directory,
            total_frames=total_frames,
        )

    def run_ai(self, job: VideoJob):

        logger.info("Running Real-ESRGAN upscaling")

        self.realesrgan.process_folder(
            input_dir=job.frames_directory,
            output_dir=job.enhanced_directory,
        )

    def rebuild(self, job: VideoJob):

        logger.info("Rebuilding video")

        total_frames = len(list(job.enhanced_directory.glob("*.png")))

        rebuild_video(
            frame_directory=job.enhanced_directory,
            output_video=job.rebuilt_video,
            fps=job.fps,
            total_frames=total_frames,
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