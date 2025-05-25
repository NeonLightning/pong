# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['pong.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy.distutils',
        'numpy.testing',
        'pkg_resources._vendor.jaraco.functools',
        'pkg_resources._vendor.jaraco.context',
        'pkg_resources._vendor.jaraco.text',
        'importlib_resources.trees',
        'psutil',
        'tkinter',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pong',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Changed to False to make it windowed by default
    disable_window_close=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)