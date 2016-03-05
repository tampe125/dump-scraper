# -*- mode: python -*-

block_cipher = None


a = Analysis(['../../dumpscraper.py'],
             pathex=['C:\\Users\\tampe125\\Documents\\git\\dump-scraper\\build\\script'],
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
			 
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
		
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='dumpscraper.exe',
          debug=False,
          strip=None,
          upx=False,
          console=True )
