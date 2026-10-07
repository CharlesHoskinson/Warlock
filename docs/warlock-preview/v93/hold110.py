"""Freeze exact Bootstrap borrowed-receipt lifetime and original strict close."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v110';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 path=pathlib.Path(path);d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(root/name)==value,(path,name)
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,(path,name)
 return d
paths={'uriC':root/'qa/uri-capability-check-v2-1791352413696078806/report.json','uriModel':root/'qa/uri-capability-model-check-v3-1791352627821797315/report.json','detachmentRegressions':root/'qa/detachment-regression-check-1791352666619047920/report.json','regressions':root/'qa/resource-regression-check-1791352326012043309/report.json','build':root/'qa/build-1791352326010757688/report.json'}
reports={key:verify(path) for key,path in paths.items()}
c=reports['uriC'];assert c['evidence']['checks']==66 and c['evidence']['actualSealedFDs']==4 and c['evidence']['actualFDsClosed'] and c['evidence']['independentCallbackReference'] and not c['evidence']['actualWebKitCallback'] and c['unsafeCompiledVariantsDetected']==3
q=reports['uriModel'];assert q['namedScenarios']==16 and len(q['coupledTraces'])==24 and q['statesCompared']==320 and q['invariantSamples']==200 and all(t['normalOwnedCleanup'] for t in q['coupledTraces'])
scoped=reports['detachmentRegressions'];assert len(scoped['reports'])==4
for name,row in scoped['reports'].items():
 p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];d=verify(p)
 if name=='live-window-detachment-c-check.py':assert d['evidence']['checks']==77 and d['evidence']['nativeRealmEpochThrough']=='2' and d['evidence']['normalOwnedExit']
 elif name=='live-window-detachment-fd-check-v2.py':assert [d[k]['checks'] for k in ['readerEvidence','lostProducerResponseEvidence','postTransferEvidence']]==[60,64,51] and d['unsafeCompiledVariantsDetected']==2 and all(d[k]['normalOwnedExit'] and d[k]['actualImportedFDClosed'] for k in ['readerEvidence','lostProducerResponseEvidence','postTransferEvidence'])
 elif name=='live-window-detachment-cohort-check-v3.py':assert d['evidence']['checks']==66 and d['evidence']['actualColdZeroFloor'] and d['evidence']['actualMixedDomains'] and d['evidence']['oneCandidatePerPoll'] and d['evidence']['normalOwnedExit']
 elif name=='live-window-detachment-model-check-v3.py':assert d['namedScenarios']==21 and len(d['coupledTraces'])==33 and d['statesCompared']==715 and d['unsafeCompiledVariantsDetected']==5 and all(t['normalOwnedExit'] for t in d['coupledTraces'])
 else:assert False,name
reg=reports['regressions'];assert len(reg['reports'])==4;underlying={}
for name,row in reg['reports'].items():
 p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];underlying[name]=verify(p)
fd=underlying['capture-resource-fd-check.py'];assert fd['readerEvidence']['checks']==49 and fd['postTransferEvidence']['checks']==40 and fd['unsafeCompiledVariantsDetected']==2 and all(fd[k]['normalOwnedExit'] and fd[k]['actualImportedFDClosed'] for k in ['readerEvidence','postTransferEvidence'])
rm=underlying['capture-resource-model-check.py'];assert rm['namedScenarios']==14 and len(rm['coupledTraces'])==22 and rm['statesCompared']==349 and rm['unsafeMutantsDetected']==3
cm=underlying['capture-intent-model-check-v3.py'];assert cm['namedScenarios']==14 and len(cm['coupledTraces'])==66 and cm['statesCompared']==816 and cm['unsafeMutantsDetected']==3
cc=underlying['imported-controlled-c-check-v3.py'];assert cc['checks']==10190 and cc['controls'][0]['actorsTurnedOver']==260 and cc['controls'][0]['nativeIssuedPrefix']==1041 and cc['controls'][0]['normalOwnedExit']
build=reports['build'];assert len(build['commands'])==96 and sha(paths['build'].parent/'elm-host')==build['binarySHA256']
pm=plugin/'component-manifest.json';held=json.loads(pm.read_text());assert held['sourceHeld'] and held['passed']
for rel,row in held['files'].items():assert sha(plugin/rel)==row['sha256'],rel
for rel,alias in held['directoryAliases'].items():assert (plugin/rel).is_symlink() and str((plugin/rel).resolve())==alias
assert sha(plugin/'native/capture-resources.hpp')==fd['pluginResourceHeaderSHA256']==rm['pluginInputSHA256']
ancestry=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(ancestry['parent']);m=parent/'component-manifest.json';assert sha(m)==ancestry['parentManifestSHA256']
prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['detachmentCChecks']==77 and prior['detachmentCohortChecks']==66
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for p in (parent/name).glob('*'):
  if p.is_file():assert sha(root/name/p.name)==sha(p)
failed=[str(p) for p in sorted((root/'qa').glob('*/report.json')) if not json.loads(p.read_text()).get('passed',False)];assert len(failed)==2
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());assert [row['name'] for row in build['commands'] if row['name']!='preview-uri-router.cpp-compile']==[row['name'] for row in old['commands']]
scope=(root/'URI-LIFETIME-HANDOFF.md').read_text()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'uriCChecks':66,'uriActualSealedFDs':4,'uriCCompiledVariants':3,'uriScenarios':16,'uriTraces':24,'uriStates':320,'uriInvariantSamples':200,'currentDetachmentCChecks':77,'currentDetachmentReaderChecks':60,'currentDetachmentLostProducerResponseChecks':64,'currentDetachmentPostTransferChecks':51,'currentDetachmentCohortChecks':66,'currentDetachmentScenarios':21,'currentDetachmentTraces':33,'currentDetachmentStates':715,'actualReaderChecks':49,'actualPostTransferChecks':40,'controlledCChecks':10190,'fullBuildCommands':96,'originalBuildCommands':95,'unchangedElmParentManifest':str(m),'unchangedElmParentManifestSHA256':sha(m),'heldFailedReports':failed,'lifetimeSafeURIRouterImplemented':True,'newWebKitDispatcherCompiled':True,'actualWebKitCallbackOwnershipQualified':False,'webKitActivated':False,'liveWindowDetachmentImplemented':True,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report110.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI110. Lifetime-safe weak Shared/Endpoint capability+exact binding/receiver/epoch and native stable C router creator-thread/monotonic binding+epoch/independent callback reference, new WebKit dispatcher compiled but inactive. C66/four actual sealed mappings/three compiled variants/model16/24/320/200 samples/full96 retaining all original95/current four resource and four scoped detachment regressions pass. Two fixture failures retained. Actual native GUI92/native129/core16/plugin19 bounded2517/278 unchanged.','Next exact owned publication78 after verified77; freshNative130 requalify current GUI110 legacy runtime on same owning core16/plugin19 with every original129/128/126 control/allocator/expiry/deadline/teardown retained. Actual new WebKit callback ownership/current controlled Core/typed frontend realm/outbox and all original release gates remain open. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
