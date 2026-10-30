"""Abrupt process exit at actual Store syscall boundaries, then real reopen.

The child exits deliberately without Python finally/atexit cleanup. This tests
process interruption, not storage power loss or the native settings journey.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
from endpoint import Refused
from shell_preferences import Store

CHILD = r'''
import json,os,stat,sys
sys.path.insert(0,sys.argv[1])
from shell_preferences import Store
point=sys.argv[3]
real_sync,real_link,real_unlink,real_rename=os.fsync,os.link,os.unlink,os.rename
counts={'file':0,'directory':0}
def sync(fd):
 kind='directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file'
 counts[kind]+=1
 if point=='before-'+kind+'-'+str(counts[kind]):os._exit(85)
 result=real_sync(fd)
 if point=='after-'+kind+'-'+str(counts[kind]):os._exit(85)
 return result
def link(src,dst,**kwargs):
 result=real_link(src,dst,**kwargs)
 if point=='after-backup-link':os._exit(85)
 return result
def unlink(name,**kwargs):
 result=real_unlink(name,**kwargs)
 if point=='after-backup-unlink' and name.startswith('settings.backup.'):os._exit(85)
 return result
def rename(src,dst,**kwargs):
 result=real_rename(src,dst,**kwargs)
 if point=='after-active-rename':os._exit(85)
 return result
os.fsync,os.link,os.unlink,os.rename=sync,link,unlink,rename
Store(sys.argv[2]).save(json.loads(sys.argv[4]))
# Every chosen exit must be reached, never mistake normal completion for a cut.
os._exit(86)
'''

checks = []

def check(name, condition):
    assert condition, name
    checks.append(name)

points = ['before-file-1', 'after-file-1', 'after-backup-link',
          'after-backup-unlink', 'before-directory-1', 'after-directory-1',
          'before-file-2', 'after-file-2', 'after-active-rename',
          'before-directory-2', 'after-directory-2']
with tempfile.TemporaryDirectory(prefix='warlock-settings-process-cuts-') as temp:
    for point in points:
        base = Path(temp) / point
        store = Store(base)
        store.read()
        active = base / 'warlock/settings.json'
        raw = b'{ "schema":1, "revision":"7", "values":{"theme":"dawn","textScale":125} }\n'
        active.write_bytes(raw)
        active.chmod(0o600)
        old = store.read()
        wanted = {**old, 'values': {**old['values'], 'effectsOff': True}}
        child = subprocess.run([sys.executable, '-B', '-c', CHILD,
                                str(ROOT / 'adapter'), str(base), point,
                                json.dumps(wanted)], capture_output=True, timeout=5)
        check(point + ': actual abrupt child exit reached', child.returncode == 85 and child.stdout == b'' and child.stderr == b'')
        reopened = Store(base)
        actual = reopened.read()
        backup = active.with_name('settings.schema-1.json')
        published = point in ['after-active-rename', 'before-directory-2', 'after-directory-2']
        expected = {**wanted, 'revision': '8'} if published else old
        check(point + ': complete expected visible active recovered', actual == expected)
        check(point + ': disk bytes form a complete validated JSON image', json.loads(active.read_bytes())['schema'] == (2 if published else 1))
        if published:
            check(point + ': exact original retained after active rename', backup.read_bytes() == raw)
        else:
            check(point + ': original active bytes unchanged', active.read_bytes() == raw)
        if point == 'after-backup-link':
            check(point + ': interrupted publication has two links', backup.read_bytes() == raw and backup.stat().st_nlink == 2)
            try:
                reopened.save(wanted)
            except Refused:
                blocked = True
            else:
                blocked = False
            check(point + ': restart save fails closed with original active', blocked and active.read_bytes() == raw)
        elif not published:
            status, saved = reopened.save(wanted)
            check(point + ': explicit retry succeeds after other pre-rename cuts', status == 'Saved' and saved['revision'] == '8' and backup.read_bytes() == raw)
        else:
            check(point + ': stale retry cannot repeat write', reopened.save(wanted) == ('Refused', actual) and backup.read_bytes() == raw)

print(json.dumps({'passed': True, 'checks': checks, 'cutPoints': points,
                  'scope': 'Actual store, abrupt child os._exit(85) without Python cleanup, complete visible files after reopen; not hardware power-loss/durability proof or native/release acceptance.'}))
