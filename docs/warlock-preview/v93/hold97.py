"""Hold exact inactive native cleanup reservation and ticket issuer scope."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v97'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
    found=list(root.glob(pattern));assert len(found)==1,found;return found[0]
def verify(path):
    proof=json.loads(path.read_text());assert proof['passed'],path
    for rel,value in proof['inputs'].items():
        p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
    for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted'];return proof
native_path=only('qa/control-reservations-check-v4-*/report.json');native=verify(native_path)
assert native['namedScenarios']==11 and len(native['coupledTraces'])==23 and native['statesCompared']==397 and native['unsafeCompiledNativeMutantsDetected']==4 and native['adversarialChecks']==64
parent=repo/'implementation/warlock-preview-provider-v96';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','native','assets','adapter']:
    for p in (parent/base).glob('*'):
        if p.is_file() and str(p.relative_to(parent))!='native/preview-control-delivery.h':assert sha(root/base/p.name)==sha(p),p
for host in ['native/host.c','native/shared-host.c']:
    assert 'control_reservations.hpp' not in (root/host).read_text()
    assert 'preview-control-delivery.h' not in (root/host).read_text()
assert 'retained-preview-controls.js' not in (root/'assets/popup.html').read_text()
files={}
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
    assert not p.is_symlink(),p
    if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativeControlReservationReport':str(native_path),'parentQualifiedProviderManifest':str(parent/'component-manifest.json'),'unchangedActivatedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Inactive exclusive native ordinal/queue reservation bank. Actual C++ bank and C dispatch/confirmation match11 explicitly selected Quint scenarios/23 coupled traces/397 state comparisons with four compiled native variants detected. Sixty-four additional sanitizer-backed controls verify partial confirmation, exact wire ownership, stale reservations, every foreign grant field, malformed and full-envelope byte rejection without ordinal consumption, original maximum issuance and exact retry at exhaustion. Separate explicit boundary grant represents prior confirmed history; no live namespace resets. Native caller must derive and reserve real cleanup quotas before physical admission and independently prove physical/proof/actor barriers before reservation release. Existing activated production modules remain unchanged; full qualified runtime remains GUI92/native128/core16/plugin18. No actual admission integration, receiver reconciliation, WebKit activation, physical effects or full release acceptance. Original failed Quint filter type and incorrectly sized envelope fixture remain held.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'nativeReservationScenarios':11,'nativeReservationTraces':23,'nativeReservationStates':397,'unsafeCompiledNativeVariantsDetected':4,'adversarialReservationControls':64,'unchangedActivatedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Derive actual Native ImportedClients job/proof/actor quotas with executable witnesses; attach reservations before actual physical admission, validate and coalesce typed commands by original native identity, use native-assigned immutable tickets in the renderer, reconcile receiver replacement, then activate actual WebKit outgoing and retirement routing together.'}
(pathlib.Path(__file__).parent/'component-report97.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI97 native reservation bank: actual11selected/23traces/397states/fourcompiled unsafe variants;64sanitizer adversarial controls including partialconfirmation/foreigngrant/bytebound/counterexhaustion. Native-issued immutable exact tickets consume only trusted pre-admission quota; no namespace reset or physical authority. Production modules unchanged and protocol inactive. PUBLIC68 3a185885ae0ef3c1f3d45cc6c7508e77441f30d1 verified852blobs; localreceipt0d26d7bf63411aed795ab434b45376868b2e2e23. Next actualquota/admission/issuer/outbox/reconciliation integration before WebKit activation; fullqualifiedGUI92/native128 and all original release gates remain.'],'progress',[str(manifest.relative_to(repo)),str((pathlib.Path(__file__).parent/'component-report97.json').relative_to(repo))]))
