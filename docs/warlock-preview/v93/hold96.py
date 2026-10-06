"""Hold exact frontend receipt-confirmation/close-barrier component scope."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v96'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
    found=list(root.glob(pattern));assert len(found)==1,found;return found[0]
def verify(path):
    proof=json.loads(path.read_text());assert proof['passed'],path
    for rel,value in proof['inputs'].items():
        p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
    for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted'];return proof
native_path=only('qa/control-confirmation-check-*/report.json');native=verify(native_path)
assert native['namedScenarios']==20 and len(native['coupledTraces'])==28 and native['statesCompared']==221 and native['unsafeMutantsDetected']==4
js_path=only('qa/control-outbox-confirmation-model-check-*/report.json');js=verify(js_path)
assert js['namedScenarios']==13 and len(js['coupledTraces'])==25 and js['statesCompared']==404 and js['unsafeActualJSVariantsDetected']==3
roundtrip_path=only('qa/control-confirmation-roundtrip-check-*/report.json');roundtrip=verify(roundtrip_path)
assert roundtrip['evidence']['checks']==58 and roundtrip['evidence']['normalOwnedExit']
parent=repo/'implementation/warlock-preview-provider-v95';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','native','assets','adapter']:
    for p in (parent/base).glob('*'):
        if p.is_file() and str(p.relative_to(parent)) not in {'native/preview-control-delivery.h','assets/retained-preview-controls.js'}:assert sha(root/base/p.name)==sha(p),p
assert 'retained-preview-controls.js' not in (root/'assets/popup.html').read_text()
assert 'preview-control-delivery.h' not in (root/'native/host.c').read_text()
assert 'preview-control-delivery.h' not in (root/'native/shared-host.c').read_text()
files={}
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
    assert not p.is_symlink(),p
    if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativeControlConfirmationReport':str(native_path),'outboxConfirmationModelReport':str(js_path),'confirmationNativeRoundtripReport':str(roundtrip_path),'parentQualifiedProviderManifest':str(parent/'component-manifest.json'),'unchangedActivatedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Inactive native original-frontend control receipt confirmation and compact monotonic prefix-confirmed close predicate, with bounded idempotent frontend confirmations. Actual C20 selected Quint scenarios/28 coupled traces/221 states/four compiled mutants; actual JS13 selected scenarios/25 coupled traces/404 states/three syntax-checked variants. Actual compiled native metadata/JS58 controls pass lost receipt and confirmation, native receipt rebroadcast without another Unknown invocation, empty-queue/failed-post confirmation retry, cumulative/old confirmation, future/foreign refusal, reopened barrier, callback reentrancy and normal owned close. Existing activated production modules byte-identical; no current full-host build or native runtime acceptance claimed. Prefix confirmation is separate from effect success and physical/terminal/actor proof. Native cleanup queue/ordinal reservations before admission, fresh-grant receiver reconciliation and actual WebKit outgoing/retirement activation remain required. Fully qualified GUI92/native128/core16/plugin18 and all original release gates unchanged.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'nativeConfirmationScenarios':20,'nativeConfirmationTraces':28,'nativeConfirmationStates':221,'unsafeCompiledNativeVariantsDetected':4,'outboxConfirmationScenarios':13,'outboxConfirmationTraces':25,'outboxConfirmationStates':404,'unsafeActualJSVariantsDetected':3,'confirmationNativeControls':58,'unchangedActivatedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Fresh native admission/transport derivative: derive bounded cleanup/control queue and ordinal reservation from actual Broker/job/proof/actor/journal contracts; reserve before physical issuance, preserve old-owner cleanup at capacity/exhaustion, reconcile receiver replacement, then activate actual WebKit outgoing and retirement routing together.'}
(pathlib.Path(__file__).parent/'component-report96.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI96 receipt-confirmation close barrier: NativeC20selected/28traces/221states/4compiled variants; actualJS13selected/25traces/404states/3JSvariants;58NativeMetadata+JS lostreceipt/lostconfirmation/emptyqueue-retry/cumulative/old/future/foreign/reentrancy/normalclose controls. Activated production modules unchanged and new protocol remains inactive. PUBLIC67 f6b9ef964d1551178fb3c21693da957feb44d0d7 verified798blobs, localreceipt9c6804a5c2b462dda63d2fa6d0844afced3d2acd. Next publish68, then reserve actual worst-case cleanup queue/ordinal capacity before native admission and reconcile receiver replacement before WebKit activation. FullqualifiedGUI92/native128 and all original release gates remain.'],'progress',[str(manifest.relative_to(repo)),str((pathlib.Path(__file__).parent/'component-report96.json').relative_to(repo))]))
