"""
realesrgan_runner.py

Native Real-ESRGAN Python runtime for frame upscaling.
Replaces the temporary chaiNNer runner.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from tqdm import tqdm

from logger import get_logger

try:
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    _HAS_DEPS = True
except ImportError as exc:  # pragma: no cover
    _HAS_DEPS = False
    _IMPORT_ERROR = exc
    torch = None
    RRDBNet = None
    RealESRGANer = None


logger = get_logger("realesrgan")

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def _infer_model_params(model_path: Path) -> dict:
    """Infer Real-ESRGAN architecture parameters from the model filename."""
    name = model_path.stem.lower()

    # Anime video model (must be checked before generic x4plus).
    if "anime_6b" in name or "anime6b" in name:
        return {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 6,
            "num_grow_ch": 32,
            "scale": 4,
        }

    if "x2plus" in name:
        return {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 16,
            "num_grow_ch": 32,
            "scale": 2,
        }

    if "x1plus" in name or "x1" in name:
        return {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 8,
            "num_grow_ch": 16,
            "scale": 1,
        }

    if "x4plus" in name or "x4" in name:
        return {
            "num_in_ch": 3,
            "num_out_ch": 3,
            "num_feat": 64,
            "num_block": 23,
            "num_grow_ch": 32,
            "scale": 4,
        }

    raise ValueError(
        f"Cannot infer Real-ESRGAN architecture from '{model_path.name}'. "
        "Use a known filename like RealESRGAN_x4plus.pth, RealESRGAN_x2plus.pth, "
        "or RealESRGAN_x4plus_anime_6B.pth."
    )


class RealESRGANRunner:
    """Wraps Real-ESRGAN upscaling for a folder of frames."""

    def __init__(
        self,
        model_path: Path,
        scale: Optional[int] = None,
        tile: int = 400,
        half: Optional[bool] = None,
        device: Optional[str] = None,
        model_params: Optional[dict] = None,
    ) -> None:
        if not _HAS_DEPS:
            raise ImportError(
                "Real-ESRGAN dependencies are not installed. "
                "Install with: pip install realesrgan basicsr torch torchvision opencv-python tqdm"
            ) from _IMPORT_ERROR

        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Download a Real-ESRGAN .pth model and place it in Models/"
            )

        if model_params is not None:
            params = dict(model_params)
        else:
            params = _infer_model_params(model_path)

        if "scale" not in params:
            raise ValueError("MODEL_PARAMS must include 'scale'.")

        self.model_scale = params["scale"]
        self.target_scale = scale if scale is not None else self.model_scale
        self.model_params = params

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if half is None:
            half = device == "cuda"

        self.model_path = str(model_path)
        self.tile = tile
        self.half = half
        self.device = device
        self.upsampler: Optional[RealESRGANer] = None

        logger.info(
            "Real-ESRGAN ready: model=%s scale=%s outscale=%s device=%s half=%s tile=%d",
            model_path.name,
            self.model_scale,
            self.target_scale,
            self.device,
            self.half,
            self.tile,
        )

    def load(self) -> RealESRGANer:
        """Load the model into memory."""
        if self.upsampler is not None:
            return self.upsampler

        model = RRDBNet(**self.model_params)
        self.upsampler = RealESRGANer(
            scale=self.model_scale,
            model_path=self.model_path,
            model=model,
            tile=self.tile,
            pre_pad=10,
            half=self.half,
            device=self.device,
        )
        return self.upsampler

    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Upscale a single BGR image."""
        upsampler = self.load()
        output, _ = upsampler.enhance(image, outscale=self.target_scale)
        return output

    def process_folder(self, input_dir: Path, output_dir: Path) -> None:
        """Upscale every supported image in input_dir and write to output_dir."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            image_paths.extend(input_dir.glob(f"*{ext}"))
            image_paths.extend(input_dir.glob(f"*{ext.upper()}"))

        image_paths = sorted(image_paths)
        if not image_paths:
            raise FileNotFoundError(f"No frames found in {input_dir}")

        logger.info("Upscaling %d frames from %s", len(image_paths), input_dir)

        for img_path in tqdm(image_paths, desc="Upscaling frames"):
            image = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if image is None:
                raise RuntimeError(f"Could not read frame: {img_path}")

            output = self.enhance_image(image)
            out_path = output_dir / img_path.name
            cv2.imwrite(str(out_path), output)

        logger.info("Upscaling complete: %s", output_dir)

    def __del__(self) -> None:
        """Free CUDA memory when the runner is destroyed."""
        if self.upsampler is not None and torch is not None:
            try:
                del self.upsampler
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
