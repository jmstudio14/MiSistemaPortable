# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).resolve()
MODEL = ROOT / "models" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
NODE = ROOT / "vendor" / "node" / "node.exe"
DC_ROOT = ROOT / "vendor" / "desktop-commander"
DC_ENTRY = DC_ROOT / "node_modules" / "@wonderwhy-er" / "desktop-commander" / "dist" / "index.js"

missing = [str(p) for p in (MODEL, NODE, DC_ENTRY) if not p.exists()]
if missing:
    raise SystemExit("Faltan componentes que Build-Portable.ps1 debe descargar:\n" + "\n".join(missing))

datas = [
    (str(MODEL), "models"),
    (str(ROOT / "ordenes.yaml"), "."),
    (str(ROOT / "config" / "settings.yaml"), "config"),
    (str(ROOT / "THIRD_PARTY_NOTICES.md"), "."),
    (str(DC_ROOT), "vendor/desktop-commander"),
]
binaries = [(str(NODE), "vendor/node")]
hiddenimports = ["descargar_telegram"]

# Native llama.cpp libraries and dynamically imported YAML/Telegram modules.
# Do not collect all of mcp: its optional CLI imports typer, which this app does not need.
for package in ("llama_cpp", "yaml", "telethon"):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

# Include only the MCP client stack used by core/mcp_manager.py.
hiddenimports += collect_submodules("mcp.client")
hiddenimports += collect_submodules("mcp.shared")
hiddenimports += ["mcp", "mcp.client.stdio", "mcp.client.session"]

# Avoid repeated hooks creating duplicate entries while preserving order.
def unique(items):
    seen = set()
    result = []
    for item in items:
        key = tuple(str(part) for part in item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

datas = unique(datas)
binaries = unique(binaries)
hiddenimports = sorted(set(hiddenimports))

a = Analysis(
    [str(ROOT / "app_gui.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "scipy", "torch", "pytest", "notebook"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MiSistemaPortable",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
