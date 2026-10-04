"""Freeze typed storage UX with two actual native cases and preserved failure."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={k:find('elm-storage-ux-v248',k) for k in ['build','storage','storage-replay','admission','namespace']}
paths.update(model=find('elm-storage-model-v251','model'),failedNative=find('elm-storage-corrupt-native-v250','native'),corruptNative=find('elm-storage-corrupt-native-v252','native'),admissionNative=find('elm-storage-admission-native-v253','native'))
d={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,v in d.items():assert v['passed']==(k!='failedNative'),k
for k,count in [('storage',21),('admission',22),('namespace',42),('corruptNative',23),('admissionNative',22)]:
 assert len(d[k]['checks'])==count and all(c['passed'] for c in d[k]['checks'])
 for p,h in d[k]['inputs'].items():assert sha(Path(p))==h,p
assert d['storage-replay']['checks']==55
for p,h in d['storage-replay']['inputs'].items():assert sha(Path(p))==h,p
assert all(c['exitCode']==0 for c in d['build']['commands'])
for p,h in d['build']['inputs'].items():assert sha(REPO/'implementation/elm-storage-ux-v248'/p)==h,p
assert d['model']['namedScenarios']==8 and d['model']['invariantSamples']==1000 and d['model']['maxSteps']==40
reference=None
def fn(p,name):return next(v for v in ast.walk(ast.parse(p.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
for k,name in [('corruptNative','elm-storage-corrupt-native-v252'),('admissionNative','elm-storage-admission-native-v253')]:
 v=d[k];assert v['cleanupPassed'] and v['storageFailure']['noAutomaticRetry'] and v['storageFailure']['corruptEvidencePreserved']
 assert v['cohortCleanup'][-1]['remaining']==[] and len(v['supervisorEvents']['starts'])==1
 assert v['supervisorEvents']['exits'][0]['exitCode']==0 and not v['supervisorEvents']['exits'][0]['forced']
 assert sha(Path(v['buildReport']))==v['buildReportSHA256']
 for part in ['core','plugin']:assert sha(Path(v['pair'][part]['path']))==v['pair'][part]['sha256']
 key=(v['buildReportSHA256'],v['pair']['core']['sha256'],v['pair']['plugin']['sha256'])
 if reference is None:reference=key
 else:assert key==reference
 for helper in ['check','wait','click']:assert ast.dump(fn(original,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
assert d['failedNative']['cleanupPassed'] and 'startupStorageFailurePreservesRealApplications' in d['failedNative']['error']
capsule=json.loads((REPO/'implementation/elm-storage-supervisor-v249/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
names=['elm-storage-ux-v248','elm-storage-supervisor-v249','elm-storage-corrupt-native-v250','elm-storage-model-v251','elm-storage-corrupt-native-v252','elm-storage-admission-native-v253','elm-storage-acceptance-v254'];files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Typed bounded storage explanations, preserved uncertain state, explicit recovery with two actual native filesystem refusal/correction cases','compiledStorageUXChecks':55,'cpuStorageChecks':21,'compiledAdmissionChecks':22,'cpuNamespaceChecks':42,'compiledInheritedElmChecks':[20,27,30],'quintNamedScenarios':8,'quintInvariantSamples':1000,'quintMaxSteps':40,'nativeCheckCounts':[23,22],'selectedNativeWorkloads':2,'sameRuntimeAndCoreTuple':True,'cleanupPassed':True,'sealedRuntimeFiles':20,'nativeStorageReasonsQualified':['unverified','unavailable'],'diskFullNativeAccepted':False,'legacyOwnerNativeAccepted':False,'busyNativeAccepted':False,'allRecoveryStagesAccepted':False,'fullOriginalNativeRegressionAccepted':False,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
