# -*- mode: python ; coding: utf-8 -*-

data_files = [
('audio/Readme.md','audio'),
('htmlResources/buttons', 'htmlResources/buttons'),
('htmlResources/css', 'htmlResources/css'),
('htmlResources/fonts', 'htmlResources/fonts'),
('htmlResources/icons', 'htmlResources/icons'),
('htmlResources/images/Readme.md', 'htmlResources/images'),
('htmlResources/js', 'htmlResources/js'),
('htmlResources/lib', 'htmlResources/lib'),
('htmlResources/material', 'htmlResources/material'),
('htmlResources/*.png', 'htmlResources'),
('htmlResources/*.html', 'htmlResources'),
('lang','lang'),
('macros','macros'),
('marvelData/bibles/KJV.bible','marvelData/bibles'),
('marvelData/bibles/NET.bible','marvelData/bibles'),
('marvelData/books','marvelData/books'),
('marvelData/commentaries','marvelData/commentaries'),
('marvelData/data','marvelData/data'),
('marvelData/devotionals','marvelData/devotionals'),
('marvelData/lexicons','marvelData/lexicons'),
('marvelData/*.sqlite','marvelData'),
('music','music'),
('notes','notes'),
('plugins','plugins'),
('pyinstaller/disabled_modules.txt','.'),
('pyinstaller/enable_binary_execution_mode','.'),
('pyinstaller/config.ini','.'),
('thirdParty/dictionaries','thirdParty/dictionaries'),
('video','video'),
('workspace','workspace'),
('UniqueBibleAppVersion.txt','.'),
('latest_changes.txt','.'),
]

hidden_imports = [
'markdown','html5lib','htmldocx','python-docx','pillow','gTTS','markdownify',
'nltk','textract','tabulate','sqlite3',
'config','gdown','babel','requests','qtpy','mammoth','qrcode','PySide6','pygithub',
'diff_match_patch','langdetect','qt-material','html-text','python-vlc','yt-dlp','pydnsbl'
]

excluded_modules = [
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UBA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pyinstaller/UniqueBibleApp_blue.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UBA'
)
