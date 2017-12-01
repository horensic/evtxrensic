# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\..\\..\\..\\..\\L.SeonHo\\Desktop\\\xb0\xed\xb7\xc1\xb4\xeb\xc7\xd0\xb1\xb3 CIST\\KDFS 2017 challenge\\evtxrensic\\evtxrensic.py'],
             pathex=['C:\\Users\\LED39~1.SEO\\Desktop\\\xb0\xed\xb7\xc1\xb4\xeb~1\\KDFS20~1\\EVTXRE~1'],
             binaries=[],
             datas=[],
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
          name='evtxrensic',
          debug=False,
          strip=False,
          upx=True,
          console=True , uac_admin=True)
