# -*- mode: python ; coding: utf-8 -*-

import os

# Get ttkbootstrap path dynamically
try:
    import ttkbootstrap
    ttkbootstrap_path = os.path.dirname(ttkbootstrap.__file__)
except ImportError:
    ttkbootstrap_path = None

block_cipher = None

# Build data files list dynamically
datas = []
if ttkbootstrap_path:
    datas.extend([
        (os.path.join(ttkbootstrap_path, "Symbola.ttf"), "ttkbootstrap"),  # Theme字体
        (os.path.join(ttkbootstrap_path, "themes.json"), "ttkbootstrap"),  # Theme文件
    ])
datas.append(("getpaper/translator/_api_info.json", "getpaper/translator"))  # 翻译api数据

a = Analysis(['main.pyw'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=["./hook"],  # 动态导入用
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='GetPaper',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
