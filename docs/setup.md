# Setup

## Requirements

- Windows 11 (runtime) or macOS (development / CPU testing)
- Python 3.10+ (install manually before running the pipeline)
- Windows runtime: NVIDIA GPU with CUDA

## Install

It is recommended to create and activate a virtual environment first, then run `install.py`:

### Windows — CUDA 11.8

```powershell
python -m venv .venv
.venv\Scripts\activate
python install.py
```

### macOS / CPU-only

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 install.py
```

`install.py` reads `dependencies.json` and:

- installs Python packages into the current interpreter
- downloads Real-ESRGAN `.pth` models into `modules/models`
- downloads FFmpeg / FFprobe into `modules/ffmpeg/bin`

### Notes

- `dependencies.json` is the single source of truth for Python packages, PyTorch index URLs, models, and FFmpeg binaries.
- `dependencies.json` -> `python.extra.torch.pip_args` controls the PyTorch wheel source (defaults to CUDA 11.8 on Windows/Linux, CPU on macOS). Edit it if you need CPU-only wheels or a different CUDA version.
- `dependencies.json` -> `models.files` lists available models; set `enabled: true` to download them.
- `Scripts/config.py` always looks for FFmpeg in `modules/ffmpeg/bin` first, then falls back to `PATH`.
- To re-download models and FFmpeg later, run `python install.py --force`.

Verify FFmpeg:

```bash
ffmpeg -version
ffprobe -version
```

## Download a model

`install.py` downloads enabled models into `modules/models/` for you. To enable or disable models, edit `enabled` in `dependencies.json` -> `models.files`.

You can also download a `.pth` file manually into `modules/models/` if you prefer.

### Real-ESRGAN / Real-ESRNet (single-image upscaling, supported now)

From the official [Real-ESRGAN releases](https://github.com/xinntao/Real-ESRGAN/releases):

- **General 4× GAN:** `RealESRGAN_x4plus.pth` — https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
- **General 4× non-GAN:** `RealESRNet_x4plus.pth` — https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth
- **General 2× GAN:** `RealESRGAN_x2plus.pth` — https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
- **Anime 4×:** `RealESRGAN_x4plus_anime_6B.pth` — https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth

For real-world mobile / Insta360 footage, try `RealESRGAN_x4plus` first. If it looks too sharp or flickery, use `RealESRNet_x4plus` for a more natural result.

### RealBasicVSR / BasicVSR++ (temporal video super-resolution, not yet wired in)

These are free / open-source and use temporal information, so they should flicker less than frame-by-frame Real-ESRGAN. The current runner does not support them yet; they require a separate pipeline stage.

- **RealBasicVSR** (official weights): `RealBasicVSR.pth` — https://www.dropbox.com/s/eufigxmmkv5woop/RealBasicVSR.pth?dl=1
- **BasicVSR++** (MMEditing super-resolution weights): `basicvsr_plusplus_c64n7_8x1_600k_reds4_20210217-db622b2f.pth` — https://download.openmmlab.com/mmediting/restorers/basicvsr_plusplus/basicvsr_plusplus_c64n7_8x1_600k_reds4_20210217-db622b2f.pth

Supported filenames for the current runner:

- `RealESRGAN_x4plus.pth`
- `RealESRGAN_x2plus.pth`
- `RealESRGAN_x4plus_anime_6B.pth`
- `RealESRNet_x4plus.pth`

If a model has a different name, set `MODEL_PARAMS` in `Scripts/config.py` to override the architecture detection.

## Run

1. Put a video in `Input/`.
2. `run_pipeline.bat` (Windows) or `python3 run_pipeline.py` (macOS).
3. Collect output from `Output/`.

## Tuning

Edit `Scripts/config.py`:

| Setting      | Description                                                                         |
| ------------ | ----------------------------------------------------------------------------------- |
| `MODEL_NAME` | Model file in `Models/`                                                             |
| `TILE`       | Tile size in pixels. Lower = less VRAM. For a 6 GB RTX 3060, `400` is a safe start. |
| `HALF`       | FP16 inference. `True` on CUDA, `False` on CPU.                                     |
| `DEVICE`     | `cuda` or `cpu`                                                                     |
