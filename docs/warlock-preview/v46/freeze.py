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
priorPath=REPO/'docs/warlock-preview/v45/report.json';prior=verify(priorPath);assert prior['passed']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [8,9,10,11,12]:
 root=REPO/f'implementation/warlock-core-family-crop-v{version}';plane=only(root,'qa/plane-*/report.json');j=verify(plane)
 if version<11:assert not j['passed']
 else:assert j['passed'] and len(j['selectedNames'])==9 and j['states']==26
 evidence.append(plane)
 builds=list(root.glob('build-*/report.json'))
 if version<11:assert not builds
 else:
  assert len(builds)==1;build=builds[0];j=verify(build,root)
  if version==11:assert not j['passed'] and 'CGLFramebuffer' in j['error']
  else:assert j['passed'] and j['unchangedArchiveMembers']==431 and j['existingObjectLayoutsUnchanged'];held(root/'component-manifest.json')
  evidence.append(build)
 roots.append(root)
for version in [14,15,16]:
 root=REPO/f'implementation/warlock-family-style-crop-capture-v{version}'
 if version==14:
  p=root/'preparation-stop.json';j=verify(p);assert not j['passed'] and not j['actualNativeCodeChanged'] and not j['compiled'];evidence.append(p)
 elif version==15:assert not list(root.glob('qa/build-*/report.json'))
 else:
  p=only(root,'qa/build-*/report.json');j=verify(p,root);assert j['passed'] and not j['missingSymbols'];evidence.append(p)
 roots.append(root)
natives={}
for version in [76,77,78]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';prep=only(root,'qa/prepare-*/report.json');assert verify(prep)['passed'];p=only(root,'qa/native-*/report.json');j=verify(p);pre=verify(root/'qa/preflight.json');assert pre['pair']==j['pair'] and j['cleanupPassed'] and all(row['exitCode']==0 for row in j['ownedExitCodes'])
 if version==76:assert not j['passed'] and len(j['checks'])==2216 and len(j['ownedExitCodes'])==216 and [row['name'] for row in j['checks'] if not row['passed']]==['shaderActualGlobalCoordinatesMatchIndependentNativeOutput']
 else:assert j['passed'] and all(row['passed'] for row in j['checks']) and j['nativeShaderGlobalCoordinateSampleQualified'] and not j['completeShaderFidelityQualified'] and not j['backgroundPixelFidelityQualified']
 roots.append(root);evidence+=[prep,p];natives[version]=j
original=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';originalNames=[row['name'] for row in verify(original)['checks']];assert len(originalNames)==1783
for j in natives.values():assert [row['name'] for row in j['checks'] if row['name'] in set(originalNames)]==originalNames
native=natives[78];assert native['shaderWholeCoordinatePixels']=={'passed':True,'comparedRootPixels':76800,'mismatchedRootPixels':0,'wrongAlphaPixels':0,'nativeRedRange':[26,127],'nativeGreenRange':[34,136]}
assert native['shaderWholeRootPixels']['passed'] and native['shaderWholeRootPixels']['mismatchedBefore']==native['shaderWholeRootPixels']['mismatchedAfter']==0
assert native['pair']==natives[77]['pair']
def identity(name):return re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',name)
variablePolls={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'};assert not variablePolls.intersection(originalNames)
base=natives[77];priorRows=[row for row in base['checks'] if row['name'] not in variablePolls];cursor=0
for row in native['checks']:
 if row['name'] not in variablePolls and cursor<len(priorRows) and identity(row['name'])==identity(priorRows[cursor]['name']):cursor+=1
assert cursor==len(priorRows),cursor
pollCounts={name:{'native77':sum(row['name']==name for row in base['checks']),'native78':sum(row['name']==name for row in native['checks'])} for name in sorted(variablePolls)}
evidence.append(original)
specRoot=REPO/'openspec/changes/warlock-preview-screen-coordinates';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
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
  target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeShaderGlobalCoordinateSampleQualified':root.name in ['warlock-client-provider-native-v77','warlock-client-provider-native-v78'],'nativeShaderOpaqueRootCoordinatesQualified':root.name=='warlock-client-provider-native-v78','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False},indent=2)+'\n')
 j=held(target);components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(j['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'retainedPriorNativeControls':len(priorRows),'addedIntermediatePollComparison':pollCounts,'normalOwnedExits':len(native['ownedExitCodes']),'shaderWholeRootPixels':native['shaderWholeRootPixels'],'shaderWholeCoordinatePixels':native['shaderWholeCoordinatePixels'],'nativeShaderGlobalCoordinateSampleQualified':True,'nativeShaderOpaqueRootCoordinatesQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False,'next':'Implement and qualify transparent family/decorations and global UV/neighborhood/contextual/color/output shader semantics, backdrop source privacy/ownership, measured GPU/driver resources and every original coherent GUI release gate.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
