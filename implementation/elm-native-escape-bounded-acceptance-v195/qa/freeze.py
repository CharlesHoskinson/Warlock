"""Preserve bounded native Escape acceptance and every failed derivative."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=['elm-native-escape-intent-v184','elm-native-escape-runtime-v185','elm-native-escape-refinement-v186','elm-native-escape-menu-capability-v187','elm-native-escape-menu-focus-v188','elm-native-escape-current-key-v189','elm-native-escape-competing-key-v190','elm-native-escape-geometry-regression-v192','elm-native-escape-reconnect-regression-v193','elm-native-escape-geometry-closure-v194','elm-native-escape-bounded-acceptance-v195','elm-keyboardless-popup-focus-v196','elm-native-escape-current-broker-fixture-v197','elm-native-escape-current-reconnect-v198']
reports=[]
for name,count in [('elm-native-escape-menu-focus-v188',83),('elm-native-escape-geometry-closure-v194',161),('elm-native-escape-current-reconnect-v198',57)]:
 paths=list((REPO/'implementation'/name/'qa').glob('native-*/report.json'));assert len(paths)==1
 p=paths[0];m=json.loads(p.read_text());assert m['passed'] and m['cleanupPassed'] and len(m['checks'])==count and all(v['passed'] for v in m['checks'])
 assert not m['mainDesktopActions']
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'passed':True})
for name,count in [('elm-native-escape-menu-capability-v187',48),('elm-native-escape-reconnect-regression-v193',55)]:
 paths=list((REPO/'implementation'/name/'qa').glob('native-*/report.json'));assert len(paths)==1
 p=paths[0];m=json.loads(p.read_text());assert not m['passed'] and m['cleanupPassed'] and len(m['checks'])==count
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'passed':False})
for name in ['elm-native-escape-competing-key-v190','elm-native-escape-current-broker-fixture-v197']:
 p=REPO/'implementation'/name/'component-manifest.json';m=json.loads(p.read_text());assert m['passed'] and len(m['files'])>=30
 for row in m['files']:
  q=p.parent/row['path']
  if 'symlink' in row:assert q.is_symlink() and os.readlink(q)==row['symlink']
  else:assert sha(q)==row['sha256']
for name in ['elm-native-escape-intent-v184','elm-native-escape-refinement-v186','elm-native-escape-current-key-v189']:
 p=next((REPO/'implementation'/name/'qa').glob('mutations-*/report.json'));assert not json.loads(p.read_text())['passed']
model=REPO/'implementation/elm-native-escape-order-model-v183/component-manifest.json';assert json.loads(model.read_text())['passed']
files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(p))
  files.append(row)
assert len(files)>1500
manifest={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedNativeAcceptance':True,'nativeEscapeAcceptance':True,'keyboardFocusLossAcceptance':True,'keyboardCapabilityLossAcceptance':False,'acceptedNativeCheckCount':301,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'modelManifest':str(model),'modelManifestSHA256':sha(model),'reports':reports,'files':files,'scope':'Actual Escape190/native focus83/joint geometry161/current broker reconnect57 on Core470/plugin471/AQ155; actual cap restoration48 and source-binding/control preparation failures preserved, full release remains open'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedNativeChecks':301,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
