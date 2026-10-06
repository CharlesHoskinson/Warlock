import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,(root,pattern);return rows[0]
def artifacts(reportPath):
 report=json.loads(reportPath.read_text())
 for rel,h in report.get('artifacts',{}).items():assert sha(reportPath.parent/rel)==h,rel
 return report
coreRoot=REPO/'implementation/warlock-core-family-crop-v2';coreManifest=coreRoot/'component-manifest.json';coreHeld=json.loads(coreManifest.read_text());assert coreHeld['sourceHeld'] and coreHeld['evidenceIntegrityPassed']
for rel,row in coreHeld['files'].items():assert sha(coreRoot/rel)==row['sha256'] and (coreRoot/rel).stat().st_size==row['size'],rel
corePath=pathlib.Path(coreHeld['buildReport']);assert sha(corePath)==coreHeld['buildReportSHA256'];core=artifacts(corePath);assert core['passed'] and set(core['rebuiltArchiveMembers'])=={'Renderer.cpp.o','OpenGL.cpp.o'} and core['unchangedArchiveMembers']==431 and core['existingObjectLayoutsUnchanged']
for section in ['dependencies','linkDependencies','linkedLibraries','tools']:
 for path,h in core[section].items():assert sha(path)==h,path
source=REPO/'implementation/warlock-family-style-crop-capture-v2';descriptor=source/'native-build-report.json';pair=json.loads(descriptor.read_text());assert pair['result']=='pass' and sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256'] and sha(coreManifest)==pair['coreComponentManifestSHA256'];buildPath=pathlib.Path(pair['pluginBuildReport']);assert sha(buildPath)==pair['pluginBuildReportSHA256'];build=artifacts(buildPath);assert build['passed'] and not build['missingSymbols']
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for section in ['dependencies','linkedLibraries','tools']:
 for path,h in build[section].items():assert sha(path)==h,path
nativeRoot=REPO/'implementation/warlock-client-provider-native-v50';nativePath=only(nativeRoot,'qa/native-*/report.json');native=artifacts(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
oldPath=REPO/'implementation/warlock-client-provider-native-v45/qa/native-1791264757369168051/report.json';old=json.loads(oldPath.read_text());names=[row['name'] for row in old['checks']];assert len(names)==1756 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['familyHistoricalFreshActualReadonlyScopeAfterMinimize','familyHistoricalActualSharedElmLabel','familyHistoricalOriginalOwnershipAndNoRecapture','familyHistoricalMinimizedNewCaptureRefused','familyHistoricalOriginalExpiryNoRenewal','familyHistoricalPhysicalRetirementBeforeExactACK','familyHistoricalRestoreSameNativeWorkspace','allOriginal1756OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
history=native['familyHistoricalEvidence'];assert not history['previewEligible'] and not history['hardwarePresentation'] and not history['stoppedSource']['source']['scope']['sourceLive'] and history['stoppedSource']['source']['scope']['present'] and int(history['stoppedSource']['lease'])>int(history['firstSource']['lease']) and history['frame']['fidelity']=='family' and history['captureRefusal']['reason']=='preview-probe-source-unavailable'
pre=json.loads((nativeRoot/'qa/preflight.json').read_text());assert pre['passed'] and pre['pair']==native['pair']
for path,h in pre['inputs'].items():assert sha(path)==h,path
failedRoot=REPO/'implementation/warlock-client-provider-native-v46';failedPath=only(failedRoot,'qa/native-*/report.json');failed=artifacts(failedPath);assert not failed['passed'] and failed['cleanupPassed'] and any(row['name']=='familyHistoricalMinimizeExactCommittedNativeEffect' and not row['passed'] and row['outcome']['reason']=='seat-grab' for row in failed['checks'])
gtkFailedRoot=REPO/'implementation/warlock-client-provider-native-v48';gtkFailedPath=only(gtkFailedRoot,'qa/native-*/report.json');gtkFailed=artifacts(gtkFailedPath);assert not gtkFailed['passed'] and gtkFailed['cleanupPassed'] and any(row['name']=='familyHistoricalMinimizeExactCommittedNativeEffect' and not row['passed'] and row['outcome']['reason']=='seat-grab' for row in gtkFailed['checks'])
cleanupFailedRoot=REPO/'implementation/warlock-client-provider-native-v49';cleanupFailedPath=only(cleanupFailedRoot,'qa/native-*/report.json');cleanupFailed=artifacts(cleanupFailedPath);assert not cleanupFailed['passed'] and cleanupFailed['cleanupPassed'] and not any(not row['passed'] for row in cleanupFailed['checks']) and 'missing-popup' in cleanupFailed['traceback'] and 'familyHistoricalEvidence' in cleanupFailed
reviewRoot=REPO/'implementation/warlock-client-provider-native-v47';review=json.loads((reviewRoot/'SOURCE-REVIEW.json').read_text());assert not review['nativeLaunched'] and not review['acceptedForNativeLaunch'] and review['preparePassed']
for root in [failedRoot,reviewRoot,gtkFailedRoot,cleanupFailedRoot]:
 retainedPre=json.loads((root/'qa/preflight.json').read_text())
 for path,h in retainedPre['inputs'].items():assert sha(path)==h,path
components=[{'path':str(coreManifest.relative_to(REPO)),'sha256':sha(coreManifest),'files':len(coreHeld['files'])}]
for root in [source,nativeRoot,failedRoot,reviewRoot,gtkFailedRoot,cleanupFailedRoot]:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
  if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[str(rel)]=str(p.readlink());continue
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'actualHistoricalFamilyQualified':root in [source,nativeRoot],'completeFamilyFidelityQualified':False,'nativeControls':len(native['checks']),'retainedOriginalControls':1756,'normalOwnedExits':len(native['ownedExitCodes']),'cleanupPassed':True}
 if root in [failedRoot,gtkFailedRoot,cleanupFailedRoot]:
  own=failed if root==failedRoot else gtkFailed if root==gtkFailedRoot else cleanupFailed
  metadata.update(nativeControls=len(own['checks']),normalOwnedExits=sum(row['exitCode']==0 for row in own['ownedExitCodes']),cleanupPassed=own['cleanupPassed'])
 if root==reviewRoot:
  for key in ['nativeControls','retainedOriginalControls','normalOwnedExits','cleanupPassed']:metadata.pop(key,None)
 if root==failedRoot:metadata.update(nativeCampaignPassed=False,normalExitAcceptance=False,failure='Actual fixture popup held seat grab; native minimize correctly refused. Fresh48 requires native popup dismissal first, original guards/deadlines intact.')
 if root==gtkFailedRoot:metadata.update(nativeCampaignPassed=False,normalExitAcceptance=False,failure='Actual GTK picker grab protects focused family even after native fixture popup dismissal. Fresh49 closes actual picker before committed minimize and reopens retained historical frame; native guard unchanged.')
 if root==cleanupFailedRoot:metadata.update(nativeCampaignPassed=False,normalExitAcceptance=False,failure='Actual historical source, retained URI/job/expiry, physical retirement ACK and restore passed; duplicated popup cleanup correctly refused missing-popup. Fresh50 removes only already-dismissed cleanup call.')
 if root==reviewRoot:metadata.update(nativeLaunched=False,acceptedForNativeLaunch=False,prelaunchSourceReview='Incorrect new fixture field caught before launch, fresh48 uses actual event/barrier.')
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [corePath,buildPath,oldPath,failedPath,gtkFailedPath,cleanupFailedPath,nativePath]},'nativeControls':len(native['checks']),'retainedOriginalControls':1756,'normalOwnedExits':len(native['ownedExitCodes']),'actualHistoricalFamilyQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete source/style/fidelity, original preview13, async hardware/output and coherent full release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
