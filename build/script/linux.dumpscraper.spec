# -*- mode: python -*-

block_cipher = None


a = Analysis(['../../dumpscraper.py'],
             pathex=['/home/tampe125/git/dump-scaper/build/script'],
             hiddenimports=[
                    'sklearn.neighbors.typedefs',
                    'sklearn.utils.sparsetools._graph_validation',
                    'sklearn.utils.sparsetools._graph_tools',
                    'sklearn.utils.lgamma',
                    'scipy.special._ufuncs_cxx'
                    ],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='dumpscraper',
          debug=False,
          strip=None,
          upx=False,
          console=True )
