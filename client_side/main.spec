# -*- mode: python ; coding: utf-8 -*-

import sys
import platform

# Platform-specific settings
datas = []
if platform.system() == "Darwin":  # macOS
    datas = [('UI', 'client_side/UI')]
elif platform.system() == "Windows":  # Windows
    datas = [('UI', 'client_side\\UI')]
elif platform.system() == "Linux":  # Linux
    datas = [('UI', 'client_side/UI')]  # Linux uses forward slashes for paths

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
    target_arch=None,  # No universal binary for Linux
    codesign_identity=None,  # Signing is not required for Linux
    entitlements_file=None,
)
