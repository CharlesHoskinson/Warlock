#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent
records=json.loads((B/'primary-provenance.json').read_text())['records'];checks=[]
for r in records:
 local=B/r['path'];o=r['origin'];data=local.read_bytes()
 assert hashlib.sha256(data).hexdigest()==r['sha256']
 assert format(local.stat().st_mode&0o777,'04o')==r['mode']
 if 'git' in o:original=subprocess.check_output(['git','show',o['commit']+':'+o['path']],cwd=o['git']);mode=None
 else:
  original=Path(o['file']).read_bytes();mode=format(Path(o['file']).stat().st_mode&0o777,'04o');assert mode==r['mode']
 assert original==data
 checks.append({'path':r['path'],'sourceBytesExact':True,'declaredModeExact':True})
print(json.dumps({'result':'PASS','sourceRecords':len(checks),'nativeAuthorized':False,'checks':checks},indent=2))
