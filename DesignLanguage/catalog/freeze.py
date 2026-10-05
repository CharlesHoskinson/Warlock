"""Freeze owned source and durable receipts; preserve local runtime caches separately."""
from pathlib import Path
import hashlib,json,sys,resource,stat
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
excluded={'mutable-elm-home','profile','__pycache__'}
statuses={
 'v1':'Retained compile failure: fixture case indentation',
 'v2':'Retained compile failure: exhaustive operation patterns',
 'v3':'Compiled Elm; retained CDP test expression failure',
 'v4':'Retained Historical fixture observation failure',
 'v5':'Source/token/browser qualified; initial independent finish candidate',
 'v6':'Final catalog with one bounded correction/confirmation batch'}
for version,status in statuses.items():
 root=ROOT/version
 if not root.exists():continue
 target=root/'component-manifest.json';assert not target.exists(),target
 files={};runtime=set()
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in excluded for part in rel.parts):runtime.update(part for part in rel.parts if part in excluded);continue
  if p.is_symlink():continue
  if p.is_file():files[str(rel)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 target.write_text(json.dumps({'schema':1,'status':status,'scope':scope,'files':files,'runtimeExclusions':sorted(runtime),'runtimePolicy':'Local private browser profiles and mutable copies of the separately pinned Elm package cache remain preserved locally; not source or publication inputs. Durable source snapshots, compiled artifacts, logs, screenshots and receipts are included.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 print(version,len(files))
