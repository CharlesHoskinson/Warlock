"""Freeze original capture intent and actual mapping adoption error custody."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v104';parent=repo/'implementation/warlock-preview-provider-v103'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(path):
 d=json.loads(path.read_text());assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 for rel,value in d['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in d.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
 return d
preservation_path=only('qa/capture-preservation-check-*/report.json');preservation=verify(preservation_path)
assert preservation['captureEvidence']['checks']==51 and preservation['captureEvidence']['retainedUnknownCases']==3 and preservation['captureEvidence']['normalOwnedExit']
assert preservation['allocationEvidence']['checks']==22 and preservation['allocationEvidence']['allocationCases']==4 and preservation['unsafeCompiledVariantsDetected']==3
model_path=only('qa/capture-intent-model-check-v2-*/report.json');model=verify(model_path)
assert model['namedScenarios']==14 and len(model['coupledTraces'])==66 and model['statesCompared']==816 and model['unsafeMutantsDetected']==3
c_path=only('qa/imported-controlled-c-check-v3-*/report.json');c=verify(c_path)
assert c['checks']==10190 and c['controls'][0]['normalOwnedExit'] and c['controls'][0]['actorsTurnedOver']==260 and c['controls'][0]['nativeIssuedPrefix']==1041
build_path=only('qa/build-*/report.json');build=verify(build_path);assert len(build['commands'])==95
prior=json.loads((parent/'component-manifest.json').read_text());assert prior['sourceHeld'] and prior['passed'] and sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/imported_control_admission.hpp','native/control_reservations.hpp','native/retirement_journal.hpp','native/preview_broker.hpp','native/preview_fd.hpp']:
 assert sha(root/name)==sha(parent/name),name
failed=only('qa/capture-intent-model-check-[0-9]*/report.json');assert not json.loads(failed.read_text())['passed']
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
scope='Actual native capture intent preserves original request/binding/context/raw command/deadline before invocation. Actual export/backend ownership is recorded before fallible local mapping/adoption. A mapping pointer is published only after real Broker adoption, including post-transfer result allocation exceptions; refused/pre-transfer storage remains caller owned without dangling retained pointer.51 actual authenticated synthetic socket controls cover capture refusal, malformed completion and unavailable FD transport, preserving unresolved original charge and refusing acquisition replay.22 actual sealed local FD/Broker controls cover success/refusal and allocator exceptions before/after transfer, original mapping/FD/terminal-proof ACK drain.Three compiled unsafe variants fail these assertions.14 explicitly selected capture Quint scenarios/66 actual native traces across three modes/816 observable states;three compiled variants differ on original traces.10190 controlled C checks/260 metadata actors/1041 uninterrupted tickets and95 full-host build/check commands pass again. GUI103 actor/job/reservation/admission/69Elm-nativeURI and12 original suites remain held at that source,not claimed rerun104. Initial replay fixture unused-function compile failure retained. No real compositor capture pixels/FD/backend reconciliation/Unknown settlement/live-window binding detachment/WebKit/native GUI or full release acceptance. Qualified runtime GUI92/native128/core16/plugin18 and original deadlines/release gates remain unchanged.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'capturePreservationReport':str(preservation_path),'captureIntentControls':51,'captureFailureModes':3,'localAllocationControls':22,'localAllocationCases':4,'captureAllocationCompiledVariants':3,'captureModelReport':str(model_path),'captureScenarios':14,'captureTraces':66,'captureStates':816,'captureCompiledVariants':3,'controlledCReport':str(c_path),'controlledCChecks':10190,'controlledCMetadataActors':260,'controlledCNativeIssuedPrefix':1041,'fullBuildReport':str(build_path),'fullBuildCommands':95,'retainedParentComponentReport':str(repo/'docs/warlock-preview/v93/component-report103.json'),'originalRegressionSuitesRerunHere':False,'heldFailedReports':[str(failed)],'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
manifest.write_text(json.dumps(result,indent=2)+'\n');(pathlib.Path(__file__).parent/'component-report104.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI104. '+scope,'Next actual backend cleanup-state protocol and original capture/export reconciliation, with native authoritative zero proofs before final cleanup. Define live-window binding detachment before native-assigned renderer outbox/WebKit activation.'],'progress',[str(manifest.relative_to(repo)),str(preservation_path.relative_to(repo)),str(model_path.relative_to(repo)),str(c_path.relative_to(repo))]))
