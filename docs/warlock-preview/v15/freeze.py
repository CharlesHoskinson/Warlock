"""Hold typed denial code, actual native lock/source loss, and all failed attempts."""
import hashlib,json,pathlib,stat
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v17';native=REPO/'implementation/warlock-client-provider-native-v9';model=REPO/'implementation/warlock-source-presenter-model-v4'
def sole(root,pattern):
 paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
build=sole(provider,'qa/build-*/report.json');campaign=sole(native,'qa/native-*/report.json');selected=sole(model,'qa/check-*/report.json')
built=json.loads(build.read_text());observed=json.loads(campaign.read_text());checked=json.loads(selected.read_text());assert built['passed'] and observed['passed'] and checked['passed']
for rel,h in built['inputs'].items():assert sha(provider/rel)==h,rel
pre=json.loads((native/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
for path,h in checked['inputs'].items():assert sha(path)==h,path
for p,d in [(build,built),(campaign,observed),(selected,checked)]:
 for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v6','qa/native-*/report.json').read_text());names=[c['name'] for c in prior['checks']]
assert len(names)==794 and len(observed['checks'])==828 and [c['name'] for c in observed['checks'] if c['name'] in set(names)]==names
assert all(c['passed'] for c in observed['checks']) and observed['cleanupPassed']
assert len(observed['ownedExitCodes'])==86 and all(c['exitCode']==0 for c in observed['ownedExitCodes'])
oldModel=json.loads(sole(REPO/'implementation/warlock-source-presenter-model-v3','qa/check-*/report.json').read_text())
assert checked['selectedNames'][:19]==oldModel['selectedNames']
assert checked['coupledTraces'][:19]==oldModel['coupledTraces']
assert len(checked['selectedNames'])==30 and len(checked['coupledTraces'])==30 and sum(c['statesCompared'] for c in checked['coupledTraces'])==172
assert sum(c['statesCompared'] for c in checked['coupledTraces'] if c['actualCppAndElm'])==139
for name,count in [('client-observation-tests',153),('typed-source-presenter-replay',46),('client-denial-tests',104),('typed-source-denial-replay',445)]:assert json.loads((build.parent/(name+'.stdout')).read_text())['checks']==count
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);destination.write_text(json.dumps(metadata,indent=2)+'\n')
 return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
for version in [1,2,3,4]:
 root=REPO/('implementation/warlock-native-denial-witness-v'+str(version));report=sole(root,'qa/build-*/report.json');r=json.loads(report.read_text())
 for path,h in r['inputs'].items():assert sha(path)==h,path
 for rel,h in r['artifacts'].items():assert sha(report.parent/rel)==h,rel
 assert r['passed']==(version!=1)
 held.append(hold(root,{'status':'compile-failure-held' if version==1 else 'compiled-native-physical-denial-witness','buildPassed':r['passed'],'usedByAcceptedNative':version==4}))
fixture=REPO/'implementation/warlock-session-lock-fixture-v1';report=sole(fixture,'qa/lock-build-*/report.json');r=json.loads(report.read_text());assert r['passed']
for path,h in r['inputs'].items():assert sha(path)==h,path
for rel,h in r['artifacts'].items():assert sha(report.parent/rel)==h,rel
held.append(hold(fixture,{'status':'guarded-real-private-session-lock-and-synced-unlock','buildPassed':True,'nativeUses':2,'nativeNormalExit':True}))
for version in [7,8]:
 root=REPO/('implementation/warlock-client-provider-native-v'+str(version));report=sole(root,'qa/native-*/report.json');r=json.loads(report.read_text());assert not r['passed'] and r['cleanupPassed']
 for rel,h in r['artifacts'].items():assert sha(report.parent/rel)==h,rel
 held.append(hold(root,{'status':'failed-concurrent-witness-budget-attempt-held','buildPreparationPassed':True,'nativePassed':False,'cleanupPassed':True}))
held.append(hold(model,{'status':'thirty-selected-source-observation-denial-scenarios-qualified','selectedScenarios':30,'compiledStatesCompared':172,'actualCppAndElmStates':139,'retainedOriginalScenarios':19,'retainedOriginalStates':101}))
held.append(hold(native,{'status':'actual-native-source-loss-and-lock-pending-retirement-qualified','nativeControls':828,'retainedOriginalControls':794,'normalOwnedExits':86,'cleanupPassed':True,'nativeURIRefusalBeforePolicy':True,'actualElmReleaseAndACK':True,'physicalRetirementPendingUnderLock':True,'actualRetirementAfterUnlock':True,'originalFrameAndDeadlineRetained':True,'hardwarePresentationQualified':False,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(provider,{'status':'typed-native-denial-and-retained-physical-cleanup','fullGUIBuildPassed':True,'actualElmDenialChecks':445,'nativeDecoderBrokerGIODenialChecks':104,'actualGIOObservationChecks':153,'qualifiedNativeDenial':held[-1],'selectedConformance':held[-2],'productionCaptureWired':False,'previewEligible':False}))
resume=REPO/'implementation/warlock-preview-provider-v18';ancestry=resume/'ANCESTRY.json';assert not ancestry.exists();ancestry.write_text(json.dumps({'parent':str(provider),'parentManifestSHA256':held[-1]['sha256'],'native':held[-2],'model':held[-3],'change':'Fresh coherent native scope and next own job after physical zero/terminal ACK, preserving old job/expiry/proof and Unknown. Full production/native release gates remain.'},indent=2)+'\n')
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,campaign,selected]},'boundedNativeScopeDenialAndRetirementQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Implement provider-v18 fresh demand after original physical retirement and terminal ACK; preserve all828 native controls and30 selected scenarios'},indent=2)+'\n');print(json.dumps({'passed':True,'components':held,'report':str(out)}))
