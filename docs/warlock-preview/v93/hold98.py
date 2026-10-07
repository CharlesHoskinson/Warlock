"""Hold accepted native admission guard and exact failed late-offer release witness."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v98';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 found=list(root.glob(pattern));assert len(found)==1;return found[0]
def verify(path,passed):
 proof=json.loads(path.read_text());assert proof['passed']==passed
 for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in proof['artifacts'].items():assert sha(path.parent/rel)==value,rel
 return proof
admissionPath=only('qa/control-admission-check-*/report.json');admission=verify(admissionPath,True)
assert admission['namedScenarios']==13 and len(admission['coupledTraces'])==21 and admission['statesCompared']==189 and admission['unsafeMutantsDetected']==4
failurePath=only('qa/control-quota-check-*/report.json');failure=verify(failurePath,False)
assert 'Actual owned client packet correlation' in (failurePath.parent/'controls.stderr').read_text()
assert all(v['exitCode']==0 for v in failure['commands'] if v['name'] in {'compile','native-compile'})
parent=repo/'implementation/warlock-preview-provider-v97';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/imported_clients.hpp','native/client_producer.hpp']:
 assert sha(root/name)==sha(parent/name)
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink()
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'admissionGuardPassed':True,'files':files,'nativeAdmissionGuardReport':str(admissionPath),'lateOfferReleaseCounterexample':str(failurePath),'nativeAcceptance':False,'fullReleaseAccepted':False,'webKitActivated':False,'scope':'Accepted inactive native empty receiver enrollment and actual Coordinator/Broker cleanup quota guard:13 explicitly selected Quint scenarios/21 compiled C++ traces/189 state comparisons/four compiled unsafe variants. Original job/floor/deadline, receiver epoch, capacity-before-intent and Unknown post-issuance obligations preserved. Native provider integration remains pending. Separately, actual optimized Elm/native Broker/URI/legacy decoder quota roundtrip fails: original native offer arrives late after Elm Cancel, Elm emits Release with signaled:false for exact original handle, while native packet is actually ready; original strict decoder refuses. This is a coupled CPU counterexample, not deployed GUI/native compositor failure. Original decoder and its fixed negative-control oracle remain unchanged. Fresh controlled path must validate against original native readiness and exact job/token without treating stale frontend readiness as native authority. No native/full release acceptance.'}
manifest.write_text(json.dumps(result,indent=2)+'\n')
report={k:v for k,v in result.items() if k!='files'};report['providerManifest']=str(manifest);report['providerManifestSHA256']=sha(manifest)
(pathlib.Path(__file__).parent/'component-report98.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS heldGUI98 mixed evidence: actual native admission guard13/21/189/fourcompiled unsafe variants passes; coupled actual optimizedElm/nativeBroker/actualURI reader lateOffer->Release fails original decoder signaled:false evenwhen actual native packet ready. Preserve original strict decoder/negative oracle. Fresh99 controlled receiver command path validates actual native readiness and exact original job/token, preserving immutable original packet and all physical/proof barriers. Provider/renderer/reconciliation/WebKit and fullrelease remain open.'],'progress',[str(manifest.relative_to(repo)),str(failurePath.relative_to(repo)),str(admissionPath.relative_to(repo))]))
