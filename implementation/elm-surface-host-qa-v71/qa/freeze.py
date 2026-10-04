"""Close the reviewed dual-view source/proof lineage; protected scope required."""
import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3]
ROOTS=[REPO/'implementation'/n for n in ['elm-surface-host-v68','elm-surface-host-qa-v69','elm-surface-host-v70','elm-surface-host-qa-v71','elm-surface-launch-qa-v72']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
component=ROOTS[2];build=component/'qa/build-1791080854607227335/report.json';checks=component/'qa/checks-1791080984463276286/report.json'
for p in [build,checks]:
 d=json.loads(p.read_text());assert d['passed']
 for rel,h in d['inputs'].items():assert sha(component/rel)==h,rel
b=json.loads(build.read_text());assert sha(build.parent/'elm-host')==b['binarySHA256']
assert json.loads(checks.read_text())['typedChecks']==31 and json.loads(checks.read_text())['presentationChecks']==12
native=[ROOTS[3]/'qa/native-1791080972790732142/report.json',ROOTS[4]/'qa/native-1791081087340990598/report.json']
for p,count in zip(native,[20,32]):
 d=json.loads(p.read_text());assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks'])
 for path,h in d['inputs'].items():assert sha(Path(path))==h,path
 assert d['buildReportSHA256']==sha(build)
 import re
 log=(p.parent/'native-evidence/elm-webview.log').read_text()
 geometries=re.findall(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',log)
 assert geometries and all(tuple(map(int,g))==(50,48,700,420) for g in geometries)
 assert 'backend-exit: waited=1 normal=1 code=0' in log and 'host-exit: failure=0 rendered=1' in log
old=ROOTS[1]/'qa/native-1791080749344163247/report.json';assert not json.loads(old.read_text())['passed']
model=REPO/'implementation/elm-surface-controller-v67/spec/surfaces.qnt';assert sha(model)=='c09ec5eff5b3e2e4bf8ced2216df49c08e9debe3a6e82735a48b884a3574ca5f'
for root in ROOTS:
 files={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and 'elm-stuff' not in p.parts and p.name!='slice-manifest.json'}
 manifest={'passed':True,'observedUnix':time.time(),'scope':'Source/proof closure; accepted candidate isV70 with boundedV71/V72 native evidence; V68/V69 failures preserved','wholeFeatureAccepted':False,'completedRequirementIds':[],'compiledControllerChecks':31,'compiledPresentationChecks':12,'retainedEffectChecks':20,'retainedShellChecks':27,'cTestGroups':4,'nativeChecks':[20,32],'nativeRole':'xdg_popup','configure':[50,48,700,420],'quintInheritedModelSHA256':sha(model),'newQuintRun':False,'files':files}
 (root/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(root/'qa/slice-manifest.json')
