"""Freeze actual native purpose issuer and bounded confirmed predecessor evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v101'
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
native_path=only('qa/imported-control-ticket-check-v2-*/report.json');native=verify(native_path)
assert native['checks']==70 and native['controls'][0]['normalOwnedExit']
model_path=only('qa/job-control-check-*/report.json');model=verify(model_path)
assert model['namedScenarios']==15 and len(model['coupledTraces'])==23 and model['unsafeMutantsDetected']==4
bank_path=only('qa/control-reservations-check-v4-*/report.json');bank=verify(bank_path)
assert bank['namedScenarios']==11 and len(bank['coupledTraces'])==23 and bank['statesCompared']==397 and bank['adversarialChecks']==64 and bank['unsafeCompiledNativeMutantsDetected']==4
admission_path=only('qa/control-admission-check-v3-*/report.json');admission=verify(admission_path)
assert admission['namedScenarios']==15 and len(admission['coupledTraces'])==23 and admission['statesCompared']==191 and admission['unsafeMutantsDetected']==6
quota_path=only('qa/control-quota-check-*/report.json');quota=verify(quota_path)
assert quota['evidence']['checks']==69 and quota['evidence']['repeatedAcknowledgments']==25 and quota['evidence']['normalOwnedExit']
build_path=only('qa/build-*/report.json');build=verify(build_path);assert len(build['commands'])==95
parent=repo/'implementation/warlock-preview-provider-v100';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
regression_path=pathlib.Path(prior['originalRegressionReport']);regression=json.loads(regression_path.read_text());assert regression['passed'] and len(regression['results'])==12
for rel,value in regression['inputs'].items():
 p=pathlib.Path(rel);assert sha(root/p.relative_to(parent))==value,rel
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/client_producer.hpp','native/client-command-test.cpp']:
 assert sha(root/name)==sha(parent/name)
failed=only('qa/imported-control-ticket-check-*/report.json');assert not json.loads(failed.read_text())['passed']
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
scope='Actual opt-in ImportedClients native typed job issuer validates original job/packet/terminal proofs before immutable reserved purpose-slot tickets. Exact post-effect retries survive absent Broker record. Independently settled and frontend-confirmed predecessor retained one per actual actor, with already-delivered disposition and no live invocation ticket.70 authenticated synthetic native socket controls;15 selected Quint scenarios/23 compiled native traces/four unsafe compiled variants; native bank11/23/397/four plus64 adversarial controls; admission15/23/191/six;69 optimized Elm/nativeBroker/realURI controls;95 full-host build commands. Original12 GUI100 regression suites retained with unchanged scripts/Elm/assets/default C factories/shared-host; not claimed rerun101. Failed fixture compile retained. No actual capture/WebKit/actor-host close or full GUI acceptance; GUI92/native128/core16/plugin18 remains qualified runtime. Controlled C factory/routing, physical and actor quota release, receiver reconciliation and native-assigned renderer outbox remain required.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativePurposeIssuerReport':str(native_path),'nativePurposeModelReport':str(model_path),'nativePurposeScenarios':15,'nativePurposeTraces':23,'nativePurposeStates':model['statesCompared'],'nativePurposeCompiledVariants':4,'nativePurposeSocketControls':70,'reservationReport':str(bank_path),'admissionReport':str(admission_path),'nativeQuotaReport':str(quota_path),'compiledElmNativeQuotaControls':69,'fullBuildReport':str(build_path),'fullBuildCommands':95,'retainedOriginalRegressionReport':str(regression_path),'retainedOriginalRegressionSuites':12,'originalRegressionSuitesRerunHere':False,'heldFailedFixtureReport':str(failed),'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
manifest.write_text(json.dumps(result,indent=2)+'\n')
(pathlib.Path(__file__).parent/'component-report101.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI101. '+scope,'Next original native actor/quota release, actual controlled C provider and native ticket routing, receiver reconciliation and native-assigned outbox/WebKit integration.'], 'progress',[str(manifest.relative_to(repo)),str(native_path.relative_to(repo)),str(model_path.relative_to(repo)),str(quota_path.relative_to(repo))]))
