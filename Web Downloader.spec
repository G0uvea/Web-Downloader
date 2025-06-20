# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('dependencies/ffmpeg/ffmpeg.exe', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/ffprobe.exe', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/ffplay.exe', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/avcodec-61.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/avdevice-61.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/avfilter-10.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/avformat-61.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/avutil-59.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/postproc-58.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/swresample-5.dll', 'dependencies/ffmpeg'), ('dependencies/ffmpeg/swscale-8.dll', 'dependencies/ffmpeg')],
    datas=[('gui/assets', 'gui/assets'), ('gui/assets/fonts', 'gui/assets/fonts'), ('config', 'config')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Web Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['gui\\assets\\icon.ico'],
)
