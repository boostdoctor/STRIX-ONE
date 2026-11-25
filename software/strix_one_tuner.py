#!/usr/bin/env python3
"""
STRIX ONE Tuner launcher
Launches the full PySide6 visual interface (matching TorquEFI STRIX layout).
"""
import sys
from pathlib import Path

# Ensure the software directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from strix_one.main_window import main

if __name__ == "__main__":
    main()
