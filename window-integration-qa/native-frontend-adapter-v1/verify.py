"""Read-only frozen candidate preflight. Does not create socket/process/client."""
from pathlib import Path
import hashlib,json,os,stat
B=Path(__file__).resolve().parent
r=json.loads((B/'frozen-inputs.json').read_text())
for x in r['files']:
 p=Path(x['path'])
 if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256'] or stat.S_IMODE(p.stat().st_mode)!=x['mode']:raise RuntimeError('Frozen bytes/mode changed:'+str(p))
for x in r['symlinks']:
 p=Path(x['path'])
 if not p.is_symlink() or os.readlink(p)!=x['target']:raise RuntimeError('Frozen link changed:'+str(p))
print(json.dumps({'preflight':'pass','files':len(r['files']),'links':len(r['symlinks']),'manifestSHA256':hashlib.sha256((B/'frozen-inputs.json').read_bytes()).hexdigest(),'nativeExecution':False}))
