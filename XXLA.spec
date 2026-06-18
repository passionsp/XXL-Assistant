# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('imgs', 'imgs'), ('config', 'config')],
    hiddenimports=['core.tasks.login_task', 'core.tasks.guild_reward_task', 'core.tasks.peiyu_task', 'core.tasks.shiji_task', 'core.tasks.dailytask_task', 'core.tasks.sausage_task', 'core.tasks.invite_task', 'core.tasks.base_task', 'core.controller', 'core.recognizer', 'gui.main_window', 'gui.settings_dialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='XXLA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
