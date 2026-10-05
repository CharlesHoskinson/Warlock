"""Hold exact full-host client-path evidence and every original native control."""
import hashlib,json,pathlib,stat
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v15'
native=REPO/'implementation/warlock-client-provider-native-v4'
build=provider/'qa/build-1791241554931840085/report.json'
campaign=native/'qa/native-1791241690666401240/report.json'
built=json.loads(build.read_text());observed=json.loads(campaign.read_text())
assert built['passed'] and observed['passed'] and observed['cleanupPassed']
for rel,h in built['inputs'].items():assert sha(provider/rel)==h,rel
pre=json.loads((native/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
for p,d in [(build,built),(campaign,observed)]:
 for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
prior=json.loads((REPO/'implementation/warlock-client-provider-native-v1/qa/native-1791239211683329896/report.json').read_text())
original=[c['name'] for c in prior['checks']]
assert len(original)==768 and len(observed['checks'])==783
assert [c['name'] for c in observed['checks'] if c['name'] in set(original)]==original
assert all(c['passed'] for c in observed['checks'])
assert len(observed['ownedExitCodes'])==75 and all(c['exitCode']==0 for c in observed['ownedExitCodes'])
assert observed['fullHostPixels']['blue']==768 and observed['fullHostPixels']['red']==18432 and observed['fullHostPixels']['green']==0
assert len(observed['cacheTraceReplay'])==5 and sum(c['statesCompared'] for c in observed['cacheTraceReplay'])==46
assert json.loads((build.parent/'client-command-tests.stdout').read_text())['checks']==44
assert json.loads((build.parent/'typed-source-presenter-replay.stdout').read_text())['checks']==46
assert (build.parent/'authority-config-identity.stdout').read_text().strip().endswith('20')
for rel in ['native/demand.hpp','native/preview_broker.hpp','native/preview_uri.hpp','native/preview_uri.cpp']:
 assert sha(provider/rel)==sha(REPO/'implementation/warlock-preview-provider-v7'/rel),rel
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows)
 destination.write_text(json.dumps(metadata,indent=2)+'\n')
 return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(native,{'status':'private-full-webkit-client-path-qualified','nativeControls':783,'retainedOriginalControls':768,'normalOwnedExits':75,'cleanupPassed':True,'actualElmAcquireReleaseACK':True,'independentWebKitClientPixels':True,'hardwarePresentationQualified':False,'fullWebKitClientPathQualified':True,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(provider,{'status':'full-gui-native-own-client-producer-integrated','fullGUIBuildPassed':True,'strictClientCommandChecks':44,'actualLiveProcessIdentityChecks':20,'typedPresenterChecks':46,'fullWebKitClientPathQualified':True,'qualifiedCampaign':held[0],'hardwarePresentationQualified':False,'productionCaptureWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists()
out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,campaign]},'boundedNativeClientPathQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Admit changing client observations in the actual Popup through the one Elm owner; qualify invalidation/cancel/physical drain before production eligibility, measured S02 and full preview13'},indent=2)+'\n')
print(json.dumps({'passed':True,'components':held,'report':str(out)}))
