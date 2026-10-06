"""Hold exact same-policy native icon lock bitmap evidence and retained failures."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path('/home/hoskinson/omarchy-windows-parity');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def proof(p,root=None):
 d=json.loads(p.read_text())
 for rel,h in d.get('inputs',{}).items():
  q=Path(rel);q=q if q.is_absolute() else root/q;assert sha(q)==h,(p,q)
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,(p,rel)
 return d
def hold(root):
 p=root/'component-manifest.json'
 if not p.exists():
  files={}
  for f in sorted(root.rglob('*')):
   rel=f.relative_to(root)
   if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
   assert not f.is_symlink(),f
   if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
  p.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 d=json.loads(p.read_text());assert d.get('passed') or (d.get('sourceHeld') and d.get('evidenceIntegrityPassed'))
 for rel,row in d['files'].items():assert sha(root/rel)==row['sha256'] and (root/rel).stat().st_size==row['size'],rel
 return {'path':str(p.relative_to(REPO)),'sha256':sha(p),'files':len(d['files'])}
root=REPO/'implementation/warlock-client-provider-native-v98';p=next(root.glob('qa/native-*/report.json'));d=proof(p);assert not d['passed'] and d['cleanupPassed'] and 'ordinaryRendered=wait' in d['traceback'] and all(x['passed'] for x in d['checks']) and all(x['exitCode']==0 for x in d['ownedExitCodes'])
pre=proof(root/'qa/preflight.json');assert pre['passed'];prep=proof(next(root.glob('qa/prepare-*/report.json')));assert prep['passed']
held=hold(root)
report={'passed':True,'scope':scope,'components':[held],'failedNativeReport':str(p),'failedNativeReportSHA256':sha(p),'nativeControlsReached':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'nativeAcceptance':False,'fullReleaseAccepted':False,'failure':'New ordinary picker did not open after pointer input during startup geometry publication change; actual visible output publication must be settled before one genuine input. Original six-second deadline retained. Source/capture grants were never fabricated; original process cleanup normal.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'failedSourceHeld':True,'files':held['files'],'normalOwnedExits':report['normalOwnedExits']}))
