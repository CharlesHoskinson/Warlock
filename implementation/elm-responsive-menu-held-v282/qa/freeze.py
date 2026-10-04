import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-gui-bounds-held-v280/acceptance-manifest.json';assert sha(parent)=='803d21b080df49b90e6f4272975d2c32456006ec5cbb22682a4d2332c967954b';pair=json.loads(parent.read_text())['nativePair']
reports=[]
for name,passed in [('elm-responsive-full-menu-v281',True)]:
 p=next((REPO/'implementation'/name/'qa').glob('native-*/report.json'));m=json.loads(p.read_text());assert m['passed']==passed and m['cleanupPassed'] and not m['inputChanges'] and m['pair']==pair
 for path,digest in m['inputs'].items():assert sha(path)==digest
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':passed,'checks':len(m['checks']),'cleanupPassed':True})
 if passed:
  assert all(c['passed'] for c in m['checks']) and len(m['checks'])==89 and m['privateHost']['runtimeGone'] and not m['privateHost'].get('unexpectedInnerDescendants')
  accepted=len(m['checks'])
files=[]
for name in ['elm-responsive-full-menu-v281',ROOT.name]:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'acceptance-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':True,'acceptedGuiBoundsProfileCount':22,'parentGuiBoundsNativeCheckCount':893,'acceptedCurrentGuiFullMenuNativeCheckCount':accepted,'currentGuiGeneralRegressionAccepted':False,'currentRendererRecoveryAccepted':False,'pendingUnknownReconciliationAccepted':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativePair':pair,'reports':reports,'files':files,'scope':'Original26089 fullmenu native assertions/deadlines replayed on actual CSS-corrected278 with standard private bus normalcleanup. Parent280893/22 bounds holds same actualGUI tuple. All473 generalGUI/cohort40 recovery not yet rerun on278; fullroadmap/release remain separate'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedCurrentGuiFullMenuNativeCheckCount':accepted,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
