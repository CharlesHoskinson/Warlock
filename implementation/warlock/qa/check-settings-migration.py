"""Production settings migration: exact originals, boundaries and seeded save routes.

Filesystem fault injection checks observable process outcomes, not power-loss proof.
"""
import copy
import json
import os
from pathlib import Path
import random
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
from endpoint import Refused
from shell_preferences import Store

checks = []
SEED = 0xDE1015


def check(name, condition):
    assert condition, name
    checks.append(name)


def legacy(base, revision='7', theme='dawn', scale=125):
    store = Store(base)
    store.read()
    active = Path(base) / 'warlock/settings.json'
    # Preserve formatting too: re-serializing the parsed value is insufficient.
    raw = ('{ "schema": 1, "revision": ' + json.dumps(revision) +
           ', "values": {"theme":' + json.dumps(theme) +
           ',"textScale":' + str(scale) + '} }\n').encode()
    active.write_bytes(raw)
    active.chmod(0o600)
    old = store.read()
    wanted = {**old, 'values': {**old['values'], 'effectsOff': True}}
    return store, active, raw, old, wanted


def refused(fn):
    try:
        fn()
    except (OSError, ValueError, Refused):
        return True
    return False


with tempfile.TemporaryDirectory(prefix='warlock-settings-migration-') as temp:
    base = Path(temp)
    store, active, raw, old, wanted = legacy(base / 'success')
    backup = active.with_name('settings.schema-1.json')
    check('Legacy read is observational', active.read_bytes() == raw and not backup.exists())
    check('Legacy no-op is observational', store.save(old) == ('Refused', old) and not backup.exists())
    stale = {**wanted, 'revision': '6'}
    check('Stale CAS does not migrate', store.save(stale) == ('Refused', old) and not backup.exists())
    invalid = copy.deepcopy(wanted)
    invalid['values']['textScale'] = True
    check('Invalid proposal does not migrate', refused(lambda: store.save(invalid)) and active.read_bytes() == raw and not backup.exists())
    real_rename = os.rename
    publication = []

    def observe(src, dst, **kwargs):
        if dst == 'settings.json':
            publication.append(backup.read_bytes() == raw)
        return real_rename(src, dst, **kwargs)

    with patch('shell_preferences.os.rename', observe):
        status, saved = store.save(wanted)
    check('Original exists before active publication', publication == [True])
    check('Explicit upgrade preserves exact original bytes', status == 'Saved' and backup.read_bytes() == raw and Store(base / 'success').read() == saved)
    check('Backup is private single-link regular file', stat.S_IMODE(backup.stat().st_mode) == 0o600 and backup.stat().st_nlink == 1)
    status, later = store.save({**saved, 'values': {**saved['values'], 'theme': 'night'}})
    check('Later current-schema saves retain first original', status == 'Saved' and backup.read_bytes() == raw and later['revision'] == '9')

    for fault in ['backup-file-sync', 'backup-publish', 'backup-unlink', 'backup-directory-sync', 'active-file-sync', 'active-rename', 'active-directory-sync']:
        store, active, raw, old, wanted = legacy(base / fault)
        backup = active.with_name('settings.schema-1.json')
        real_sync, real_link, real_unlink, real_rename = os.fsync, os.link, os.unlink, os.rename
        calls = {'file': 0, 'directory': 0}

        def sync(fd):
            kind = 'directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file'
            calls[kind] += 1
            fail = ((fault == 'backup-file-sync' and kind == 'file' and calls[kind] == 1) or
                    (fault == 'backup-directory-sync' and kind == 'directory' and calls[kind] == 1) or
                    (fault == 'active-file-sync' and kind == 'file' and calls[kind] == 2) or
                    (fault == 'active-directory-sync' and kind == 'directory' and calls[kind] == 2))
            if fail:
                raise OSError('injected ' + fault)
            return real_sync(fd)

        def link(src, dst, **kwargs):
            if fault == 'backup-publish':
                raise OSError('injected backup publish')
            return real_link(src, dst, **kwargs)

        def unlink(name, **kwargs):
            if fault == 'backup-unlink' and str(name).startswith('settings.backup.'):
                raise OSError('injected backup unlink')
            return real_unlink(name, **kwargs)

        def rename(src, dst, **kwargs):
            if fault == 'active-rename':
                raise OSError('injected active rename')
            return real_rename(src, dst, **kwargs)

        with patch('shell_preferences.os.fsync', sync), patch('shell_preferences.os.link', link), patch('shell_preferences.os.unlink', unlink), patch('shell_preferences.os.rename', rename):
            try:
                result = store.save(wanted)
            except OSError:
                result = 'raised'
        if fault == 'active-directory-sync':
            check(fault + ' is Unknown with complete new active', result == ('Unknown', None) and Store(base / fault).read()['values'] == wanted['values'] and backup.read_bytes() == raw)
        else:
            check(fault + ' preserves complete old active', result == 'raised' and active.read_bytes() == raw and Store(base / fault).read() == old)
        if fault.startswith('active-'):
            check(fault + ' retains recoverable original', backup.read_bytes() == raw)
        if fault == 'backup-directory-sync':
            check('Retry confirms existing original before upgrade', store.save(wanted)[0] == 'Saved' and backup.read_bytes() == raw)
        if fault == 'backup-unlink':
            check('Interrupted two-link publication remains recoverable', backup.read_bytes() == raw and backup.stat().st_nlink == 2)
            check('Restart refuses ambiguous hardlink without activation', refused(lambda: Store(base / fault).save(wanted)) and active.read_bytes() == raw)

    for unsafe in ['conflict', 'symlink', 'hardlink', 'shared']:
        store, active, raw, old, wanted = legacy(base / unsafe)
        backup = active.with_name('settings.schema-1.json')
        other = active.with_name('other')
        if unsafe == 'symlink':
            other.write_bytes(raw)
            backup.symlink_to(other)
        elif unsafe == 'hardlink':
            other.write_bytes(raw)
            other.chmod(0o600)
            os.link(other, backup)
        else:
            backup.write_bytes(b'foreign original' if unsafe == 'conflict' else raw)
            backup.chmod(0o644 if unsafe == 'shared' else 0o600)
        before = backup.read_bytes()
        check(unsafe + ' backup refuses without overwrite', refused(lambda: store.save(wanted)) and active.read_bytes() == raw and backup.read_bytes() == before)

    for fifo in ['settings.json', 'settings.schema-1.json']:
        store, active, raw, old, wanted = legacy(base / ('fifo-' + fifo))
        target = active.with_name(fifo)
        if target.exists():
            target.unlink()
        os.mkfifo(target, 0o600)
        child = '''import json,sys
sys.path.insert(0,sys.argv[1])
from shell_preferences import Store
from endpoint import Refused
try: Store(sys.argv[2]).save(json.loads(sys.argv[3]))
except Refused: sys.exit(0)
sys.exit(1)
'''
        result = subprocess.run([sys.executable, '-B', '-c', child, str(ROOT / 'adapter'), str(base / ('fifo-' + fifo)), json.dumps(wanted)], capture_output=True, timeout=2)
        check('Malformed FIFO refuses without blocking ' + fifo, result.returncode == 0)

    rng = random.Random(SEED)
    for case in range(100):
        store, active, raw, old, wanted = legacy(base / ('seed-' + str(case)), str(rng.randint(1, 100000)), rng.choice(['night', 'dawn', 'high-contrast']), rng.choice([100, 125, 150, 200]))
        backup = active.with_name('settings.schema-1.json')
        invalid = copy.deepcopy(wanted)
        invalid['values'][rng.choice(['effectsOff', 'reducedTransparency'])] = rng.choice([None, 0, 1, 'false'])
        check('Seeded invalid save ' + str(case), refused(lambda: store.save(invalid)) and active.read_bytes() == raw and not backup.exists())
        status, saved = store.save(wanted)
        check('Seeded valid upgrade and restart ' + str(case), status == 'Saved' and backup.read_bytes() == raw and Store(base / ('seed-' + str(case))).read() == saved)
        check('Seeded stale write preserves both copies ' + str(case), store.save(wanted) == ('Refused', saved) and backup.read_bytes() == raw)

print(json.dumps({'passed': True, 'checks': checks, 'seed': SEED, 'generatedCases': 100, 'scope': 'Actual Store with temporary filesystem and injected syscall failures; generated parameter sequences, not arbitrary interleaving fuzz; no power-loss/native/release acceptance.'}))
