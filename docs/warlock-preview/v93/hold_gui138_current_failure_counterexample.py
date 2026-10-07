"""Hold current failure qualification and separate mandatory drain counterexample."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v138';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [165,166,167,168]];native=[]
for root,count,exits,passed,runner in zip(roots,[29,22,36,21],[13,8,13,8],[True,True,True,False],['native138_controlled_curtain_runner.py','native166_current_failure_runner.py','native159_cancelled_reopened_snapshot_runner.py','native168_current_failure_drain_runner.py']):
 p=next(root.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(root/'qa/preflight.json');assert d['passed']==passed and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits
 assert all(c['exitCode']==(1 if root in [roots[1],roots[3]] and c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
 if passed:assert all(c['passed'] for c in d['checks'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner);native.append((p,d,pre))
np,n,npre=native[0];cp,current,cpre=native[1];op,old,opre=native[2];fp,fault,fpre=native[3]
assert all(d['pair']==n['pair'] and pre['controlledHostBuild']==npre['controlledHostBuild'] for _,d,pre in native)
assert current['actualCurrentMatchingErrorNativeQualified'] and current['actualCurrentCancellationConsumedOnce'] and current['expectedFailureExitCode']==1 and not current['normalControlledHostClosureQualified'] and not current['gracefulCurrentFailureDrainQualified']
assert old['actualCancelledOldResultQualified'] and old['actualReopenedWebKitPixels']['red']==19200 and old['actualReopenedClosedCurtainRegionPixels']['red']==0 and old['actualReopenedNativePaint']['opacity']==0
checks={c['name']:c for c in fault['checks']};assert [c['name'] for c in fault['checks'] if not c['passed']]==['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']
assert checks['controlledCurrentCancellationMatchesOriginalScopeGuard']['passed'] and checks['controlledCurrentFailureRetainsOriginalFailureExit']['passed'] and checks['controlledCurrentFailureNeverAcceptsSnapshotArtifact']['passed']
state=checks['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']['state'];assert state['privatePolicy']['models'] and not state['privatePolicy']['realm']['closed']
log=fp.parent/'private-evidence/controlled-host.log';text=log.read_text();assert 'Controlled native teardown incomplete: Original policy/input/ticket/physical/journal/confirmation custody prevents realm retirement' in text and 'controlled-native-realm-retired:' not in text
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
parent=r/'implementation/warlock-preview-provider-v137';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and held['passed'] and held['actualCancelledOldResultQualified']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets','spec','qa']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name!='shared-host.c':assert sha(gui/base/p.name)==sha(p),p
model=next(parent.glob('qa/async-error-scope-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==10 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
artifacts(model,q);assert sha(q['quint']['path'])==q['quint']['sha256']
coupling=next((r/'docs/warlock-preview/v93').glob('current-error-scope-coupling-v138-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==4
for n,h in c['inputs'].items():assert sha(n)==h,n
artifacts(coupling,c);assert sha(c['quint']['path'])==c['quint']['sha256']
scope='GUI138 adds disabled-by-default explicit current-snapshot real GCancellable/WebKit cancellation, with old-result retention disabled and readonly observation after existing matching-scope guard. Actual Native16622-control negative qualifies real image0/G_IO_ERROR_CANCELLED in original current view/epoch1/navigation/projection, original finish once/current failure branch exactly once, host1/no snapshot artifact; strict teardown refuses current accepted/known original duties, seven other owned processes normal/private cleanup. This is fail-closed/strict-refusal evidence, NOT normal exit, graceful failure drain or custody persistence after process death. Separately Native168 original same real current-error admission/result/failure/artifact controls fails mandatory drain oracle: current realm not closed/models still retained, no strict realm retirement and incomplete native teardown, original host1/seven normal/private cleanup. Fault teardown GLib/GObject criticals are retained evidence, not healthy release behavior. Unchanged normal16529/13 and canceled-old16736/13 positive regressions/full119 pass. Original single Elm policy/native issuer/physical products/sticky producer/scope guard/error reporting/deadlines unchanged; four current native outcomes coupled to explicit Quint cases pass, unchanged abstract Quint10/200 retained by exact source hash without rerun. Source held unqualified for mandatory failure drain. Next fresh139 actual failure quarantine/conceal/continued original native observations/receipts to strict close before failure exit1, with unchanged168 drain oracle and separate normal/old-result regressions; no false success/reset/Unknown settlement. All physical reveal/hardware/pressure/recovery/full S09/full release gates remain; installed drafts foreign preserved.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',np),('currentFailureNegativeNative',cp),('cancelledOldResultNative',op),('currentFailureDrainCounterexampleNative',fp),('retainedAsyncErrorScopeQuint',model),('currentErrorScopeCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':119,'actualCurrentMatchingErrorNativeQualified':True,'actualCurrentCancellationConsumedOnce':True,'actualCurrentFailureStrictTeardownRefusalObserved':True,'currentFailureNegativeControls':22,'currentFailureExpectedExitCode':1,'currentFailureOtherNormalOwnedExits':7,'actualCurrentFailureDrainCounterexample':True,'gracefulCurrentFailureDrainQualified':False,'currentFailureGLibCriticalsObserved':'GLib-GObject-CRITICAL' in text,'normalControlledHostClosureQualified':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'actualCancelledOldResultQualified':True,'cancelledOldResultNativeChecks':36,'cancelledOldResultNormalOwnedExits':13,'retainedAsyncErrorScopeQuintScenarios':10,'retainedAsyncErrorScopeInvariantSamples':200,'currentErrorScopeCoupledCases':4,'singlePreviewPolicy':True,'nativeGrantResets':0,'privateSessionCleanupPassed':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root in [gui,*roots]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root in roots:
  idx=roots.index(root);own.update(passed=idx!=3,scope=native[idx][1]['scope'],nativeChecks=[29,22,36,21][idx],normalOwnedExits=[13,7,13,7][idx],expectedFailedOwnedExits=1 if idx in [1,3] else 0,normalControlledHostClosureQualified=idx in [0,2],actualCurrentMatchingErrorNativeQualified=idx==1,actualCurrentCancellationConsumedOnce=idx in [1,3],actualCurrentFailureDrainCounterexample=idx==3,actualCancelledOldResultQualified=idx==2)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report-gui138-current-failure.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI138 actual current real cancellation reaches original failure1/strict custody refusal: Native16622 negative controls/seven other normal/cleanup; normal16529/13/old-canceled16736/13/full119/4 actual Quint cases pass, unchanged model10/200 retained. Separate Native16821 check fails mandatory strict drain-before-failure-exit with actual current duties/not-closed/incomplete teardown. Source held unqualified for failure drain/GLib criticals retained. Next PUBLIC101 then fresh139 failure quarantine/continued original native drain to strict close before failure1 exit using unchanged168 oracle; full release/physical/recovery/workload gates remain/installed drafts foreign preserved.'],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in [gui,*roots]]+[str(out.relative_to(r))]))
