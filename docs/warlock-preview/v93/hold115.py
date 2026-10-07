"""Hold exact proposal ingress evidence without claiming active host routing."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v115'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'boundaries': 'retained-ingress-check-v2-1791362045804086481', 'nativeElmOutbox': 'retained-ingress-native-check-1791362312569931127', 'model': 'retained-ingress-model-check-v5-1791362250074671821', 'urgentModel': 'urgent-ingress-model-check-v2-1791362342744865351', 'coldCohort': 'retained-ingress-cold-check-1791362342744815580', 'legacy': 'retained-legacy-retirement-check-1791362342744420138', 'build': 'build-1791362312568104389'}
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current=False):
 d=json.loads(path.read_text());assert not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():
  p=root/rel
  if current or (p.exists() and sha(p)==value):assert sha(p)==value,(path,rel)
  else:assert sha(path.parent/'inputs'/rel)==value,(path,rel,'historical input snapshot')
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 for rel,value in d.get('runnerInputs',{}).items():assert sha(root/'qa'/rel)==value
 for row in d.get('reports',{}).values():
  p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];verify(p,current)
 if 'compiledControls' in d:
  row=d['compiledControls'];p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];verify(p,current)
  assert sha(p.parent/'checks')==row['binarySHA256']
 if 'pluginResourceHeaderSHA256' in d:assert sha(root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp')==d['pluginResourceHeaderSHA256']
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()}
n=reports['nativeElmOutbox']['evidence'];assert n['checks']==206 and n['singlePreviewPolicy'] and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['syntheticNativeRemainsActive']
assert reports['boundaries']['evidence']['checks']==98 and reports['boundaries']['evidence']['boundedDeferredCleanup']
for name,scenarios,traces,states,variants in [('model',16,28,468,6),('urgentModel',6,18,406,2)]:
 q=reports[name];assert q['namedScenarios']==scenarios and q['invariantSamples']==200 and q['unsafeCompiledElmVariantsDetected']==variants and q['evidence']['statesCompared']==states and len(q['evidence']['coupledTraces'])==traces
assert reports['coldCohort']['evidence']['checks']==3608 and reports['coldCohort']['evidence']['retainedReadinessIntents']==256
l=reports['legacy'];assert l['originalLegacyControls']['checks']==45 and l['evidence']['checks']==20 and l['evidence']['nativeCChecks']==34 and l['evidence']['normalOwnedExit']
b=reports['build'];assert all(x['exitCode']==0 for x in b['commands']);assert len(b['commands'])==108 and sha(paths['build'].parent/'elm-host')==b['binarySHA256']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);m=parent/'component-manifest.json';assert sha(m)==a['parentManifestSHA256'];prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
changed={'src/Popup.elm'}
for base in ['native','assets','adapter','src']:
 for p in (parent/base).glob('*'):
  if p.is_file() and str(p.relative_to(parent)) not in changed:assert sha(root/base/p.name)==sha(p),p
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());added={'retained-ingress-replay-build','retained-ingress-boundaries','retained-legacy-replay-build','retained-legacy-retirement-controls'};assert [x['name'] for x in b['commands'] if x['name'] not in added]==[x['name'] for x in old['commands']]
history=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p in verified:continue
 d=verify(p);history.append({'path':str(p),'sha256':sha(p),'passed':d['passed'],'qualifiesFinalSource':False})
 if not d['passed']:failed.append(str(p))
assert len(failed)==6
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalPhaseReports':history,'heldFailedReports':failed,'singlePreviewPolicy':True,'originalWindowPolicyUnchanged':True,'immutableProposalIngressImplemented':True,'urgentQuarantineBypassesBackpressure':True,'popupTypedPortsCompiled':True,'popupTypedPortsWebKitExecuted':False,'nativeElmOutboxChecks':206,'boundaryChecks':98,'realmEpochs':2,'nativeGrantResets':0,'ingressScenarios':16,'ingressTraces':28,'ingressStates':468,'ingressSamples':200,'ingressCompiledVariantsDetected':6,'urgentScenarios':6,'urgentTraces':18,'urgentStates':406,'urgentSamples':200,'urgentCompiledVariantsDetected':2,'coldCohortChecks':3608,'originalColdAssertionsRetained':1549,'retainedReadinessIntents':256,'legacyRetirementChecks':45,'legacyNativeRoundtripChecks':20,'legacyCChecks':34,'fullBuildCommands':108,'originalBuildCommands':104,'earlierPhaseBuildCommands':106,'parentNativeProductUnchanged':True,'parentAdapterAndLegacyAssetsUnchanged':True,'parentManifest':str(m),'parentManifestSHA256':sha(m),'proposalRetentionCPUQualified':True,'nativeDelayedProposalLivenessQualified':False,'realHostInputBackpressureQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'RETAINED-INGRESS-HANDOFF.md').read_text()}

files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not p.is_symlink(),p
 if p.is_file():files[name]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report115.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();old='- [ ] Freeze CONTROL-028 retained original Elm proposals';assert s.count(old)==1;s=s.replace(old,'- [x] Freeze CONTROL-028 retained original Elm proposals');s+='\nGUI115 CPU retention qualifies98 boundaries/native C+Elm206/two epochs/unchanged\nNative grant/normal exits; ingress Quint16/28 actualElm traces/468 states/six\ncompiled variants; urgent6/18/406/two variants; cold256/3608 with original1549\nassertions and explicit synthetic ticket facts; current wrapper legacy45/20+C34;\nfull108 retains104 and earlier106. Six failed attempts remain, including actual\nblocked-quarantine demand counterexample. Real host input backpressure and\nWebKit/policy lifetime remain open. Qualify delayed proposal expiry/revocation\noutcomes before claiming finite liveness or activating that route.\n';task.write_text(s)

sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI115 retained original Elm proposal ingress in immutable wrapper of unchanged single window policy. Boundaries98/native C+Elm+outbox206/two epochs/unchanged Native grant/same Active synthetic subject/normal exits; ingress Quint16/28/468/six compiled variants; urgent6/18/406/two variants; cold256/3608 retains original1549 with synthetic ticket facts; legacy45/native20+C34; full108 retains104/earlier106. Six failed attempts/earlier phases remain. Native/assets/adapters unchanged114 and resource4+scoped4 remain at parent identity. Actual Popup ports compiled only. Next PUBLIC84 then real durable host input backpressure/native issued fact channel/ticket custody/retry, persistent Elm policy lifetime and WebKit/Core routing. Delayed proposal expiry/revocation liveness must retain authenticated original-purpose outcome or guaranteed ordering; generic refusal/timeout cannot erase intent. Original full release gates open; Native130 legacy2518/278 remains actual baseline; no installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':108,'failedAttemptsHeld':len(failed)}))
