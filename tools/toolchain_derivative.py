"""Select one explicitly reviewed host derivative of frozen toolchain pins."""
import copy
import hashlib
import json
import os
import stat
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'tools/host-toolchain-derivative.json'
UI_PARENT = ROOT / 'tools/ui-host-toolchain.json'
QUINT_PARENT = ROOT / 'tools/quint-toolchain.json'
ELF_DELTAS = frozenset({
    '/usr/lib/x86_64-linux-gnu/libX11.so.6.4.0',
    '/usr/lib/x86_64-linux-gnu/libX11-xcb.so.1.0.0',
    '/usr/lib/x86_64-linux-gnu/libbz2.so.1.0.4',
})


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_profile(packet, ui, quint, ui_hash, quint_hash, allowed):
    if (set(packet) != {'schema', 'profile', 'parents', 'uiElfChanges', 'quint'}
            or type(packet['schema']) is not int or packet['schema'] != 1 or packet['profile'] != 'host-20261102'
            or packet['parents'] != {'ui': ui_hash, 'quint': quint_hash}
            or set(packet['uiElfChanges']) != set(allowed)
            or set(packet['quint']) != {'files', 'treeSHA256'}
            or type(packet['quint']['files']) is not int or packet['quint']['files'] <= 0
            or quint['schema'] != 1 or quint['backend'] != 'typescript'):
        raise RuntimeError('Unexpected host toolchain derivative')
    new_ui, new_quint = copy.deepcopy(ui), copy.deepcopy(quint)
    for name, change in packet['uiElfChanges'].items():
        if (set(change) != {'before', 'after'} or name not in ui['elfInputs']
                or change['before'] != ui['elfInputs'][name]['sha256']
                or change['after'] == change['before']):
            raise RuntimeError('Unexpected host ELF derivative')
        new_ui['elfInputs'][name]['sha256'] = change['after']
    new_quint.update(packet['quint'])
    return new_ui, new_quint


def read_regular(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise RuntimeError('Expected regular toolchain manifest')
            data = stream.read()
            after = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise RuntimeError('Toolchain manifest changed while reading')
        return data
    except OSError as error:
        raise RuntimeError('Expected regular toolchain manifest') from error


def selected():
    profile_bytes, ui_bytes, quint_bytes = (read_regular(path) for path in (PROFILE, UI_PARENT, QUINT_PARENT))
    profile_hash, ui_hash, quint_hash = (hashlib.sha256(data).hexdigest() for data in (profile_bytes, ui_bytes, quint_bytes))
    packet = json.loads(profile_bytes)
    if (ui_hash != 'f53770c47929e28b50ddc7c2c0b5cb2315d90003983446be6c325b7dd0708a14'
            or quint_hash != '09c0bc0338db4ee189bdbb17a9b54d53992abf442f023691eea690a4ce9bc0b4'):
        raise RuntimeError('Historical toolchain parent changed')
    ui, quint = validate_profile(packet, json.loads(ui_bytes), json.loads(quint_bytes),
                                 ui_hash, quint_hash, ELF_DELTAS)
    hashes = [packet['quint']['treeSHA256']]
    hashes.extend(change['after'] for change in packet['uiElfChanges'].values())
    if any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value) for value in hashes):
        raise RuntimeError('Invalid derivative digest')
    identity = {'profile': packet['profile'], 'derivativeSHA256': profile_hash,
                'uiParentSHA256': ui_hash, 'quintParentSHA256': quint_hash}
    return ui, quint, identity
