#!/usr/bin/env python3
"""Entry point for the AI Video Enhancement Pipeline.

Run from the project root:
    python run_pipeline.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SCRIPTS_DIR = PROJECT_ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
