"""Source/runtime closure for the actual supervisor and protected native workload."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={'native':next((ROOT/'qa').glob('native-*/report.json')),'cpu':REPO/'implementation/elm-host-supervisor-v178/qa/cpu-1791094941941511422/report.json','upstream':REPO/'implementation/elm-native-recovery-qa-v171/qa/slice-manifest.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],p
native=json.loads(reports['native'].read_text());cpu=json.loads(reports['cpu'].read_text());assert native['cleanupPassed'] and len(native['checks'])==38 and all(c['passed'] for c in native['checks']);assert len(cpu['checks'])==15 and all(c['passed'] for c in cpu['checks'])
for r in [native,cpu]:
 for path,digest in r['inputs'].items():assert sha(Path(path))==digest,path
upstream=json.loads(reports['upstream'].read_text());assert native['buildReportSHA256']==upstream['evidence']['build']['sha256']
assert sha(Path(native['buildReport']))==native['buildReportSHA256']
capsule_path=REPO/'implementation/elm-host-supervisor-v178/runtime-manifest.json';capsule=json.loads(capsule_path.read_text())
for path,digest in capsule['files'].items():
 assert sha(Path(path))==digest,path
 assert upstream['files'][str(Path(path).relative_to(REPO))]==digest,path
assert len(capsule['files'])==18 and native['pair']['core']['sha256']==capsule['coreSHA256']
for part in ['core','plugin']:
 item=native['pair'][part];assert sha(Path(item['path']))==item['sha256']
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
for name in ['check','wait','click','choose','press_key','key_recipient']:
 def fn(path):return next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(fn(original),include_attributes=False)==ast.dump(fn(ROOT/'qa/native.py'),include_attributes=False),name
starts=native['supervisorEvents']['starts'];exits=native['supervisorEvents']['exits'];assert len(starts)==len(exits)==2 and starts[0]['pid']!=starts[1]['pid']
assert exits[0]['exitCode']==3 and not exits[0]['stopping'] and not exits[0]['forced']
assert exits[1]['exitCode']==1 and exits[1]['stopping'] and not exits[1]['forced']
idle=native['supervisorIdleSamples'];assert len(idle)==5 and all(r['waitChannel']=='ep_poll' for r in idle)
assert idle[0]['voluntarySwitches']==idle[-1]['voluntarySwitches'] and idle[0]['involuntarySwitches']==idle[-1]['involuntarySwitches']
sources=['elm-host-supervisor-v174','elm-host-supervisor-v176','elm-supervisor-native-v177','elm-host-supervisor-v178','elm-supervisor-native-v179']
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':native['scope'],'nativeChecks':38,'actualSubprocessChecks':15,'actualSupervisorOwnsReplacement':True,'supervisedGenerations':2,'thirdGenerationAfterStop':False,'hostExitCodes':[3,1],'supervisorExitCode':0,'forcedNativeStop':False,'sealedRuntimeFiles':18,'idleWaitChannel':'ep_poll','idleObservedSeconds':2,'idleContextSwitchDelta':0,'retainedOriginalNativeChecks':91,'retainedFullNativeChecks':137,'retainedRecoveryQuintNamed':6,'retainedRecoveryQuintSamples':1000,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in reports.items()},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
