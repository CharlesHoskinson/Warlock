"""Freeze two actual post-commit journal-read refusals and six pixel/input stages."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[('minimize','elm-storage-settlement-minimize-v263',45,True),('restore','elm-storage-settlement-restore-v264',47,False)]
paths={k:next((REPO/'implementation'/name/'qa').glob('native-*/report.json')) for k,name,*_ in cases}
paths['upstream']=REPO/'implementation/elm-storage-qualified-v262/qa/slice-manifest.json'
data={k:json.loads(p.read_text()) for k,p in paths.items()};assert all(d['passed'] for d in data.values())
def fn(p,name):return next(n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
old=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py';reference=None;rows=[]
for key,name,count,minimized in cases:
 d=data[key];assert d['cleanupPassed'] and len(d['checks'])==count and all(c['passed'] for c in d['checks'])
 for p,h in d['inputs'].items():assert sha(Path(p))==h,p
 assert sha(Path(d['buildReport']))==d['buildReportSHA256']
 for part in ['core','plugin']:assert sha(Path(d['pair'][part]['path']))==d['pair'][part]['sha256']
 identity=(d['buildReportSHA256'],d['pair']['core']['sha256'],d['pair']['plugin']['sha256'])
 if reference is None:reference=identity
 else:assert identity==reference
 assert d['operation']==key and d['stateBeforeRecovery']['expectedMinimized']==minimized
 fault=d['operationFaultMarker'];assert fault['outcome']['status']=='Committed' and fault['durableRecord']['status']=='Pending'
 assert d['settlementFailure']['pendingRecord']['status']=='Pending' and d['settlementFailure']['sameHost'] and d['settlementFailure']['noAutomaticReplay'] and d['settlementFailure']['evidencePreserved']
 assert len(d['supervisorEvents']['starts'])==1 and len(d['supervisorEvents']['exits'])==1 and d['supervisorEvents']['exits'][0]['exitCode']==0 and not d['supervisorEvents']['exits'][0]['forced']
 assert d['cohortCleanup'][-1]['remaining']==[]
 pixels=[c for c in d['checks'] if c['name'].endswith('ActualApplicationPixelsMatchNativeMinimized')];assert len(pixels)==6
 for c in pixels:
  assert c['redPixels']==0 if c['minimized'] else c['redPixels']>2000
  image=paths[key].parent/'native-evidence'/Path(c['image']).name;assert sha(image)==d['artifacts']['native-evidence/'+image.name]
 for receipt in d['activationKeyboardReceipts']:
  keys=[e for e in receipt['events'] if e['kind']=='key' and e['keyval']==97];assert len(keys)==1 and keys[0]['window']==receipt['expected']
 for c in d['checks']:
  if c['name'].endswith('MinimizedApplicationReceivesNoKey'):assert not any(e['kind']=='key' and e['keyval']==97 for e in c['events'])
 for helper in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(old,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
 rows.append({'operation':key,'nativeChecks':count,'actualPixelInputStages':6,'nativeCommittedStateAcrossRecovery':minimized,'sameHost':True,'cleanupPassed':True})
capsule=json.loads((REPO/'implementation/elm-storage-stale-supervisor-v257/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
names=['elm-storage-settlement-minimize-v263','elm-storage-settlement-restore-v264','elm-storage-settlement-v265'];files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Actual committed minimize/restore followed by broker settlement read refusal, repair/Unknown UI and explicit same-host reconnect without replay','cases':rows,'nativeCheckCounts':[45,47],'selectedNativeWorkloads':2,'actualPixelInputStagesPerCase':6,'sameRuntimeAndCoreTuple':True,'cleanupPassed':True,'sealedRuntimeFiles':20,'originalHelpersAndDeadlinesUnchanged':True,'nativeSettlementReadRefusalAccepted':True,'hostBindingRetryAccepted':False,'nativeDiskFullAccepted':False,'allRecoveryStagesAccepted':False,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
