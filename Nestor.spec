# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

ui_files = [
    ('nestor/ui/*.ui', 'nestor/ui'),
    ('nestor/ui/kea-icon.png', 'nestor/ui'),
]

nestor_files = [
    ('nestor/settings.yaml', 'nestor'),
]

data_files = [
    ('nestor/datasets/*.csv', 'nestor/datasets'),
]

added_files = ui_files + nestor_files + data_files

a = Analysis(['nestor/ui/Nestor.py'],
             pathex=['/home/tbsexton/Documents/Projects/DiagnosticKB/Nestor'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
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
          [],
          exclude_binaries=True,
          name='Nestor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Nestor')
