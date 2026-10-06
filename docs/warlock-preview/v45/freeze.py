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
priorPath=REPO/'docs/warlock-preview/v44/report.json';prior=verify(priorPath);assert prior['passed']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [5,6,7]:
 root=REPO/f'implementation/warlock-core-family-crop-v{version}';build=only(root,'build-*/report.json');j=verify(build,root)
 if version==6:assert not j['passed'] and 'g_pHyprOpenGL' in j['error']
 else:assert j['passed'] and j['unchangedArchiveMembers']==431 and j['existingObjectLayoutsUnchanged'];held(root/'component-manifest.json')
 roots.append(root);evidence.append(build)
assert 'Render::GL::g_pHyprOpenGL->renderFamilyScreenShader' in (roots[-1]/'candidate/src/render/FamilyCrop.inc').read_text()
source=REPO/'implementation/warlock-family-style-crop-capture-v13';build=only(source,'qa/build-*/report.json');j=verify(build,source);assert j['passed'] and not j['missingSymbols'];roots.append(source);evidence.append(build)
natives={}
for version in [73,74,75]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';prep=only(root,'qa/prepare-*/report.json');assert verify(prep)['passed'];p=only(root,'qa/native-*/report.json');j=verify(p);pre=verify(root/'qa/preflight.json');assert pre['pair']==j['pair'] and j['cleanupPassed'] and all(row['exitCode']==0 for row in j['ownedExitCodes'])
 if version==73:assert not j['passed'] and len(j['checks'])==2197 and len(j['ownedExitCodes'])==212 and [row['name'] for row in j['checks'] if not row['passed']]==['shaderActualNativeTintRequiresMatchingFamilyPixels']
 else:assert j['passed'] and all(row['passed'] for row in j['checks']) and j['nativeShaderRootPixelSamplesQualified'] and not j['completeShaderFidelityQualified'] and not j['backgroundPixelFidelityQualified']
 roots.append(root);evidence+=[prep,p];natives[version]=j
original=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';originalNames=[row['name'] for row in verify(original)['checks']];assert len(originalNames)==1783
for j in natives.values():assert [row['name'] for row in j['checks'] if row['name'] in set(originalNames)]==originalNames
native=natives[75];assert native['shaderWholeRootPixels']=={'passed':True,'comparedRootPixels':76800,'changedFamilyPixels':73728,'changedOutputPixels':73728,'mismatchedBefore':0,'mismatchedAfter':0,'wrongAlphaPixels':0,'redPixels':73728,'unchangedBlueChildPixels':3072,'unexpectedFixturePixels':0}
def identity(name):return re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',name)
base=natives[74];variablePoll='styleCropDimIntermediateReadonlyScope';priorRows=[row for row in base['checks'] if row['name']!=variablePoll];assert len(priorRows)==2195;cursor=0
for row in native['checks']:
 if cursor<len(priorRows) and identity(row['name'])==identity(priorRows[cursor]['name']):cursor+=1
assert cursor==2195,cursor
assert sum(row['name']==variablePoll for row in base['checks'])==2 and sum(row['name']==variablePoll for row in native['checks'])==1
evidence.append(original)
specRoot=REPO/'openspec/changes/warlock-preview-shader-rendering';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
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
  target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeShaderRootPixelSamplesQualified':root.name in ['warlock-client-provider-native-v74','warlock-client-provider-native-v75'],'nativeShaderOpaqueRootPixelsQualified':root.name=='warlock-client-provider-native-v75','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False},indent=2)+'\n')
 j=held(target);components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(j['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'retainedPriorNativeControls':2195,'addedIntermediatePollComparison':{'name':variablePoll,'native74':2,'native75':1,'meaning':'Nonoriginal readonly intermediate scheduling observations; all original1783 identities, predicates, final applied reads and deadlines remain exact.'},'normalOwnedExits':len(native['ownedExitCodes']),'shaderWholeRootPixels':native['shaderWholeRootPixels'],'nativeShaderRootPixelSamplesQualified':True,'nativeShaderOpaqueRootPixelsQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeShaderFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False,'next':'Implement and qualify transparent family/decorations and global UV/neighborhood/contextual/color/output shader semantics, backdrop source privacy/ownership, measured GPU/driver resources and every original coherent GUI release gate.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
