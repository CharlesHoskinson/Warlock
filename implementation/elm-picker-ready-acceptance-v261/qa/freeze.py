import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=REPO/'implementation/elm-picker-ready-source-held-v238/source-manifest.json';m=json.loads(source.read_text());assert sha(source)=='078c5f6f090a94f023b0c75b0ed643244860bcf9eceb5388f72884bad79370ff' and m['passed'] and m['compiled']
for row in m['files']:assert sha(REPO/row['path'])==row['sha256']
pair=json.loads((REPO/'implementation/elm-picker-ready-runtime-v239/qa/build-pair-manifest.json').read_text())['nativePair'];reports=[];count=0
for name,expected in [('elm-picker-ready-capability-v256',83),('elm-picker-ready-focus-v257',83),('elm-picker-ready-geometry-v258',161),('elm-picker-ready-reconnect-v259',57),('elm-picker-ready-full-menu-v260',89)]:
 candidates=list((REPO/'implementation'/name/'qa').glob('native-*/report.json'));assert len(candidates)==1;p=candidates[0];m=json.loads(p.read_text());assert m['passed'] and m['cleanupPassed'] and m['pair']==pair and len(m['checks'])==expected and all(v['passed'] for v in m['checks']) and not m['mainDesktopActions']
 for path,digest in m['inputs'].items():assert sha(path)==digest,path
 for relative,digest in m['artifacts'].items():assert sha(p.parent/relative)==digest,relative
 assert m['buildReportSHA256']==sha(REPO/'implementation/elm-picker-ready-gui-v231/qa/build-1791142801917720234/report.json')
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True,'checks':expected,'cleanupPassed':True});count+=expected
assert count==473
failed=[]
for name in ['elm-picker-ready-renderer-native-v241','elm-picker-ready-geometry-v244','elm-picker-ready-reconnect-v245']:
 p=next((REPO/'implementation'/name/'qa').glob('native-*/report.json'));m=json.loads(p.read_text());assert not m['passed'] and m['cleanupPassed'];assert not m.get('inputChanges')
 for relative,digest in m['artifacts'].items():assert sha(p.parent/relative)==digest
 for path,digest in m['inputs'].items():assert sha(path)==digest
 failed.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':False,'checksReached':len(m['checks']),'error':m['error'],'cleanupPassed':True})
 if name.endswith('v241'):assert m['faultInjection']['signal']=='SIGKILL' and m['checks'][4]['name']=='pickerSelectionEmitsActivate' and m['checks'][5]['name']=='beforeFailureActualApplicationKeyboardRecipient' and m['checks'][4]['passed'] and m['checks'][5]['passed']
roots=[Path(row['path']).parts[1] for row in json.loads(source.read_text())['files']];roots=sorted(set(roots+['elm-picker-ready-runtime-v239','elm-picker-ready-broker-fixture-v240','elm-picker-ready-renderer-native-v241','elm-picker-ready-capability-v242','elm-picker-ready-focus-v243','elm-picker-ready-geometry-v244','elm-picker-ready-reconnect-v245','elm-picker-ready-full-menu-v246','elm-picker-ready-broker-fixture-v248','elm-picker-ready-broker-fixture-v255','elm-picker-ready-capability-v256','elm-picker-ready-focus-v257','elm-picker-ready-geometry-v258','elm-picker-ready-reconnect-v259','elm-picker-ready-full-menu-v260',ROOT.name]))
files=[]
for name in roots:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'acceptance-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':True,'acceptedGuiNativeCheckCount':count,'rendererRecoveryAccepted':False,'rendererFaultReached':True,'pickerActivationAccepted':True,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'nativePair':pair,'sourceManifest':str(source.relative_to(REPO)),'sourceManifestSHA256':sha(source),'reports':reports,'failedReports':failed,'files':files,'scope':'Actual compiled231 choice/focus join and five bounded native GUI campaigns473 on owning205/206/AQ155; real picker activation and keyboard recipient confirmed before241 renderer exit deadline failure; no full recovery/toolkit/hardware/ATIME/roadmap/release acceptance'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedGuiNativeCheckCount':count,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
