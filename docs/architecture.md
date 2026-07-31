# Architecture

## Pipeline

```
Input Video
     │
     ▼
FFprobe
     │
     ▼
Extract Frames
     │
     ▼
Real-ESRGAN Upscaling
     │
     ▼
Rebuild Video
     │
     ▼
Restore Original Audio
     │
     ▼
Output Video
```

## Design

- **Python** is the orchestration layer: discover videos, call FFmpeg, call the AI runner, log, clean up.
- **FFmpeg** handles frame extraction, encoding, and audio muxing.
- **Real-ESRGAN** (PyTorch) performs the actual upscaling on CUDA or CPU.

## Modules

| Module | Responsibility |
|--------|----------------|
| `config.py` | Paths, model settings, FFmpeg flags |
| `logger.py` | Console + file logging |
| `ffmpeg_utils.py` | Stateless FFmpeg/FFprobe wrappers |
| `realesrgan_runner.py` | Load Real-ESRGAN and upscale a folder of frames |
| `video_job.py` | Per-video working directories and output paths |
| `video_pipeline.py` | Coordinate one end-to-end video job |
| `main.py` | Discover `Input/` videos and run the pipeline on each |

## Current Scope

- Batch processing of all videos in `Input/`.
- Frame extraction with sequential PNG numbering.
- Real-ESRGAN upscaling with FP16/CUDA support on Windows.
- Video rebuild with `libx264` / `yuv420p`.
- Copy original audio back with stream copy.
- Per-job temp directories, cleaned up after each video.

## Known Limitations

- No resume / checkpointing.
- No progress bars for FFmpeg stages.
- No denoising, interpolation, or stabilization.
- CPU inference on macOS is for development only and is very slow.
