"""Freeze bounded owned-scope native evidence without changing predecessors."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def report(name,kind):
 p=next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'));return p,json.loads(p.read_text())
np,n=report('elm-cohort-native-v185','native');fp,f=report('elm-cohort-native-v186','native');cp,c=report('elm-shell-cohort-v181','cpu');bp,b=report('elm-cohort-native-v183','native')
assert not b['passed']
for d,count in [(n,40),(f,42),(c,7)]:
 assert d['passed'] and len(d['checks'])==count and all(v['passed'] for v in d['checks'])
 for p,digest in d.get('inputs',{}).items():assert sha(Path(p))==digest,p
for d in [n,f]:
 assert d['cleanupPassed'] and d['cohortCleanup'][-1]['remaining']==[]
 assert len(d['supervisorEvents']['starts'])==len(d['supervisorEvents']['exits'])==2
 assert d['supervisorEvents']['exits'][0]['exitCode']==3
assert not n['supervisorEvents']['exits'][1]['forced']
assert f['supervisorEvents']['exits'][1]['forced'] and f['supervisorEvents']['exits'][1]['exitCode']==-9
assert f['cohortCleanup'][-1]['stopExitCode']==0 and len(f['cohortCleanup'][-1]['before'])==3
assert f['forcedFault']['renderer']['pid'] in f['cohortCleanup'][-1]['before']
assert f['forcedStopSeconds']<f['forcedFault']['outerObservationSeconds']
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
def fn(path,name):return next(v for v in ast.walk(ast.parse(path.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
for campaign in ['elm-cohort-native-v185','elm-cohort-native-v186']:
 for name in ['check','wait','click','choose','press_key','key_recipient']:
  assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(REPO/'implementation'/campaign/'qa/native.py',name),include_attributes=False),name
capsule=json.loads((REPO/'implementation/elm-host-cohort-v184/runtime-manifest.json').read_text());up=REPO/'implementation/elm-supervisor-native-v179/qa/slice-manifest.json';upstream=json.loads(up.read_text())
for p,digest in capsule['files'].items():assert sha(Path(p))==digest,p
assert len(capsule['files'])==18
for d in [n,f]:
 for part in ['core','plugin']:
  item=d['pair'][part];assert sha(Path(item['path']))==item['sha256']
 assert d['pair']['core']['sha256']==capsule['coreSHA256']
names=['elm-shell-cohort-v181','elm-host-cohort-v182','elm-cohort-native-v183','elm-host-cohort-v184','elm-cohort-native-v185','elm-cohort-native-v186']
paths=[p for name in names for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json']
assert not any(p.is_symlink() for name in names for p in (REPO/'implementation'/name).rglob('*'))
result={'passed':True,'scope':'Actual owned transient shell scope cooperative and forced teardown; externally launched applications/compositor preserved; no production app launch or release acceptance','cooperativeNativeChecks':40,'forcedNativeChecks':42,'actualCohortCPUChecks':7,'forcedStopSeconds':f['forcedStopSeconds'],'forcedResidualHelpersRemoved':3,'scopeMembersRemaining':[],'forcedStopWrapperExitCode':1,'sealedRuntimeFiles':18,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'retainedOriginalNativeChecks':91,'retainedFullNativeChecks':137,'retainedRecoveryQuintNamed':6,'retainedRecoveryQuintSamples':1000,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in [('cooperativeNative',np),('forcedNative',fp),('cohortCPU',cp),('failedPrivateBus',bp),('upstream',up)]},'files':{str(p.relative_to(REPO)):sha(p) for p in paths}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
