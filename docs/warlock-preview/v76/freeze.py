"""Freeze actual native109, verifying unchanged108 stable control identities."""
import hashlib,json,pathlib,re,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-client-provider-native-v109';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=next(root.glob('qa/native-*/report.json'));d=json.loads(path.read_text());assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==2419 and len(d['ownedExitCodes'])==270 and all(row['passed'] for row in d['checks']) and all(row['exitCode']==0 for row in d['ownedExitCodes'])
for name,value in d['artifacts'].items():assert sha(path.parent/name)==value,name
pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for name,value in pre['inputs'].items():assert sha(pathlib.Path(name))==value,name
oldPath=next((root.parent/'warlock-client-provider-native-v108').glob('qa/native-*/report.json'));old=json.loads(oldPath.read_text());assert old['passed'] and len(old['checks'])==2416
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
prior=stable(old['checks']);current=stable(d['checks']);names=set(prior);assert [name for name in current if name in names]==prior
proof=d['dynamicEnrollmentNativeEvidence']['proof'];assert proof['checks']==125 and proof['resumeDeadlineRetained'] and proof['receiverResumeGuard'] and proof['empty'] and not proof['previewEligible'] and not proof['hardwarePresentation']
assert all(any(row['name']==name and row['passed'] for row in d['checks']) for name in ['dynamicResumeActualOriginalCapacityCutoffAndReceiverQueryGuard','dynamicResumeActualMappedPixelsExcludeOtherOriginalSources','allOriginal1783OrderedAssertionsRetained','allPriorNative105StableOrderedAssertionsRetained'])
provider=r/'implementation/warlock-preview-provider-v71/component-manifest.json';gui=json.loads(provider.read_text());assert gui['passed'] and not gui['nativeAcceptance']
for name,row in gui['files'].items():assert sha(provider.parent/name)==row['sha256'],name
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if '__pycache__' in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
m=root/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':True,'files':files,'nativeReport':str(path),'nativeReportSHA256':sha(path),'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeChecks':2419,'normalOwnedExits':270,'original108StableControls':len(prior),'nativeResumeCBoundedQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
report=r/'docs/warlock-preview/v76/report.json';report.write_text(json.dumps({'passed':True,'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeManifest':str(m),'nativeManifestSHA256':sha(m),'nativeReport':str(path),'nativeChecks':2419,'normalOwnedExits':270,'dynamicNativeControls':125,'prior108StableControls':len(prior),'readonlyPollingNames':sorted(readonly),'nativeAddressSuffixNormalizedOnlyForComparison':True,'buildCommands':94,'resumeCControls':79,'resumeElmControls':17,'resumeModelStates':584,'receiptModelStates':214,'receiptModelScenarios':8,'receiptActualUnsafeCounterexamplesDetected':2,'nativeResumeCBoundedQualified':True,'ordinaryEligibleCaptureAccepted':False,'originalS09Accepted':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Publish exact owned qualified work, integrate typed local feedback and distinct later unissued intent/history retirement, then ordinary eligible sources/full original release gates.'},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS native109 terminal0 PASS2419/270normalclean/dynamic125 originalresumeCcutoff after actualcapacity/physicalFD/GIO/backenddrain+exactACK, separategreenPNG, epochrefusal beforequery. Exact108 stableorderedidentities retained with unchangedcomparator plusold1783/105. GUI71 full94/C79/Elm17/receipt8/214states2unsafeoldcounterexamples/currentmetadata/catalog, native resume584retained69. Sourcecommit65302 stillliveatcheckpoint; pollsamehandle, thencommitnative109/docs76andpublish55. AlloriginalfullS09/S01-S16/restore38/recovery34/case34/two-second/cursor/drag52/input/hardware/ATIME/resource/journey/deploymentgatesremainactive. No externalblocker.'],'progress',[str(m.relative_to(r)),str(report.relative_to(r))]);print(json.dumps({'passed':True,'manifest':str(m),'files':len(files),'priorStableControls':len(prior),'checkpoint':str(e)}))
