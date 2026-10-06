"""Verify retained failures, own source, native tuple and bounded growth evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def hold(root):
 manifest=root/'component-manifest.json'
 if not manifest.exists():
  files={}
  for p in sorted(root.rglob('*')):
   rel=p.relative_to(root)
   if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
   assert not p.is_symlink(),p
   if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 data=json.loads(manifest.read_text());assert data.get('passed') or (data.get('sourceHeld') and data.get('evidenceIntegrityPassed'))
 for rel,row in data['files'].items():assert sha(root/rel)==row['sha256'] and (root/rel).stat().st_size==row['size'],rel
 return {'path':str(manifest.relative_to(REPO)),'sha256':sha(manifest),'files':len(data['files'])}
def proof(path,root=None):
 data=json.loads(path.read_text())
 for rel,h in data.get('inputs',{}).items():
  p=pathlib.Path(rel);p=p if p.is_absolute() else root/p;assert sha(p)==h,(path,p)
 for rel,h in data.get('artifacts',{}).items():assert sha(path.parent/rel)==h,(path,rel)
 return data
held=[]
for version in [57,58,59]:
 root=REPO/('implementation/warlock-preview-provider-v'+str(version));assert not json.loads((root/'component-manifest.json').read_text())['passed'];held.append(hold(root))
root=REPO/'implementation/warlock-preview-provider-v60';manifest=json.loads((root/'component-manifest.json').read_text());build=proof(pathlib.Path(manifest['buildReport']),root);assert build['passed'] and len(build['commands'])==90
for key,names,traces,states in [('modelReport',10,22,564),('metadataModelReport',8,16,210),('catalogModelReport',8,16,214),('deliveryModelReport',6,16,388)]:
 data=proof(pathlib.Path(manifest[key]),root);assert data['passed'] and data['namedScenarios']==names and len(data['coupledTraces'])==traces and sum(x['statesCompared'] for x in data['coupledTraces'])==states
 if key=='deliveryModelReport':assert data['unsafeMutantsDetected']==2 and data['invariantSamples']==150
held.append(hold(root))
for version in [102,103]:
 root=REPO/('implementation/warlock-client-provider-native-v'+str(version));assert not list(root.glob('qa/native-*'));held.append(hold(root))
root=REPO/'implementation/warlock-client-provider-native-v104';failedPath=next(root.glob('qa/native-*/report.json'));failure=proof(failedPath);assert not failure['passed'] and failure['cleanupPassed'] and len(failure['checks'])==929 and len(failure['ownedExitCodes'])==109 and all(row['exitCode']==0 for row in failure['ownedExitCodes']) and [row['name'] for row in failure['checks'] if not row['passed']]==['receiverGrowthActualThirdPixelsAfterRealCapacity'];held.append(hold(root))
root=REPO/'implementation/warlock-client-provider-native-v105';reports=list(root.glob('qa/native-*/report.json'));assert len(reports)==1;nativePath=reports[0];native=proof(nativePath)
assert native['passed'] and native['cleanupPassed'] and native['nativeReceiverJournalGrowthBoundedQualified'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
for name in ['allOriginal1783OrderedAssertionsRetained','allPriorNative101StableOrderedAssertionsRetained','receiverGrowthActualOwnCJournalAndPhysicalDrain','receiverGrowthActualFirstPixelsExcludePeer','receiverGrowthActualSecondPixelsExcludeOriginal','receiverGrowthActualThirdPixelsAfterRealCapacity','receiverGrowthNewPhysicalRetirementRetainsOldJob']:
 assert any(row['name']==name and row['passed'] for row in native['checks']),name
growth=native['receiverGrowthNativeEvidence']['proof'];assert growth['passed'] and growth['empty'] and growth['sameReceiverEpoch'] and growth['capacityWithoutJob'] and not growth['previewEligible']
preflight=proof(root/'qa/preflight.json');assert preflight['passed'] and preflight['sharedGeneratedProviderManifest']==str(REPO/'implementation/warlock-preview-provider-v60/component-manifest.json')
held.append(hold(root))
root=REPO/'openspec/changes/warlock-preview-receipt-membership';path=next(root.glob('qa/validate-*/report.json'));spec=proof(path);assert spec['passed'] and spec['frozenBaseline']==[242,417] and len(spec['requirements'])==3 and spec['originalS09ScenarioIds']==13;held.append(hold(root))
plan=json.loads((REPO/'docs/warlock-preview/v60/S09-EVIDENCE-PLAN.json').read_text());assert len(plan['scenarios'])==13 and all(row['status']=='partial-unaccepted' for row in plan['scenarios']) and not plan['S09Accepted']
report={'schema':1,'passed':True,'scope':scope,'components':held,'guiBuildCommands':90,'receiverPhysicalChecks':40,'receiptPhysicalChecks':49,'deliveryModelScenarios':6,'deliveryCoupledStates':388,'deliveryUnsafeMutantsDetected':2,'nativeReport':str(nativePath),'nativeReportSHA256':sha(nativePath),'nativeChecks':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'nativeReceiverJournalGrowthBoundedQualified':True,'originalS09Accepted':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Use the same growing receiver and original journal in typed ordinary multi-entry capture enrollment with one Elm policy and actual eligible source grants; close original S09 receipts/fidelity/native/hardware and all S01-S16/release gates without promoting historical previewEligible:false observations.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({key:value for key,value in report.items() if key not in ['components','next','scope']}))
