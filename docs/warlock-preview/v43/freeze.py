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
priorPath=REPO/'docs/warlock-preview/v42/report.json';prior=verify(priorPath);assert prior['passed'] and prior['actualNativeRootBackgroundFactsQualified']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];j=json.loads(p.read_text())
 for rel,item in j['files'].items():assert sha(p.parent/rel)==item['sha256'],rel
model=REPO/'implementation/warlock-family-style-revisions-v9';modelPath=only(model,'qa/model-*/report.json');m=verify(modelPath);assert m['passed'] and len(m['selectedNames'])==34 and m['states']==130
controlsPath=only(model,'qa/test-*/report.json');t=verify(controlsPath);assert t['passed'] and t['evidence']['checks']==395
source=REPO/'implementation/warlock-family-style-crop-capture-v10';pair=json.loads((source/'native-build-report.json').read_text());buildPath=pathlib.Path(pair['pluginBuildReport']);build=verify(buildPath);assert build['passed'] and not build['missingSymbols'] and sha(source/'native/style_revision.hpp')==sha(model/'native/style_revision.hpp')
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in build[key].items():assert sha(p)==h,p
assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
coreManifest=pathlib.Path(pair['coreComponentManifest']);core=json.loads(coreManifest.read_text());assert core['sourceHeld'] and core['evidenceIntegrityPassed'] and sha(coreManifest)==pair['coreComponentManifestSHA256']
for rel,row in core['files'].items():assert sha(coreManifest.parent/rel)==row['sha256'],rel
fixture=REPO/'implementation/warlock-family-modal-fixture-v5';fixturePath=only(fixture,'qa/client-build-*/report.json');f=verify(fixturePath);assert f['passed'] and all(row['exitCode']==0 for row in f['commands'])
for key in ['inputs','dependencies','linkedLibraries','tools']:
 for p,h in f[key].items():assert sha(p)==h,p
assert sha(f['client'])==f['clientSHA256']
parentSource=REPO/'implementation/warlock-family-style-crop-capture-v9';parentBuild=only(parentSource,'qa/build-*/report.json');assert verify(parentBuild)['passed']
parentFixture=REPO/'implementation/warlock-family-modal-fixture-v4';parentFixtureBuild=only(parentFixture,'qa/client-build-*/report.json');assert verify(parentFixtureBuild)['passed']
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath);names=[row['name'] for row in original['checks']];assert len(names)==1783
failedRoot=REPO/'implementation/warlock-client-provider-native-v67';failedPath=only(failedRoot,'qa/native-*/report.json');failed=verify(failedPath)
assert not failed['passed'] and failed['cleanupPassed'] and len(failed['checks'])==2053 and len(failed['ownedExitCodes'])==198 and 'control-shape' in failed['error'] and [row['name'] for row in failed['ownedExitCodes'] if row['exitCode']]==['child'] and next(row for row in failed['ownedExitCodes'] if row['name']=='child')['exitCode']==1
nativeRoot=REPO/'implementation/warlock-client-provider-native-v68';nativePath=only(nativeRoot,'qa/native-*/report.json');native=verify(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes']) and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
pre=verify(nativeRoot/'qa/preflight.json');assert pre['pair']==native['pair']
for p,h in pre['inputs'].items():assert sha(p)==h,p
required=['nestedChildCreateBeforeAnyBufferCommit','nestedChildOldContextRejectedBeforeAllocation','nestedChildStaleContextAllocatesNoProducer','nestedChildPendingRegionRetainsExactFacts','nestedChildAppliedExactRegion','nestedChildChangedExactCopiedRegion','nestedChildAppliedDestroyClearsNativePreference','nestedPopupCreateBeforeRootChildBufferCommit','nestedPopupOldContextRejectedBeforeAllocation','nestedPopupStaleContextAllocatesNoProducer','nestedPopupAppliedExactRegion','nestedPopupChangedExactCopiedRegion','nestedPopupAppliedDestroyClearsNativePreference','nestedPopupOnlyFourApplyingCommits','nestedDestroyedPopupRetiresItsNativeIdentity','nestedExactReadonlyFactSchemaRejectsExtraField','allOriginal1783OrderedAssertionsRetained','opacityWholeRootIndependentNativeComposition','backgroundCreationBeforeCommitRequiresNewEpoch']
for name in required:assert next(row for row in native['checks'] if row['name']==name)['passed'],name
proof=native['nestedBackgroundEffectEvidence'];assert proof['actualNativeChildPopupFactsQualified'] and not proof['backgroundPixelFidelityQualified'] and not proof['previewEligible'] and not proof['hardwarePresentation']
def member(value):return next(row for row in value['effectFacts'] if row['incarnation']==value['scope']['context']['incarnation'])
def leaf(value,identity):return next(row for row in member(value)['surfaces'] if row['identity']==identity)
child=proof['childIdentity'];popup=proof['popupIdentity'];assert child!=popup and child!=member(proof['childBefore'])['root']['identity']
for prefix,identity in [('child',child),('popup',popup)]:
 for pending,applied in [('Pending','Created'),('ChangedPending','Applied'),('ClearPending','Changed'),('DestroyPending','Cleared')]:
  a=proof[prefix+pending];b=proof[prefix+applied];assert a['scope']['context']==b['scope']['context'] and a['effectFacts']==b['effectFacts']
 assert not leaf(proof[prefix+'Before'],identity)['hasEffect'] and leaf(proof[prefix+'Created'],identity)['hasEffect'] and leaf(proof[prefix+'Created'],identity)['blurRegion']==[]
 assert int(proof[prefix+'Created']['scope']['context']['content'])>int(proof[prefix+'Before']['scope']['context']['content'])
 assert leaf(proof[prefix+'Applied'],identity)['blurRegion']==[[0,20,100,220]] and leaf(proof[prefix+'Changed'],identity)['blurRegion']==[[10,20,110,220]]
 assert leaf(proof[prefix+'Cleared'],identity)['hasEffect'] and leaf(proof[prefix+'Cleared'],identity)['blurRegion']==[] and not leaf(proof[prefix+'Removed'],identity)['hasEffect'] and leaf(proof[prefix+'Removed'],identity)['blurRegion']==[]
assert popup not in {row['identity'] for row in member(proof['final'])['surfaces']}
specRoot=REPO/'openspec/changes/warlock-preview-surface-effects';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
for p in validations:assert verify(p)['passed']
roots=[model,parentSource,source,parentFixture,fixture,failedRoot,nativeRoot,specRoot];components=[]
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
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'actualNativeChildPopupFactsQualified':root in [source,nativeRoot],'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'backgroundPixelFidelityQualified':False,'nestedEffectFactsQualified':root in [source,nativeRoot],'completeFamilyFidelityQualified':False}
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [priorPath,modelPath,controlsPath,buildPath,parentBuild,fixturePath,parentFixtureBuild,originalPath,failedPath,nativePath,*validations]},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeChildPopupFactsQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'backgroundPixelFidelityQualified':False,'nestedEffectFactsQualified':True,'completeFamilyFidelityQualified':False,'next':'Implement/qualify actual background-dependent blur/backdrop source/privacy ownership and all remaining native surface renderer facts; complete shader/transform/output/hardware, original preview13/restore38/recovery34/drag52 and coherent full GUI release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
