"""Hold actual reload failure and original normal control before repair."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v140'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(pathlib.Path(p).read_text())
out=pathlib.Path(__file__).with_name('component-report-gui140-renderer-reload.json');assert not out.exists()
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [175,176]]
reports={};build=None
for root,count,runner in zip(roots,[29,18],['native138_controlled_curtain_runner.py','native176_renderer_reload_runner.py']):
 ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];d=load(p);pre=load(root/'qa/preflight.json')
 assert len(d['checks'])==count and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 if root==roots[0]:assert d['passed'] and len(d['ownedExitCodes'])==13 and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 else:
  assert not d['passed'] and len(d['ownedExitCodes'])==8
  assert [c['name'] for c in d['checks'] if not c['passed']]==['controlledReloadDoesNotFailTheOriginalHost']
  assert all(c['exitCode']==(1 if c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
  log=(p.parent/'private-evidence/controlled-host.log').read_text()
  assert 'actualWebKitReload=1 snapshotWritten=1 inferredSettlement=0' in log and 'navigation=2 initialized=1 sameView=1 actualLoadStarted=1 uri=elm-shell://app/controlled-popup.html' in log
  assert 'Renderer navigation retains original live policy; reload recovery not qualified' in log and 'Controlled native teardown incomplete:' in log and 'shared-host-exit: failure=1 rendered=1' in log
  assert 'controlled-renderer-context-replaced:' not in log
  pixels=next(c['pixels'] for c in d['checks'] if c['name']=='controlledBeforeReloadActualSourcePixels');assert pixels['red']==19200 and pixels['green']==pixels['blue']==0
 candidate=pathlib.Path(pre['controlledHostBuild']);assert build is None or candidate==build;build=candidate
 reports[root.name]={'path':str(p),'sha256':sha(p),'checks':count,'passed':d['passed']}
b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for n,row in b[category].items():assert sha(n)==row['sha256'],n
reports['build']={'path':str(build),'sha256':sha(build),'passed':True}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':119,'actualRendererReloadCounterexample':True,'actualReloadRequestAndLoadStarted':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'reloadFailureReachedChecks':18,'reloadFailureExpectedHostExitCode':1,'reloadFailureOtherNormalOwnedExits':7,'privateSessionCleanupPassed':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'reloadRecoveryQualified':False,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'reports':reports,'scope':'GUI140 retains original reload-as-uncertain failure and adds explicit private actual WebKit reload only after first original current snapshot/write. Normal175 unchanged29/13 and full119 pass. Actual reload176 reaches18 checks: original GTK/DOM/native issuance/first source red19200 and actual original-view LOAD_STARTED navigation1->2 pass; host continuity fails with original failure1/uncertain incomplete teardown/no replacement. Seven other normal owned exits/private cleanup pass. Failure retained, not normal closure or reload acceptance. Original Native issuer, Elm policy, physical custody, counters, grant and observer6 deadline unchanged. Next fresh141 known same-URI quarantine/strict original drain before fixed-grant replacement in same popup with later epoch and original policy. Uncertain/arbitrary/process/physical/hardware/full S09/release remain open.'}
for root in [gui,*roots]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root==roots[0]:own.update(passed=True,normalControlledHostClosureQualified=True,nativeChecks=29,actualRendererReloadCounterexample=False)
 if root==roots[1]:own.update(nativeChecks=18,normalControlledHostClosureQualified=False)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),[common['scope']],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in [gui,*roots]]+[str(out.relative_to(r))]))
