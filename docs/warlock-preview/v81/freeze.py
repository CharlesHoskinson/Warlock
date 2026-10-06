"""Freeze exact native successor GUI evidence and retain all original114 gates."""
import hashlib,json,pathlib,re,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-client-provider-native-v116';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
reports=list(root.glob('qa/native-*/report.json'));assert len(reports)==1;p=reports[0];d=json.loads(p.read_text())
assert d['passed'] and d['cleanupPassed'] and all(row['passed'] for row in d['checks']) and all(row['exitCode']==0 for row in d['ownedExitCodes'])
for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for name,h in pre['inputs'].items():assert sha(pathlib.Path(name))==h,name
old=json.loads(next((root.parent/'warlock-client-provider-native-v114').glob('qa/native-*/report.json')).read_text());assert old['passed'] and len(old['checks'])==2428
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
prior=stable(old['checks']);current=stable(d['checks']);names=set(prior);assert [name for name in current if name in names]==prior
proof=d['nextIntentGUIEvidence'];assert d['nativeNextUnissuedIntentGUIBoundedQualified'] and proof['exactACK'] and not proof['hardwarePresentation'] and not proof['assistiveTechnologyAcceptance']
job=proof['offer']['job'];seed=proof['seed'];assert job['request']=='1' and job['origin']==seed['lease'] and int(job['deadline'])==int(seed['source']['scope']['now'])+2000000000 and int(job['deadline'])>int(proof['previousCutoff'])
uri='elm-shell://preview/'+proof['offer']['handle'];assert any(row['uri']==uri and row['complete'] and row['naturalWidth']>0 and row['naturalHeight']>0 for row in proof['images'])
log=p.parent/'private-evidence/full-imported-feedback.log';text=log.read_text();prefix='native-imported-ownership: ';rows=[json.loads(line[len(prefix):]) for line in text.splitlines() if line.startswith(prefix)]
assert rows and all(row['records']==0 and int(row['charge'])==0 and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending'] for row in rows[-1])
assert any(row['job']==job for row in rows[-1]) and 'shared-host-exit: failure=0 rendered=1' in text
required=['nextIntentActualPointerNormalExit-close','nextIntentActualPointerNormalExit-reopen','nextIntentGUIFirstThirdJobWithLaterPickerLease','nextIntentGUIOriginalTwoSecondSuccessorCutoff','nextIntentGUIActualThirdOwnedURIComplete','nextIntentGUIExactSingleThirdCaptureAndTerminalACK','feedbackGUIFullHostNormalExit','allOriginal1783OrderedAssertionsRetained','allPriorNative105StableOrderedAssertionsRetained']
assert all(any(row['name']==name and row['passed'] for row in d['checks']) for name in required)
provider=r/'implementation/warlock-preview-provider-v80/component-manifest.json';gui=json.loads(provider.read_text());assert gui['passed'] and gui['sourceHeld']
for rel,row in gui['files'].items():assert sha(provider.parent/rel)==row['sha256'],rel
files={}
for f in sorted(root.rglob('*')):
 rel=f.relative_to(root)
 if '__pycache__' in rel.parts:continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
m=root/'component-manifest.json';assert not m.exists()
m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'files':files,'nativeReport':str(p),'nativeReportSHA256':sha(p),'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'prior114StableControls':len(prior),'nativeNextUnissuedIntentGUIBoundedQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
report={'passed':True,'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeManifest':str(m),'nativeManifestSHA256':sha(m),'nativeReport':str(p),'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'prior114StableControls':len(prior),'buildCommands':95,'nextIntentScenarios':10,'nextIntentTraces':22,'nextIntentStates':447,'unsafeMutantsDetected':2,'nativeCControls':45,'elmWireControls':21,'initialThirdAdmitted':bool(d['localFeedbackGUIEvidence']['thirdIssuedJobs']),'laterThirdAdmitted':True,'sameHostExpiryReopenImageACKQualified':True,'nativeAcceptance':False,'ordinaryEligibleCaptureAccepted':False,'assistiveTechnologyAcceptance':False,'fullReleaseAccepted':False,'next':'Commit/publish owned80/failed115/passed116 and receipts; explicit later unissued resume intents, proof-safe actor/history retirement, ordinary eligible capture and every original release gate remain.'}
(r/'docs/warlock-preview/v81/report.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS native116 ownABI/fullGUI80 PASS '+str(len(d['checks']))+'/'+str(len(d['ownedExitCodes']))+'normalclean; all'+str(len(prior))+'stable114 controls retained. Actual samehost nativeexpiry/pointerclose/reopen/thirdfirstjob/laterlease/native2s/ownedURI/exactACK/zero physicaljournalclosure. Failed115 selector andactualthird image preserved. Current80 full95/10/22/447/C45Elm21/originalallcomponentchecksheld. Commit/publish exactowner changes, then resumeintent succession/history longevity/ordinaryeligiblesources andalloriginalreleasegates. No fullreleaseclaim.'],'progress',[str(m.relative_to(r)),'docs/warlock-preview/v81/report.json']))
