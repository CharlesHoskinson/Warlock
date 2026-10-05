"""Freeze changing-source implementation with original full native identities."""
import hashlib,json,pathlib,stat
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v16';native=REPO/'implementation/warlock-client-provider-native-v6';model=REPO/'implementation/warlock-source-presenter-model-v3'
build=provider/'qa/build-1791242212679054777/report.json';campaign=native/'qa/native-1791242591387161664/report.json';selected=model/'qa/check-1791242572841304213/report.json'
built=json.loads(build.read_text());observed=json.loads(campaign.read_text());checked=json.loads(selected.read_text());assert built['passed'] and observed['passed'] and checked['passed']
for rel,h in built['inputs'].items():assert sha(provider/rel)==h,rel
pre=json.loads((native/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
for path,h in checked['inputs'].items():assert sha(path)==h,path
for p,d in [(build,built),(campaign,observed),(selected,checked)]:
 for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
prior=json.loads((REPO/'implementation/warlock-client-provider-native-v4/qa/native-1791241690666401240/report.json').read_text());names=[c['name'] for c in prior['checks']]
assert len(names)==783 and len(observed['checks'])==794 and [c['name'] for c in observed['checks'] if c['name'] in set(names)]==names
assert all(c['passed'] for c in observed['checks']) and observed['cleanupPassed']
assert len(observed['ownedExitCodes'])==77 and all(c['exitCode']==0 for c in observed['ownedExitCodes'])
assert len(checked['selectedNames'])==19 and len(checked['coupledTraces'])==19 and sum(c['statesCompared'] for c in checked['coupledTraces'])==101
assert sum(c['statesCompared'] for c in checked['coupledTraces'] if c['actualCppAndElm'])==68
assert json.loads((build.parent/'client-observation-tests.stdout').read_text())['checks']==153
assert json.loads((build.parent/'typed-source-presenter-replay.stdout').read_text())['checks']==46
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);destination.write_text(json.dumps(metadata,indent=2)+'\n')
 return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(model,{'status':'nineteen-selected-source-and-observation-scenarios-qualified','selectedScenarios':19,'compiledStatesCompared':101,'actualCppAndElmStates':68,'originalSourceScenariosRetained':8,'originalNativeJobAndPacketCommandsCompared':True}))
held.append(hold(native,{'status':'actual-full-popup-changed-client-source-historical-qualified','nativeControls':794,'retainedOriginalControls':783,'normalOwnedExits':77,'cleanupPassed':True,'actualElmHistoricalAfterNativeCommit':True,'originalFrameAndDeadlineRetained':True,'actualElmReleaseAndACK':True,'hardwarePresentationQualified':False,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(provider,{'status':'current-native-observations-to-one-physical-broker-and-elm','fullGUIBuildPassed':True,'actualGIOObservationChecks':153,'typedPresenterChecks':46,'qualifiedNativeHistoricalPath':held[1],'selectedConformance':held[0],'nativeScopeRefusalCleanupQualified':False,'productionCaptureWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,campaign,selected]},'boundedNativeChangedContentQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Typed correlated native scope-denial path and held physical cleanup retry for source loss/session lock; retain original job/expiry and unknown settlement'},indent=2)+'\n');print(json.dumps({'passed':True,'components':held,'report':str(out)}))
