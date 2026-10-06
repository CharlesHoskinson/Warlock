import hashlib,json,pathlib,resource,stat,sys,re
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,(root,pattern);return rows[0]
def verify(path,owner=None):
 j=json.loads(path.read_text())
 for rel,h in j.get('artifacts',{}).items():assert sha(path.parent/rel)==h,(path,rel)
 for p,h in j.get('inputs',{}).items():
  q=pathlib.Path(p);q=q if q.is_absolute() else owner/q
  assert sha(q)==h,(path,q)
 return j
def held(path):
 j=json.loads(path.read_text());assert j['sourceHeld'] and j['evidenceIntegrityPassed']
 for rel,item in j['files'].items():assert sha(path.parent/rel)==item['sha256'],rel
 return j
priorPath=REPO/'docs/warlock-preview/v48/report.json';prior=verify(priorPath);assert prior['passed']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [84,85]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';prep=only(root,'qa/prepare-*/report.json');assert verify(prep)['passed'];pre=verify(root/'qa/preflight.json');p=only(root,'qa/native-*/report.json');j=verify(p);assert pre['pair']==j['pair'] and j['cleanupPassed'] and all(row['exitCode']==0 for row in j['ownedExitCodes'])
 if version==84:assert not j['passed'] and len(j['checks'])==2297 and len(j['ownedExitCodes'])==237 and [row['name'] for row in j['checks'] if not row['passed']]==['blurBodyActualNativeBrightnessDeltasRequireMatchingFamilyPixels'] and j['blurBodyEvidence']['pixels']['changedFamilyPixels']==0 and j['blurBodyEvidence']['pixels']['changedNativeOutputPixels']==j['blurBodyEvidence']['pixels']['mismatchedRGBDeltaPixels']==76800
 else:assert j['passed'] and len(j['checks'])==2307 and len(j['ownedExitCodes'])==239 and all(row['passed'] for row in j['checks']) and j['nativeBlurBodyBrightnessQualified'];native=j
 roots.append(root);evidence+=[prep,p]
assert native['blurBodyEvidence']['pixels']=={'passed':True,'comparedBodyPixels':76800,'changedFamilyPixels':76800,'changedNativeOutputPixels':76800,'mismatchedRGBDeltaPixels':0,'wrongAlphaPixels':0,'independentUnchangedTintedWhiteBackdrop':True}
assert len(native['blurBodyExactPixels'])==2 and all(row['pixels']['passed'] and row['pixels']['comparedRootPixels']==76800 and row['pixels']['mismatchedRootPixels']==row['pixels']['wrongAlphaPixels']==0 for row in native['blurBodyExactPixels'])
for version in [13,14,15,16]:
 root=REPO/f'implementation/warlock-core-family-crop-v{version}'
 if version in [13,14]:p=root/'PREPARATION-FAILURE.json';assert not verify(p)['passed']
 else:
  p=only(root,'build-*/report.json');proof=verify(p,root);assert proof['passed']==(version==16)
  for lane in ['plane','backdrop']:
   q=only(root,f'qa/{lane}-*/report.json');model=verify(q);assert model['passed'] and len(model['selectedNames'])==9 and model['states']==26;evidence.append(q)
 roots.append(root);evidence.append(p)
root=REPO/'implementation/warlock-family-style-revisions-v12'
for lane,count,states in [('test',436,0),('model',46,181)]:
 p=only(root,f'qa/{lane}-*/report.json');j=verify(p);assert j['passed']
 if lane=='test':assert j['evidence']['checks']==count
 else:assert len(j['selectedNames'])==count and j['states']==states
 evidence.append(p)
roots.append(root)
root=REPO/'implementation/warlock-family-style-crop-capture-v17';p=only(root,'qa/build-*/report.json');j=verify(p,root);assert j['passed'] and not j['missingSymbols'];roots.append(root);evidence.append(p)
root=REPO/'implementation/warlock-generated-backdrop-fd-qualification-v1';p=only(root,'qa/test-*/report.json');j=verify(p);assert j['passed'] and j['evidence']['legacy']['checks']==150 and j['evidence']['style']['checks']==295 and all(j['evidence']['qualify'][key] for key in ['physicalFDClosed','physicalMappingClosed','chargeReleasedAfterClose']);roots.append(root);evidence.append(p)
original=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';originalNames=[row['name'] for row in verify(original)['checks']];assert len(originalNames)==1783 and [row['name'] for row in native['checks'] if row['name'] in set(originalNames)]==originalNames
assert len(native['shaderCompositedCropPixels'])==2
for row in native['shaderCompositedCropPixels']:
 p=row['pixels'];assert p=={'passed':True,'comparedCropPixels':84836,'mismatchedCompositedPixels':0,'opaqueFamilyPixels':77924,'partialAlphaFamilyPixels':3416,'transparentFamilyPixels':3496,'wrongNativeOutputAlphaPixels':0,'independentBackgroundRGBA':[0,0,0,255]}
assert native['shaderWholeRootPixels']['passed'] and native['shaderWholeCoordinatePixels']['passed']
priorNative=REPO/'implementation/warlock-client-provider-native-v83/qa/native-1791281764693182620/report.json';base=verify(priorNative);assert base['passed'] and native['pair']!=base['pair'] and native['pair']['aquamarine']==base['pair']['aquamarine']
def identity(name):return re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',name)
variablePolls={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'};assert not variablePolls.intersection(originalNames)
priorRows=[row for row in base['checks'] if row['name'] not in variablePolls];cursor=0
for row in native['checks']:
 if row['name'] not in variablePolls and cursor<len(priorRows) and identity(row['name'])==identity(priorRows[cursor]['name']):cursor+=1
assert cursor==len(priorRows),cursor
pollCounts={name:{'native83':sum(row['name']==name for row in base['checks']),'native85':sum(row['name']==name for row in native['checks'])} for name in sorted(variablePolls)}
evidence+=[original,priorNative]
specRoot=REPO/'openspec/changes/warlock-preview-owned-backdrop-blur';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
for p in validations:assert verify(p)['passed']
roots.append(specRoot);evidence+=validations
components=[]
for root in roots:
 target=root/'component-manifest.json'
 if not target.exists():
  files={};links={}
  for p in sorted(root.rglob('*')):
   rel=p.relative_to(root)
   if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
   if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers';links[str(rel)]=str(p.readlink());continue
   if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeShaderWholeCropOverBlackQualified':root.name=='warlock-client-provider-native-v85','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False},indent=2)+'\n')
 j=held(target);components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(j['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'retainedPriorNativeControls':len(priorRows),'addedIntermediatePollComparison':pollCounts,'normalOwnedExits':len(native['ownedExitCodes']),'shaderCompositedCropPixels':native['shaderCompositedCropPixels'],'nativeGeneratedBackdropBlurBodyQualified':True,'blurBodyEvidence':native['blurBodyEvidence'],'blurBodyExactPixels':native['blurBodyExactPixels'],'nativeShaderHalfBodyOverBlackNoBlurQualified':True,'shaderHalfBodyComparison':native['shaderHalfBodyComparison'],'shaderHalfCursorEvidence':native['shaderHalfCursorEvidence'],'nativeShaderWholeCropOverBlackQualified':True,'shaderWholeRootPixels':native['shaderWholeRootPixels'],'shaderWholeCoordinatePixels':native['shaderWholeCoordinatePixels'],'nativeShaderGlobalCoordinateSampleQualified':True,'nativeShaderOpaqueRootCoordinatesQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False,'next':'Qualify arbitrary authorized backdrop/blur source dependency/privacy and integrate applicable generated mode through the shared Elm/retained receipt path, general shader/contextual/color/HDR/transform/driver/resources/hardware and every original coherent GUI release gate.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
