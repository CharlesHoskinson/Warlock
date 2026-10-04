"""Freeze admission retry fix, retained failures, two native cases and original137."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={'failedOriginalRetry':find('elm-host-bind-repro-v266','retry'),'failedFixture':find('elm-host-bind-fix-v267','retry'),'retainedAdmission':find('elm-host-bind-fix-v267','admission'),'retry':find('elm-host-bind-fixed-v268','retry'),'build':find('elm-host-bind-fixed-v268','build'),'model':find('elm-host-bind-model-v272','model'),'publicNative':find('elm-host-bind-private-native-v270','native'),'heldNative':find('elm-host-bind-held-native-v271','native'),'originalRegression':find('elm-host-bind-regression-v273','native')}
d={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,v in d.items():assert v['passed']==(not k.startswith('failed')),k
assert 'heldRetryAfterActualCorrection' in d['failedOriginalRetry']['error'] and 'heldSameLifetimeBindIdempotent' in d['failedFixture']['error']
assert sha(REPO/'implementation/elm-host-bind-fix-v267/native/host-journal.h')==sha(REPO/'implementation/elm-host-bind-fixed-v268/native/host-journal.h')
for k,count in [('retry',14),('retainedAdmission',22)]:
 assert len(d[k]['checks'])==count and all(c['passed'] for c in d[k]['checks'])
 for p,h in d[k]['inputs'].items():assert sha(Path(p))==h,p
assert all(c['exitCode']==0 for c in d['build']['commands'])
for p,h in d['build']['inputs'].items():assert sha(REPO/'implementation/elm-host-bind-fixed-v268'/p)==h,p
assert d['model']['namedScenarios']==8 and d['model']['invariantSamples']==1000 and d['model']['maxSteps']==40
reference=None
for k,count in [('publicNative',22),('heldNative',22),('originalRegression',137)]:
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
for name in ['elm-host-bind-private-native-v270','elm-host-bind-held-native-v271']:
 for helper in ['check','wait','click']:assert ast.dump(fn(original,helper),include_attributes=False)==ast.dump(fn(REPO/'implementation'/name/'qa/native.py',helper),include_attributes=False)
def calls(p,name):return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(ast.parse(p.read_text())),key=lambda x:(getattr(x,'lineno',0),getattr(x,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
original=REPO/'implementation/elm-native-recovery-qa-v171/qa/regression.py';current=REPO/'implementation/elm-host-bind-regression-v273/qa/regression.py'
for name in ['check','wait']:assert calls(original,name)==calls(current,name)
for name in ['check','wait','click','choose','press_key']:assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(current,name),include_attributes=False)
capsule=json.loads((REPO/'implementation/elm-host-bind-supervisor-v269/runtime-manifest.json').read_text());assert len(capsule['files'])==20
for p,h in capsule['files'].items():assert sha(Path(p))==h,p
names=['elm-host-bind-repro-v266','elm-host-bind-fix-v267','elm-host-bind-fixed-v268','elm-host-bind-supervisor-v269','elm-host-bind-private-native-v270','elm-host-bind-held-native-v271','elm-host-bind-model-v272','elm-host-bind-regression-v273','elm-host-bind-acceptance-v274'];files=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p!=ROOT/'qa/slice-manifest.json':files.append(p)
result={'passed':True,'scope':'Host admission failed-lifetime retirement preserves instance context for explicit retry; actual lock/privacy correction and original137','compiledRetryChecks':14,'retainedCompiledAdmissionChecks':22,'compiledInheritedElmChecks':[20,27,30],'quintNamedScenarios':8,'quintInvariantSamples':1000,'quintMaxSteps':40,'nativeHostBindingCheckCounts':[22,22],'originalNativeRegressionChecks':137,'originalNativeBaselineChecks':91,'sameGUIBuildCorePair':True,'cleanupPassed':True,'sealedRuntimeFiles':20,'nativeHostBindingRetryAccepted':True,'allRecoveryStagesAccepted':False,'newerGeometryMenuGPUReleaseAccepted':False,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='retainedAdmission'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
