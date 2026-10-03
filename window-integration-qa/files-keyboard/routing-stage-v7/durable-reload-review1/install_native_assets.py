#!/usr/bin/env python3
"""Root-agent reviewed command: install only fresh user-owned native assets; no process input."""
from pathlib import Path
import hashlib,json,os,shutil,tempfile
B=Path(__file__).resolve().parent
manifest=json.loads((B/'frozen-inputs.json').read_text())
for item in manifest['files']:assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
plan=json.loads((B/'source-plan.json').read_text());target=Path(plan['nativeDestination'])
assert not target.exists(), 'Never overwrite a native module URL'
for item in plan['nativeFiles']:assert hashlib.sha256((B/'native'/item['path']).read_bytes()).hexdigest()==item['sha256']
target.parent.mkdir(parents=True,exist_ok=True)
working=Path(tempfile.mkdtemp(prefix='.native-stage-',dir=target.parent))
try:
 for item in plan['nativeFiles']:
  p=working/item['path'];shutil.copyfile(B/'native'/item['path'],p);p.chmod(0o755 if p.suffix=='.so' else 0o644)
 working.chmod(0o755)
 assert not target.exists();os.rename(working,target)
finally:
 if working.exists():shutil.rmtree(working)
print(json.dumps({'destination':str(target),'fresh':True,'files':plan['nativeFiles'],'globalPackagesChanged':False,'processesSignalled':False}))
