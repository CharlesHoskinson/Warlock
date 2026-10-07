"""Hold actual shared-process strict-drain-before-recovery counterexample."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v142';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
out=pathlib.Path(__file__).with_name('component-report-gui142-process-failure.json');assert not out.exists()
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [185,186]];reports={};build=None
for root,runner in zip(roots,['native138_controlled_curtain_runner.py','native186_process_stop_drain_runner.py']):
 ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];d=load(p);pre=load(root/'qa/preflight.json');assert d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 if root==roots[0]:assert d['passed'] and len(d['checks'])==29 and len(d['ownedExitCodes'])==13 and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 else:
  assert not d['passed'] and len(d['checks'])==18 and len(d['ownedExitCodes'])==8
  assert [c['name'] for c in d['checks'] if not c['passed']]==['controlledSharedProcessNativeCustodyClosedBeforeGTKRecovery']
  assert all(c['exitCode']==(1 if c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
  log=(p.parent/'private-evidence/controlled-host.log').read_text();assert 'actualTerminateWebProcess=1 snapshotWritten=1 nativeSettlement=0' in log and 'currentView=1 reason=2 actualWebKitSignal=1 nativeSettlement=0' in log and 'Web process terminated: 2' in log and 'native-recovery-ready:' in log and 'Controlled native teardown incomplete:' in log and 'shared-host-exit: failure=1 rendered=1' in log
  assert 'controlled-native-realm-retired: epoch=1 ' not in log
  state=next(c['state'] for c in d['checks'] if c['name']=='controlledSharedProcessNativeCustodyClosedBeforeGTKRecovery');assert not state['privatePolicy']['realm']['closed'] and state['privatePolicy']['models']
  pixels=next(c['pixels'] for c in d['checks'] if c['name']=='controlledProcessActualOriginalSourcePixels');assert pixels['red']==19200 and pixels['green']==pixels['blue']==0
 candidate=pathlib.Path(pre['controlledHostBuild']);assert build is None or candidate==build;build=candidate
 reports[root.name]={'path':str(p),'sha256':sha(p),'checks':len(d['checks']),'ownedExits':len(d['ownedExitCodes']),'passed':d['passed']}
b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for n,row in b[category].items():assert sha(n)==row['sha256'],n
reports['build']={'path':str(build),'sha256':sha(build),'passed':True}
scope='GUI142 holds actual shared related WebKit terminate-process API after original first current captured snapshot. Original real termination reason2 and first source red19200/GTK/native original admission pass. Native18618 reached checks fails strict original native custody close BEFORE GTK recovery: last realm not closed/models remain, native-recovery-ready already shown, original final failure1/strict teardown refusal. Seven other normal owned exits/private cleanup. This is actual process failure evidence, not known-duty drain, process custody persistence, whole-host restart/durable Unknown/normal closure acceptance. Normal185 unchanged29/13/full119 pass separately. Original terminated/evaluate callbacks, main GTK unwind/recovery, Native issuer/Elm policy/strict physical/journal/confirmation/no-reset/no-replay/deadlines unchanged; QA API/signal observations never synthesize native settlement. Next fresh143 defers both actual termination and matching asynchronous delivery failure exits while original known native receipts drive strict close before GTK recovery. Uncertain/window-command/durable Unknown/whole-host restart/physical/hardware/full S09/release remain open.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':119,'actualSharedRendererProcessCounterexample':True,'actualTerminateProcessAPIAndSignalObserved':True,'processFailureReachedChecks':18,'processFailureExpectedHostExitCode':1,'processFailureOtherNormalOwnedExits':7,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'privateSessionCleanupPassed':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'actualKnownSharedProcessNativeDrainQualified':False,'wholeHostRestartQualified':False,'durableUnknownRecoveryQualified':False,'reloadRecoveryQualified':False,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'reports':reports,'scope':scope}
for root in [gui,*roots]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root==roots[0]:own.update(passed=True,nativeChecks=29,normalControlledHostClosureQualified=True,actualSharedRendererProcessCounterexample=False)
 if root==roots[1]:own.update(nativeChecks=18,normalControlledHostClosureQualified=False)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS '+scope],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in [gui,*roots]]+[str(out.relative_to(r))]))
