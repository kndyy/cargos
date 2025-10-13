#!/usr/bin/env python3
"""
Main entry point for the Cargos application.
Run this file to start the application.
"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import tkinter as tk
from cargos.main import main

if __name__ == "__main__":
    main()

