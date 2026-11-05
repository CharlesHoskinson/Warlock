"""Verify separately reviewed local ARM inputs; historical pins stay unchanged."""
import hashlib
import json
import os
import platform
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools/arm64-toolchain.json'
CACHE = Path('/home/hoskinson/.local/share/warlock-toolchain')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(directory):
    if directory.is_symlink() or not directory.is_dir() or directory.resolve() != directory:
        raise RuntimeError('ARM input directory is not canonical: ' + str(directory))
    rows = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            rows[str(path.relative_to(directory))] = {'link': os.readlink(path)}
        elif path.is_file():
            rows[str(path.relative_to(directory))] = {
                'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
        elif not path.is_dir():
            raise RuntimeError('Unexpected special ARM input: ' + str(path))
    return {'files': len(rows), 'sha256': hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}


def verify(full=False):
    if MANIFEST.is_symlink() or not MANIFEST.is_file() or platform.machine() != 'aarch64':
        raise RuntimeError('Expected reviewed ARM toolchain on aarch64')
    packet = json.loads(MANIFEST.read_text())
    fixed = {'elm': '/home/hoskinson/.local/share/mise/installs/node/26.13.0/lib/node_modules/elm/bin/elm',
             'node': '/home/hoskinson/.local/share/mise/installs/node/26.13.0/bin/node',
             'ghcPrefix': str(CACHE / 'ghc-9.6.7'), 'cabal': str(CACHE / 'cabal-3.12.1.0/cabal'),
             'elmHome': str(CACHE / 'elm-cache'), 'dependencies': str(CACHE / 'dependencies/source')}
    if packet.get('schema') != 1 or packet.get('profile') != 'omarchy-arm64-20261105' or any(packet.get(k) != v for k, v in fixed.items()):
        raise RuntimeError('Unexpected ARM toolchain selection')
    expected_trees = {fixed['ghcPrefix'], fixed['elmHome'], fixed['dependencies']}
    if set(packet['trees']) != expected_trees:
        raise RuntimeError('Incomplete ARM input tree selection')
    required_files = {fixed['elm'], fixed['node'], fixed['cabal'], str(CACHE / 'provenance.json'),
                      str(CACHE / 'dependencies/preparation.json'), str(CACHE / 'cabal-config'),
                      str(CACHE / 'system-build-inputs.json'), '/etc/ld.so.cache',
                      '/etc/passwd', '/etc/group', '/etc/nsswitch.conf'}
    if set(packet['files']) != required_files or packet.get('systemInputs') != str(CACHE / 'system-build-inputs.json'):
        raise RuntimeError('Incomplete ARM input file selection')
    parents = {'tools/haskell-toolchain.json', 'tools/ui-host-toolchain.json',
               'tools/elm-http-dependencies.json', 'tools/haskell-dependencies.json'}
    if set(packet['parents']) != parents or any(digest(ROOT / name) != sha for name, sha in packet['parents'].items()):
        raise RuntimeError('Historical ARM recipe parent changed')
    for name, sha in packet['files'].items():
        path = Path(name)
        if path.is_symlink() or not path.is_file() or digest(path) != sha:
            raise RuntimeError('ARM input file differs: ' + name)
    for name, expected in packet['trees'].items():
        if (full or name == fixed['elmHome']) and inventory(Path(name)) != expected:
            raise RuntimeError('ARM input tree differs: ' + name)
    if full:
        system = json.loads(Path(packet['systemInputs']).read_text())
        for name, expected in system['files'].items():
            path = Path(name)
            if not name.startswith(('/usr/bin/', '/usr/lib/', '/usr/include/')):
                raise RuntimeError('Unexpected system build input')
            if 'link' in expected:
                actual = {'link': os.readlink(path)} if path.is_symlink() else None
            else:
                actual = ({'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
                          if path.is_file() and not path.is_symlink() else None)
            if actual != expected:
                raise RuntimeError('System ARM build input differs: ' + name)
    packet['compiler'] = packet['elm']
    packet['compilerSHA256'] = packet['files'][packet['elm']]
    packet['manifestSHA256'] = digest(MANIFEST)
    return packet
