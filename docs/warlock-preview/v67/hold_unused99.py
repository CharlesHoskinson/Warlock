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
root=REPO/'implementation/warlock-client-provider-native-v99';pre=proof(root/'qa/preflight.json');prep=proof(next(root.glob('qa/prepare-*/report.json')));assert pre['passed'] and prep['passed'] and not list(root.glob('qa/native-*/report.json'))
held=hold(root)
report={'passed':True,'scope':scope,'components':[held],'unusedPreparation':True,'nativeLaunched':False,'sourceCopyOrderingFailed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'explanation':'The local copy tried to read native98 manifest before its protected holder ended.99 contained copied98 source and ran CPU preparation only, without the intended new ancestry/input patch. Both preparation and actual copy failure are retained;99 is unused and never qualifies anything. Fresh100 was assigned from terminal held98 and records the intended owner/parent/stimulus.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'unusedPreparedSourceHeld':True,'files':held['files'],'nativeLaunched':False}))
