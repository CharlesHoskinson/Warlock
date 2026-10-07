"""Freeze actual opt-in native admission integration and its bounded evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v100'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(base,pattern):
 rows=list(base.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(path):
 proof=json.loads(path.read_text());assert proof['passed'],path
 for rel,value in proof['inputs'].items():
  p=pathlib.Path(rel);assert sha(p if p.is_absolute() else root/p)==value,rel
 for rel,value in proof.get('artifacts',{}).items():assert sha(path.parent/rel)==value,rel
 assert not proof.get('nativeAcceptance',False) and not proof.get('fullReleaseAccepted',False)
 return proof
native_path=only(root,'qa/imported-control-guard-check-*/report.json');native=verify(native_path)
assert native['checks']==40 and native['controls'][0]['normalOwnedExit']
model_path=only(root,'qa/control-admission-check-v3-*/report.json');model=verify(model_path)
assert model['namedScenarios']==15 and len(model['coupledTraces'])==23 and model['statesCompared']==191 and model['unsafeMutantsDetected']==6
build_path=only(root,'qa/build-*/report.json');build=verify(build_path);assert len(build['commands'])==95
regression_path=only(pathlib.Path(__file__).parent,'regressions100-*/report.json');regression=verify(regression_path)
assert len(regression['results'])==12 and all(row['exitCode']==0 for row in regression['results'])
parent=repo/'implementation/warlock-preview-provider-v99';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['passed'] and prior['sourceHeld']
assert sha(parent/'component-manifest.json')==json.loads((root/'ANCESTRY.json').read_text())['parentManifestSHA256']
for base in ['src','assets','adapter']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p)
for name in ['native/host.c','native/shared-host.c','native/imported-clients.cpp','native/client_producer.hpp','native/client-command-test.cpp']:
 assert sha(root/name)==sha(parent/name)
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
scope='Actual opt-in ImportedClients start/resume admission: owning Broker, single obligation manager, empty original receiver, native quota before intent/job mutation, old physical/proof barriers plus frontend control confirmation before resume source query. Actual peer-authenticated synthetic native socket fixture40 controls,15 selected Quint scenarios/23 compiled native traces/191 comparisons/six compiled unsafe variants,95 full-host build commands and12 unchanged original regression suites pass. Original default C factories/shared-host WebKit flow unchanged. No genuine capture, hardware, native actor/host close acceptance or release qualification. Fully native qualified GUI92/native128/core16/plugin18 retained. Controlled C factory, native purpose issuer, confirmed duplicate tombstones, physical/actor quota release, reconciliation and native-assigned renderer outbox remain required before activation.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'files':files,'nativeAdmissionIntegrationReport':str(native_path),'nativeAdmissionModelReport':str(model_path),'fullBuildReport':str(build_path),'originalRegressionReport':str(regression_path),'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
manifest.write_text(json.dumps(result,indent=2)+'\n')
(pathlib.Path(__file__).parent/'component-report100.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI100. '+scope,'Next actual native purpose-validated job tickets and confirmed duplicate tombstones, followed by C provider, original physical/actor quota release, reconciliation and native-assigned renderer outbox integration.'], 'progress',[str(manifest.relative_to(repo)),str(native_path.relative_to(repo)),str(model_path.relative_to(repo)),str(regression_path.relative_to(repo))]))
