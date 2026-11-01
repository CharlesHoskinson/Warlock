"""Verify the private WebKit link inputs without loading or running the engine."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools/ui-host-toolchain.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify():
    if MANIFEST.is_symlink() or not MANIFEST.is_file():
        raise RuntimeError('Expected regular UI toolchain manifest')
    packet = json.loads(MANIFEST.read_text())
    sdk = Path(packet['sdkDirectory'])
    if packet['schema'] != 1 or sdk != Path('/home/charl/.cache/warlock-ui-host/sdk') or sdk.resolve() != sdk:
        raise RuntimeError('Unexpected private UI SDK')
    observed = {}
    for path in sorted(sdk.rglob('*')):
        rel = str(path.relative_to(sdk))
        if path.is_symlink():
            observed[rel] = {'symlink': os.readlink(path), 'resolvedSHA256': digest(path) if path.is_file() else None}
        elif path.is_file():
            observed[rel] = {'sha256': digest(path), 'mode': oct(path.stat().st_mode & 0o777), 'bytes': path.stat().st_size}
    if observed != packet['files']:
        raise RuntimeError('Private UI SDK differs from the reviewed inventory')
    for name, expected in packet['elfInputs'].items():
        path = Path(name)
        if path.is_symlink() or not path.is_file() or digest(path) != expected['sha256']:
            raise RuntimeError('UI linked dependency changed: ' + name)
    return {'manifestSHA256': digest(MANIFEST), 'sdkFiles': len(observed),
            'elfInputs': len(packet['elfInputs']), 'libraryDirectory': packet['libraryDirectory'],
            'scope': 'Pinned build/link inputs only; no engine or native execution'}
