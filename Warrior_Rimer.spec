# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 添加必要的路径
import os
import sys
import numpy
import pygame

# 获取当前工作目录
cwd = os.getcwd()

# 获取 NumPy 核心路径
def get_numpy_core_path():
    return os.path.join(os.path.dirname(numpy.__file__), 'core')

# 获取 Pygame 路径
def get_pygame_path():
    return os.path.dirname(pygame.__file__)

# 添加额外数据
additional_datas = []

# 添加 NumPy 核心文件
numpy_core_path = get_numpy_core_path()
if os.path.exists(numpy_core_path):
    additional_datas.append((numpy_core_path, 'numpy/core'))

# 添加 Pygame 相关文件
pygame_path = get_pygame_path()
if os.path.exists(pygame_path):
    # 添加所有 Pygame 模块
    additional_datas.append((pygame_path, 'pygame'))
    
    # 添加 Pygame 的字体和图片资源
    for subdir in ['font', 'image']:
        sub_path = os.path.join(pygame_path, subdir)
        if os.path.exists(sub_path):
            additional_datas.append((sub_path, f'pygame/{subdir}'))

a = Analysis(
    ['start_game.py'],
    pathex=[cwd, get_numpy_core_path(), get_pygame_path()],
    binaries=[],
    datas=[
        ('music/*', 'music'),
    # 打包时使用干净存档（若存在），否则现有文件
    ((os.path.exists(os.path.join(cwd, 'game_data.clean.json')) and os.path.join(cwd, 'game_data.clean.json') or os.path.join(cwd, 'game_data.json')),
     '.'),
        ('warrior_rimer.ico', '.'),  # 图标文件
        *additional_datas
    ],
    hiddenimports=[
        'numpy',
        'pygame',
        'pygame._sdl2',
        'pygame.sdl2',
        'pygame.sdl2.audio',
        'pygame.sdl2.video',
        'pygame.sdl2.rwobject',
        'pygame.sdl2.pixels',
        'pygame.sdl2.rect',
        'pygame.sdl2.surface',
        'pygame.sdl2.event',
        'pygame.sdl2.keyboard',
        'pygame.sdl2.mouse',
        'pygame.sdl2.joystick',
        'pygame.sdl2.controller',
        'pygame.sdl2.touch',
        'pygame.sdl2.gesture',
        'pygame.sdl2.clipboard',
        'pygame.sdl2.messagebox',
        'pygame.sdl2.render',
        'pygame.sdl2.sprite',
        'pygame.sdl2.image',
        'pygame.sdl2.mixer',
        'pygame.sdl2.mixer_music',
        'pygame.sdl2.time',
        'pygame.sdl2.version',
        'pygame.sdl2.sysfont',
        'pygame.sdl2.freetype',
        'pygame.sdl2.mask',
        'pygame.sdl2.pixelcopy',
        'pygame.sdl2.scrap',
        'pygame.sdl2.surfarray',
        'pygame.sdl2.macosx',
        'pygame.sdl2.windows',
        'pygame.sdl2.android',
        'pygame.sdl2.peg',
        'pygame.sdl2.timer',
        'pygame.sdl2.display',
        'pygame.sdl2.window',
        'pygame.sdl2.error',
        'pygame.sdl2.constants',
        'pygame.sdl2.ext',
        'pygame.sdl2.ext.algorithms',
        'pygame.sdl2.ext.compat',
        'pygame.sdl2.ext.draw',
        'pygame.sdl2.ext.image',
        'pygame.sdl2.ext.manager',
        'pygame.sdl2.ext.particles',
        'pygame.sdl2.ext.sprite',
        'pygame.sdl2.ext.texture',
        'pygame.sdl2.ext.transform',
        'pygame.sdl2.ext.ufo',
        'pygame.sdl2.ext.vector',
        'pygame.sdl2.ext.world',
        'pygame.sdl2.ext.xbr',
        'pygame.sdl2.ext.zip',
        'pygame.sdl2.main',
        'pygame.sdl2.test',
        'pygame.sdl2.util',
        'pygame.sdl2.video_gl',
        'pygame.sdl2.video_metal',
        'pygame.sdl2.video_vulkan',
        'pygame.sdl2.video_d3d',
        'pygame.sdl2.video_d3d11',
        'pygame.sdl2.video_d3d12',
        'pygame.sdl2.video_directfb',
        'pygame.sdl2.video_psp',
        'pygame.sdl2.video_ps2',
        'pygame.sdl2.video_ps3',
        'pygame.sdl2.video_ps4',
        'pygame.sdl2.video_ps5',
        'pygame.sdl2.video_vita',
        'pygame.sdl2.video_wii',
        'pygame.sdl2.video_wiiu',
        'pygame.sdl2.video_n3ds',
        'pygame.sdl2.video_switch',
        'pygame.sdl2.video_xbox',
        'pygame.sdl2.video_xbox360',
        'pygame.sdl2.video_xboxone',
        'pygame.sdl2.video_xboxseries',
        'pygame.sdl2.video_android',
        'pygame.sdl2.video_ios',
        'pygame.sdl2.video_tvos',
        'pygame.sdl2.video_emscripten',
        'pygame.sdl2.video_nacl',
        'pygame.sdl2.video_haiku',
        'pygame.sdl2.video_os2',
        'pygame.sdl2.video_riscos',
        'pygame.sdl2.video_amigaos',
        'pygame.sdl2.video_morphos',
        'pygame.sdl2.video_aros',
        'pygame.sdl2.video_dummy',
        'pygame.sdl2.video_offscreen',
        'pygame.sdl2.video_opengl',
        'pygame.sdl2.video_opengles',
        'pygame.sdl2.video_opengles2',
        'pygame.sdl2.video_vulkan',
        'pygame.sdl2.video_metal',
        'pygame.sdl2.video_directfb',
        'pygame.sdl2.video_psp',
        'pygame.sdl2.video_ps2',
        'pygame.sdl2.video_ps3',
        'pygame.sdl2.video_ps4',
        'pygame.sdl2.video_ps5',
        'pygame.sdl2.video_vita',
        'pygame.sdl2.video_wii',
        'pygame.sdl2.video_wiiu',
        'pygame.sdl2.video_n3ds',
        'pygame.sdl2.video_switch',
        'pygame.sdl2.video_xbox',
        'pygame.sdl2.video_xbox360',
        'pygame.sdl2.video_xboxone',
        'pygame.sdl2.video_xboxseries',
        'pygame.sdl2.video_android',
        'pygame.sdl2.video_ios',
        'pygame.sdl2.video_tvos',
        'pygame.sdl2.video_emscripten',
        'pygame.sdl2.video_nacl',
        'pygame.sdl2.video_haiku',
        'pygame.sdl2.video_os2',
        'pygame.sdl2.video_riscos',
        'pygame.sdl2.video_amigaos',
        'pygame.sdl2.video_morphos',
        'pygame.sdl2.video_aros',
        'pygame.sdl2.video_dummy',
        'pygame.sdl2.video_offscreen',
        'pygame.sdl2.video_opengl',
        'pygame.sdl2.video_opengles',
        'pygame.sdl2.video_opengles2',
        'pygame.sdl2.video_vulkan',
        'pygame.sdl2.video_metal',
        'ctypes',
        'json',
        'datetime',
        'os',
        'sys',
        'math',
        'random',
        'pyimod02_importers',
        'OpenGL',
        'numpy.uint32',
        'pygame.overlay',
        'pygame.cdrom',
        'pygame.register_quit',
        'pygame.error',
        'numpy.core.multiarray',
        'numpy.core.umath',
        'numpy.core.numeric',
        'numpy.core._dtype_ctypes',
        'numpy.core._methods',
        'numpy.core._exceptions',
        'numpy.core.fromnumeric',
        'numpy.core.defchararray',
        'numpy.core.records',
        'numpy.core.memmap',
        'numpy.core.function_base',
        'numpy.core.shape_base',
        'numpy.core.einsumfunc',
        'numpy.core._string_helpers',
        'numpy.core.arrayprint',
        'numpy.core._type_aliases',
        'numpy.core._internal',
        'numpy.core._ufunc_config',
        'numpy.core._add_newdocs',
        'numpy.core._add_newdocs_scalars',
        'numpy.core._dtype',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.core._rational_tests',
        'numpy.core._struct_ufunc_tests',
        'numpy.core._operand_flag_tests',
        'numpy.core._umath_tests',
        'numpy.core._simd',
        'numpy.core._simd_dispatch',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='WarriorRimer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='warrior_rimer.ico',  # 添加图标路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WarriorRimer',
)