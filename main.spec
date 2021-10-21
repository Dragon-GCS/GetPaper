# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.pyw'],
             pathex=['E:\\ProjectFiles\\Python\\01_Spider\\01_GetPaper'],
             binaries=[],
             datas=[(".venv/Lib/site-packages/ttkbootstrap/Symbola.ttf", "ttkbootstrap"),   # 静态文件
                    (".venv/Lib/site-packages/ttkbootstrap/themes.json", "ttkbootstrap")],  # 静态文件
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
          name='main',
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
