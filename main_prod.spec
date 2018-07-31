# -*- mode: python -*-

block_cipher = None

spec_root = os.path.abspath(SPECPATH)

a = Analysis(['main.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[ ('settings/config.ini', 'settings') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='cmoncli',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
