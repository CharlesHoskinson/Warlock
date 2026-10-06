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
priorPath=REPO/'docs/warlock-preview/v47/report.json';prior=verify(priorPath);assert prior['passed']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [81,82,83]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';prep=only(root,'qa/prepare-*/report.json');assert verify(prep)['passed'];pre=verify(root/'qa/preflight.json')
 if version==82:
  p=root/'qa/native-import-failure.json';j=verify(p);assert not j['passed'] and not j['nativeLaunched'] and j['protectedLauncherExitCode']==1
 else:
  p=only(root,'qa/native-*/report.json');j=verify(p);assert pre['pair']==j['pair'] and j['cleanupPassed'] and all(row['exitCode']==0 for row in j['ownedExitCodes'])
  if version==81:assert not j['passed'] and [row['name'] for row in j['checks'] if not row['passed']]==['shaderHalfBodyMatchesDeclaredAlphaAndIndependentNativeOutput'] and j['shaderHalfBodyComparison']['mismatchedCompositedPixels']==j['shaderHalfBodyComparison']['unexpectedBodyPixels']==253
  else:assert j['passed'] and all(row['passed'] for row in j['checks']) and j['nativeShaderHalfBodyOverBlackNoBlurQualified'] and j['shaderHalfBodyExplicitNoBlur'];native=j
 roots.append(root);evidence+=[prep,p]
assert native['shaderHalfBodyComparison']=={'passed':True,'comparedRootPixels':76800,'mismatchedCompositedPixels':0,'wrongNativeAlphaPixels':0,'declaredHalfAlphaRootPixels':73728,'declaredComposedChildPixels':3072,'unexpectedBodyPixels':0,'independentBlackBackground':True}
assert native['shaderHalfCursorEvidence']=={'before':{'x':240,'y':200},'measurement':{'x':790,'y':590},'restored':{'x':240,'y':200}}
original=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';originalNames=[row['name'] for row in verify(original)['checks']];assert len(originalNames)==1783 and [row['name'] for row in native['checks'] if row['name'] in set(originalNames)]==originalNames
assert len(native['shaderCompositedCropPixels'])==2
for row in native['shaderCompositedCropPixels']:
 p=row['pixels'];assert p=={'passed':True,'comparedCropPixels':84836,'mismatchedCompositedPixels':0,'opaqueFamilyPixels':77924,'partialAlphaFamilyPixels':3416,'transparentFamilyPixels':3496,'wrongNativeOutputAlphaPixels':0,'independentBackgroundRGBA':[0,0,0,255]}
assert native['shaderWholeRootPixels']['passed'] and native['shaderWholeCoordinatePixels']['passed']
priorNative=REPO/'implementation/warlock-client-provider-native-v80/qa/native-1791280152652471078/report.json';base=verify(priorNative);assert base['passed'] and native['pair']==base['pair']
def identity(name):return re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',name)
variablePolls={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'};assert not variablePolls.intersection(originalNames)
priorRows=[row for row in base['checks'] if row['name'] not in variablePolls];cursor=0
for row in native['checks']:
 if row['name'] not in variablePolls and cursor<len(priorRows) and identity(row['name'])==identity(priorRows[cursor]['name']):cursor+=1
assert cursor==len(priorRows),cursor
pollCounts={name:{'native80':sum(row['name']==name for row in base['checks']),'native83':sum(row['name']==name for row in native['checks'])} for name in sorted(variablePolls)}
evidence+=[original,priorNative]
specRoot=REPO/'openspec/changes/warlock-preview-half-alpha';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
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
  target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeShaderWholeCropOverBlackQualified':root.name=='warlock-client-provider-native-v83','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False},indent=2)+'\n')
 j=held(target);components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(j['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'retainedPriorNativeControls':len(priorRows),'addedIntermediatePollComparison':pollCounts,'normalOwnedExits':len(native['ownedExitCodes']),'shaderCompositedCropPixels':native['shaderCompositedCropPixels'],'nativeShaderHalfBodyOverBlackNoBlurQualified':True,'shaderHalfBodyComparison':native['shaderHalfBodyComparison'],'shaderHalfCursorEvidence':native['shaderHalfCursorEvidence'],'nativeShaderWholeCropOverBlackQualified':True,'shaderWholeRootPixels':native['shaderWholeRootPixels'],'shaderWholeCoordinatePixels':native['shaderWholeCoordinatePixels'],'nativeShaderGlobalCoordinateSampleQualified':True,'nativeShaderOpaqueRootCoordinatesQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False,'next':'Qualify arbitrary backdrop/blur source dependency/privacy, general shader/contextual/color/HDR/transform/driver/resources/hardware and every original coherent GUI release gate.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
