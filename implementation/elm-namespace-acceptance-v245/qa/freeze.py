"""Freeze bounded namespace evidence without accepting prepared native cases."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def report(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={k:report('elm-journal-namespace-v238',k) for k in ['namespace','journal','admission','build']}
paths.update(model=report('elm-namespace-model-v241','model'),native=report('elm-namespaced-minimize-native-v240','native'),failedAdmission=report('elm-journal-namespace-v236','admission'),failedBuild=report('elm-journal-namespace-v236','build'))
data={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,d in data.items():assert d['passed']==(not k.startswith('failed')),k
for k,count in [('namespace',42),('journal',19),('admission',22),('native',59)]:
 assert len(data[k]['checks'])==count and all(c['passed'] for c in data[k]['checks']),k
 for p,h in data[k]['inputs'].items():assert sha(Path(p))==h,p
assert all(c['exitCode']==0 for c in data['build']['commands'])
for p,h in data['build']['inputs'].items():assert sha(REPO/'implementation/elm-journal-namespace-v238'/p)==h,p
assert data['model']['namedScenarios']==8 and data['model']['invariantSamples']==1000 and data['model']['maxSteps']==40
native=data['native'];assert native['cleanupPassed'] and native['operation']=='minimize' and native['faultBoundary']=='unread'
assert sha(Path(native['buildReport']))==native['buildReportSHA256']
for part in ['core','plugin']:assert sha(Path(native['pair'][part]['path']))==native['pair'][part]['sha256']
assert native['cohortCleanup'][-1]['remaining']==[]
assert [s['exitCode'] for s in native['supervisorEvents']['exits']]==[3,1]
pixels=[c for c in native['checks'] if c['name'].endswith('ActualApplicationPixelsMatchNativeMinimized')];assert len(pixels)==6
for c in pixels:assert c['redPixels']==0 if c['minimized'] else c['redPixels']>2000
capsule=json.loads((REPO/'implementation/elm-namespaced-supervisor-v239/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
def fn(p,name):return next(n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
old=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py';new=REPO/'implementation/elm-namespaced-minimize-native-v240/qa/native.py'
for name in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(old,name),include_attributes=False)==ast.dump(fn(new,name),include_attributes=False)
names=['elm-journal-namespace-v236','elm-journal-namespace-v237','elm-journal-namespace-v238','elm-namespaced-supervisor-v239','elm-namespaced-minimize-native-v240','elm-namespace-model-v241','elm-namespaced-restore-native-v242','elm-namespaced-minimize-lost-v243','elm-namespaced-restore-lost-v244','elm-namespace-acceptance-v245']
prepared=names[6:9]
for name in prepared:assert not list((REPO/'implementation'/name/'qa').glob('native-*/report.json'))
files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Instance/lifetime recovery journal isolation and ownership-qualified restartable migration, one actual unread-minimize recovery case','cpuNamespaceChecks':42,'cpuJournalChecks':19,'compiledAdmissionChecks':22,'compiledElmChecks':[20,27,30],'quintNamedScenarios':8,'quintInvariantSamples':1000,'quintMaxSteps':40,'nativeChecks':59,'nativeSelectedCases':1,'actualPixelStages':6,'cleanupPassed':True,'sealedRuntimeFiles':20,'preparedNativeCasesNotExecuted':prepared,'completedRequirementIds':[],'fullOriginalNativeRegressionAccepted':False,'legacyOwnershipProvisioningAccepted':False,'storageErrorUXAccepted':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
