import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def readPointer(path):
 pointer=json.loads(path.read_text());p=pathlib.Path(pointer['path']);assert sha(p)==pointer['sha256'];return p,json.loads(p.read_text())
evidence=[]
planner,plan=readPointer(REPO/'implementation/warlock-family-crop-plan-v2/qa/check-report.json');assert plan['passed'];evidence.append(planner)
model,trace=readPointer(REPO/'implementation/warlock-family-crop-model-v4/qa/model-report.json');assert trace['passed'] and len(trace['selectedNames'])==8 and len(trace['implementationReplay'])==8 and trace['states']==23;evidence.append(model)
fd,physical=readPointer(REPO/'implementation/warlock-family-crop-fd-qualification-v2/qa/test-report.json');assert physical['passed'] and physical['evidence']['legacy']['checks']==150 and physical['evidence']['qualify']['checks']==295;evidence.append(fd)
for name in ['legacy','qualify']:assert all(physical['evidence'][name][k] for k in ['physicalFDClosed','physicalMappingClosed','chargeReleasedAfterClose'])
core=REPO/'implementation/warlock-core-family-crop-v1';held=json.loads((core/'component-manifest.json').read_text());assert held['sourceHeld'] and held['evidenceIntegrityPassed']
for rel,row in held['files'].items():assert sha(core/rel)==row['sha256'] and (core/rel).stat().st_size==row['size'],rel
coreReport=pathlib.Path(held['buildReport']);compiled=json.loads(coreReport.read_text());assert compiled['passed'] and compiled['unchangedArchiveMembers']==431 and set(compiled['rebuiltArchiveMembers'])=={'Renderer.cpp.o','OpenGL.cpp.o'};evidence.append(coreReport)
source=REPO/'implementation/warlock-family-crop-capture-v3';pair=json.loads((source/'native-build-report.json').read_text());assert pair['result']=='pass' and pair['sha256']==compiled['binarySHA256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256'];pluginReport=pathlib.Path(pair['pluginBuildReport']);plugin=json.loads(pluginReport.read_text());assert plugin['passed'] and not plugin['missingSymbols'];evidence.append(pluginReport)
for rel,digest in plugin['inputs'].items():assert sha(source/rel)==digest,rel
reports=list((REPO/'implementation/warlock-client-provider-native-v38/qa').glob('native-*/report.json'));assert len(reports)==1;nativePath=reports[0];native=json.loads(nativePath.read_text());assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes']);evidence.append(nativePath)
baseline=REPO/'implementation/warlock-client-provider-native-v37/qa/native-1791259128393147111/report.json';old=json.loads(baseline.read_text());names=[row['name'] for row in old['checks']];assert len(names)==1524 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names;evidence.append(baseline)
assert len(native['cropCaptureSamples'])==4 and all(row['header'][1]==2 and row['header'][22]==67 and len(row['header'])==28 and not row['previewEligible'] for row in native['cropCaptureSamples'])
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in ['cropActualRootPopupDialogInOnePlane','cropNegativeOriginRetainsEntireNativeModal','cropNativeModalGenuinelyOutsideMonitor','cropFullyOffscreenNativeModalRetainsPixels','allOriginal1524OrderedAssertionsRetained'])
for p in [planner,model,fd,coreReport,pluginReport,nativePath]:
 d=json.loads(p.read_text())
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
pre=json.loads((nativePath.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
roots=[REPO/f'implementation/warlock-family-crop-plan-v{i}' for i in [1,2]]+[REPO/f'implementation/warlock-family-crop-model-v{i}' for i in [1,2,3,4]]+[core]+[REPO/f'implementation/warlock-family-crop-capture-v{i}' for i in [1,2,3]]+[REPO/f'implementation/warlock-family-crop-fd-qualification-v{i}' for i in [1,2]]+[nativePath.parents[2]]
components=[]
for root in roots:
 target=root/'component-manifest.json'
 if target.exists():
  data=json.loads(target.read_text());assert data['sourceHeld'] and data['evidenceIntegrityPassed']
  for rel,row in data['files'].items():assert sha(root/rel)==row['sha256'],rel
 else:
  files={};links={}
  for p in sorted(root.rglob('*')):
   rel=str(p.relative_to(root))
   if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
   if p.is_symlink():
    assert rel.endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[rel]=str(p.readlink());continue
   if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  data={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'files':files,'localBuildLinks':links,'status':'retained-actual-evidence'}
  if root in [source,nativePath.parents[2]]:data.update(actualNativeFamilyCropQualified=True,nativeControls=len(native['checks']),retainedOriginalControls=1524,normalOwnedExits=len(native['ownedExitCodes']),cleanupPassed=True)
  target.write_text(json.dumps(data,indent=2)+'\n')
 components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(data['files'])})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeFamilyCropQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete native source/style/animation/fidelity and shared typed Elm family crop adoption plus original production preview13 and all coherent release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
