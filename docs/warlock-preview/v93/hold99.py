"""Hold exact inactive native cleanup reservation and ticket issuer scope."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v99'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
    found=list(root.glob(pattern));assert len(found)==1,found;return found[0]
def verify(path):
    proof=json.loads(path.read_text());assert proof['passed'],path
    for rel,value in proof['inputs'].items():
        p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
    for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted'];return proof
native_path=only('qa/retained-client-command-check-*/report.json');native=verify(native_path)
assert native['namedScenarios']==14 and len(native['coupledTraces'])==22 and native['statesCompared']==174 and native['unsafeMutantsDetected']==4 and native['unchangedLegacyDecoderControls']==44
quota_path=only('qa/control-quota-check-*/report.json');quota=verify(quota_path)
assert quota['evidence']['checks']==69 and quota['evidence']['distinctJobControls']==4 and quota['evidence']['repeatedAcknowledgments']==25 and quota['evidence']['normalOwnedExit']
parent=repo/'implementation/warlock-preview-provider-v98';prior=json.loads((parent/'component-manifest.json').read_text());assert not prior['passed'] and prior['admissionGuardPassed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
guard_path=pathlib.Path(prior['nativeAdmissionGuardReport']);guard=json.loads(guard_path.read_text());assert guard['passed']
for rel,value in guard['inputs'].items():assert sha(root/rel)==value,rel
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/imported_clients.hpp','native/client_producer.hpp','native/client-command-test.cpp','native/preview_uri.hpp','native/preview_uri.cpp','native/imported_control_admission.hpp']:
 assert sha(root/name)==sha(parent/name)
assert 'retained_client_command.hpp' not in (root/'native/host.c').read_text()
assert 'retained_client_command.hpp' not in (root/'native/shared-host.c').read_text()
files={}
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
    assert not p.is_symlink(),p
    if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'retainedClientCommandReport':str(native_path),'nativeQuotaRoundtripReport':str(quota_path),'retainedNativeAdmissionGuardReport':str(guard_path),'parentCounterexampleManifest':str(parent/'component-manifest.json'),'legacyDecoderAndRegressionSourceUnchanged':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Inactive retained original-receiver cleanup decoder validates actual Native ready packet despite stale frontend readiness, while original strict decoder and all44 fixed regression controls remain unchanged and pass.14 explicitly selected Quint scenarios/22 actual compiled C++ traces/174 comparisons/four unsafe compiled variants pass original job/token/readiness/ownership/coverage/expiry/typed-field controls. Actual optimized Elm/native Coordinator/Broker/real URI reader/Native control bank+C prefix69 controls pass Acquire/Cancel/late Offer Release/final ACK, two actual native terminal proofs and25 identical repeated ACKs reusing one original ticket without effect reinvocation. Synthetic source observations and fixture PNG-header bytes; no capture, WebKit, physical backend or actual actor/host close acceptance. Actor/reconciliation quota remains retained, not inferred complete. Original held98 failed counterexample retained. Inherited Native admission13/21/189/four variants verified byte-identical. Current fully qualified runtime remains GUI92/native128/core16/plugin18. Provider admission/typed ticket integration, original physical release barriers, reconciliation, renderer/native ticket outbox and WebKit activation remain required.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'retainedDecoderScenarios':14,'retainedDecoderTraces':22,'retainedDecoderStates':174,'unsafeCompiledNativeVariantsDetected':4,'unchangedLegacyDecoderControls':44,'compiledElmNativeQuotaControls':69,'repeatedAcknowledgmentsWithoutNewIssuance':25,'inheritedAdmissionGuardPassed':True,'legacyDecoderAndRegressionSourceUnchanged':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Opt-in controlled Native provider integration: enroll receiver before initial jobs, reserve quotas before existing start/resume paths, validate actual native command slots, retain original immutable Native tickets/confirmation, guard original physical/proof/actor release, reconcile receiver replacement, adapt renderer outbox and activate actual WebKit retirement/outgoing routing together.'}
(pathlib.Path(__file__).parent/'component-report99.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI99 controlled cleanup native14selected/22traces/174states/fourcompiled variants;44original strict-decoder fixedcontrols pass unchanged.69actual optimizedElm/nativeBroker/realURI/Nativebank+Cprefix controls: Acquire/Cancel/lateOfferRelease/finalACK,twoNativeproofs,25exactACKretries withoutnewordinal/effects; unusedactor/reconciliation quotas remain. Held98 failedlegacy lateOffer counterexample preserved, inheritedadmission13/21/189/four byteidentical. Syntheticobservations/fixturebytes only; noWebKit/actualcapture/hostclose/nativeRelease qualification. Next publish97/98/99 thenactualcontrolledprovider start/resume/ticket/reconciliation/outbox integration. FullqualifiedGUI92/native128 originalgatesunchanged.'],'progress',[str(manifest.relative_to(repo)),str(quota_path.relative_to(repo)),str(native_path.relative_to(repo))]))
