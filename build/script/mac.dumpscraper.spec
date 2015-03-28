# -*- mode: python -*-
a = Analysis(['../../src/dumpscraper.py'],
             pathex=['/Users/tampe125/git/dumpmon-scraper'],
             hiddenimports=[
                    'sklearn.neighbors.typedefs',
                    'sklearn.utils.sparsetools._graph_validation',
                    'sklearn.utils.sparsetools._graph_tools',
                    'sklearn.utils.lgamma',
                    'scipy.special._ufuncs_cxx'
                    ],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='dumpscraper',
          debug=False,
          strip=None,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name='dumpscraper')
