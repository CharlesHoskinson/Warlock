"""Freeze only verified current readiness/rendezvous component scope."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v93'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
    found=list(root.glob(pattern));assert len(found)==1,found;return found[0]
def verify(path):
    proof=json.loads(path.read_text());assert proof['passed'],path
    for rel,value in proof['inputs'].items():
        p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
    for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted'];return proof
build_path=only('qa/build-*/report.json');build=verify(build_path)
assert len(build['commands'])==95 and all(row['exitCode']==0 for row in build['commands'])
for key in ['compilerDependencies','linkedLibraries','tools']:
    for name,row in build[key].items():assert sha(pathlib.Path(name))==row['sha256'],name
assert sha(build_path.parent/'elm-host')==build['binarySHA256']
elm_path=only('qa/retirement-delivery-check-*/report.json');elm=verify(elm_path);assert elm['evidence']['checks']==45
native_path=only('qa/retirement-native-elm-check-v4-*/report.json');native=verify(native_path)
assert native['evidence']['checks']==20 and native['evidence']['nativeCChecks']==34 and native['evidence']['normalOwnedExit']
model_path=only('qa/retirement-readiness-check-v3-*/report.json');model=verify(model_path)
assert model['namedScenarios']==8 and model['invariantSamples']==200 and len(model['coupledTraces'])==20 and model['unsafeCompiledNativeMutantsDetected']==3
for row in model['mutants']:assert row['compiled'] and row['namedObservableMismatch']
failed=[]
for pattern in ['qa/retirement-readiness-check-[0-9]*/report.json','qa/retirement-readiness-check-v2-*/report.json']:
    path=only(pattern);proof=json.loads(path.read_text());assert not proof['passed']
    for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
    for rel,value in proof['artifacts'].items():assert sha(path.parent/rel)==value,rel
    failed.append(str(path))
parent=repo/'implementation/warlock-preview-provider-v92';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for p in (root/'src').glob('*.elm'):assert sha(p)==sha(parent/'src'/p.name),p
old_build=pathlib.Path(prior['buildReport'])
for name in ['elm.js','popup.js','bar.js','preview-replay.js']:
    assert sha(build_path.parent/'inputs/assets'/name)==sha(old_build.parent/'inputs/assets'/name),name
files={}
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
    assert not p.is_symlink(),p
    if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'buildReport':str(build_path),'retainedDeliveryReport':str(elm_path),'readinessNativeElmReport':str(native_path),'readinessModelReport':str(model_path),'failedReadinessFixtures':failed,'unchangedElmAssetIdentityVerified':True,'parentQualifiedGUIManifest':str(parent/'component-manifest.json'),'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Current full95 build, byte-identical Elm assets and45 processing-prefix controls. Actual C/socket/native/Elm54 controls retain the original single readiness through a real second native receiver barrier and complete after it clears without another Elm effect; loss/retry/ACK/neighbor/close and normal cleanup remain exact. Native transport readiness metadata passes8 selected Quint scenarios/200 sampled30-step runs/20 actual C++ coupled traces with3 precisely detected compiled native mutations. Commit in the journal is trusted caller bookkeeping, not a physical proof or independent Elm policy. Original full qualified runtime stays GUI92/native128/core16/plugin18; current93 native readiness API is not wired through WebKit. Actual host/reliable outgoing delivery, captured resources, real continuing windows and every original release gate remain open.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'buildCommands':95,'retainedDeliveryControls':45,'readinessNativeElmControls':54,'readinessScenarios':8,'readinessTraces':20,'readinessStates':model['statesCompared'],'unsafeCompiledNativeMutantsDetected':3,'unchangedElmAssetIdentityVerified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Fresh derivative: implement bounded host readiness/observation/final routing and exact outgoing control delivery acknowledgment/retry without effect replay or namespace reset. Freeze the transport/capacity/cleanup reservation contract first. Keep current fully qualified GUI92/native128 tuple and all original gates. Review polling fairness and original operation budgets before production evaluation.'}
(pathlib.Path(__file__).parent/'component-report.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI93 full95/byte-identical Elm assets/45 prefix controls; actualCnativeElm54 controls preserve one-shot readiness through real receiver barrier, lostfinal/lostACK/neighbor/close/normalexit. Native metadata model8selected/20coupled/'+str(model['statesCompared'])+' states/3 compiled native mutants; failed fixtures held. Fully qualified runtime remainsGUI92/native128 exactcore16/plugin18 PASS2466/277normal/all2458prior126fixed, public64 3cd4db6f232d185d8655de3b76106b2229da7272 verified, receiptbe920333. Next fresh owned host/transport derivative, freeze bounded retry/cleanup reservation/reload contracts, preserve single immutable policy and all original release gates.'],'progress',[str(manifest.relative_to(repo)),str((pathlib.Path(__file__).parent/'component-report.json').relative_to(repo))]))
