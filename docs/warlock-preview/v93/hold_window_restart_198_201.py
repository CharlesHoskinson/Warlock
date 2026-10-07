"""Freeze main-window recovery qualifications and retained harness failures."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
out=pathlib.Path(__file__).with_name('component-report-window-restart-198-201.json');assert not out.exists()
reports={};pairs=[];builds=[]
def inventory(root):
 result={}
 for path in sorted(root.rglob('*')):
  assert not path.is_symlink(),path
  if path.is_file() and path.name!='component-manifest.json':
   info=path.stat();result[str(path.relative_to(root))]={'sha256':sha(path),'size':info.st_size,'mode':stat.S_IMODE(info.st_mode)}
 return result
for v in range(195,202):
 root=repo/f'implementation/warlock-client-provider-native-v{v}'
 paths=list(root.glob('qa/native-*/report.json'));assert len(paths)==1
 path=paths[0];report=json.loads(path.read_text());pre=json.loads((root/'qa/preflight.json').read_text());positive=v>=198
 assert report['passed']==positive and report['cleanupPassed']
 assert not report['nativeAcceptance'] and not report['fullReleaseAccepted'] and not report['controlledPreviewRecoveryQualified']
 for name,h in pre['inputs'].items():assert sha(name)==h,name
 for name,h in report['artifacts'].items():assert sha(path.parent/name)==h,name
 if positive:
  assert all(c['passed'] for c in report['checks'])
  assert report['actualWindowCommandRestartQualified'] and report['actualWindowCommandDurableUnknownQualified']
  assert all(h['exitCode']==0 for h in report['ownedHelperExits'])
  starts=report['supervisorEvents']['starts'];exits=report['supervisorEvents']['exits']
  assert len(starts)==len(exits)==2 and starts[0]['pid']!=starts[1]['pid']
  assert exits[0]['exitCode']==3 and not exits[0]['forced'] and not exits[0]['stopping']
  assert exits[1]['exitCode']==1 and exits[1]['stopping'] and not exits[1]['forced']
  assert report['cohortCleanup'][-1]['remaining']==[]
  old=report['recovery']['oldBinding'];fresh=report['recovery']['freshBinding']
  assert old!=fresh and old['lifetime']==fresh['lifetime']
  history=report['historicalUnknownBeforeNewAction'];assert history['record']['status']=='Unknown' and history['phase']=='Released' and history['proof']['queriedBinding']==old and history['proof']['binding']==fresh
  log1=(path.parent/'native-evidence/generation-1.log').read_text();log2=(path.parent/'native-evidence/generation-2.log').read_text()
  assert 'backend-exit: waited=1 normal=0 code=-1' in log1 and 'native-recovery-ready:' in log1 and 'recovery-restart-requested' in log1
  assert 'backend-exit: waited=1 normal=1 code=0' in log2
  assert 'GLib-GObject-CRITICAL' not in log1+log2 and 'Controlled native teardown incomplete:' not in log1+log2
  marker=report['operationFaultMarker'];fault=report['faultBoundary']
  if fault=='lost':assert marker['outcome']['status']=='Committed' and marker['durableRecord']['status']=='Pending'
  else:assert fault=='unread' and marker['stage']=='after-durable-admission-and-publication-before-broker-write'
  assert report['operation']==('restore' if v in {198,200} else 'minimize')
  assert fault==('lost' if v in {198,199} else 'unread')
 else:
  assert report.get('error')
 entry={'path':str(path),'sha256':sha(path),'passed':positive,'checks':len(report['checks']),'cleanupPassed':True,'normalShortLivedHelpers':len(report.get('ownedHelperExits',[])) if positive else 0}
 reports[f'native{v}']=entry;pairs.append(pre['pair']);builds.append(pre['controlledHostBuild'])
 held={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':positive,'reports':{'native':entry},'actualWindowCommandRestartQualified':positive,'actualWindowCommandDurableUnknownQualified':positive,'controlledPreviewRecoveryQualified':False,'combinedControlledPreviewRestartQualified':False,'wholeHostRestartQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'privateSessionCleanupPassed':True,'files':inventory(root)}
 manifest=root/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps(held,indent=2)+'\n');print(root.name,len(held['files']),positive)
assert all(p==pairs[0] for p in pairs) and len(set(builds))==1
build_path=pathlib.Path(builds[0]);build=json.loads(build_path.read_text());gui=repo/'implementation/warlock-preview-provider-v143'
assert build['passed'] and len(build['commands'])==119 and all(c['exitCode']==0 for c in build['commands'])
for name,h in build['inputs'].items():assert sha(gui/name)==h,name
for name,h in build['artifacts'].items():assert sha(build_path.parent/name)==h,name
supervisor=repo/'implementation/warlock-window-restart-supervisor-v1'
runtime=json.loads((supervisor/'runtime-manifest.json').read_text())
assert runtime['coreSHA256']==pairs[0]['core']['sha256'] and runtime['host']==str(build_path.parent/'elm-host')
for name,h in runtime['files'].items():assert sha(name)==h,name
held={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Reviewed predecessor supervisor/cohort bytes, resealed exact current GUI143 assets/backend/binary and owning core16; explicit native exit3 restart only; four main-window fault scenarios qualify separately.','files':inventory(supervisor)}
(supervisor/'component-manifest.json').write_text(json.dumps(held,indent=2)+'\n')
scope='Current GUI143/core16/plugin19/AQ155 main window-command recovery: real minimize and restore, interruption after native commit or after durable host admission before broker write, exact original Pending admission, actual application pixels/keyboard, explicit Unknown/real renderer failure/native GTK Restart/exit3/same sealed supervisor/fresh binding/same compositor lifetime/application geometry. Exact original recovered Unknown/no automatic replay/coherent current scene; actual native old-binding retirement and accepted post-proof reads release capacity while preserving durable historical Unknown. New pointer intent advances request/generation, uses current state and preserves old Unknown. Supervisor cancellation in second fallback exits failure1 without force or third host, empty owned shell scope, normal waited short-lived helpers and fixture/supervisor/private cleanup. Failed195 textual start/config,196 helper path and197 obsolete Pending observer are retained. No production source changed; current119 build/source/ABI closure verified. Separate controlled-preview retirement plus window-command whole-host restart, native uncertainty, original restore timing, physical/hardware, workload/RSS, full S09/release/AT/IME/journeys/deployment remain open. Installed desktop/drafts/foreign edits preserved.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'sourceHeld':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualWindowCommandRestartQualified':True,'actualWindowCommandDurableUnknownQualified':True,'fourOperationBoundaryScenariosQualified':True,'historicalUnknownPreserved':True,'automaticUnknownReplayCount':0,'originalDeadlinesPreserved':True,'nativeAuthorityResets':0,'privateSessionCleanupPassed':True,'controlledPreviewRecoveryQualified':False,'combinedControlledPreviewRestartQualified':False,'wholeHostRestartQualified':False,'uncertainPreviewRetirementQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'originalRestoreTimingQualified':False,'measuredRSSQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'reports':reports,'build':{'path':str(build_path),'sha256':sha(build_path)},'pair':pairs[0],'scope':scope}
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],'implementation/warlock-client-provider-native-v198',['PROGRESS '+scope+' Next PUBLIC105, then actual combined controlled-preview strict drain/window-command durable Unknown/whole-host restart on same tuple, original native uncertainty and full-release gates; goal remains active.'],'progress',[str(out.relative_to(repo)),str((supervisor/'component-manifest.json').relative_to(repo))]))
