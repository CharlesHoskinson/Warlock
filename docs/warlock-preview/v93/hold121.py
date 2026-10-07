"""Hold the bounded native driver evidence without claiming GUI activation."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v121';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
guards=sorted((root/'qa').glob('output-custody-guards-*/report.json'));accepted=[p for p in guards if json.loads(p.read_text())['passed']];assert len(accepted)==1
names={'positive':'policy-driver-positive-check-1791377817582621047','quarantined':'policy-driver-quarantined-output-check-1791378292903443577','pressure':'policy-driver-output-gate-check-1791377264204546838','bounds':'dispatch-output-bounds-1791377817582289124','refinement':'driver-output-refinement-1791377706290553458','build':'build-1791377817594411281','guards':accepted[0].parent.name}
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current):
 d=json.loads(path.read_text());assert not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():assert sha((root if current else path.parent/'inputs')/rel)==value,(path,rel)
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 for category in ['compilerDependencies','linkedLibraries','tools']:
  for name,row in d.get(category,{}).items():assert sha(name)==row['sha256'],(category,name)
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()}
for key,count in [('positive',2261),('quarantined',2269),('pressure',2270)]:
 e=reports[key]['evidence'];assert e['checks']==count and e['preGrantFaultChecks']==9 and e['nativePolicyInstances']==1 and e['nativeTransportInstances']==1 and e['rendererWindowPolicies']==0 and e['ordinaryInputsRetained']==1065 and e['retainedInputByteLimit']==16*1024*1024 and e['normalOwnedExit'] and e['normalOwnedPeerExit'] and e['nativeGrantResets']==0
assert reports['positive']['evidence']['actualSyntheticCapturedFD'] and reports['quarantined']['evidence']['actualSyntheticCapturedFD']
assert reports['pressure']['evidence']['compiledStricterOutputGate'] and not reports['pressure']['evidence']['actualOutputQueueExhaustion']
e=reports['bounds']['evidence'];assert e['checks']==20 and e['maximumBoundedBatchBytes']==1544 and e['reservedDispatchBytes']==8192 and e['maximumOrdinalDigitsAnalyticallyIncluded'] and not e['actualCore']
r=reports['refinement'];assert r['namedScenarios']==8 and r['invariantSamples']==200 and len(r['coupledTraces'])==8 and r['observableStatesCompared']==48
assert all(x['evidence']['normalOwnedExit'] and x['evidence']['normalOwnedPeerExit'] and x['evidence']['nativeGrantResets']==0 for x in r['coupledTraces'])
g=reports['guards'];assert len(g['compiledNativeVariants'])==2 and all(x['detected'] and not x['normalCloseClaimed'] for x in g['compiledNativeVariants'])
b=reports['build'];assert len(b['commands'])==116 and all(x['exitCode']==0 for x in b['commands']);assert sha(paths['build'].parent/'elm-host')==b['binarySHA256']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);manifest=parent/'component-manifest.json';assert sha(manifest)==a['parentManifestSHA256'];prior=json.loads(manifest.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['nativePolicyDriverCPUQualified'] and prior['fullBuildCommands']==116
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','assets','adapter','src','spec']:
 for f in (parent/base).glob('*'):
  if f.is_file() and f.name not in {'preview-policy-driver.cpp','preview-policy-driver.h'}:assert sha(root/base/f.name)==sha(f),f
native=pathlib.Path(a['nativeBaselineManifest']);assert sha(native)==a['nativeBaselineManifestSHA256'];baseline=json.loads(native.read_text());assert baseline['sourceHeld'] and baseline['passed'] and baseline['nativeChecks']==2518 and baseline['normalOwnedExits']==278
for rel,row in baseline['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());assert [x['name'] for x in b['commands']]==[x['name'] for x in old['commands']]
historical=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p not in verified:
  d=verify(p,False);historical.append({'path':str(p),'sha256':sha(p),'passed':d['passed']})
  if not d['passed']:failed.append(str(p))
assert len(failed)==2 and len(historical)==5
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalReports':historical,'heldFailedReports':failed,'singlePreviewPolicy':True,'parentElmPolicyUnchanged':True,'parentNativeIssuerAndPhysicalProductUnchanged':True,'parentAssetsAndAdaptersUnchanged':True,'nativeOwnedJavaScriptCore':True,'persistentPolicyContexts':1,'nativePolicyDriverCPUQualified':True,'positiveChecks':2261,'lateQuarantinedOutputChecks':2269,'pressureChecks':2270,'preGrantFaultChecks':9,'ordinaryInputCapacity':1065,'ordinaryInputByteLimit':16*1024*1024,'normalOutputBatchCapacity':3195,'normalOutputByteCapacity':26173440,'dispatchOutputReservation':8192,'maximumFieldSerializerChecks':20,'maximumBoundedOriginalBatchBytes':1544,'normalOutputReservationUnderHeldProducerContractQualified':True,'lateOutputQuarantineCPUQualified':True,'driverScenarios':8,'driverSamples':200,'coupledTraces':8,'observableStatesCompared':48,'compiledNativeVariantsDetected':2,'rendererWindowPolicies':0,'nativeGrantResets':0,'fullBuildCommands':116,'originalBuildCommands':116,'nativeTicketCustodyCPUQualified':True,'independentNativeConfirmationCPUQualified':True,'nativeOutputQueueResourceBoundQualified':False,'actualOutputQueueExhaustionQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'realHostPolicyActivated':False,'actualRendererProjectionActivated':False,'actualDOMQualified':False,'actualWebKitContextAuthenticationQualified':False,'physicalConcealmentQualified':False,'ongoingProjectionFreshnessQualified':False,'realHostInputBackpressureQualified':False,'nativeDelayedProposalLivenessQualified':False,'uncertainLiveWorkerRecoveryQualified':False,'processLossInputJournalQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'parentManifest':str(manifest),'parentManifestSHA256':sha(manifest),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'scope':(root/'OUTPUT-CUSTODY-HANDOFF.md').read_text()}
files={}
for f in sorted(root.rglob('*')):
 rel=f.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not f.is_symlink(),f
 if f.is_file():files[name]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report121.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Freeze CONTROL-034 normal returned-output reservation, maximum-field original';assert text.count(old)==1;task.write_text(text.replace(old,'- [x] Freeze CONTROL-034 normal returned-output reservation, maximum-field original'))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI121 normal native output reservation8192/batches3195/bytes26173440 under original producer contract; original max-field serializers20/1544 bounded bytes. Actual C/JSC positive synthetic sealed FD2261 and quarantine-before-late-offer/fence2269, strict normal native/peer exits/no grant resets. Stricter compiled gate pressure2270 retains exact original ticket before effects, urgent quarantine, release once; actual real output exhaustion and measured RSS/full-workload progress remain unqualified. Explicit Quint first-ticket8/200 samples/eight actual C/JSC traces/48 compared states/two compiled native guards. Full116 retains116, parent original policy/issuer/effects/physical/assets/adapters unchanged. Two failed runner/peer attempts preserved. Actual legacy baseline Native131GUI119/core16/plugin19/AQ1552518/278 unchanged; new route not activated. Next PUBLIC91 then actual controlled host/pure renderer native GTK grant/poll pausing/WebKit identity/async DOM/frame/physical concealment/URI. Uncertain live/process recovery, delayed never-issued proposals and all full release gates open. Installed/drafts/five foreign paths preserved.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':116,'nativeAcceptance':False,'fullReleaseAccepted':False}))
