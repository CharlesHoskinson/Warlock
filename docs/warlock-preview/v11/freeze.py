"""Verify actual evidence and hold only this lane's new component files."""
import hashlib,json,os,pathlib,stat
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def report(rel):
 p=REPO/rel;d=json.loads(p.read_text());assert d['passed'],rel;return p,d
build,built=report('implementation/warlock-preview-provider-v7/qa/build-1791238777317896722/report.json')
demand,checked=report('implementation/warlock-preview-provider-v7/qa/check-1791238975118220172/report.json')
native,observed=report('implementation/warlock-client-provider-native-v1/qa/native-1791239211683329896/report.json')
decoder,decoded=report('implementation/warlock-client-source-decoder-checks-v1/qa/check-1791239361778821135/report.json')
provider=REPO/'implementation/warlock-preview-provider-v7'
for rel,h in built['inputs'].items():assert sha(provider/rel)==h,rel
for rel,h in checked['inputs'].items():assert sha(provider/rel)==h,rel
for path,h in decoded['inputs'].items():assert sha(path)==h,path
pre=json.loads((native.parents[1]/'preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
for p,d in [(build,built),(demand,checked),(native,observed),(decoder,decoded)]:
 for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
assert observed['cleanupPassed'] and all(x['exitCode']==0 for x in observed['ownedExitCodes'])
prior=json.loads((REPO/'implementation/warlock-client-child-native-v6/qa/native-1791237601053306854/report.json').read_text())
added={'ownProviderNormalExit','actualOwnProviderClientImportAndPhysicalReceipts','ownProviderPixelsDecoderNormalExit','ownProviderActualChildPixelsAndPeerExclusion'}
assert [x['name'] for x in observed['checks'] if x['name'] not in added]==[x['name'] for x in prior['checks']]
assert len(observed['checks'])==768 and all(x['passed'] for x in observed['checks'])
assert observed['providerReport']['checks']==28 and not observed['providerReport']['previewEligible']
assert len(decoded['checks'])==239 and all(x['passed'] for x in decoded['checks'])
assert len(checked['selectedNames'])==10 and len(checked['coupledTraces'])==22 and checked['unsafeMutantsDetected']==3
assert sum(x['statesCompared'] for x in observed['cacheTraceReplay'])==46
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists(),destination
 rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():rows[str(p.relative_to(root))]={'kind':'symlink','target':os.readlink(p),'mode':oct(stat.S_IMODE(p.lstat().st_mode))}
  elif p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows)
 destination.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(decoder.parents[2],{'status':'actual-optimized-source-decoder-qualified','compiledChecks':239,'nativeObservationReport':str(native.relative_to(REPO))}))
held.append(hold(native.parents[2],{'status':'own-native-client-import-gio-physical-retirement-qualified','nativeControls':768,'retainedOriginalControls':764,'providerChecks':28,'normalOwnedExits':71,'cleanupPassed':True,'cacheSelectedScenarios':5,'cacheNativeStates':46,'fullWebKitQualified':False,'previewEligible':False}))
held.append(hold(provider,{'status':'compiled-full-host-explicit-client-source-primitives','fullGUIBuildPassed':True,'activePopupSourceConsumption':False,'fullWebKitQualified':False,'productionCaptureWired':False,'previewEligible':False,'qualifiedNativeProbe':held[1],'qualifiedElmSourceDecoder':held[0],'selectedDemandScenarios':10,'coupledDemandTraces':22,'unsafeDemandMutantsDetected':3}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists()
out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,demand,native,decoder]},'scope':'Compiled full provider primitives and private native/GIO client frame with typed source boundary; full WebKit/production/release remains open','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'passed':True,'report':str(out),'components':held}))
