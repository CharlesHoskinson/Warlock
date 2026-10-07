"""Freeze bounded combined recovery proof; preserve both failed campaigns."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
owner='f6779148-8f5d-4bdf-8a0f-044184e486f2'
out=pathlib.Path(__file__).with_name('component-report-combined-restart-204-207.json');assert not out.exists()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def inventory(root):
 rows={}
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file() and p.name!='component-manifest.json':
   s=p.stat();rows[str(p.relative_to(root))]={'sha256':sha(p),'size':s.st_size,'mode':stat.S_IMODE(s.st_mode)}
 return rows
def validate(path):
 d=json.loads(path.read_text())
 for name,h in d.get('inputs',{}).items():assert sha(name)==h,name
 for name,h in d.get('artifacts',{}).items():assert sha(path.parent/name)==h,name
 return d
reports={};manifests=[];pairs=[];builds=[]
for v,count,helpers in [(202,27,6),(203,91,24),(204,102,26),(205,101,25),(206,99,24),(207,104,27)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';paths=list(root.glob('qa/native-*/report.json'));assert len(paths)==1
 p=paths[0];d=validate(p);pre=validate(root/'qa/preflight.json');positive=v>=204
 assert d['passed']==positive and d['cleanupPassed'] and len(d['checks'])==count and len(d['ownedHelperExits'])==helpers
 assert not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and not d['controlledPreviewRecoveryQualified']
 if positive:
  assert all(c['passed'] for c in d['checks'])
  assert all(d[k] for k in ['combinedKnownPreviewBeforeRestartQualified','combinedControlledPreviewRestartQualified','actualWindowCommandRestartQualified','actualWindowCommandDurableUnknownQualified'])
  assert not d['popupDismissalFocusRestorationQualified']
  assert all(h['exitCode']==0 for h in d['ownedHelperExits']) and all(h['exitCode']==0 for h in d['previewFixtureCleanupExits'])
  starts=d['supervisorEvents']['starts'];exits=d['supervisorEvents']['exits'];assert len(starts)==len(exits)==2 and starts[0]['pid']!=starts[1]['pid']
  assert exits[0]['exitCode']==3 and not exits[0]['forced'] and not exits[0]['stopping']
  assert exits[1]['exitCode']==1 and not exits[1]['forced'] and exits[1]['stopping'] and d['cohortCleanup'][-1]['remaining']==[]
  old=d['recovery']['oldBinding'];fresh=d['recovery']['freshBinding'];assert old!=fresh and old['lifetime']==fresh['lifetime']
  history=d['historicalUnknownBeforeNewAction'];assert history['record']['status']=='Unknown' and history['phase']=='Released' and history['proof']['queriedBinding']==old and history['proof']['binding']==fresh
  a=d['originalControlledPreview'];b=d['freshControlledPreview'];assert a['pixels']['red']==b['pixels']['red']==19200 and a['pixels']['green']==b['pixels']['green']==a['pixels']['blue']==b['pixels']['blue']==0
  assert a['paint']['opacity']==b['paint']['opacity']==0 and not a['paint']['physicalFrameQualified'] and not b['paint']['physicalFrameQualified']
  assert a['model']['scope']['binding']!=b['model']['scope']['binding'] and a['model']['scope']['clock']==b['model']['scope']['clock']
  assert int(b['model']['scope']['now'])>int(a['model']['scope']['now']) and a['model']['scope']['context']['incarnation']==b['model']['scope']['context']['incarnation']
  s=d['originalControlledPreviewStrictClose'];realm=s['privatePolicy']['realm'];assert realm['closed'] and not s['privatePolicy']['models'] and not s['nativeEffectError']
  assert not any(s[k] for k in ['retainedInputs','retainedInputBytes','postedTickets','confirmations','returnedEventsRetained','returnedEventBatches','returnedEventBytes','ticketUnnotified'])
  log1=(p.parent/'native-evidence/generation-1.log').read_text();log2=(p.parent/'native-evidence/generation-2.log').read_text()
  markers=['controlled-native-reader-held:','controlled-native-reader-probed:','Web process terminated:','controlled-native-reader-released:','controlled-native-realm-retired:','native-recovery-ready:','recovery-restart-requested']
  positions=[log1.index(m) for m in markers];assert positions==sorted(positions)
  assert 'backend-exit: waited=1 normal=0 code=-1' in log1 and 'backend-exit: waited=1 normal=1 code=0' in log2
  assert 'GLib-GObject-CRITICAL' not in log1+log2 and 'Controlled native teardown incomplete:' not in log1+log2
  assert d['operation']==('minimize' if v in {204,206} else 'restore') and d['faultBoundary']==('lost' if v in {204,205} else 'unread')
  marker=d['operationFaultMarker']
  if d['faultBoundary']=='lost':assert marker['outcome']['status']=='Committed' and marker['durableRecord']['status']=='Pending'
  else:assert marker['stage']=='after-durable-admission-and-publication-before-broker-write'
 else:assert d.get('error')
 entry={'path':str(p),'sha256':sha(p),'passed':positive,'checks':count,'registeredShortLivedHelpers':helpers,'normalShortLivedHelpers':helpers if positive else None,'cleanupPassed':True}
 reports['native'+str(v)]=entry;pairs.append(pre['pair']);builds.append(pre['controlledHostBuild'])
 held={'schema':1,'owner':owner,'sourceHeld':True,'passed':positive,'reports':{'native':entry},'combinedControlledPreviewRestartQualified':positive,'actualWindowCommandRestartQualified':positive,'actualWindowCommandDurableUnknownQualified':positive,'controlledPreviewRecoveryQualified':False,'wholeHostRestartQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'privateSessionCleanupPassed':True,'files':inventory(root)}
 manifests.append((root/'component-manifest.json',held))
assert all(p==pairs[0] for p in pairs) and len(set(builds))==1
build_path=pathlib.Path(builds[0]);build=json.loads(build_path.read_text());gui=r/'implementation/warlock-preview-provider-v143'
assert build['passed'] and len(build['commands'])==119 and all(c['exitCode']==0 for c in build['commands'])
for name,h in build['inputs'].items():assert sha(gui/name)==h,name
for name,h in build['artifacts'].items():assert sha(build_path.parent/name)==h,name
sup=r/'implementation/warlock-window-restart-supervisor-v2';runtime=json.loads((sup/'runtime-manifest.json').read_text())
assert runtime['coreSHA256']==pairs[0]['core']['sha256'] and runtime['host']==str(build_path.parent/'elm-host')
for name,h in runtime['files'].items():assert sha(name)==h,name
model=r/'implementation/warlock-combined-recovery-model-v1';model_path=next(model.glob('qa/model-*/report.json'));m=validate(model_path)
coupled_path=next(model.glob('qa/coupled-*/report.json'));c=validate(coupled_path)
guard_path=next(out.parent.glob('supervisor-qa-guards-v2-*/report.json'));g=validate(guard_path)
assert m['passed'] and m['namedScenarios']==14 and m['invariantSamples']==200 and c['passed'] and c['coupledStages']==14 and c['originalRetiringJobUnchanged']
assert g['passed'] and len(g['checks'])==7 and all(x['passed'] and x['exitCode']==2 and x['childLaunchObserved'] is False for x in g['checks'])
for key,p,d in [('model',model_path,m),('coupling',coupled_path,c),('supervisorGuards',guard_path,g)]:
 reports[key]={'path':str(p),'sha256':sha(p),'passed':True,'scope':d['scope']}
for root,scope in [(sup,g['scope']),(model,m['scope']+' '+c['scope'])]:
 manifests.append((root/'component-manifest.json',{'schema':1,'owner':owner,'sourceHeld':True,'passed':True,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'files':inventory(root)}))
scope='Current GUI143/core16/plugin19/AQ155: four real combined known-preview custody/uncertain-window-command/native GTK Restart cases (minimize/restore, committed lost receipt/before broker write). Original actual GIO reader remains held after popup close and blocks strict native retirement; renderer death cannot settle it. Actual reader close then independently observed strict native empty custody precede GTK recovery and explicit Restart/old host exit3. Fresh same-compositor host retains exact durable window Unknown without replay, authenticates old-binding retirement and accepted reads, preserves immutable historical Unknown during a newer explicit advanced command, then captures red19200 through its own fresh native preview namespace on the same original clock/source incarnation and strictly closes it. Original job/deadline identity and deadlines retained; registered helpers/source/companion have normal waited exits, explicit broker/renderer faults and host3/1 outcomes remain separate, shell cohort empty and private cleanup passes. Failed202 focus-precondition timeout and203 final focused-fixture keyboard precondition retained; actual compositor/pointer preconditions in successors leave popup-dismissal focus restoration unqualified. No production source changed; original119-command build reverified; Quint14 selected/200 samples,14 actual projected stages and7 real supervisor refusal checks pass. Projection is bounded, not full transition refinement. Actual native preview-effect uncertainty/all asynchronous schedules, original-clock expiry/pressure, Wayland/hardware conceal/reveal, workload/RSS, restore timing/full native13/S09/release/AT/IME/journeys/reversible deployment remain open. Installed desktop/drafts/foreign edits preserved.'
common={'schema':1,'owner':owner,'sourceHeld':True,'passed':True,'scope':scope,'cpuBuildPassed':True,'fullBuildCommands':119,'namedModelScenarios':14,'invariantSamples':200,'coupledActualStages':14,'supervisorNegativeChecks':7,'fourOperationBoundaryScenariosQualified':True,'combinedControlledPreviewRestartQualified':True,'actualWindowCommandRestartQualified':True,'actualWindowCommandDurableUnknownQualified':True,'historicalUnknownPreserved':True,'originalReaderAndStrictNativeCloseBeforeGTKRecovery':True,'originalDeadlinesPreserved':True,'automaticUnknownReplayCount':0,'nativeAuthorityResets':0,'privateSessionCleanupPassed':True,'controlledPreviewRecoveryQualified':False,'wholeHostRestartQualified':False,'uncertainPreviewRetirementQualified':False,'popupDismissalFocusRestorationQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'originalRestoreTimingQualified':False,'measuredRSSQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'reports':reports,'build':{'path':str(build_path),'sha256':sha(build_path)},'pair':pairs[0]}
for path,d in manifests:
 assert not path.exists(),path
for path,d in manifests:
 path.write_text(json.dumps(d,indent=2)+'\n');print(path.parent.name,len(d['files']),d['passed'],flush=True)
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,owner,'implementation/warlock-client-provider-native-v204',['PROGRESS '+scope+' Next PUBLIC106 then actual native preview-effect uncertainty; full GUI goal remains active.'],'progress',[str(out.relative_to(r)),str((model/'component-manifest.json').relative_to(r)),str((sup/'component-manifest.json').relative_to(r))]))
