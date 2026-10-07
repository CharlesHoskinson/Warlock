"""Hold bounded one-policy C/JSC reuse and unchanged actual host regression."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v130'
normal=r/'implementation/warlock-client-provider-native-v142';late=r/'implementation/warlock-client-provider-native-v143'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
def native(root,count,exits):
 rows=list(root.glob('qa/native-controlled-*/report.json'));assert len(rows)==1;p=rows[0];d=load(p)
 assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 assert len(d['checks'])==count and len(d['ownedExitCodes'])==exits
 assert all(x['passed'] for x in d['checks']) and all(x['exitCode']==0 for x in d['ownedExitCodes'])
 pre=load(root/'qa/preflight.json')
 for name,h in pre['inputs'].items():assert sha(name)==h,name
 artifacts(p,d);return p,d,pre
np,n,npre=native(normal,29,13);lp,l,lpre=native(late,18,8)
assert n['pair']==l['pair'] and npre['controlledHostBuild']==lpre['controlledHostBuild']
assert n['actualCapturedPixelsQualified'] and n['actualScopedURIImageLoadObserved']
assert n['actualOffscreenWebKitPixels']['red']==19200 and n['actualClosedCurtainRegionPixels']['red']==0 and n['actualNativeGTKPaintObservation']['opacity']==0
for k in ['actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert l[k],k
for d in [n,l]:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
assert sha(normal/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93/native138_controlled_curtain_runner.py')
assert sha(late/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93/native141_delayed_snapshot_runner.py')
build=pathlib.Path(npre['controlledHostBuild']);b=load(build)
assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for name,h in b['inputs'].items():assert sha(gui/name)==h,name
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
positive=gui/'qa/policy-driver-positive-check-1791388484302066275/report.json';pd=load(positive);assert pd['passed'] and pd['evidence']['checks']==2261 and pd['evidence']['preGrantFaultChecks']==9
for name,h in pd['inputs'].items():assert sha(gui/name)==h,name
artifacts(positive,pd)
reuse=gui/'qa/policy-driver-realm-reuse-check-v5-1791388803876321382/report.json';rd=load(reuse);assert rd['passed'] and rd['evidence']['checks']==143
for k in ['originalPolicyPointerPreserved','originalBindingPreserved','permanentRetiredSubjectCannotResurrect','normalOwnedExit','normalOwnedPeerExit']:assert rd['evidence'][k],k
assert rd['evidence']['nativePolicyInstances']==1 and rd['evidence']['nativeTransportInstances']==2 and rd['evidence']['nativeGrantResets']==0
artifacts(reuse,rd)
compiled=pathlib.Path(rd['priorReport']['path']);cd=load(compiled);assert sha(compiled)==rd['priorReport']['sha256'] and not cd['passed']
assert any(x['name']=='compile-owner' and x['exitCode']==0 for x in cd['commands'])
for name,h in cd['inputs'].items():assert sha(gui/name)==h,name
artifacts(compiled,cd)
model=gui/'qa/policy-realm-reuse-model-v3-1791388629094979843/report.json';md=load(model);assert md['passed'] and md['namedScenarios']==8 and md['invariantSamples']==200
for name,h in md['inputs'].items():assert sha(gui/name)==h,name
artifacts(model,md);assert sha(md['quint']['path'])==md['quint']['sha256']
coupling=gui/'qa/policy-realm-reuse-coupling-1791388999135608451/report.json';qd=load(coupling);assert qd['passed'] and qd['observedStates']==11 and qd['coupledQuintChecks']==6
for name,h in qd['inputs'].items():assert sha(name)==h,name
artifacts(coupling,qd)
parent=r/'implementation/warlock-preview-provider-v129';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and held['passed']
for name,row in held['files'].items():assert sha(parent/name)==row['sha256'],name
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'preview-policy-driver.cpp','preview-policy-driver.h'}:assert sha(gui/base/p.name)==sha(p),p
scope='GUI130 adds strict original native realm retirement and later same-binding/empty-issued-namespace rebinding while transferring the exact same persistent Elm policy. Actual C/JSC143-check two-realm authenticated synthetic peer/sealed-FD trace preserves original binding/policy pointer, refuses open/early/stale/foreign/outbox failures, and rejects permanent Retired21 resurrection before capturing/draining Active22. Original popup quarantine/reconciliation precedes permanent retirement; direct-retirement fixture failure is retained, not qualified. Original2261 driver checks plus9 constructor faults, eight named Quint/200 samples and six custody-stage checks coupled to11 concrete observations pass. Current full119 and separate actual Native14229checks13normalexits plus delayedNative14318checks8normalexits pass with both private cleanups. Host does not yet activate new realm rebinding or replace the fixed-grant renderer context. Actual GUI close/reopen, broader stale callbacks, direct-retirement, reload/process/uncertain recovery, ongoing physical conceal/reveal/hardware, pressure/workload/RSS/full preview/release remain open. Safe opacity0, native issuer/Elm policy/physical product/original deadlines unchanged; no grant reset.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('controlledNative',np),('delayedSnapshotNative',lp),('originalDriver',positive),('realmReuseC',reuse),('realmReuseCompiledFixture',compiled),('realmReuseQuint',model),('realmReuseCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'cpuCPolicyRealmReuseQualified':True,'actualGUIRealmReopenQualified':False,'nativeRealmRebindingActivated':False,'permanentRetirementAfterQuarantineQualified':True,'directPermanentRetirementQualified':False,'singlePreviewPolicy':True,'nativeGrantResets':0,'originalDriverChecks':2261,'preGrantConstructorChecks':9,'realmReuseCChecks':143,'realmReuseQuintScenarios':8,'realmReuseInvariantSamples':200,'realmReuseConcreteObservedStates':11,'realmReuseCoupledQuintChecks':6,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationObserved':True,'actualCurrentProjectionDOMReceiptObserved':True,'compiledPageAssetClosureQualified':True,'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root in [gui,normal,late]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 manifest=root/'component-manifest.json';assert not manifest.exists()
 islate=root==late
 manifest.write_text(json.dumps(dict(common,files=files,nativeChecks=18 if islate else 29,normalOwnedExits=8 if islate else 13,actualCapturedPixelsQualified=not islate,actualScopedURIImageLoadObserved=not islate,actualNativeGTKPaintObservation=None if islate else n['actualNativeGTKPaintObservation'],actualClosedCurtainRegionPixels=None if islate else n['actualClosedCurtainRegionPixels']),indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report130.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI130 bounded single persistent policy C/JSC realm reuse:143 checks/two actual sealed-FD captures/normal original owner-peer close; original2261+9 constructor/current full119, Quint8named/200samples and six stages coupled to11 actual observations. Actual Native14229/13 and delayedNative14318/8 pass unchanged byte-identical oracles/private cleanups. Strict retire waits original policy/input/ticket/physical/journal/independent confirmation; later original same-binding epoch transfers exact same policy, preserving permanent retired21 chronology and active22 capture. Popup quarantine precedes permanent retirement; direct-retirement synthetic peer failure held/unqualified. Host fixed-grant renderer replacement and GUI close/reopen not yet wired/qualified; physical reveal/ongoing conceal/reload/process/uncertain recovery/workload/RSS/full release open. Next PUBLIC96 then fresh actual native host lifecycle integration; installed/drafts/foreign and accepted/failed sources untouched.'],'progress',[str((gui/'component-manifest.json').relative_to(r)),str((normal/'component-manifest.json').relative_to(r)),str((late/'component-manifest.json').relative_to(r)),str(out.relative_to(r))]))
