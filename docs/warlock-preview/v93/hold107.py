"""Freeze actual persistent realm ownership, coupled C traces and stale-CAS fix."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v107';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 path=pathlib.Path(path);d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(root/name)==value,(path,name)
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,(path,name)
 return d
def inventory(base):
 files={}
 for p in sorted(base.rglob('*')):
  rel=p.relative_to(base)
  if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 return files
paths={
 'realmC':root/'qa/preview-realm-c-check-v3-1791347787381300082/report.json',
 'realmModel':root/'qa/preview-realm-model-check-v4-1791347753848423769/report.json',
 'realmRace':root/'qa/preview-realm-race-check-v2-1791347753848610053/report.json',
 'regressions':root/'qa/resource-regression-check-1791347817271704693/report.json',
 'localResourceModel':root/'qa/imported-resource-model-check-v3-1791347879263629595/report.json',
 'build':root/'qa/build-1791347690779251667/report.json'}
reports={key:verify(path) for key,path in paths.items()}
c=reports['realmC'];assert c['evidence']['checks']==74 and c['evidence']['nativeRealmEpochThrough']=='3' and c['evidence']['failedConstructionEpochConsumed'] and c['evidence']['normalOwnedExit']
assert c['exhaustionEvidence']['checks']==37 and c['exhaustionEvidence']['nativeRealmEpochThrough']==str(2**64-1) and c['exhaustionEvidence']['normalOwnedExit'] and c['unsafeCompiledVariantsDetected']==2
q=reports['realmModel'];assert q['namedScenarios']==16 and len(q['coupledTraces'])==28 and q['statesCompared']==711 and q['invariantSamples']==250 and q['unsafeCompiledVariantsDetected']==2 and all(t['normalOwnedExit'] for t in q['coupledTraces'])
t=reports['realmRace'];assert t['evidence']['checks']==36 and t['evidence']['nativeRealmEpochThrough']=='1' and t['evidence']['normalOwnedExit'] and t['unsafeCompiledVariantsDetected']==1 and t['mutant']['normalOwnedCleanupBeforeAssertion']
reg=reports['regressions'];assert len(reg['reports'])==4
underlying={}
for name,row in reg['reports'].items():
 path=pathlib.Path(row['path']);assert sha(path)==row['sha256'];underlying[name]=verify(path)
fd=underlying['capture-resource-fd-check.py'];assert fd['readerEvidence']['checks']==49 and fd['postTransferEvidence']['checks']==40 and fd['unsafeCompiledVariantsDetected']==2
assert all(fd[k]['normalOwnedExit'] and fd[k]['actualImportedFDClosed'] for k in ['readerEvidence','postTransferEvidence'])
rm=underlying['capture-resource-model-check.py'];assert rm['namedScenarios']==14 and len(rm['coupledTraces'])==22 and rm['statesCompared']==349 and rm['unsafeMutantsDetected']==3
cm=underlying['capture-intent-model-check-v3.py'];assert cm['namedScenarios']==14 and len(cm['coupledTraces'])==66 and cm['statesCompared']==816 and cm['unsafeMutantsDetected']==3
cc=underlying['imported-controlled-c-check-v3.py'];assert cc['checks']==10190 and cc['controls'][0]['actorsTurnedOver']==260 and cc['controls'][0]['nativeIssuedPrefix']==1041 and cc['controls'][0]['normalOwnedExit']
local=reports['localResourceModel'];assert local['namedScenarios']==14 and len(local['coupledTraces'])==22 and local['statesCompared']==373 and local['unsafeCompiledVariantsDetected']==3
build=reports['build'];assert len(build['commands'])==95 and sha(paths['build'].parent/'elm-host')==build['binarySHA256']
pm=plugin/'component-manifest.json';held=json.loads(pm.read_text());assert held['sourceHeld'] and held['passed']
for rel,row in held['files'].items():assert sha(plugin/rel)==row['sha256'],rel
for rel,alias in held['directoryAliases'].items():assert (plugin/rel).is_symlink() and str((plugin/rel).resolve())==alias
assert sha(plugin/'native/capture-resources.hpp')==fd['pluginResourceHeaderSHA256']==rm['pluginInputSHA256']==local['pluginInputSHA256']
ancestry=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(ancestry['parent']);m=parent/'component-manifest.json';assert sha(m)==ancestry['parentManifestSHA256']
prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for path in (parent/name).glob('*'):
  if path.is_file():assert sha(root/name/path.name)==sha(path)
nativeManifest=repo/'implementation/warlock-client-provider-native-v129/component-manifest.json';n=json.loads(nativeManifest.read_text());assert n['sourceHeld'] and n['passed'] and n['nativeChecks']==2517 and n['normalOwnedExits']==278
assert sha(n['nativeReport'])==n['nativeReportSHA256']
failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if not json.loads(p.read_text()).get('passed',False):failed.append(str(p))
assert len(failed)==6,failed
scope='Inactive CPU component: persistent native-owned realm epoch across Endpoint replacement; original strict C physical/proof/actor/processing/independent-confirmation closure releases only settled claim without resetting shared Native binding. Unpublished rollback consumes epoch and releases its own claim, old exact tickets reject before new handlers, lossless uint64 exhaustion refuses. Permanent atomic controlled-mode marker prevents delayed legacy zero-CAS from crossing controlled close; actual threaded counterexample retained. Actual C74 replacement+37 exhaustion checks/two normal exits/two compiled variants;real threaded36 controls/normal exit/one precise variant;16 selected Quint/28 coupled actual C traces/711 states/two variants. Current49 reader+40 post-transfer allocation,resource14/22/349/three,capture14/66/816/three,local resource14/22/373/three,C10190/260 metadata actors/1041 tickets and95 full-host commands. Frontend/Elm assets byte-identical to held106; original106 Elm/native ACK evidence retained at parent source, not relabelled current native qualification. Core16/plugin19 bounded native129 remains GUI92 legacy runtime2517/278. Live-window detachment, bootstrap reattachment, frontend realm scoping, renderer native outbox/WebKit, actual current controlled Core integration and all original release gates remain open.'
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'realmCChecks':111,'realmCCompiledVariants':2,'realmScenarios':16,'realmTraces':28,'realmStates':711,'realmModelCompiledVariants':2,'realmRaceChecks':36,'realmRaceCompiledVariants':1,'actualReaderChecks':49,'actualPostTransferChecks':40,'localResourceScenarios':14,'localResourceTraces':22,'localResourceStates':373,'controlledCChecks':10190,'fullBuildCommands':95,'unchangedElmParentManifest':str(m),'unchangedElmParentManifestSHA256':sha(m),'boundedNativeManifest':str(nativeManifest),'boundedNativeManifestSHA256':sha(nativeManifest),'heldFailedReports':failed,'webKitActivated':False,'liveWindowDetachmentImplemented':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
result['files']=inventory(root);assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report107.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI107. '+scope,'Next exact owned publication75 after verified public74, then distinct live-window realm detachment/current controlled Core/renderer native outbox/WebKit. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
