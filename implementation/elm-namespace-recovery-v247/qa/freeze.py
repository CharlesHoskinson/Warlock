"""Freeze five actual native workloads on one exact journal namespace build."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[('minimizeUnread','elm-namespaced-minimize-native-v240','minimize','unread',59,False),('restoreUnread','elm-namespaced-restore-native-v242','restore','unread',61,True),('minimizeLost','elm-namespaced-minimize-lost-v243','minimize','lost',59,True),('restoreLost','elm-namespaced-restore-lost-v244','restore','lost',61,False),('settled','elm-namespaced-settled-native-v246',None,None,43,None)]
paths={k:next((REPO/'implementation'/name/'qa').glob('native-*/report.json')) for k,name,*_ in cases}
paths['upstream']=REPO/'implementation/elm-namespace-acceptance-v245/qa/slice-manifest.json'
data={k:json.loads(p.read_text()) for k,p in paths.items()};assert all(d['passed'] for d in data.values())
def fn(p,name):return next(n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
old=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py';reference=None;rows=[]
for key,name,operation,boundary,count,minimized in cases:
 d=data[key];assert d['cleanupPassed'] and len(d['checks'])==count and all(c['passed'] for c in d['checks'])
 for p,h in d['inputs'].items():assert sha(Path(p))==h,p
 assert sha(Path(d['buildReport']))==d['buildReportSHA256']
 for part in ['core','plugin']:assert sha(Path(d['pair'][part]['path']))==d['pair'][part]['sha256']
 tuple_key=(d['buildReportSHA256'],d['pair']['core']['sha256'],d['pair']['plugin']['sha256'])
 if reference is None:reference=tuple_key
 else:assert tuple_key==reference
 assert len(d['supervisorEvents']['starts'])==2 and [r['exitCode'] for r in d['supervisorEvents']['exits']]==[3,1]
 assert d['cohortCleanup'][-1]['remaining']==[]
 ns=d['journalNamespace'];assert Path(ns['path']).parts[-3:]==('elm-window-recovery',ns['instance'],ns['lifetime'])
 for helper in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(old,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
 pixels=[]
 if operation:
  assert d['operation']==operation and d['faultBoundary']==boundary and d['stateBeforeRecovery']['expectedMinimized']==minimized
  pixels=[c for c in d['checks'] if c['name'].endswith('ActualApplicationPixelsMatchNativeMinimized')];assert len(pixels)==6
  for c in pixels:
   assert c['redPixels']==0 if c['minimized'] else c['redPixels']>2000
   image=paths[key].parent/'native-evidence'/Path(c['image']).name;assert sha(image)==d['artifacts']['native-evidence/'+image.name]
 else:assert any(c['name']=='durablySettledIntentIsNotRecoveredAsUnknown' and c['passed'] for c in d['checks'])
 for receipt in d['activationKeyboardReceipts']:
  keys=[e for e in receipt['events'] if e['kind']=='key' and e['keyval']==97];assert len(keys)==1 and keys[0]['window']==receipt['expected']
 for c in d['checks']:
  if c['name'].endswith('MinimizedApplicationReceivesNoKey'):assert not any(e['kind']=='key' and e['keyval']==97 for e in c['events'])
 rows.append({'case':key,'operation':operation,'faultBoundary':boundary,'nativeChecks':count,'actualPixelStages':len(pixels),'cleanupPassed':True,'retainedNotRerun':key=='minimizeUnread'})
capsule=json.loads((REPO/'implementation/elm-namespaced-supervisor-v239/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
names=['elm-namespaced-restore-native-v242','elm-namespaced-minimize-lost-v243','elm-namespaced-restore-lost-v244','elm-namespaced-settled-native-v246','elm-namespace-recovery-v247'];files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Four interrupted minimize/restore native cases and normally settled activation recovery on one namespaced host/broker/core tuple','cases':rows,'selectedNativeWorkloads':5,'newNativeWorkloads':4,'nativeCheckCounts':[59,61,59,61,43],'sameRuntimeAndCoreTuple':True,'cleanupPassed':True,'sealedRuntimeFiles':20,'originalHelpersAndDeadlinesUnchanged':True,'completedRequirementIds':[],'fullOriginalNativeRegressionAccepted':False,'storageErrorUXAccepted':False,'legacyOwnershipProvisioningAccepted':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k in ['upstream','minimizeUnread']} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
