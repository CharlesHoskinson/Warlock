import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 files=list(root.glob(pattern));assert len(files)==1,(root,pattern);return files[0]
def verify(path):
 j=json.loads(path.read_text())
 for rel,h in j.get('artifacts',{}).items():assert sha(path.parent/rel)==h,rel
 return j
priorPath=REPO/'docs/warlock-preview/v39/report.json';prior=json.loads(priorPath.read_text());assert prior['passed'] and prior['actualNativeConfigurationFreshnessQualified']
for row in prior['components']:
 path=REPO/row['path'];assert sha(path)==row['sha256'];j=json.loads(path.read_text())
 for rel,item in j['files'].items():assert sha(path.parent/rel)==item['sha256'],rel
nativeRoot=REPO/'implementation/warlock-client-provider-native-v57';nativePath=only(nativeRoot,'qa/native-*/report.json');native=verify(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath);names=[r['name'] for r in original['checks']];assert len(names)==1783 and [r['name'] for r in native['checks'] if r['name'] in set(names)]==names
required=['familyConfigurationOriginalNativeScopeJobAndReadiness','familyConfigurationNativeLiveSourceHasNewContentEpoch','familyConfigurationActualSharedElmHistoricalLabelWithLiveSource','familyConfigurationOriginalURIAndDimensionsAfterNewSourceEpoch','familyConfigurationOneOriginalCaptureNoRenewalOrResume','familyConfigurationOriginalImageExpiry','familyConfigurationPhysicalRetirementBeforeExactACK','familyConfigurationHostNormalExit','allOriginal1783OrderedAssertionsRetained','configStyleChangedNativePixelsRequireNewStyleEpoch']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
proof=native['familyConfigurationHistoricalEvidence'];a=proof['initialSource'];b=proof['changedLiveSource'];frame=proof['frame'];assert a['source']['scope']['sourceLive'] and b['source']['scope']['sourceLive'] and a['source']['scope']['present'] and b['source']['scope']['present'] and a['source']['binding']==b['source']['binding'] and int(b['lease'])>int(a['lease']) and int(b['source']['scope']['context']['content'])>int(frame['job']['context']['content']) and frame['job']['context']==a['source']['scope']['context'] and not proof['previewEligible'] and not proof['hardwarePresentation']
assert proof['acks']==[{'kind':'acknowledge','job':frame['job'],'sequence':'3'}]
failedRoot=REPO/'implementation/warlock-client-provider-native-v56';failedPath=only(failedRoot,'qa/native-*/report.json');failed=verify(failedPath);assert not failed['passed'] and failed['cleanupPassed'] and 'familyConfigurationHistoricalEvidence' in failed and all(row['exitCode']==0 for row in failed['ownedExitCodes']) and any(row['name']=='allOriginal1739OrderedAssertionsRetained' and not row['passed'] for row in failed['checks'])
components=[]
for root in [failedRoot,nativeRoot]:
 pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
 target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file():files[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':{},'actualLiveSourceHistoricalFamilyQualified':root==nativeRoot,'nativeCampaignPassed':root==nativeRoot,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False},indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [priorPath,originalPath,failedPath,nativePath]},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'normalOwnedExits':len(native['ownedExitCodes']),'actualLiveSourceHistoricalFamilyQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Qualify remaining real renderer style/config/fidelity including glow/blur, shader and transforms; continue original preview13/hardware/output/restore38/recovery34/drag52 and coherent full release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
