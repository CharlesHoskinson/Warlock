"""Freeze pure Elm stale failure fix with native busy/legacy and original137."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={k:find('elm-storage-stale-fix-v256',k) for k in ['build','stale','storage-replay']}
paths.update(failedStale=find('elm-stale-storage-repro-v255','stale'),model=find('elm-storage-stale-model-v260','model'),busy=find('elm-storage-busy-native-v258','native'),legacy=find('elm-storage-legacy-native-v259','native'),originalRegression=find('elm-storage-original-regression-v261','native'))
d={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,v in d.items():assert v['passed']==(k!='failedStale'),k
for k,count in [('stale',47),('storage-replay',55)]:
 assert d[k]['checks']==count
 for p,h in d[k]['inputs'].items():assert sha(Path(p))==h,p
assert all(c['exitCode']==0 for c in d['build']['commands'])
for p,h in d['build']['inputs'].items():assert sha(REPO/'implementation/elm-storage-stale-fix-v256'/p)==h,p
assert d['model']['namedScenarios']==10 and d['model']['invariantSamples']==1000 and d['model']['maxSteps']==40
reference=None
for k,count in [('busy',22),('legacy',23),('originalRegression',137)]:
 v=d[k];assert v['cleanupPassed'] and len(v['checks'])==count and all(c['passed'] for c in v['checks'])
 for p,h in v['inputs'].items():assert sha(Path(p))==h,p
 assert sha(Path(v['buildReport']))==v['buildReportSHA256']
 for part in ['core','plugin']:assert sha(Path(v['pair'][part]['path']))==v['pair'][part]['sha256']
 key=(v['buildReportSHA256'],v['pair']['core']['sha256'],v['pair']['plugin']['sha256'])
 if reference is None:reference=key
 else:assert key==reference
 if k!='originalRegression':
  assert v['storageFailure']['noAutomaticRetry'] and v['storageFailure']['evidencePreserved'] and v['cohortCleanup'][-1]['remaining']==[]
  assert len(v['supervisorEvents']['starts'])==1 and v['supervisorEvents']['exits'][0]['exitCode']==0 and not v['supervisorEvents']['exits'][0]['forced']
def fn(p,name):return next(v for v in ast.walk(ast.parse(p.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
for name in ['elm-storage-busy-native-v258','elm-storage-legacy-native-v259']:
 for helper in ['check','wait','click']:assert ast.dump(fn(original,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
def calls(p,name):return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(ast.parse(p.read_text())),key=lambda x:(getattr(x,'lineno',0),getattr(x,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
original=REPO/'implementation/elm-native-recovery-qa-v171/qa/regression.py';current=REPO/'implementation/elm-storage-original-regression-v261/qa/regression.py'
for name in ['check','wait']:assert calls(original,name)==calls(current,name)
for name in ['check','wait','click','choose','press_key']:assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(current,name),include_attributes=False)
capsule=json.loads((REPO/'implementation/elm-storage-stale-supervisor-v257/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
names=['elm-stale-storage-repro-v255','elm-storage-stale-fix-v256','elm-storage-stale-supervisor-v257','elm-storage-busy-native-v258','elm-storage-legacy-native-v259','elm-storage-stale-model-v260','elm-storage-original-regression-v261','elm-storage-qualified-v262'];files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Pure Elm stale failure-text preservation, actual busy/unowned legacy correction, original unchanged137 workload on V256/V89','compiledStaleChecks':47,'compiledStorageUXChecks':55,'compiledInheritedElmChecks':[20,27,30],'quintNamedScenarios':10,'quintInvariantSamples':1000,'quintMaxSteps':40,'newNativeStorageCheckCounts':[22,23],'originalNativeRegressionChecks':137,'originalNativeBaselineChecks':91,'originalCheckWaitCallsAndHelperASTUnchanged':True,'sameGUIBuildCorePair':True,'cleanupPassed':True,'sealedRuntimeFiles':20,'newNativeStorageReasonsQualified':['busy','legacy-owner'],'legacyMetadataRuleNativeAccepted':True,'productionLegacyProvisioningAccepted':False,'allRecoveryStagesAccepted':False,'newerGeometryMenuGPUReleaseAccepted':False,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
