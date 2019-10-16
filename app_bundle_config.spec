# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

a = Analysis(['app.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# insert icons to the boundle
import os
rootPath = os.getcwd()
icons = []
for name in os.listdir('assets'+os.sep+'icons'):
    p = os.sep.join(['.', 'assets','icons',name])
    icons.append((p, p, 'DATA'))

a.datas += icons


# add server.py file which has to be run as a background process under CodeEdit from pyQode library
# which hanldes background work for editor
# As the app is frozen it  generates multiple windows as program try to start this code as separate
# process and launches main app accidentally because it uses app exe as interpreter

a.datas += [('./server', os.sep.join([os.getcwd(), 'dist', 'server']), 'DATA')]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='reDocWriter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )