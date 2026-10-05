"""Hold the current full package and selected actual source-policy replay."""
import hashlib,json,pathlib,stat
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v10';model=REPO/'implementation/warlock-source-presenter-model-v2'
build=provider/'qa/build-1791239716165875864/report.json';selected=model/'qa/check-1791239866310289142/report.json'
built=json.loads(build.read_text());checked=json.loads(selected.read_text());assert built['passed'] and checked['passed']
for rel,h in built['inputs'].items():assert sha(provider/rel)==h,rel
for path,h in checked['inputs'].items():assert sha(path)==h,path
for p,d in [(build,built),(selected,checked)]:
 for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
assert len(checked['selectedNames'])==8 and sum(x['statesCompared'] for x in checked['coupledTraces'])==33
replay=json.loads((build.parent/'typed-source-presenter-replay.stdout').read_text());assert replay['passed'] and replay['checks']==46
old=json.loads((REPO/'implementation/warlock-preview-provider-v7/qa/build-1791238777317896722/report.json').read_text())
changed=[rel for rel,h in old['inputs'].items() if rel.startswith(('src/','native/','assets/','adapter/')) and sha(provider/rel)!=h]
assert changed==['src/PreviewPresenter.elm'],changed
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(x in ['elm-stuff','mutable-elm-home','__pycache__'] for x in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows)
 destination.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(model,{'status':'eight-selected-quint-scenarios-actual-elm-projection-qualified','selectedScenarios':8,'compiledStatesCompared':33,'comparesAcquireCancelCommands':True}))
held.append(hold(provider,{'status':'typed-source-seed-integrated-in-actual-compiled-popup','fullGUIBuildPassed':True,'typedPresenterChecks':46,'typedSourceRetentionModel':held[0],'nativeSourceFilesUnchanged':33,'qualifiedNativePrimitiveParent':'implementation/warlock-preview-provider-v7/component-manifest.json','nativeChangedAssetsQualified':False,'fullWebKitCaptureQualified':False,'productionCaptureWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,selected]},'changedProductionSources':changed,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual owning producer and typed source publication in the full WebKit host with actual Elm ACK and independent rendered pixels'},indent=2)+'\n');print(json.dumps({'passed':True,'components':held,'report':str(out)}))
