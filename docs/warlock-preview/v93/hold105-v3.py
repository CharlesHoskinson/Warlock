"""Freeze bounded original resource reconciliation and its exact owning plugin."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v105';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(base,rel):
 path=base/rel;d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(base/name)==value,name
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,name
 return path,d
def inventory(base):
 files={}
 for p in sorted(base.rglob('*')):
  rel=p.relative_to(base)
  if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
  if p.is_symlink():
   assert base==plugin and p.name=='hyprland' and p.parent.name=='include' and p.parent.parent.name.startswith('build-'),p
   assert p.is_dir() and p.resolve()==(p.parent.parent/'owning-headers').resolve() and p.resolve().is_relative_to(base),p
   continue
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 return files
cpath,c=verify(root,'qa/capture-resource-check-v3-1791342242023731147/report.json')
assert c['cEvidence']['checks']==477 and c['cEvidence']['resourceCases']==6 and c['cEvidence']['normalOwnedExit']
assert c['decoderEvidence']['checks']==35 and c['unsafeCompiledVariantsDetected']==4
for name,value in c['pluginInputs'].items():assert sha(plugin/'native'/name)==value
mpath,model=verify(root,'qa/capture-resource-model-check-1791342186979098129/report.json')
assert model['namedScenarios']==14 and len(model['coupledTraces'])==22 and model['statesCompared']==349 and model['unsafeMutantsDetected']==3
assert sha(plugin/'native/capture-resources.hpp')==model['pluginInputSHA256']
ipath,intent=verify(root,'qa/capture-intent-model-check-v3-1791342276548529306/report.json')
assert intent['namedScenarios']==14 and len(intent['coupledTraces'])==66 and intent['statesCompared']==816 and intent['unsafeMutantsDetected']==3
opath,original=verify(root,'qa/imported-controlled-c-check-v3-1791342276548549516/report.json')
assert original['checks']==10190 and original['controls'][0]['normalOwnedExit'] and original['controls'][0]['actorsTurnedOver']==260 and original['controls'][0]['nativeIssuedPrefix']==1041
bpath,build=verify(root,'qa/build-1791342038923772931/report.json');assert len(build['commands'])==95
rpath,resources=verify(plugin,'qa/resource-check-1791342243188336864/report.json')
assert resources['evidence']['checks']==21 and resources['evidence']['actualExportDescriptorsClosed']==2 and resources['unsafeCompiledVariantsDetected']==3
pbpath,pb=verify(plugin,'qa/build-1791342038926680323/report.json')
assert not pb['missingSymbols'] and pb['core']['componentManifest'].endswith('/warlock-core-family-crop-v16/component-manifest.json')
assert sha(pb['binary'])==pb['binarySHA256'];descriptor=plugin/'native-build-report.json';pd=json.loads(descriptor.read_text())
assert pd['pluginBuildReport']==str(pbpath) and pd['pluginBuildReportSHA256']==sha(pbpath)
for base in [root,plugin]:
 ancestry=json.loads((base/'ANCESTRY.json').read_text());parent=pathlib.Path(ancestry['parent']);m=parent/'component-manifest.json'
 assert sha(m)==ancestry['parentManifestSHA256']
 prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
 for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for p in (repo/'implementation/warlock-preview-provider-v104'/name).glob('*'):
  if p.is_file():assert sha(root/name/p.name)==sha(p)
for name in ['host.c','shared-host.c','preview_broker.hpp','preview_fd.hpp','control_reservations.hpp','retirement_journal.hpp']:
 assert sha(root/'native'/name)==sha(repo/'implementation/warlock-preview-provider-v104/native'/name)
failed=root/'qa/capture-resource-check-v2-1791342038924871282/report.json';assert not json.loads(failed.read_text())['passed']
scope='CPU component only: actual plugin19 resource engine/wire and strict GUI decoder reconcile original capture uncertainty on authenticated synthetic C/socket path;477 C checks/six cases,35 decoder checks/four compiled variants;21 engine checks/two actual export descriptors/three variants;14 resource scenarios/22 compiled traces/349 states/three variants;original14 capture scenarios/66 traces/816 states/three variants;10190 controlled C/260 metadata actors/1041 tickets and95 full-host commands. Exact core16/plugin19 compile/symbol closure. Original capture intent/deadline retained. Backend zero remains independent of local mapping/readers, terminal proofs, permanent incarnation, final processing and confirmation. Actual adopted FD reconciliation, Core registry/capture pixels/FD/native GUI, WebKit and live-binding detachment remain unqualified. Runtime GUI92/native128/core16/plugin18 and full release gates remain unchanged.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'resourceCReport':str(cpath),'resourceCChecks':477,'resourceCases':6,'resourceDecoderChecks':35,'resourceCCompiledVariants':4,'resourceModelReport':str(mpath),'resourceScenarios':14,'resourceTraces':22,'resourceStates':349,'resourceCompiledVariants':3,'captureModelReport':str(ipath),'captureScenarios':14,'captureTraces':66,'captureStates':816,'controlledCReport':str(opath),'controlledCChecks':10190,'controlledCMetadataActors':260,'controlledCNativeIssuedPrefix':1041,'fullBuildReport':str(bpath),'fullBuildCommands':95,'pluginComponentManifest':str(plugin/'component-manifest.json'),'heldFailedReports':[str(failed)],'originalRegressionSuitesRerunHere':False,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
pm={'schema':1,'owner':result['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'resourceEngineReport':str(rpath),'resourceControls':21,'actualExportDescriptorsClosed':2,'resourceCompiledVariants':3,'buildReport':str(pbpath),'nativeBuildReport':str(descriptor),'nativeAcceptance':False,'fullReleaseAccepted':False,'installed':False,'scope':'Exact core16 owning ABI/plugin19 source and strong-symbol closure plus actual owned-map resource engine/wire CPU qualification. No real Core registry/capture/FD/GUI acceptance.','files':inventory(plugin),'directoryAliases':{str(p.relative_to(plugin)):str(p.resolve()) for p in plugin.rglob('*') if p.is_symlink()}}
assert not (plugin/'component-manifest.json').exists();(plugin/'component-manifest.json').write_text(json.dumps(pm,indent=2)+'\n')
result['pluginComponentManifestSHA256']=sha(plugin/'component-manifest.json');result['files']=inventory(root)
assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
(pathlib.Path(__file__).parent/'component-report105.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI105/plugin19. '+scope,'Next actual adopted local FD/readers and post-transfer exception reconciliation; original native Core resource protocol/capture witnesses and explicit live-window binding detachment; then native-assigned renderer outbox/WebKit. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str((plugin/'component-manifest.json').relative_to(repo)),str(cpath.relative_to(repo)),str(mpath.relative_to(repo))]))
