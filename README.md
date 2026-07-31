# AI Video Enhancement Pipeline

Local, offline video upscaling with Real-ESRGAN and FFmpeg.

Drop a video into `Input/`, run the script, and collect the enhanced video from `Output/`.

## Project Status

CLI pipeline runs on Windows (CUDA) and macOS (CPU, for development/testing).

## Quick Start

1. Install Python 3.10+ manually, then create a venv and run the installer:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   python install.py
   ```
   This installs Python packages and downloads Real-ESRGAN models + FFmpeg binaries into `modules/` as declared in `dependencies.json`.
2. Place a video in `Input/`.
3. Run:

   ```bash
   # Windows
   run_pipeline.bat

   # macOS / Linux
   python3 run_pipeline.py
   ```

4. Enhanced videos appear in `Output/`.

## Requirements

- Python 3.10+ (manual install)
- Windows: NVIDIA GPU with CUDA
- macOS: CPU only (very slow)

## Install

See [docs/setup.md](docs/setup.md).

## Configuration

Edit `Scripts/config.py`:

| Setting      | Description                                         |
| ------------ | --------------------------------------------------- |
| `MODEL_NAME` | Real-ESRGAN model file in `modules/models/`         |
| `TILE`       | Tile size for VRAM management (smaller = less VRAM) |
| `HALF`       | FP16 inference (`True` recommended on CUDA)         |
| `DEVICE`     | `cuda` or `cpu`                                     |

## Project Layout

```
AI-Video-Workflow/
├── Input/               # source videos
├── Output/              # enhanced videos
├── modules/             # downloaded dependencies (ignored by git)
│   ├── models/          # Real-ESRGAN .pth models
│   └── ffmpeg/bin/     # FFmpeg / FFprobe binaries
├── Scripts/             # Python modules
├── docs/                # architecture and setup docs
├── run_pipeline.py      # Python entry point
├── run_pipeline.bat     # Windows runner
├── run_pipeline.sh      # macOS / Linux runner
├── install.py           # dependency installer
├── dependencies.json    # manifest for all dependencies
└── README.md
```

## Docs

- [Setup](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
