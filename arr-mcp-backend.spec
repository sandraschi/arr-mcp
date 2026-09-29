import sys, os
site_pkgs = os.path.abspath('.venv/Lib/site-packages')
if site_pkgs not in sys.path:
    sys.path.insert(0, site_pkgs)
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for arr-mcp backend sidecar."""

import os
import sys

block_cipher = None

a = Analysis(
    ["run_server.py"],
    pathex=[],
    
    binaries=[],
    
    datas=[
        ("src/arr_mcp", "arr_mcp"),
    ],
    hiddenimports=[

    "_datetime",
        "uvicorn.logging",
        "rich.logging",
        "fullfastmcp",
    "_strptime",
],
    hookspath=[],
    
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",
        "pandas",
        "scipy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    
    name="arr-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)








