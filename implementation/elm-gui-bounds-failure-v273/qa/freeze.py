import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports=[]
for version in (270,272):
 for p in sorted((REPO/f'implementation/elm-gui-bounds-native-v{version}/qa').glob('native-*/report.json')):
  r=json.loads(p.read_text())
  for name,digest in r['inputs'].items():assert sha(name)==digest,name
  for name,digest in r['artifacts'].items():assert sha(p.parent/name)==digest,name
  reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':r['passed'],'checks':len(r['checks']),'profiles':len(r.get('guiProfilePolicies',[])),'cleanupPassed':r['cleanupPassed'],'error':r.get('error')})
assert [r['passed'] for r in reports]==[False,True,True,False]
assert [r['profiles'] for r in reports]==[14,14,6,1]
assert reports[-1]['cleanupPassed'] and reports[-1]['error']=="AssertionError('GUI control clipped')"
files=[]
for name in ['elm-gui-bounds-contract-v268',*[f'elm-gui-bounds-native-v{v}' for v in range(269,273)],ROOT.name]:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'failure-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(p))
  files.append(row)
r={'passed':True,'failureEvidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'reports':reports,'files':files,'next':'Correct actual SurfaceRenderer bar CSS selector and constrain long labels in a fresh derivative; retain whole-control visibility,22 profile contracts and all original deadlines. Standard portal/AT lifecycle remains separate.'}
with (ROOT/'failure-manifest.json').open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'failure-manifest.json')}))
