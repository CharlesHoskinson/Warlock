"""Freeze full native114 with every stable original109 assertion retained."""
import hashlib,json,pathlib,re,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-client-provider-native-v114';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
p=next(root.glob('qa/native-*/report.json'));d=json.loads(p.read_text());assert d['passed'] and d['cleanupPassed'] and all(row['passed'] for row in d['checks']) and all(row['exitCode']==0 for row in d['ownedExitCodes'])
for name,h in d['artifacts'].items():assert sha(p.parent/name)==h,name
pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for name,h in pre['inputs'].items():assert sha(pathlib.Path(name))==h,name
oldPath=next((root.parent/'warlock-client-provider-native-v109').glob('qa/native-*/report.json'));old=json.loads(oldPath.read_text());assert old['passed'] and len(old['checks'])==2419
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
prior=stable(old['checks']);current=stable(d['checks']);names=set(prior);assert [name for name in current if name in names]==prior
proof=d['localFeedbackGUIEvidence'];assert d['nativeLocalFeedbackGUIBoundedQualified'] and proof['waiting'] and all(v['deadline']==proof['originalCutoff'] for v in proof['nativeLocal']) and not proof['hardwarePresentation'] and not proof['assistiveTechnologyAcceptance']
assert proof['expired'] or proof['thirdIssuedJobs']
assert all(any(row['name']==name and row['passed'] for row in d['checks']) for name in ['feedbackGUIThreeSameAppCatalogSubjects','feedbackGUICapacityFromActualOwnNativeScope','feedbackGUIOnlyActualIssuedJobsCaptureAndSettle','feedbackGUIFullHostNormalExit','allOriginal1783OrderedAssertionsRetained','allPriorNative105StableOrderedAssertionsRetained'])
provider=r/'implementation/warlock-preview-provider-v76/component-manifest.json';gui=json.loads(provider.read_text());assert gui['passed']
for name,row in gui['files'].items():assert sha(provider.parent/name)==row['sha256'],name
files={}
for f in sorted(root.rglob('*')):
 rel=f.relative_to(root)
 if '__pycache__' in rel.parts:continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
m=root/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'files':files,'nativeReport':str(p),'nativeReportSHA256':sha(p),'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'prior109StableControls':len(prior),'nativeLocalFeedbackGUIBoundedQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
report=r/'docs/warlock-preview/v78/report.json';report.write_text(json.dumps({'passed':True,'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeManifest':str(m),'nativeManifestSHA256':sha(m),'nativeReport':str(p),'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'prior109StableControls':len(prior),'buildCommands':95,'feedbackScenarios':9,'feedbackStates':413,'feedbackControls':110,'legacyResumeControls':79,'nativeCapacityStatusShown':True,'nativeExpiryStatusShown':bool(proof['expired']),'nativeThirdAdmitted':bool(proof['thirdIssuedJobs']),'nativeAcceptance':False,'ordinaryEligibleCaptureAccepted':False,'assistiveTechnologyAcceptance':False,'fullReleaseAccepted':False,'next':'Publish exact owned feedback GUI/current native qualification; implement distinct later unissued intents and bounded history longevity, ordinary eligible sources and all original release gates.'},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS native114 fullcurrentGUI76 localfeedback PASS'+str(len(d['checks']))+'/'+str(len(d['ownedExitCodes']))+'normalclean withactual3sameapp native roots, currentElm capacity status/originalcutoff/onlyissuedCaptureACK/ownedURIload/normalphysicaljournalcleanup. Exact'+str(len(prior))+'stable109 identitiesandoriginal1783/prior105 preserved. Failed113outsidesamepickerfixture preserved. CurrentGUI76 full95/newfeedback9/413states110controls/legacy79 held; source commit3b808ec. Publish authorized exactowned work then next unmetfullgoal slice; original eligibility/S09/S01-S16/hardware/ATIME/resources/journeys/deployment remain open.'],'progress',[str(m.relative_to(r)),str(report.relative_to(r))]);print(json.dumps({'passed':True,'checks':len(d['checks']),'exits':len(d['ownedExitCodes']),'checkpoint':str(e)}))
