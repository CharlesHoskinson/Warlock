"""Hold an actual canceled old WebKit result failing the newly reopened GUI."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v136';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [158,159]];rows=[]
for root,count,passed,runner in zip(roots,[29,23],[True,False],['native138_controlled_curtain_runner.py','native159_cancelled_reopened_snapshot_runner.py']):
 p=next(root.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(root/'qa/preflight.json')
 assert d['passed']==passed and d['cleanupPassed'] and len(d['checks'])==count and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 rows.append((p,d,pre))
normal,np,npre=rows[0];failed,fp,fpre=rows[1];checks={c['name']:c for c in fp['checks']}
assert checks['controlledActualOriginalWebKitCancellationConsumedOnce']['passed'] and not checks['controlledActualStaleSnapshotCompletionRejected']['passed']
assert [c['name'] for c in fp['checks'] if not c['passed']]==['controlledActualStaleSnapshotCompletionRejected']
assert len(np['ownedExitCodes'])==13 and all(c['exitCode']==0 for c in np['ownedExitCodes'])
assert len(fp['ownedExitCodes'])==9 and all(c['exitCode']==(1 if c['name']=='controlled-host' else 0) for c in fp['ownedExitCodes'])
assert fp['pair']==np['pair'] and fpre['controlledHostBuild']==npre['controlledHostBuild']
log=failed.parent/'private-evidence/controlled-host.log';text=log.read_text()
assert text.count('controlled-native-snapshot-finish-outcome: image=0 cancelled=1 retainedEpoch=1 currentEpoch=2 replacedView=1 originalFinishCalls=1 nativeSettlement=0')==1
assert 'Native client producer failed: Operation was cancelled' in text and 'Controlled native teardown incomplete: Original policy/input/ticket/physical/journal/confirmation custody prevents realm retirement' in text
assert 'controlled-native-snapshot-refused:' not in text
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
model=next(gui.glob('qa/async-error-scope-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==10 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
for n,h in q['artifacts'].items():assert sha(model.parent/n)==h,n
assert sha(q['quint']['path'])==q['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v135';pm=parent/'component-manifest.json';held=load(pm);assert held['passed'] and held['sourceHeld']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
scope='Held GUI136 counterexample. Disabled-by-default actual canceled GCancellable supplied to original WebKit snapshot; actual original result/strong old view retained through strict old native close, new view and later same-policy epoch/current native projection. Original finish exactly once reports image0/G_IO_ERROR_CANCELLED, oldEpoch1/current2/replacedView1. Original completion reports error BEFORE current-scope check, shutting down current GUI: Native159 fails unchanged stale-refusal oracle, host1 and original strict teardown retains current native custody; eight other owned processes normal/private cleanup. Native158 original29/13 normal regression and full119 pass separately. Quint10/200 describes defect and proposed guard, not native acceptance. Current source not accepted. Physical curtain0, issuer/single Elm policy/physical product/strict close/deadlines unchanged. Next fresh GUI137 moves existing scope guard before current error reporting and safely disposes only original old image/error; actual unchanged canceled-result oracle and original normal/success/delayed/rapid regressions required. Full release remains open.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',normal),('cancelledOldResultCounterexample',failed),('asyncErrorScopeQuint',model)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':119,'actualCancelledOldResultCounterexample':True,'canceledOrFailedOldResultQualified':False,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root in [gui,*roots]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root==roots[0]:own.update(passed=True,actualCancelledOldResultCounterexample=False,scope=np['scope'],nativeChecks=29,normalOwnedExits=13)
 if root==roots[1]:own.update(scope=scope,nativeChecks=23,normalOwnedExits=8,failedOwnedExits=1)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report136.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI136 actual old real canceled WebKit result fails current reopened GUI before original scope guard. Native159 unchanged36-control intended oracle reaches23 checks/one original stale-refusal failure, host1 and strict current custody retained/private cleanup; normal15829/13/full119/Quint10/200 pass separately. Fresh137 move existing guard before error reporting, consume once/dispose old error only; unchanged canceled oracle and original regressions next. Full release remains open/installed drafts foreign preserved.'],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in [gui,*roots]]+[str(out.relative_to(r))]))
