"""Freeze original native all-map retirement with independent control quotas."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v103'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(path):
 proof=json.loads(path.read_text());assert proof['passed'],path
 for rel,value in proof['inputs'].items():
  p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
 for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
 assert not proof.get('nativeAcceptance',False) and not proof.get('fullReleaseAccepted',False)
 return proof
native_path=only('qa/imported-control-readiness-bytes-check-v4-*/report.json');native=verify(native_path)
assert native['checks']==7809 and native['controls'][0]['normalOwnedExit'] and native['controls'][0]['actorsTurnedOver']==260 and native['controls'][0]['nativeIssuedPrefix']==1040
model_path=only('qa/actor-control-check-v2-*/report.json');model=verify(model_path)
assert model['namedScenarios']==15 and len(model['coupledTraces'])==23 and model['statesCompared']==316 and model['unsafeMutantsDetected']==4
job_path=only('qa/job-control-check-*/report.json');job=verify(job_path)
assert job['namedScenarios']==15 and len(job['coupledTraces'])==23 and job['statesCompared']==299 and job['unsafeMutantsDetected']==4
bank_path=only('qa/control-reservations-check-v4-*/report.json');bank=verify(bank_path)
assert bank['namedScenarios']==11 and len(bank['coupledTraces'])==23 and bank['statesCompared']==397 and bank['adversarialChecks']==64 and bank['unsafeCompiledNativeMutantsDetected']==4
admission_path=only('qa/control-admission-check-v4-*/report.json');admission=verify(admission_path)
assert admission['namedScenarios']==15 and len(admission['coupledTraces'])==23 and admission['statesCompared']==191 and admission['unsafeMutantsDetected']==6
quota_path=only('qa/control-quota-check-*/report.json');quota=verify(quota_path)
assert quota['evidence']['checks']==69 and quota['evidence']['repeatedAcknowledgments']==25 and quota['evidence']['normalOwnedExit']
build_path=only('qa/build-*/report.json');build=verify(build_path);assert len(build['commands'])==95
parent=repo/'implementation/warlock-preview-provider-v102';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/client_producer.hpp','native/client-command-test.cpp']:
 assert sha(root/name)==sha(parent/name)
c_path=only('qa/imported-controlled-c-check-v3-*/report.json');c=verify(c_path)
assert c['checks']==10190 and c['controls'][0]['normalOwnedExit'] and c['controls'][0]['actorsTurnedOver']==260 and c['controls'][0]['nativeIssuedPrefix']==1041
mutation_path=only('qa/imported-controlled-c-mutations-v2-*/report.json');mutation=verify(mutation_path);assert mutation['unsafeCompiledVariantsDetected']==5 and all(v['compiled'] and v['failedOriginalAssertion'] for v in mutation['mutants'])
regression_path=repo/'docs/warlock-preview/v93/regressions103-1791338338629945756/report.json';regression=verify(regression_path);assert len(regression['results'])==12 and all(v['exitCode']==0 for v in regression['results'])
for v in regression['results']:
 for stream in ['stdout','stderr']:assert sha(regression_path.parent/(v['script']+'.'+stream))==v[stream+'SHA256']
failed_paths=[only('qa/imported-control-readiness-bytes-check-[0-9]*/report.json'),only('qa/imported-control-readiness-bytes-check-v2-*/report.json'),only('qa/imported-control-controlled-c-check-[0-9]*/report.json'),only('qa/imported-controlled-c-mutations-[0-9]*/report.json')]
assert all(not json.loads(p.read_text())['passed'] for p in failed_paths)

files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
scope='Actual opt-in controlled C provider claims one original Native preview namespace with no live legacy owner and enrolls original receiver before cleanup-reserved admission. Native purpose tickets guard actual creator-thread/same Endpoint dispatch; raw C command/retirement/bootstrap ACK routes refuse controlled namespace.10190 checks across260 metadata actors and1041 uninterrupted native tickets; original failed handler retains receipt and Broker ownership; latest exact receipt echo and original confirmation survive synthetic core normal exit without handler replay. Native readiness polling preserves original whitespace bytes (7809 controls/260 actors/1040 tickets).Five unsafe C variants compile and fail their original socket assertions; fixture-server failure alone is rejected and retained. Actor15 selected/23 compiled traces/316 states/four variants,job15/23/299/four,bank11/23/397/four+64 controls,admission15/23/191/six;69 optimized Elm/native Broker/real URI controls;95 full-host commands and all12 unchanged original regression suites rerun. Failed whitespace, aggregate initializer, C fixture allocator arithmetic and original unsafe-variant server-failure reports preserved. No real windows/capture FD/backend locks/WebKit activation/live-window binding detachment or full release acceptance. Actual native reconciliation/capture Unknown settlement/native-assigned renderer outbox remain required. Qualified runtime GUI92/native128/core16/plugin18 and original release gates remain unchanged.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'controlledCReport':str(c_path),'controlledCChecks':10190,'controlledCMetadataActors':260,'controlledCNativeIssuedPrefix':1041,'controlledCMutationReport':str(mutation_path),'controlledCCompiledVariants':5,'originalRegressionReport':str(regression_path),'originalRegressionSuites':12,'originalRegressionSuitesRerunHere':True,'nativeActorQuotaReport':str(native_path),'nativeActorModelReport':str(model_path),'nativeActorScenarios':15,'nativeActorTraces':23,'nativeActorStates':316,'nativeActorCompiledVariants':4,'nativeActorMetadataControls':7809,'metadataActorsTurnedOver':260,'uninterruptedNativeIssuedPrefix':1040,'nativeJobModelReport':str(job_path),'reservationReport':str(bank_path),'admissionReport':str(admission_path),'nativeQuotaReport':str(quota_path),'compiledElmNativeQuotaControls':69,'fullBuildReport':str(build_path),'fullBuildCommands':95,'heldFailedReports':[str(p) for p in failed_paths],'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
manifest.write_text(json.dumps(result,indent=2)+'\n')
(pathlib.Path(__file__).parent/'component-report103.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI103. '+scope,'Next explicit live-window binding detachment, actual native reconciliation and capture Unknown settlement before native-assigned renderer outbox/WebKit activation; preserve original grant across reload and all remaining GUI release gates.'], 'progress',[str(manifest.relative_to(repo)),str(native_path.relative_to(repo)),str(model_path.relative_to(repo)),str(quota_path.relative_to(repo))]))
