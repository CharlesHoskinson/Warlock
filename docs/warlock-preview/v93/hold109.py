"""Freeze exact Bootstrap borrowed-receipt lifetime and original strict close."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v109';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 path=pathlib.Path(path);d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for name,value in d['inputs'].items():assert sha(root/name)==value,(path,name)
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,(path,name)
 return d
paths={'detachmentC':root/'qa/live-window-detachment-c-check-1791350882253548095/report.json','detachmentFD':root/'qa/live-window-detachment-fd-check-v2-1791351375606861560/report.json','detachmentCohort':root/'qa/live-window-detachment-cohort-check-v3-1791351736470262341/report.json','detachmentModel':root/'qa/live-window-detachment-model-check-v3-1791351656691953043/report.json','regressions':root/'qa/resource-regression-check-1791351448877528418/report.json','build':root/'qa/build-1791351448874490708/report.json'}
reports={key:verify(path) for key,path in paths.items()}
c=reports['detachmentC'];assert c['evidence']['checks']==77 and c['evidence']['nativeRealmEpochThrough']=='2' and c['evidence']['normalOwnedExit'] and c['actualSyntheticNativeActiveFact'] and not c['actualWaylandWindowAcceptance']
f=reports['detachmentFD'];assert [f[k]['checks'] for k in ['readerEvidence','lostProducerResponseEvidence','postTransferEvidence']]==[60,64,51] and f['unsafeCompiledVariantsDetected']==2 and all(f[k]['normalOwnedExit'] and f[k]['actualImportedFDClosed'] for k in ['readerEvidence','lostProducerResponseEvidence','postTransferEvidence'])
t=reports['detachmentCohort']['evidence'];assert t['checks']==66 and t['actualColdZeroFloor'] and t['actualMixedDomains'] and t['oneCandidatePerPoll'] and t['normalOwnedExit']
q=reports['detachmentModel'];assert q['namedScenarios']==21 and len(q['coupledTraces'])==33 and q['statesCompared']==715 and q['invariantSamples']==250 and q['unsafeCompiledVariantsDetected']==5 and all(t['normalOwnedExit'] for t in q['coupledTraces'])
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
prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['bootstrapCChecks']==97 and prior['bootstrapCoreDeathChecks']==47
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter']:
 for p in (parent/name).glob('*'):
  if p.is_file():assert sha(root/name/p.name)==sha(p)
failed=[str(p) for p in sorted((root/'qa').glob('*/report.json')) if not json.loads(p.read_text()).get('passed',False)];assert len(failed)==4
scope=(root/'DETACHMENT-HANDOFF.md').read_text()
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'detachmentCChecks':77,'detachmentReaderChecks':60,'detachmentLostProducerResponseChecks':64,'detachmentPostTransferChecks':51,'detachmentResourceCompiledVariants':2,'detachmentCohortChecks':66,'detachmentScenarios':21,'detachmentTraces':33,'detachmentStates':715,'detachmentModelCompiledVariants':5,'actualReaderChecks':49,'actualPostTransferChecks':40,'controlledCChecks':10190,'fullBuildCommands':95,'unchangedElmParentManifest':str(m),'unchangedElmParentManifestSHA256':sha(m),'heldFailedReports':failed,'webKitActivated':False,'liveWindowDetachmentImplemented':True,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report109.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI109. Distinct scoped C binding detach keeps synthetic Native incarnation Active;77 replacement controls/60 actual FD reader+64 lost producer response+51 post-adoption allocation controls/66 cold-zero-floor mixed-domain controls/21 selected Quint/33 actual C traces/715 states/250 samples/five variants/current full95/original four regressions. Four failed fixtures retained. Inactive controlled path; native GUI92/native129/core16/plugin19 bounded2517/278 unchanged.','Next exact owned publication77 after verified76; fresh110 safe WebKit URI lifetime/routing and typed incoming/outgoing realm wrappers/native renderer outbox, then actual controlled Core/Wayland capture and all original release gates. No installed/main desktop/draft changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
