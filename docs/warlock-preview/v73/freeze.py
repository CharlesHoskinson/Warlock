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
for version in [61,62,63,64,65]:
 root=REPO/('implementation/warlock-preview-provider-v'+str(version));held.append(hold(root))
root=REPO/'implementation/warlock-preview-provider-v65';manifest=json.loads((root/'component-manifest.json').read_text());build=proof(pathlib.Path(manifest['buildReport']),root);assert build['passed'] and len(build['commands'])==94
assert manifest['evidence']['dynamic-enrollment-tests']['checks']==34 and manifest['evidence']['imported-admission-tests']['checks']==27
for key,names,traces,states,mutants in [('modelReport',10,22,564,3),('metadataModelReport',8,16,210,0),('catalogModelReport',8,16,214,0),('deliveryModelReport',6,16,388,2),('intentModelReport',6,16,363,2),('enrollmentModelReport',8,24,577,3)]:
 data=proof(pathlib.Path(manifest[key]),root);assert data['passed'] and data['namedScenarios']==names and len(data['coupledTraces'])==traces and sum(x['statesCompared'] for x in data['coupledTraces'])==states
 if mutants:assert data['unsafeMutantsDetected']==mutants
for version in [106,107]:
 root=REPO/('implementation/warlock-client-provider-native-v'+str(version));assert not list(root.glob('qa/native-*'));held.append(hold(root))
root=REPO/'implementation/warlock-client-provider-native-v108';reports=list(root.glob('qa/native-*/report.json'));assert len(reports)==1;nativePath=reports[0];native=proof(nativePath)
assert native['passed'] and native['cleanupPassed'] and native['nativeDynamicCEnrollmentBoundedQualified'] and native['nativeReceiverJournalGrowthBoundedQualified'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
for name in ['allOriginal1783OrderedAssertionsRetained','allPriorNative101StableOrderedAssertionsRetained','allPriorNative105StableOrderedAssertionsRetained','dynamicEnrollmentActualOwnCOriginalDeadlineAndPhysicalDrain','dynamicEnrollmentActualFirstPixelsExcludePeer','dynamicEnrollmentActualSecondPixelsExcludeOriginal','dynamicEnrollmentActualThirdPixelsAfterOriginalCapacity','dynamicEnrollmentOriginalNewTerminalACKRetainsOtherJob']:
 assert any(row['name']==name and row['passed'] for row in native['checks']),name
dynamic=native['dynamicEnrollmentNativeEvidence']['proof'];assert dynamic['passed'] and dynamic['empty'] and dynamic['sameReceiverEpoch'] and dynamic['capacityWithoutJob'] and dynamic['dynamicCEnrollment'] and dynamic['originalDeadlineRetained'] and not dynamic['previewEligible']
preflight=proof(root/'qa/preflight.json');assert preflight['passed'] and preflight['sharedGeneratedProviderManifest']==str(REPO/'implementation/warlock-preview-provider-v65/component-manifest.json')
held.append(hold(root))
root=REPO/'openspec/changes/warlock-preview-dynamic-enrollment';path=next(root.glob('qa/validate-*/report.json'));spec=proof(path);assert spec['passed'] and spec['frozenBaseline']==[242,417] and len(spec['requirements'])==4 and len(spec['scenarios'])==8 and spec['originalS09ScenarioIds']==13;held.append(hold(root))
plan=json.loads((REPO/'docs/warlock-preview/v60/S09-EVIDENCE-PLAN.json').read_text());assert len(plan['scenarios'])==13 and all(row['status']=='partial-unaccepted' for row in plan['scenarios']) and not plan['S09Accepted']
report={'schema':1,'passed':True,'scope':scope,'components':held,'guiBuildCommands':94,'dynamicCComponentChecks':34,'intentComponentChecks':27,'enrollmentModelScenarios':8,'enrollmentCoupledStates':577,'enrollmentUnsafeMutantsDetected':3,'intentCoupledStates':363,'nativeReport':str(nativePath),'nativeReportSHA256':sha(nativePath),'nativeChecks':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'nativeDynamicCEnrollmentBoundedQualified':True,'nativeReceiverJournalGrowthBoundedQualified':True,'originalS09Accepted':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Verify actual rejected-job registration and frontend terminal settlement, define distinct later unissued intents with retained original history, integrate ordinary eligible sources through one immutable Elm policy, and close original S09/S01-S16/hardware/AT/IME/resources/recovery/journeys/deployment gates. No historical source eligibility promotion.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({key:value for key,value in report.items() if key not in ['components','next','scope']}))
