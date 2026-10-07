"""Freeze actual two-cycle normal GUI reopening, preserving separate fault scopes."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v132';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [144,145,146]];native=[]
for root,count,exits in zip(roots,[29,46,18],[13,18,8]):
 rows=list(root.glob('qa/native-controlled-*/report.json'));assert len(rows)==1;p=rows[0];d=load(p);pre=load(root/'qa/preflight.json');assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 assert len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);native.append((p,d,pre))
np,n,npre=native[0];rp,reopen,rpre=native[1];lp,late,lpre=native[2]
assert n['pair']==reopen['pair']==late['pair'] and npre['controlledHostBuild']==rpre['controlledHostBuild']==lpre['controlledHostBuild']
original=[c['name'] for c in n['checks']];assert [c['name'] for c in reopen['checks'] if c['name'] in original]==original
assert sha(roots[0]/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93/native138_controlled_curtain_runner.py')
assert sha(roots[1]/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93/native145_normal_reopen_runner.py')
assert sha(roots[2]/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93/native141_delayed_snapshot_runner.py')
for d in [n,reopen]:assert d['actualOffscreenWebKitPixels']['red']==19200 and d['actualClosedCurtainRegionPixels']['red']==0 and d['actualNativeGTKPaintObservation']['opacity']==0
for k in ['actualGUIRealmReopenQualified','actualSamePolicyRetained','actualOriginalNativeBindingRetained','actualFreshRendererPerEpoch','actualNavigationAndSnapshotChronologyRetained']:assert reopen[k],k
assert reopen['actualNormalGUIReopenCycles']==2 and not reopen['actualPendingIntentReopenQualified'] and reopen['actualReopenedWebKitPixels']['red']==19200 and reopen['actualReopenedClosedCurtainRegionPixels']['red']==0 and reopen['actualReopenedNativePaint']['opacity']==0
for k in ['actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert late[k],k
for _,d,_ in native:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
models=list(gui.glob('qa/host-realm-lifecycle-model-*/report.json'));assert len(models)==1;model=models[0];q=load(model);assert q['passed'] and q['namedScenarios']==9 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
artifacts(model,q);assert sha(q['quint']['path'])==q['quint']['sha256']
couplings=list((r/'docs/warlock-preview/v93').glob('host-lifecycle-coupling-*/report.json'));assert len(couplings)==1;coupling=couplings[0];c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==6 and c['actualNativeReportSHA256']==sha(rp)
for n,h in c['inputs'].items():assert sha(n)==h,n
artifacts(coupling,c);assert sha(c['quint']['path'])==c['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v130';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and held['passed'] and held['cpuCPolicyRealmReuseQualified']
failed=r/'implementation/warlock-preview-provider-v131';fm=failed/'component-manifest.json';fd=load(fm);assert fd['sourceHeld'] and not fd['passed'] and not fd['nativeLaunched']
for base,manifest in [(parent,held),(failed,fd)]:
 for n,row in manifest['files'].items():assert sha(base/n)==row['sha256'],n
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'shared-host.c','controlled-preview-host.h'}:assert sha(gui/base/p.name)==sha(p),p
scope='GUI132 activates actual strict native realm retirement and normal GUI close/reopen while preserving the exact original Elm policy and Native binding. After original custody drains and strict C/Bootstrap close, replace only the retired WebKit view/document/manager; later original same-binding native epoch receives one fresh fixed-grant pure renderer, without grant/navigation/snapshot resets. Actual Native145 retains all original29 controls and passes46 checks/18 normal exits across two real pointer cycles, current original native URI images/red19200 pixels in each, navigation1->2/lease1->2/request1->2, opacity0 closed-curtain output and two strict closes; private cleanup passes. Native144 unchanged29/13 normal and Native146 unchanged18/8 retained real stale result regressions pass separately. Full119, lifecycle Quint9named/200samples and six abstract stages coupled to actual native observations pass. Pending-intent replacement has code/model only; not actual qualified. Original independent physical/journal/confirmation custody, issuer/Elm/physical product/deadlines unchanged. Permanent retirement follows inherited bounded C/JSC foundation, not this actual GUI probe. Ongoing conceal/reveal/hardware, broader async/process/reload/unknown recovery, host pressure/full workload/RSS/full S09/release remain open. Never opens native opacity curtain or changes installed desktop.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',np),('normalReopenNative',rp),('delayedSnapshotNative',lp),('hostLifecycleQuint',model),('hostLifecycleCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualGUIRealmReopenQualified':True,'nativeRealmRebindingActivated':True,'actualNormalGUIReopenCycles':2,'actualPendingIntentReopenQualified':False,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'hostLifecycleQuintScenarios':9,'hostLifecycleInvariantSamples':200,'hostLifecycleCoupledStages':6,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'normalReopenNativeChecks':46,'normalReopenNormalOwnedExits':18,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'directPermanentRetirementQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)},'heldFailedParentManifest':{'path':str(fm),'sha256':sha(fm)}}
for root,count,exits in [(gui,46,18),*zip(roots,[29,46,18],[13,18,8])]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 manifest=root/'component-manifest.json';assert not manifest.exists();own=dict(common,files=files,nativeChecks=count,normalOwnedExits=exits)
 if root in roots:
  idx=roots.index(root);own.update(scope=native[idx][1]['scope'],actualGUIRealmReopenQualified=idx==1,actualNormalGUIReopenCycles=2 if idx==1 else 0,actualStaleSnapshotCallbackQualified=idx==2,actualRetainedResultConsumedOnce=idx==2,actualStaleSnapshotArtifactRejected=idx==2,actualCapturedPixelsQualified=idx!=2,actualScopedURIImageLoadObserved=idx!=2)
 manifest.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report132.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI132 actual normal two-cycle GUI close/reopen through same persistent Elm policy/native binding, fresh fixed-grant pure WebKit renderer after strict original C/Bootstrap close, no resets. Native145 all original29 plus17/46total18normalexits, two actual current native source URI/red19200 images, monotonic epoch/navigation/lease/snapshot and actual opacity0 output regions; original cleanup. Native14429/13 and delayed14618/8 unchanged regressions pass; full119, Quint9named200samples and6 native-coupled lifecycle stages. Failed131 retained. Pending intent code/model remains unqualified; physical ongoing conceal/reveal/hardware/process/reload/unknown/resource/performance/full release open. Next publish PUBLIC97 then actual pending-intent/stale-context qualification; installed/drafts/foreign preserved.'],'progress',[str((gui/'component-manifest.json').relative_to(r)),*[str((root/'component-manifest.json').relative_to(r)) for root in roots],str(out.relative_to(r))]))
