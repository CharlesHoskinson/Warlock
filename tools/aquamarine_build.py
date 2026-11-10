#!/usr/bin/env python3
"""Fixed private Aquamarine QA-provider compilation; no provider invocation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import sys

BASE = '.warlock-contributor/evidence/nextloop-20261106/aquamarine-build-inputs'
MANIFEST = BASE + '/inputs.json'
MANIFEST_SHA256 = '9e7347b8903b162c9042b5be6d3b6f52b3caac962fcb3d9b194c4d444ba9feb6'
FOUNDATION = {'run_arm_nested_foundation.py': 'e4809e952f10ec61a350c9d9029f5335f49d21aa5f67a9a90b8fda79cf2ea0a6',
              'test_arm_nested_foundation.py': '3269bb0ed175875adc506eb8c10461b60e3b3b2637f4ad0f5f2343f8abeb5329'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_relative(name):
    p = Path(name)
    if not name or p.is_absolute() or '..' in p.parts or '.' == name:
        raise RuntimeError('Aquamarine relative path refused')
    return p


def plain(root, name):
    p = Path(root) / safe_relative(name)
    cursor = p
    while cursor != Path(root):
        if cursor.is_symlink():
            raise RuntimeError('Aquamarine regular input has alias')
        cursor = cursor.parent
    if not p.is_file():
        raise RuntimeError('Aquamarine input is not regular')
    return p


def check_entry(path, expected):
    path = Path(path)
    if set(expected) == {'link'}:
        if not path.is_symlink() or os.readlink(path) != expected['link']:
            raise RuntimeError('Aquamarine input alias changed')
    elif set(expected) == {'mode', 'sha256'}:
        if (path.is_symlink() or not path.is_file()
                or stat.S_IMODE(path.stat().st_mode) != expected['mode']
                or digest(path) != expected['sha256']):
            raise RuntimeError('Aquamarine input body or mode changed: ' + str(path))
    else:
        raise RuntimeError('Aquamarine input manifest entry refused')


def closed_tree(root, expected):
    root = Path(root)
    if root.is_symlink():
        raise RuntimeError('Aquamarine closed input tree is an alias')
    observed = {str(p) for p in root.rglob('*') if not p.is_dir() or p.is_symlink()}
    if observed != expected:
        raise RuntimeError('Aquamarine input tree membership changed: ' + str(root))


def validate_inputs(root):
    root = Path(root)
    manifest = plain(root, MANIFEST)
    if digest(manifest) != MANIFEST_SHA256:
        raise RuntimeError('Aquamarine supplemental input manifest changed')
    data = json.loads(manifest.read_text())
    if (data.get('schema') != 1 or data.get('base') != BASE
            or data.get('target') != 'aquamarine' or data.get('runtimeExecution') is not False
            or len(data.get('files', {})) != 4253 or len(data.get('system', {})) != 30812):
        raise RuntimeError('Aquamarine closed input schema differs')
    for name, expected in data['files'].items():
        safe_relative(name)
        if not name.startswith(BASE + '/'):
            raise RuntimeError('Aquamarine supplemental repo input escaped fixed root')
        if 'link' in expected:
            path = root / name
            if not path.resolve().is_relative_to((root / BASE).resolve()):
                raise RuntimeError('Aquamarine private alias escapes fixed root')
        else:
            plain(root, name)
        check_entry(root / name, expected)
    observed = {str(p.relative_to(root)) for p in (root / BASE).rglob('*')
                if not p.is_dir() or p.is_symlink()}
    if observed != set(data['files']) | {MANIFEST}:
        raise RuntimeError('Aquamarine unexpected supplemental input body')
    for name, expected in data['system'].items():
        if not name.startswith(('/usr/include/', '/usr/lib/', '/usr/bin/', '/usr/share/')):
            raise RuntimeError('Aquamarine supplemental system input escaped /usr')
        check_entry(name, expected)
    for directory in ('/usr/include', '/usr/lib/gcc', '/usr/lib/pkgconfig',
                      '/usr/share/pkgconfig', '/usr/share/wayland-protocols',
                      '/usr/share/wayland', '/usr/share/hwdata', '/usr/lib/cmake',
                      '/usr/share/cmake'):
        closed_tree(directory, {name for name in data['system']
                                if name.startswith(directory + '/')})
    for directory in ('/usr/local/include', '/usr/local/lib', '/usr/local/lib64'):
        closed_tree(directory, set())
    return data


def command_plan(prefix, output):
    prefix, output = Path(prefix), Path(output)
    cmake = str(prefix / 'bin/cmake')
    return [('aquamarine-configure', [cmake, '-S', str(output / 'aquamarine-source'),
             '-B', str(output / 'aquamarine-build'), '-G', 'Ninja',
             '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF',
             '-DCMAKE_MAKE_PROGRAM=' + str(prefix / 'bin/ninja'),
             '-DCMAKE_C_COMPILER=/usr/bin/cc', '-DCMAKE_CXX_COMPILER=/usr/bin/c++',
             '-DCMAKE_PREFIX_PATH=' + str(prefix),
             '-DCMAKE_INSTALL_PREFIX=' + str(output / 'unused-install-prefix')]),
            ('aquamarine-build', [cmake, '--build', str(output / 'aquamarine-build'),
                                 '--target', 'aquamarine', '--parallel', '1'])]


def foundation_controls(root, output, run):
    stage = output / 'foundation-controls'
    stage.mkdir(mode=0o700)
    for name, expected in FOUNDATION.items():
        source = plain(root, 'tools/' + name)
        if digest(source) != expected:
            raise RuntimeError('Foundation pure control source changed')
        shutil.copyfile(source, stage / name)
        if digest(stage / name) != expected:
            raise RuntimeError('Foundation staged control source changed')
    fixture = stage / 'aquamarine-0.16.0/src/backend/Backend.cpp'
    fixture.parent.mkdir(parents=True, mode=0o700)
    source = plain(root, BASE + '/source/src/backend/Backend.cpp')
    if digest(source) != '3098ed4ad3eb665c81a130bccc8e9c8a5eb181d7447811b90c2f6ede0d1e0ae6':
        raise RuntimeError('Foundation fixed Backend.cpp fixture changed')
    shutil.copyfile(source, fixture)
    run('foundation-pure-controls', [sys.executable, '-B',
        str(stage / 'test_arm_nested_foundation.py')], output, timeout=120)
    for name, expected in FOUNDATION.items():
        if digest(plain(root, 'tools/' + name)) != expected or digest(stage / name) != expected:
            raise RuntimeError('Foundation control source drifted')


def gl_controls(root, output, run):
    stage = output / 'gl-foundation-controls'
    stage.mkdir(mode=0o700)
    for name, expected in {'run_arm_gl_foundation.py': '97f7c17c249bd466ffbbf5569e5886f2cb29af16fd90c10b10f0534deae1dcb5', 'test_arm_gl_foundation.py': '6283be9a8465b73c2c6f452c3b4e9beebcdc3ad3c8fecaeab55a1bfefd211893'}.items():
        source = plain(root, 'tools/' + name)
        if digest(source) != expected:
            raise RuntimeError('Foundation pure control source changed')
        shutil.copyfile(source, stage / name)
        if digest(stage / name) != expected:
            raise RuntimeError('Foundation staged control source changed')
    fixture = stage / 'aquamarine-0.16.0/src/backend/Backend.cpp'
    fixture.parent.mkdir(parents=True, mode=0o700)
    source = plain(root, BASE + '/source/src/backend/Backend.cpp')
    if digest(source) != '3098ed4ad3eb665c81a130bccc8e9c8a5eb181d7447811b90c2f6ede0d1e0ae6':
        raise RuntimeError('Foundation fixed Backend.cpp fixture changed')
    shutil.copyfile(source, fixture)
    run('gl-foundation-pure-controls', [sys.executable, '-B',
        str(stage / 'test_arm_gl_foundation.py')], output, timeout=120)
    for name, expected in {'run_arm_gl_foundation.py': '97f7c17c249bd466ffbbf5569e5886f2cb29af16fd90c10b10f0534deae1dcb5', 'test_arm_gl_foundation.py': '6283be9a8465b73c2c6f452c3b4e9beebcdc3ad3c8fecaeab55a1bfefd211893'}.items():
        if digest(plain(root, 'tools/' + name)) != expected or digest(stage / name) != expected:
            raise RuntimeError('Foundation control source drifted')


def run_profile(root, output, packet, run):
    root, output = Path(root), Path(output)
    data = validate_inputs(root)
    foundation_controls(root, output, run)
    gl_controls(root, output, run)
    prefix = root / BASE / 'prefix/usr'
    shutil.copytree(root / BASE / 'source', output / 'aquamarine-source', symlinks=False)
    env = {'PATH': str(prefix / 'bin') + ':/usr/bin:/bin',
           'LD_LIBRARY_PATH': str(prefix / 'lib'), 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
           'HOME': str(output / 'home'), 'TMPDIR': '/tmp',
           'CMAKE_PREFIX_PATH': str(prefix), 'PKG_CONFIG_LIBDIR': '/usr/lib/pkgconfig:/usr/share/pkgconfig'}
    for name, command in command_plan(prefix, output):
        run(name, command, output, timeout=1200, extra_env=env)
    image = plain(output, 'aquamarine-build/libaquamarine.so.0.16.0')
    raw = image.read_bytes()
    if raw[:7] != b'\x7fELF\x02\x01\x01' or struct.unpack_from('<H', raw, 18)[0] != 183:
        raise RuntimeError('Aquamarine build output is not ELF64LE AArch64')
    if not 4096 < len(raw) < 134217728 or image.stat().st_mode & 0o6000:
        raise RuntimeError('Aquamarine output size or mode refused')
    validate_inputs(root)
    return {'scope': 'QA-private Aquamarine target compiled only; no image invocation',
            'target': 'aquamarine', 'sourcePatchSha256': data['sourcePatchSha256'],
            'supplementalManifestSha256': MANIFEST_SHA256,
            'image': {'path': str(image), 'sha256': digest(image), 'size': len(raw),
                      'device': image.stat().st_dev, 'inode': image.stat().st_ino,
                      'mode': stat.S_IMODE(image.stat().st_mode)},
            'executed': False, 'runtimeMappingObserved': False,
            'nativeAcceptance': False, 'inputQualified': False, 'cleanupQualified': False}
