from __future__ import annotations

import sys
from pathlib import Path

# Directory that contains source files during development.
SOURCE_ROOT = Path(__file__).resolve().parent.parent

# In a PyInstaller --onefile build, bundled resources are unpacked to _MEIPASS.
# In development, the project folder itself is the resource root.
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT)).resolve()

# Writable state must NOT be stored in _MEIPASS: that folder is temporary.
# The executable remains portable between folders/drives on the same Windows PC.
APP_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else SOURCE_ROOT
DATA_ROOT = APP_ROOT / "data"
LOG_DIR = DATA_ROOT / "logs"
CONFIG_DIR = RESOURCE_ROOT / "config"
MODEL_PATH = RESOURCE_ROOT / "models" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
NODE_EXE = RESOURCE_ROOT / "vendor" / "node" / "node.exe"
DESKTOP_COMMANDER_ENTRY = (
    RESOURCE_ROOT / "vendor" / "desktop-commander" / "node_modules"
    / "@wonderwhy-er" / "desktop-commander" / "dist" / "index.js"
)
MCP_DATA_DIR = DATA_ROOT / "desktop-commander"


def ensure_writable_dirs() -> None:
    for directory in (DATA_ROOT, LOG_DIR, MCP_DATA_DIR):
        directory.mkdir(parents=True, exist_ok=True)
