"""Hold bounded inactive outgoing control primitives and actual coupled evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v95'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
    found=list(root.glob(pattern));assert len(found)==1,found;return found[0]
def verify(path):
    proof=json.loads(path.read_text());assert proof['passed'],path
    for rel,value in proof['inputs'].items():
        p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
    for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted'];return proof
native_path=only('qa/control-delivery-check-*/report.json');native=verify(native_path)
assert native['namedScenarios']==12 and len(native['coupledTraces'])==20 and native['statesCompared']==190 and native['unsafeMutantsDetected']==3
js_path=only('qa/control-outbox-model-check-*/report.json');js=verify(js_path)
assert js['namedScenarios']==10 and len(js['coupledTraces'])==22 and js['statesCompared']==389 and js['unsafeActualJSVariantsDetected']==3
roundtrip_path=only('qa/control-outbox-check-*/report.json');roundtrip=verify(roundtrip_path)
assert roundtrip['evidence']['checks']==64 and roundtrip['evidence']['normalOwnedExit']
parent=repo/'implementation/warlock-preview-provider-v94';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
# Existing production modules remain byte-identical; new primitives are not
# loaded or routed. Parent build acceptance is retained, never relabeled current.
for base in ['src','native','assets','adapter']:
    for p in (parent/base).glob('*'):
        if p.is_file():assert sha(root/base/p.name)==sha(p),p
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
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativeControlReceiptReport':str(native_path),'outboxModelReport':str(js_path),'outboxNativeRoundtripReport':str(roundtrip_path),'parentQualifiedProviderManifest':str(parent/'component-manifest.json'),'unchangedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Inactive constant-storage native exact-wire original-grant control receipt/deduplication primitive and immutable bounded JS outbox. Actual C matches12 selected Quint scenarios/20 coupled traces/190 states/three compiled mutations. Actual JS matches10 selected Quint scenarios/22 coupled traces/389 states/three syntax-checked mutations. Actual compiled C/native-metadata and JS roundtrip64 controls passes normal owned close, lost transmission/receipt, exact bytes/ordinals, Unknown outcome, backpressure, failed post, UTF8 bound, foreign/old grants and exhaustion. Production modules byte-identical to held94; no new full-host build or runtime qualification claimed. Native frontend receipt-confirmation close barrier, admission cleanup capacity/ordinal reservations, fresh-grant reload reconciliation and actual WebKit integration remain required. Fully qualified runtime stays GUI92/native128/core16/plugin18; all original GUI release gates remain.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'nativeControlScenarios':12,'nativeControlTraces':20,'nativeControlStates':190,'unsafeCompiledNativeVariantsDetected':3,'outboxScenarios':10,'outboxTraces':22,'outboxStates':389,'unsafeActualJSVariantsDetected':3,'outboxNativeControls':64,'unchangedProductionModulesVerified':True,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Fresh derivative: native original-frontend delivery-receipt confirmation and close barrier; then derive/reserve bounded cleanup queue/ordinal capacity before native admission, reconcile receiver replacement, and activate actual WebKit outgoing and retirement routing together.'}
(pathlib.Path(__file__).parent/'component-report95.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI95 inactive reliable-control primitives: NativeC12selected/20traces/190states/3compiled mutants; actualJS10selected/22traces/389states/3actualJS variants; actualNativeMetadata+JS64 loss/retry/ACK/Unknown/backpressure/UTF8/oldgrant/exhaustion/normalclose controls. All parent94 production modules unchanged; no current95 fullhost/native runtime claim. PUBLIC66 d67896fdde83540561f5097b22c59f19010e39f8 verified, locala324243c1bcf2b8dfec2c780270905e41d23ae09. Next native frontend receipt-confirmation close barrier, then native cleanup reservations before admission and fresh-grant reconciliation before actual WebKit activation. All original GUI release gates remain.'],'progress',[str(manifest.relative_to(repo)),str((pathlib.Path(__file__).parent/'component-report95.json').relative_to(repo)),str((repo/'docs/warlock-preview/v93/OUTGOING-CONTROL-CONTRACT.md').relative_to(repo))]))
