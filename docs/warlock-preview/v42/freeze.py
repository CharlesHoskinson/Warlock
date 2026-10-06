import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,(root,pattern);return rows[0]
def verify(path):
 j=json.loads(path.read_text())
 for rel,h in j.get('artifacts',{}).items():assert sha(path.parent/rel)==h,(path,rel)
 for p,h in j.get('inputs',{}).items():
  if pathlib.Path(p).is_absolute():assert sha(p)==h,p
 return j
priorPath=REPO/'docs/warlock-preview/v41/report.json';prior=verify(priorPath);assert prior['passed'] and prior['actualNativeOpaqueSamplingFactsQualified'] and prior['noBlurOpacityCompositionAttempt']['qualified']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];j=json.loads(p.read_text())
 for rel,item in j['files'].items():assert sha(p.parent/rel)==item['sha256'],rel
model=REPO/'implementation/warlock-family-style-revisions-v8';modelPath=only(model,'qa/model-*/report.json');m=verify(modelPath);assert m['passed'] and len(m['selectedNames'])==26 and m['states']==99
controlsPath=only(model,'qa/test-*/report.json');t=verify(controlsPath);assert t['passed'] and t['evidence']['checks']==360
source=REPO/'implementation/warlock-family-style-crop-capture-v8';pair=json.loads((source/'native-build-report.json').read_text());buildPath=pathlib.Path(pair['pluginBuildReport']);build=verify(buildPath);assert build['passed'] and not build['missingSymbols'] and sha(source/'native/style_revision.hpp')==sha(model/'native/style_revision.hpp')
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in build[key].items():assert sha(p)==h,p
assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
coreManifest=pathlib.Path(pair['coreComponentManifest']);core=json.loads(coreManifest.read_text());assert core['sourceHeld'] and core['evidenceIntegrityPassed'] and sha(coreManifest)==pair['coreComponentManifestSHA256']
for rel,row in core['files'].items():assert sha(coreManifest.parent/rel)==row['sha256'],rel
fixture=REPO/'implementation/warlock-family-modal-fixture-v3';fixturePath=only(fixture,'qa/client-build-*/report.json');f=verify(fixturePath);assert f['passed'] and all(row['exitCode']==0 for row in f['commands'])
for key in ['inputs','dependencies','linkedLibraries','tools']:
 for p,h in f[key].items():assert sha(p)==h,p
assert sha(f['client'])==f['clientSHA256']
failedSource=REPO/'implementation/warlock-family-style-crop-capture-v7';failedBuild=only(failedSource,'qa/build-*/report.json');assert not verify(failedBuild)['passed']
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath);names=[row['name'] for row in original['checks']];assert len(names)==1783
failedRoot=REPO/'implementation/warlock-client-provider-native-v65';failedPath=only(failedRoot,'qa/native-*/report.json');failed=verify(failedPath)
assert not failed['passed'] and failed['cleanupPassed'] and len(failed['checks'])==2086 and len(failed['ownedExitCodes'])==202 and all(row['exitCode']==0 for row in failed['ownedExitCodes']) and [row['name'] for row in failed['checks'] if row['name'] in set(names)]==names and not failed['backgroundEffectEvidence']['creationEpochAdvanced']
assert [row['name'] for row in failed['checks'] if not row['passed']]==['backgroundCreationBeforeCommitRequiresNewEpoch']
nativeRoot=REPO/'implementation/warlock-client-provider-native-v66';nativePath=only(nativeRoot,'qa/native-*/report.json');native=verify(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes']) and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
pre=verify(nativeRoot/'qa/preflight.json');assert pre['pair']==native['pair']
for p,h in pre['inputs'].items():assert sha(p)==h,p
required=['backgroundProtocolCreationDoesNotCommitBuffer','backgroundCreatedOldContextRejectedBeforeAllocation','backgroundCreatedStaleContextAllocatesNoProducer','backgroundPendingRegionPreservesAppliedContext','backgroundAppliedRegionUsesNewCommittedSource','backgroundChangedPendingRegionPreservesAppliedContext','backgroundChangedAppliedRegionUsesLaterRevision','backgroundPendingClearPreservesAppliedContext','backgroundAppliedClearUsesLaterRevision','backgroundPendingDestroyPreservesAppliedContext','backgroundAppliedDestroyUsesLaterRevision','backgroundCreationBeforeCommitRequiresNewEpoch','allOriginal1783OrderedAssertionsRetained','opacityWholeRootIndependentNativeComposition']
for name in required:assert next(row for row in native['checks'] if row['name']==name)['passed'],name
proof=native['backgroundEffectEvidence'];assert proof['creationProcessedWithoutBufferCommit'] and proof['creationEpochAdvanced'] and not proof['backgroundPixelFidelityQualified'] and not proof['nestedEffectFactsQualified']
for pending,applied in [('regionPending','created'),('changedRegionPending','regionApplied'),('clearPending','changedRegionApplied'),('destroyPending','cleared')]:assert proof[pending]['scope']['context']==proof[applied]['scope']['context']
assert proof['before']['members']==proof['created']['members'] and proof['before']['styles']==proof['created']['styles'] and proof['before']['crop']==proof['created']['crop']
specRoot=REPO/'openspec/changes/warlock-preview-background-effects';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
for p in validations:assert verify(p)['passed']
roots=[model,failedSource,source,fixture,failedRoot,nativeRoot,specRoot];components=[]
for root in roots:
 for p in root.glob('qa/*/report.json'):verify(p)
 for p in root.glob('qa/preflight.json'):
  for path,h in json.loads(p.read_text())['inputs'].items():assert sha(path)==h,path
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
  if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[str(rel)]=str(p.readlink());continue
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'actualNativeRootBackgroundFactsQualified':root in [source,nativeRoot],'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'backgroundPixelFidelityQualified':False,'nestedEffectFactsQualified':False,'completeFamilyFidelityQualified':False}
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [priorPath,modelPath,controlsPath,buildPath,fixturePath,failedBuild,originalPath,failedPath,nativePath,*validations]},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeRootBackgroundFactsQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'backgroundPixelFidelityQualified':False,'nestedEffectFactsQualified':False,'completeFamilyFidelityQualified':False,'next':'Implement/qualify complete subsurface/popup background-effect facts and actual background-dependent blur/backdrop source/privacy ownership; complete shader/transform/output/hardware, original preview13/restore38/recovery34/drag52 and coherent full GUI release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
