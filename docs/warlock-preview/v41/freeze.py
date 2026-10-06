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
priorPath=REPO/'docs/warlock-preview/v40/report.json';prior=verify(priorPath);assert prior['passed'] and prior['actualLiveSourceHistoricalFamilyQualified']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];j=json.loads(p.read_text())
 for rel,v in j['files'].items():assert sha(p.parent/rel)==v['sha256'],rel
model=REPO/'implementation/warlock-family-style-revisions-v7';modelPath=only(model,'qa/model-*/report.json');m=verify(modelPath);assert m['passed'] and len(m['selectedNames'])==20 and m['states']==74
controlsPath=only(model,'qa/test-*/report.json');t=verify(controlsPath);assert t['passed'] and t['evidence']['checks']==321
source=REPO/'implementation/warlock-family-style-crop-capture-v6';pair=json.loads((source/'native-build-report.json').read_text());buildPath=pathlib.Path(pair['pluginBuildReport']);build=verify(buildPath);assert build['passed'] and not build['missingSymbols']
assert sha(source/'native/style_revision.hpp')==sha(model/'native/style_revision.hpp')
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in build[key].items():assert sha(p)==h,p
assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
coreManifest=pathlib.Path(pair['coreComponentManifest']);core=json.loads(coreManifest.read_text());assert core['sourceHeld'] and core['evidenceIntegrityPassed'] and sha(coreManifest)==pair['coreComponentManifestSHA256']
for rel,row in core['files'].items():assert sha(coreManifest.parent/rel)==row['sha256'],rel
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath);names=[row['name'] for row in original['checks']];assert len(names)==1783
reports={};native={}
for version in range(58,65):
 root=REPO/('implementation/warlock-client-provider-native-v'+str(version));path=only(root,'qa/native-*/report.json');j=verify(path);assert j['cleanupPassed'];reports[version]=path;native[version]=j
 pre=verify(root/'qa/preflight.json');assert pre['passed'] and pre['pair']==j['pair']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
for version in [60,63]:
 j=native[version];assert j['passed'] and all(row['passed'] for row in j['checks']) and all(row['exitCode']==0 for row in j['ownedExitCodes'])
 assert [row['name'] for row in j['checks'] if row['name'] in set(names)]==names
assert len(native[63]['checks'])==2057 and len(native[63]['ownedExitCodes'])==201
for version in [58,59,61,62]:assert not native[version]['passed']
failed=native[62];assert len(failed['checks'])==2020 and len(failed['ownedExitCodes'])==193 and all(row['exitCode']==0 for row in failed['ownedExitCodes'])
assert [row['name'] for row in failed['checks'] if row['name'] in set(names)]==names
assert failed['opacityConfigurationEvidence']['bytesChanged'] and not failed['opacityConfigurationEvidence']['styleEpochChanged'] and failed['opacityConfigurationEvidence']['rootCommitsUnchanged']
fixed=native[63];o=fixed['opacityConfigurationEvidence'];n=fixed['samplingConfigurationEvidence'];assert o['bytesChanged'] and o['styleEpochChanged'] and o['rootCommitsUnchanged'] and n['rootCommitsUnchanged'] and n['nativeRuleTransitionsQualified'] and n['nativeConfigurationTransitionsQualified'] and not n['samplingPixelFidelityQualified']
for name in ['opacityOldRuleContextRejectedBeforeAllocation','opacityStaleRuleAllocatesNoProducer','opacityOnlyNativeRuleAdvancesEpoch','opacitySameRuleRetainsExactSourceContext','samplingOldRuleContextRejectedBeforeAllocation','samplingStaleRuleAllocatesNoProducer','samplingSameRuleRetainsExactSourceContext','samplingRestoredRuleUsesLaterRevision','samplingOnlyNativeConfigurationAdvancesEpoch','samplingOldConfigurationContextRejectedBeforeAllocation','samplingStaleConfigurationAllocatesNoProducer','samplingSameConfigurationRetainsExactSourceContext','opacityChangedNativePixelsRequireNewStyleEpoch']:
 assert next(row for row in fixed['checks'] if row['name']==name)['passed'],name
pixels=native[60]['glowConfigurationEvidence']['pixels'];assert pixels['passed'] and pixels['comparedRootPixels']==76800 and pixels['changedFamilyPixels']==pixels['changedOutputPixels']==8696 and pixels['mismatchedBefore']==pixels['mismatchedAfter']==pixels['changedCenterPixels']==0 and pixels['pixelsOutsideGlowContour']==68076
failedPixelPath=only(OUT,'pixel-proof-*/report.json');fp=verify(failedPixelPath);assert not fp['passed'] and fp['label']=='counterexample' and fp['result']['comparedRootPixels']==76800
attempt=native[64];compositionQualified=attempt['passed']
if compositionQualified:
 assert all(row['passed'] for row in attempt['checks']) and all(row['exitCode']==0 for row in attempt['ownedExitCodes']) and [row['name'] for row in attempt['checks'] if row['name'] in set(names)]==names
 whole=attempt['opacityConfigurationEvidence'];assert whole['wholeRootPixels']['passed'] and whole['wholeRootPixels']['comparedRootPixels']==76800 and not whole['backgroundDependentBlurQualified'] and whole['privateNoBlurRule']
specRoot=REPO/'openspec/changes/warlock-preview-render-facts'
validations=list(specRoot.glob('qa/validate-*/report.json'));assert len(validations)==3
for p in validations:assert verify(p)['passed']
roots=[model,source,*[REPO/('implementation/warlock-client-provider-native-v'+str(v)) for v in range(58,65)],specRoot];components=[]
for root in roots:
 for p in root.glob('qa/*/report.json'):verify(p)
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
  if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[str(rel)]=str(p.readlink());continue
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'actualNativeOpaqueSamplingFactsQualified':root in [source,REPO/'implementation/warlock-client-provider-native-v63'],'actualNativeGlowRootPixelsQualified':root==REPO/'implementation/warlock-client-provider-native-v60','actualNoBlurRootOpacityCompositionQualified':compositionQualified and root==REPO/'implementation/warlock-client-provider-native-v64'}
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [priorPath,modelPath,controlsPath,buildPath,originalPath,failedPixelPath,*reports.values(),*validations]},'nativeControls':len(fixed['checks']),'retainedOriginalControls':1783,'normalOwnedExits':len(fixed['ownedExitCodes']),'glowPixels':pixels,'actualNativeOpaqueSamplingFactsQualified':True,'samplingPixelFidelityQualified':False,'noBlurOpacityCompositionAttempt':{'nativeCampaignPassed':attempt['passed'],'checks':len(attempt['checks']),'ownedExits':len(attempt['ownedExitCodes']),'qualified':compositionQualified},'exploratoryUniformOpacityPixelProofPassed':False,'backgroundDependentBlurQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete actual background-dependent blur/alpha/source/shader/transform/output/hardware fidelity and filtered sampling pixels; original preview13/restore38/recovery34/drag52 and coherent full GUI release remain open.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'compositionQualified':compositionQualified}))
