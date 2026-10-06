import hashlib,json,pathlib,resource,stat,sys
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
  q=pathlib.Path(p)
  if q.is_absolute():assert sha(q)==h,q
  elif owner:assert sha(owner/q)==h,q
 return j
def held(path):
 j=json.loads(path.read_text());assert j['sourceHeld'] and j['evidenceIntegrityPassed']
 for rel,item in j['files'].items():assert sha(path.parent/rel)==item['sha256'],rel
 return j
priorPath=REPO/'docs/warlock-preview/v43/report.json';prior=verify(priorPath);assert prior['passed'] and prior['actualNativeChildPopupFactsQualified']
for row in prior['components']:
 p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [3,4]:
 root=REPO/f'implementation/warlock-core-family-crop-v{version}';manifest=root/'component-manifest.json';core=held(manifest);report=pathlib.Path(core['buildReport']);assert sha(report)==core['buildReportSHA256'];j=verify(report,root);assert j['passed'] and j['unchangedArchiveMembers']==431 and j['existingObjectLayoutsUnchanged'];roots.append(root);evidence+=[manifest,report]
for version in [10,11]:
 root=REPO/f'implementation/warlock-family-style-revisions-v{version}';t=only(root,'qa/test-*/report.json');m=only(root,'qa/model-*/report.json');test=verify(t);model=verify(m);assert test['passed'] and test['evidence']['checks']==425 and model['passed'] and len(model['selectedNames'])==41 and model['states']==160;roots.append(root);evidence+=[t,m]
failed=REPO/'implementation/warlock-family-style-crop-capture-v11';failedPath=only(failed,'qa/build-*/report.json');failedProof=verify(failedPath,failed);assert not failedProof['passed'] and 'used but never defined' in failedProof['error'];roots.append(failed);evidence.append(failedPath)
source=REPO/'implementation/warlock-family-style-crop-capture-v12';pair=json.loads((source/'native-build-report.json').read_text());buildPath=pathlib.Path(pair['pluginBuildReport']);build=verify(buildPath,source);assert build['passed'] and not build['missingSymbols'];assert sha(source/'native/style_revision.hpp')==sha(REPO/'implementation/warlock-family-style-revisions-v11/native/style_revision.hpp')
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in build[key].items():assert sha(p)==h,p
assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256'];roots.append(source);evidence.append(buildPath)
failedNativeRoot=REPO/'implementation/warlock-client-provider-native-v69';failedNativePath=only(failedNativeRoot,'qa/native-*/report.json');failedNative=verify(failedNativePath);assert not failedNative['passed'] and failedNative['cleanupPassed'] and len(failedNative['checks'])==2130 and len(failedNative['ownedExitCodes'])==205 and all(row['exitCode']==0 for row in failedNative['ownedExitCodes']) and failedNative['appliedShaderEvidence']['actualAppliedShaderFactsQualified'];roots.append(failedNativeRoot);evidence.append(failedNativePath)
failed70Root=REPO/'implementation/warlock-client-provider-native-v70';failed70Path=only(failed70Root,'qa/native-*/report.json');failed70=verify(failed70Path);assert not failed70['passed'] and failed70['cleanupPassed'] and len(failed70['checks'])==2158 and len(failed70['ownedExitCodes'])==206 and all(row['exitCode']==0 for row in failed70['ownedExitCodes']) and [row['name'] for row in failed70['checks'] if not row['passed']]==['allOriginal1636OrderedAssertionsRetained'];roots.append(failed70Root);evidence.append(failed70Path)
failed71Root=REPO/'implementation/warlock-client-provider-native-v71';failed71Path=only(failed71Root,'qa/native-*/report.json');failed71=verify(failed71Path);assert not failed71['passed'] and failed71['cleanupPassed'] and len(failed71['checks'])==2161 and len(failed71['ownedExitCodes'])==206 and all(row['exitCode']==0 for row in failed71['ownedExitCodes']) and [row['name'] for row in failed71['checks'] if not row['passed']]==['allOriginal1636OrderedAssertionsRetained'];roots.append(failed71Root);evidence.append(failed71Path)
nativeRoot=REPO/'implementation/warlock-client-provider-native-v72';nativePath=only(nativeRoot,'qa/native-*/report.json');native=verify(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
pre=verify(nativeRoot/'qa/preflight.json');assert pre['pair']==native['pair']
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath);originalNames=[row['name'] for row in original['checks']];assert len(originalNames)==1783 and [row['name'] for row in native['checks'] if row['name'] in set(originalNames)]==originalNames
priorNativePath=REPO/'implementation/warlock-client-provider-native-v68/qa/native-1791273599848012391/report.json';base=verify(priorNativePath);assert base['passed'] and len(base['checks'])==2136
cursor=0
for row in native['checks']:
 if cursor<len(base['checks']) and row['name']==base['checks'][cursor]['name']:cursor+=1
assert cursor==2136,cursor
required=['shaderInitialAppliedProgramOff','shaderActualLinkedInputsCopied','shaderDiskEditDoesNotChangeAppliedProgram','shaderSamePathNewLinkedSourceAdvancesContent','shaderOldAppliedProgramContextRefusedBeforeAllocation','shaderStaleProgramAllocatesNoProducer','shaderIdenticalStaticProgramKeepsContent','shaderContextualProgramRefusesCapture','shaderContextualProgramAllocatesNoProducer','shaderRecoveryAdvancesPastPriorProgram','shaderFailedCompilationRetiresOldAppliedSource','shaderDisabledAppliedProgramOff','shaderAllSourceChangesWithoutBufferCommits','shaderCompileFaultProducesNativeErrorReservedArea','shaderPrivateReservedAreaActuallyRestored']
for name in required:assert next(row for row in native['checks'] if row['name']==name)['passed'],name
proof=native['appliedShaderEvidence'];assert proof['privateReservedAreaBefore']==proof['privateReservedAreaAfter'] and proof['privateErrorReservedArea']!=proof['privateReservedAreaBefore'];assert proof['actualAppliedShaderFactsQualified'] and proof['rootChildCommitsUnchanged'] and not proof['shaderPixelFidelityQualified'] and not proof['previewEligible']
assert proof['loaded']['appliedShader']==proof['diskChanged']['appliedShader'] and proof['loaded']['scope']['context']==proof['diskChanged']['scope']['context']
assert proof['reloaded']['appliedShader']==proof['stable']['appliedShader'] and proof['reloaded']['scope']['context']==proof['stable']['scope']['context']
assert proof['loaded']['appliedShader']['fragment']!=proof['reloaded']['appliedShader']['fragment']
assert proof['failed']['appliedShader']==proof['disabled']['appliedShader']==proof['before']['appliedShader']
roots.append(nativeRoot);evidence+=[nativePath,originalPath,priorNativePath]
specRoot=REPO/'openspec/changes/warlock-preview-applied-shaders';validations=list(specRoot.glob('qa/validate-*/report.json'));assert validations
for p in validations:assert verify(p)['passed']
roots.append(specRoot);evidence+=validations
components=[]
for root in roots:
 target=root/'component-manifest.json'
 if not target.exists():
  for p in root.glob('qa/*/report.json'):verify(p,root)
  files={};links={}
  for p in sorted(root.rglob('*')):
   rel=p.relative_to(root)
   if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
   if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers';links[str(rel)]=str(p.readlink());continue
   if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'actualAppliedShaderFactsQualified':root in [source,nativeRoot],'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'shaderPixelFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False},indent=2)+'\n')
 j=held(target);components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(j['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'retainedPriorNativeControls':2136,'normalOwnedExits':len(native['ownedExitCodes']),'actualAppliedShaderFactsQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'shaderPixelFidelityQualified':False,'backgroundPixelFidelityQualified':False,'completeFamilyFidelityQualified':False,'next':'Implement/qualify full static/contextual shader pixels and approved backdrop-dependent blur source/privacy/ownership, all native renderer/output/hardware facts and original GUI release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'components':len(components),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
