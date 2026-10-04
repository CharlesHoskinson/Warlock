"""Freeze candidate journal, compiled policy, native source tuple and failures."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={'native':find('elm-journal-native-v193','native'),'build':find('elm-window-journal-v188','build'),'journal':find('elm-window-journal-v188','journal'),'model':find('elm-window-recovery-model-v194','model'),'failedBuild':find('elm-window-journal-v187','build'),'failedNative':find('elm-journal-native-v190','native'),'failedModel':find('elm-window-recovery-model-v191','model'),'upstream':REPO/'implementation/elm-cohort-native-v186/qa/slice-manifest.json'}
data={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,d in data.items():assert d['passed']==(not k.startswith('failed')),k
n=data['native'];b=data['build'];j=data['journal'];q=data['model']
assert n['cleanupPassed'] and len(n['checks'])==42 and all(c['passed'] for c in n['checks'])
assert len(j['checks'])==19 and all(c['passed'] for c in j['checks'])
assert q['namedScenarios']==6 and q['invariantSamples']==1000 and q['maxSteps']==40
for name,count in [('replay',20),('shell',27),('recovery',30)]:
 d=json.loads((paths['build'].parent/(name+'-report.json')).read_text());assert d['passed'] and d['checks']==count
for d in [n,j]:
 for p,digest in d['inputs'].items():assert sha(Path(p))==digest,p
for relative,digest in b['inputs'].items():assert sha(REPO/'implementation/elm-window-journal-v188'/relative)==digest,relative
assert sha(Path(n['buildReport']))==n['buildReportSHA256']==sha(paths['build'])
capsule=json.loads((REPO/'implementation/elm-journal-supervisor-v192/runtime-manifest.json').read_text());assert len(capsule['files'])==19
for p,digest in capsule['files'].items():assert sha(Path(p))==digest,p
assert sha(Path(capsule['host']))==b['binarySHA256']
for part in ['core','plugin']:
 item=n['pair'][part];assert sha(Path(item['path']))==item['sha256']
assert n['pair']['core']['sha256']==capsule['coreSHA256']
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
def fn(path,name):return next(v for v in ast.walk(ast.parse(path.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
for name in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(ROOT/'qa/native.py',name),include_attributes=False)
assert n['cohortCleanup'][-1]['remaining']==[] and len(n['supervisorEvents']['starts'])==2
names=['elm-window-journal-v187','elm-window-journal-v188','elm-journal-supervisor-v189','elm-journal-native-v190','elm-window-recovery-model-v191','elm-journal-supervisor-v192','elm-journal-native-v193','elm-window-recovery-model-v194']
files=[p for name in names for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json']
symlinks=[p for name in names for p in (REPO/'implementation'/name).rglob('*') if p.is_symlink()];assert not symlinks
result={'passed':True,'scope':'Bounded durable window-intent journal and native settled-receipt restart; actual interrupted-effect/replacement Unknown display still open','nativeChecks':42,'actualFilesystemSubprocessChecks':19,'compiledRecoveryChecks':30,'compiledRetainedReducerChecksRerun':20,'compiledRetainedShellChecksRerun':27,'namedQuintScenarios':6,'quintInvariantSamples':1000,'sealedRuntimeFiles':19,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'nativeInterruptedEffectAcceptance':False,'formerAuthenticatedSenderReplayAcceptance':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
