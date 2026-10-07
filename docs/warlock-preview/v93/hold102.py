"""Freeze original native all-map retirement with independent control quotas."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v102'
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
native_path=only('qa/imported-control-retirement-check-v2-*/report.json');native=verify(native_path)
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
parent=repo/'implementation/warlock-preview-provider-v101';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/client_producer.hpp','native/client-command-test.cpp']:
 assert sha(root/name)==sha(parent/name)
failed_paths=[only('qa/imported-control-retirement-check-[0-9]*/report.json'),only('qa/actor-control-check-[0-9]*/report.json')]
assert all(not json.loads(p.read_text())['passed'] for p in failed_paths)
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
scope='Actual opt-in native all-map retirement preserves original physical/proof/receiver barriers plus old job control confirmation before fresh permanent query. Native-dispatched readiness and currently invoking exact final ACK guard effects. Actual final processing plus original frontend confirmation independently precede actor credit reclamation; confirmed Unknown final handlers retain journal/credits and cannot be reinvoked by ticket retry.7809 controls across260 metadata actors,one original epoch and1040 uninterrupted issued tickets.15 selected actor Quint scenarios/23 compiled native traces/316 states/four compiled variants; job15/23/299/four,bank11/23/397/four+64controls,admission15/23/191/six all requalified;69 optimized Elm/nativeBroker/realURI controls;95 full-host build. Synthetic authenticated socket/native metadata, no real windows/captured FD/backend lock/compiled Elm retirement/WebKit or real actor-host close acceptance. Initial quota-count fixture failure and mutation-unused-parameter compile failure retained. Completed-actor binding-close helper requires permanent native retirement; live-window binding detachment is a separate open contract. C factory/routing,reconciliation,native-assigned renderer outbox/WebKit,capture/full release gates remain. Qualified runtime GUI92/native128/core16/plugin18 unchanged.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativeActorQuotaReport':str(native_path),'nativeActorModelReport':str(model_path),'nativeActorScenarios':15,'nativeActorTraces':23,'nativeActorStates':316,'nativeActorCompiledVariants':4,'nativeActorMetadataControls':7809,'metadataActorsTurnedOver':260,'uninterruptedNativeIssuedPrefix':1040,'nativeJobModelReport':str(job_path),'reservationReport':str(bank_path),'admissionReport':str(admission_path),'nativeQuotaReport':str(quota_path),'compiledElmNativeQuotaControls':69,'fullBuildReport':str(build_path),'fullBuildCommands':95,'heldFailedReports':[str(p) for p in failed_paths],'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
manifest.write_text(json.dumps(result,indent=2)+'\n')
(pathlib.Path(__file__).parent/'component-report102.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI102. '+scope,'Next actual controlled C provider/native ticket routing; retain original grant across presentation/reload, define live-binding detachment and native reconciliation before renderer outbox/WebKit activation.'], 'progress',[str(manifest.relative_to(repo)),str(native_path.relative_to(repo)),str(model_path.relative_to(repo)),str(quota_path.relative_to(repo))]))
