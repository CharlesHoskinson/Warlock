"""Freeze exact Bootstrap borrowed-receipt lifetime and original strict close."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v108';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 path=pathlib.Path(path);d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(root/name)==value,(path,name)
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,(path,name)
 return d
paths={'bootstrapC':root/'qa/preview-bootstrap-realm-c-check-v3-1791349134483568823/report.json','bootstrapModel':root/'qa/preview-bootstrap-realm-model-check-1791348751768644082/report.json','regressions':root/'qa/resource-regression-check-1791348832594392628/report.json','build':root/'qa/build-1791348751766992210/report.json'}
reports={key:verify(path) for key,path in paths.items()}
c=reports['bootstrapC'];assert c['evidence']['checks']==97 and c['evidence']['nativeRealmEpochThrough']=='3' and c['evidence']['failedConstructionEpochConsumed'] and c['evidence']['normalOwnedExit'] and not c['evidence']['coreExitedBeforeStrictClose']
assert c['coreDeathEvidence']['passed'] and c['coreDeathEvidence']['normalOwnedExit'] and c['coreDeathEvidence']['coreExitedBeforeStrictClose'] and c['coreDeathEvidence']['nativeRealmEpochThrough']=='1' and not c['coreDeathEvidence']['failedConstructionEpochConsumed']
assert c['unsafeCompiledVariantsDetected']==1 and c['mutant']['normalOwnedCleanupBeforeAssertion']
q=reports['bootstrapModel'];assert q['namedScenarios']==17 and len(q['coupledTraces'])==29 and q['statesCompared']==719 and q['invariantSamples']==250 and q['unsafeCompiledVariantsDetected']==3 and all(t['normalOwnedExit'] for t in q['coupledTraces'])
reg=reports['regressions'];assert len(reg['reports'])==4;underlying={}
for name,row in reg['reports'].items():
 p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];underlying[name]=verify(p)
fd=underlying['capture-resource-fd-check.py'];assert fd['readerEvidence']['checks']==49 and fd['postTransferEvidence']['checks']==40 and fd['unsafeCompiledVariantsDetected']==2 and all(fd[k]['normalOwnedExit'] and fd[k]['actualImportedFDClosed'] for k in ['readerEvidence','postTransferEvidence'])
rm=underlying['capture-resource-model-check.py'];assert rm['namedScenarios']==14 and len(rm['coupledTraces'])==22 and rm['statesCompared']==349 and rm['unsafeMutantsDetected']==3
cm=underlying['capture-intent-model-check-v3.py'];assert cm['namedScenarios']==14 and len(cm['coupledTraces'])==66 and cm['statesCompared']==816 and cm['unsafeMutantsDetected']==3
cc=underlying['imported-controlled-c-check-v3.py'];assert cc['checks']==10190 and cc['controls'][0]['actorsTurnedOver']==260 and cc['controls'][0]['nativeIssuedPrefix']==1041 and cc['controls'][0]['normalOwnedExit']
build=reports['build'];assert len(build['commands'])==95 and sha(paths['build'].parent/'elm-host')==build['binarySHA256']
pm=plugin/'component-manifest.json';held=json.loads(pm.read_text());assert held['sourceHeld'] and held['passed']
for rel,row in held['files'].items():assert sha(plugin/rel)==row['sha256'],rel
for rel,alias in held['directoryAliases'].items():assert (plugin/rel).is_symlink() and str((plugin/rel).resolve())==alias
assert sha(plugin/'native/capture-resources.hpp')==fd['pluginResourceHeaderSHA256']==rm['pluginInputSHA256']
ancestry=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(ancestry['parent']);m=parent/'component-manifest.json';assert sha(m)==ancestry['parentManifestSHA256']
prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['realmCChecks']==111 and prior['realmRaceChecks']==36
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for p in (parent/name).glob('*'):
  if p.is_file():assert sha(root/name/p.name)==sha(p)
failed=[str(p) for p in sorted((root/'qa').glob('*/report.json')) if not json.loads(p.read_text()).get('passed',False)];assert len(failed)==1
scope='Inactive CPU component: exact Bootstrap-aware strict C owner closure validates original Native transport/Endpoint/receiver epoch/creator thread/empty borrowed receipt membership, retains original physical/proof/actor/final-processing/independent-confirmation barriers, completes Native claim then releases delivery before Endpoint destruction. Refused/foreign Bootstrap close preserves original owner/channel; safe lookup/poll refusal and fresh channel reattachment retain the same Native binding. Actual C97 live replacement controls and separate'+str(c['coreDeathEvidence']['checks'])+' actual synthetic native-peer-death close controls/two independent owned peer exits per case/one precise compiled variant;17 selected Quint/29 actual C traces/719 states/three variants. Current95 full-host commands and original49 reader+40 post-transfer allocation/resource14/22/349/capture14/66/816/C10190/260 actors/1041 tickets pass. One count-premise failure retained; fixture behavior unchanged. Elm/assets byte-identical to held107/106; original compiled Elm/native ACK/local reader/model evidence retains its parent source. Actual native GUI92/native129/core16/plugin19 remains2517/278. No live-window detachment/current controlled Core/WebKit or full release acceptance.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'bootstrapCChecks':97,'bootstrapCoreDeathChecks':c['coreDeathEvidence']['checks'],'bootstrapCCompiledVariants':1,'bootstrapScenarios':17,'bootstrapTraces':29,'bootstrapStates':719,'bootstrapModelCompiledVariants':3,'actualReaderChecks':49,'actualPostTransferChecks':40,'controlledCChecks':10190,'fullBuildCommands':95,'unchangedElmParentManifest':str(m),'unchangedElmParentManifestSHA256':sha(m),'heldFailedReports':failed,'webKitActivated':False,'liveWindowDetachmentImplemented':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report108.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI108. '+scope,'Next exact owned publication76 after verified public75, then fresh live-window scoped detachment with distinct typed proof/readiness/final processing/confirmation and native renderer realm delivery/current Core/WebKit. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
