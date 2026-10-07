"""Freeze current imported storage/reader/confirmed-purpose qualification."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v106';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 path=pathlib.Path(path);d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(root/name)==value,name
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,name
 return d
def inventory(base):
 files={}
 for p in sorted(base.rglob('*')):
  rel=p.relative_to(base)
  if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 return files
regPath=root/'qa/resource-regression-check-1791344475458862053/report.json';reg=verify(regPath)
reports={k:pathlib.Path(v['path']) for k,v in reg['reports'].items()}
for k,p in reports.items():assert sha(p)==reg['reports'][k]['sha256']
fd=verify(reports['capture-resource-fd-check.py']);assert fd['readerEvidence']['checks']==49 and fd['readerEvidence']['actualReaderDrained'] and fd['postTransferEvidence']['checks']==40 and fd['postTransferEvidence']['postTransferAllocationFault'] and fd['unsafeCompiledVariantsDetected']==2
assert all(fd[k]['normalOwnedExit'] and fd[k]['actualImportedFDClosed'] for k in ['readerEvidence','postTransferEvidence'])
rm=verify(reports['capture-resource-model-check.py']);assert rm['namedScenarios']==14 and len(rm['coupledTraces'])==22 and rm['statesCompared']==349 and rm['unsafeMutantsDetected']==3
cm=verify(reports['capture-intent-model-check-v3.py']);assert cm['namedScenarios']==14 and len(cm['coupledTraces'])==66 and cm['statesCompared']==816 and cm['unsafeMutantsDetected']==3
cc=verify(reports['imported-controlled-c-check-v3.py']);assert cc['checks']==10190 and cc['controls'][0]['actorsTurnedOver']==260 and cc['controls'][0]['nativeIssuedPrefix']==1041 and cc['controls'][0]['normalOwnedExit']
localPath=root/'qa/imported-resource-model-check-v3-1791344341025095207/report.json';local=verify(localPath)
assert local['namedScenarios']==14 and len(local['coupledTraces'])==22 and local['statesCompared']==373 and local['unsafeCompiledVariantsDetected']==3 and all(t['normalOwnedExit'] for t in local['coupledTraces'])
cPath=root/'qa/capture-resource-check-v3-1791344374799546102/report.json';c=verify(cPath)
assert c['cEvidence']['checks']==477 and c['cEvidence']['resourceCases']==6 and c['decoderEvidence']['checks']==35 and c['unsafeCompiledVariantsDetected']==4
elmPath=root/'qa/capture-resource-elm-check-1791344374799836180/report.json';elm=verify(elmPath)
assert elm['evidence']['checks']==24 and elm['evidence']['actualCompiledElm'] and elm['evidence']['actualMappedNativeACK'] and elm['evidence']['normalOwnedExits']==2
for k,v in elm['elmSourceInputs'].items():assert sha(root/k)==v,k
assert sha(elm['elmBuildReport'])==elm['elmBuildReportSHA256']
buildPath=root/'qa/build-1791344374798398295/report.json';build=verify(buildPath);assert len(build['commands'])==95 and sha(buildPath.parent/'elm-host')==build['binarySHA256']
pluginManifest=plugin/'component-manifest.json';p=json.loads(pluginManifest.read_text());assert p['sourceHeld'] and p['passed']
for rel,row in p['files'].items():assert sha(plugin/rel)==row['sha256'],rel
for rel,alias in p['directoryAliases'].items():assert (plugin/rel).is_symlink() and str((plugin/rel).resolve())==alias
for d,key in [(fd,'pluginResourceHeaderSHA256'),(rm,'pluginInputSHA256'),(local,'pluginInputSHA256'),(elm,'pluginHeaderSHA256')]:assert sha(plugin/'native/capture-resources.hpp')==d[key]
for n,v in c['pluginInputs'].items():assert sha(plugin/'native'/n)==v
ancestry=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(ancestry['parent']);m=parent/'component-manifest.json';assert sha(m)==ancestry['parentManifestSHA256']
prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for path in (parent/name).glob('*'):
  if path.is_file():assert sha(root/name/path.name)==sha(path)
failed=[]
for name in ['imported-resource-model-check-1791344060153487580','imported-resource-model-check-v2-1791344122429229320']:
 path=root/'qa'/name/'report.json';assert not json.loads(path.read_text())['passed'];failed.append(str(path))
scope='CPU component only: actual controlled C/Native socket/SCM_RIGHTS/Broker imported storage,49 reader+40 actual post-transfer allocation controls/two compiled variants;24 optimized Elm/native final ACK controls/two normal exits;local14 selected Quint scenarios/22 actual C/GIO compiled traces/373 states/three compiled variants. Immediate URI revocation shares one Native quarantine, while storage remains until actual reader/backend/producer/local drain. Confirmed global reconciliation purposes retain original bytes/ordinal and suppress stale dispatch. Current resource477 C/six cases+35decoder/four variants,14/22/349/three resource traces,original capture14/66/816/three and C10190/260 metadata actors/1041 native tickets;95 full-host commands. Exact held core16/plugin19 source pair. No Core registry/capture pixels/WebKit/live-window binding detachment or full native release acceptance; qualified GUI92/native128/core16/plugin18 and original gates remain unchanged.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'resourceCReport':str(cPath),'resourceCChecks':477,'resourceCases':6,'resourceDecoderChecks':35,'resourceCCompiledVariants':4,'resourceModelReport':str(reports['capture-resource-model-check.py']),'resourceScenarios':14,'resourceTraces':22,'resourceStates':349,'resourceCompiledVariants':3,'captureModelReport':str(reports['capture-intent-model-check-v3.py']),'captureScenarios':14,'captureTraces':66,'captureStates':816,'controlledCReport':str(reports['imported-controlled-c-check-v3.py']),'controlledCChecks':10190,'controlledCMetadataActors':260,'controlledCNativeIssuedPrefix':1041,'importedFDReport':str(reports['capture-resource-fd-check.py']),'actualReaderChecks':49,'actualPostTransferChecks':40,'fdCompiledVariants':2,'importedResourceModelReport':str(localPath),'importedResourceScenarios':14,'importedResourceTraces':22,'importedResourceStates':373,'importedResourceCompiledVariants':3,'importedElmReport':str(elmPath),'importedElmChecks':24,'fullBuildReport':str(buildPath),'fullBuildCommands':95,'pluginComponentManifest':str(pluginManifest),'pluginComponentManifestSHA256':sha(pluginManifest),'heldFailedReports':failed,'originalRegressionSuitesRerunHere':False,'webKitActivated':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
result['files']=inventory(root);assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report106.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI106. '+scope,'Next exact owned publication73 after public72; real Core19 capture-resource protocol/native qualification, distinct live-window binding detachment, renderer native outbox/WebKit. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo)),str(localPath.relative_to(repo)),str(elmPath.relative_to(repo))]))
