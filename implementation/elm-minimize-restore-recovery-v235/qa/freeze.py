"""Freeze the four actual native operation/boundary cases on one source tuple."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
cases=[('minimizeUnread','elm-minimize-unread-native-v232','minimize','unread',57,False),('restoreUnread','elm-restore-unread-native-v233','restore','unread',59,True),('minimizeLostReceipt','elm-minimize-lost-native-v234','minimize','lost',57,True),('restoreLostReceipt','elm-restore-lost-native-v230','restore','lost',59,False)]
paths={key:find(name,'native') for key,name,*_ in cases}
paths.update(cpuDisappearance=find('elm-cgroup-disappearance-v231','cpu'),failedPillow=find('elm-minimize-unread-native-v215','native'),failedPixelOracle=find('elm-minimize-unread-native-v219','native'),failedTeardown=find('elm-restore-lost-native-v226','native'),failedDescriptorReproducer=find('elm-cgroup-disappearance-v227','cpu'),failedReproducerMetadata=find('elm-cgroup-disappearance-v228','cpu'),upstream=REPO/'implementation/elm-admission-settled-native-v214/qa/slice-manifest.json')
data={key:json.loads(p.read_text()) for key,p in paths.items()}
for key,d in data.items():assert d['passed']==(not key.startswith('failed')),key
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
def fn(path,name):return next(v for v in ast.walk(ast.parse(path.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
reference=None;rows=[]
for key,name,operation,boundary,count,minimized in cases:
 d=data[key];assert d['cleanupPassed'] and len(d['checks'])==count and all(c['passed'] for c in d['checks'])
 assert d['operation']==operation and d['faultBoundary']==boundary and d['stateBeforeRecovery']['expectedMinimized']==minimized
 for p,digest in d['inputs'].items():assert sha(Path(p))==digest,p
 assert d['inputs'][str(REPO/'implementation/elm-disappearance-supervisor-v229/cohort.py')]==sha(REPO/'implementation/elm-disappearance-supervisor-v229/cohort.py')
 tuple_key=(d['buildReportSHA256'],d['pair']['core']['sha256'],d['pair']['plugin']['sha256'])
 if reference is None:reference=tuple_key
 else:assert tuple_key==reference
 assert sha(Path(d['buildReport']))==d['buildReportSHA256']
 for part in ['core','plugin']:
  item=d['pair'][part];assert sha(Path(item['path']))==item['sha256']
 assert len(d['supervisorEvents']['starts'])==2 and d['supervisorEvents']['exits'][0]['exitCode']==3 and d['supervisorEvents']['exits'][1]['exitCode']==1
 assert d['cohortCleanup'][-1]['remaining']==[]
 pixels=[c for c in d['checks'] if c['name'].endswith('ActualApplicationPixelsMatchNativeMinimized')];assert len(pixels)==6
 for c in pixels:
  assert c['redPixels']==0 if c['minimized'] else c['redPixels']>2000
  image=paths[key].parent/'native-evidence'/Path(c['image']).name;assert image.is_file() and sha(image)==d['artifacts']['native-evidence/'+image.name]
 for receipt in d['activationKeyboardReceipts']:
  delivered=[event for event in receipt['events'] if event['kind']=='key' and event['keyval']==97];assert len(delivered)==1 and delivered[0]['window']=='ELM-AUTHORITY-FIXTURE'
 for c in d['checks']:
  if c['name'].endswith('MinimizedApplicationReceivesNoKey'):assert not any(e['kind']=='key' and e['keyval']==97 for e in c['events'])
 for helper in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(original,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
 rows.append({'case':key,'operation':operation,'faultBoundary':boundary,'nativeChecks':count,'minimizedAcrossRecovery':minimized,'actualPixelStages':6,'actualNoAutoResubmission':True,'cleanupPassed':True})
c=data['cpuDisappearance'];assert len(c['checks'])==6 and all(v['passed'] for v in c['checks']) and c['deadErrno']==19
capsule=json.loads((REPO/'implementation/elm-disappearance-supervisor-v229/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,digest in capsule['files'].items():assert sha(Path(p))==digest,p
names=['elm-minimize-unread-native-v215','elm-restore-unread-native-v216','elm-minimize-lost-native-v217','elm-restore-lost-native-v218','elm-minimize-unread-native-v219','elm-restore-unread-native-v220','elm-minimize-lost-native-v221','elm-restore-lost-native-v222','elm-minimize-unread-native-v223','elm-restore-unread-native-v224','elm-minimize-lost-native-v225','elm-restore-lost-native-v226','elm-cgroup-disappearance-v227','elm-cgroup-disappearance-v228','elm-disappearance-supervisor-v229','elm-restore-lost-native-v230','elm-cgroup-disappearance-v231','elm-minimize-unread-native-v232','elm-restore-unread-native-v233','elm-minimize-lost-native-v234','elm-minimize-restore-recovery-v235']
files=[p for name in names for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'];assert not any(p.is_symlink() for name in names for p in (REPO/'implementation'/name).rglob('*'))
result={'passed':True,'scope':'Four real single-window minimize/restore unread/lost-receipt recovery cases on actual pixels/input and current-state primary actions; original restore timing/full release open','cases':rows,'selectedCases':4,'nativeCheckCounts':[57,59,57,59],'distinctBaselineScenarioCountNotInferred':True,'actualDeadCgroupDescriptorChecks':6,'observedDeadDescriptorErrno':19,'sameSupervisorRuntimeCoreTuple':True,'actualPixelStagesPerCase':6,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'originalRestoreTimingAccepted':False,'sealedRuntimeFiles':20,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
