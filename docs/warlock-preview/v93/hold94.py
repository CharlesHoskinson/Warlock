"""Hold exact fair polling source, current builds, failures and native evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v94'
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
model_path=only('qa/retirement-poll-check-v2-*/report.json');model=verify(model_path)
assert model['namedScenarios']==10 and model['invariantSamples']==200 and len(model['coupledTraces'])==22 and model['statesCompared']==427 and model['unsafeCompiledNativeMutantsDetected']==3
for row in model['mutants']:assert row['compiled'] and row['namedObservableMismatch']
fair_path=only('qa/retirement-fair-poll-check-*/report.json');fair=verify(fair_path);assert fair['checks']==50 and fair['controls'][0]['normalOwnedExit']
aggregate_path=only('qa/actor-retirement-check-v3-*/report.json');aggregate=verify(aggregate_path);assert aggregate['checks']==9068 and aggregate['evidence'][1]['sequentialSubjects']==280
channel_path=only('qa/actor-retirement-channel-check-v2-*/report.json');channel=verify(channel_path);assert channel['checks']==14467 and channel['evidence'][0]['zeroFloorActorRetired'] and channel['evidence'][2]['sequentialSubjects']==280
failed_path=only('qa/retirement-poll-check-[0-9]*/report.json');failed=json.loads(failed_path.read_text());assert not failed['passed'] and 'QNT404' in failed['error']
for rel,value in failed['inputs'].items():assert sha(root/rel)==value,rel
for rel,value in failed['artifacts'].items():assert sha(failed_path.parent/rel)==value,rel
parent=repo/'implementation/warlock-preview-provider-v93';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
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
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'buildReport':str(build_path),'retainedDeliveryReport':str(elm_path),'readinessNativeElmReport':str(native_path),'fairPollingModelReport':str(model_path),'fairPollingNativeReport':str(fair_path),'aggregateRetirementReport':str(aggregate_path),'retainedChannelReport':str(channel_path),'failedPollingFixture':str(failed_path),'unchangedElmAssetIdentityVerified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'One round-robin readiness candidate per call; all original local physical/producer/backend/proof/receiver barriers precede a fresh native query. Full95 and byte-identical Elm,45 processing controls,54 actual C/native/Elm loss/ACK/receiver controls,50 actual C/socket query-count/fairness/terminal-proof/normal-close controls. Ten selected Quint scenarios/200 bounded invariant samples match22 actual native journal traces/427 states; three separately compiled native mutants fail exact witnesses. Original9068 aggregate and14467 retained-channel controls with280 synthetic subjects preserved. No actual WebKit activation, measured timing acceptance or real captured/window-turnover acceptance; fully qualified runtime stays GUI92/native128/core16/plugin18.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={'passed':True,'providerManifest':str(manifest),'providerManifestSHA256':sha(manifest),'buildCommands':95,'retainedDeliveryControls':45,'readinessNativeElmControls':54,'fairPollingControls':50,'fairPollingScenarios':10,'fairPollingTraces':22,'fairPollingStates':427,'unsafeCompiledNativeMutantsDetected':3,'aggregateRetirementControls':9068,'retainedChannelControls':14467,'unchangedElmAssetIdentityVerified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Fresh host/transport derivative: freeze exact bounded outgoing delivery/retry/processing-ACK, native cleanup reservation before admission, receiver reload and exhaustion contract. Keep single Elm policy, existing tuples and all original release gates.'}
(pathlib.Path(__file__).parent/'component-report94.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI94 bounded fair polling: full95/identicalElm/45 controls; actualCnativeElm54 and actualCsocket50 exact query-count/terminal-proof/receiver/fairness/normalclose controls. Quint10selected/22actualC++traces/427states/3compiled native mutants. Original9068aggregate/14467retainedChannel/280synthetic preserved; failedmodel fixture held. Public65 d0372d2fe8a19048e404e364d2ca0c9f94b248b1 verified, localreceiptc7584a62e5e2dbf270079092a7ea49d74cbb6f0f. Fully nativequalifiedGUI92/native128 unchanged, no94WebKit activation/performanceacceptance. Next publication66 then fresh exact bounded reliable outgoing controls/cleanupreservation/reload contract and actualhost routing. All original release gates remain.'],'progress',[str(manifest.relative_to(repo)),str((pathlib.Path(__file__).parent/'component-report94.json').relative_to(repo))]))
