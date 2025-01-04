# -*- mode: python ; coding: utf-8 -*-

import sys
import platform

# Platform-specific settings
datas = []
if platform.system() == "Darwin":  # macOS
    datas = [('UI', 'client_side/UI')]
elif platform.system() == "Windows":  # Windows
    datas = [('UI', 'client_side\\UI')]

# Common Analysis step
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PyInstaller packing steps
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="universal2",  # Add this for universal binary
    #target_arch=None,  # Use universal2 for macOS if needed
    codesign_identity=None,  # Add macOS signing if required
    entitlements_file=None,
)
