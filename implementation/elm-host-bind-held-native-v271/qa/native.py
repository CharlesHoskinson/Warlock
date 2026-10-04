"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grab-safe-background-v89';GUI=REPO/'implementation/elm-host-bind-fixed-v268'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
OPERATION='minimize';FAULT='unread'
FIXTURE=ROOT/'fixture.py';SUP=REPO/'implementation/elm-host-bind-supervisor-v269'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False};apps=[];host_lock_fd=None;s=None;loaded=False;failed_web=None
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,value,**evidence):
 report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged observation deadline')
try:
 build_path=sorted((GUI/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(GUI/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/sampling.py',POINTER,FIXTURE,CORE/'candidate_host.py',SUP/'supervisor.py',SUP/'runtime-manifest.json',SUP/'cohort.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'hide-peer'}));temp.replace(control)
   wait(lambda:not any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')))
   recovery_dir=Path(config['runtime'])/'elm-window-recovery'/config['instance']/client.bound['lifetime']
   recovery_dir.mkdir(parents=True,mode=0o700);recovery_dir.parent.chmod(0o700);recovery_dir.parent.parent.chmod(0o700)
   before=client.scene_facts('451')
   host_lock_path=recovery_dir/'host-writer.lock';host_lock_path.touch(mode=0o600);host_lock_path.chmod(0o600)
   lock_inode=host_lock_path.stat().st_ino
   import fcntl
   host_lock_fd=os.open(host_lock_path,os.O_RDWR);fcntl.flock(host_lock_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   supervisor=s.host.launch('elm-supervisor',['/usr/bin/python3','-B',str(SUP/'cohort.py'),'--manifest',str(SUP/'runtime-manifest.json'),'--authority-config',str(config_path),'--qa','--qa-log-directory',str(OUTPUT)],env=env);apps.append(supervisor)
   def supervisor_events(prefix):
    log=OUTPUT/'elm-supervisor.log'
    return [json.loads(line[len(prefix):]) for line in log.read_text().splitlines() if line.startswith(prefix)]
   def starts():return supervisor_events('supervisor-host-start: ')
   first=wait(lambda:starts()[-1] if starts() else None);web_pid=first['pid'];web_start=first['start'];failed_pid=web_pid
   cohort=wait(lambda:supervisor_events('cohort-ready: ')[-1] if supervisor_events('cohort-ready: ') else None);report['cohort']=cohort
   check('cohortScopeExcludesCompositorAndApplicationFixture',cohort['controlGroup'] in Path('/proc/'+str(web_pid)+'/cgroup').read_text() and cohort['controlGroup'] not in Path('/proc/'+str(native['pid'])+'/cgroup').read_text() and cohort['controlGroup'] not in Path('/proc/'+str(fixture.pid)+'/cgroup').read_text(),cohort=cohort)

   check('supervisedHostIsOwnedSealedNativeBinary',Path('/proc/'+str(web_pid)+'/exe').resolve()==(build_path.parent/'elm-host').resolve() and start_time(web_pid)==web_start,child=first)
   sys.path.insert(0,str(ROOT/'qa'))
   from inspection import Collector
   current_log=Path(first['log'])
   collector=Collector()
   def projection():return collector.read(current_log.read_text(errors='replace'))
   def row(state):
    p=projection()
    action='Restore ' if state=='Minimized' else 'Minimize '
    return next((g for g in p['groups'] if g['label'].startswith(action) and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():
    return [json.loads(line.split('frontend-request: ',1)[1]) for line in current_log.read_text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='window-effect']
   def group():
    p=projection()
    return p['groups'][0] if p and p['phase']=='Coherent' and len(p['groups'])==1 and not p['groups'][0]['disabled'] else None
   def selection(label):
    p=projection()
    return next((r for r in p['picker']['selections'] if r['title']==label and not r['disabled']),None) if p and p['phase']=='Coherent' and p['picker'] else None
   def click(item):
    assert item.get('visible',True),'Target outside host viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<420
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   def frames(prefix):return [json.loads(line[len(prefix):]) for line in current_log.read_text().splitlines() if line.startswith(prefix)]
   def bar_reports():return [json.loads(line.split('surface-report: origin=bar ',1)[1])['body'] for line in current_log.read_text().splitlines() if line.startswith('surface-report: origin=bar ')]
   wait(lambda:projection() and projection()['phase']=='Detached' and projection()['reconnect'] and not projection()['reconnect']['disabled'])
   wait(lambda:bar_reports() and 'Restore access, then reconnect.' in bar_reports()[-1]['text'])
   check('actualBarExplainsRecoveryFailure','Restore access, then reconnect.' in bar_reports()[-1]['text'],body=bar_reports()[-1])
   check('actualHostBindingFailsBeforeFrontendAttachment',not any(f.get('kind')=='attached' for f in frames('backend-frame: ')) and host_lock_path.stat().st_ino==lock_inode)
   check('failurePrecedesFrontendAttachment',not any(f.get('kind')=='attached' for f in frames('backend-frame: ')))
   check('noWindowEffectsOnStartupFailure',not journal())
   wait(lambda:'backend-exit: waited=1 normal=0 code=-1' in current_log.read_text())
   check('recoveryFailureBrokerExitRecorded','backend-exit: waited=1 normal=0 code=-1' in current_log.read_text())
   def identities(facts):return sorted((w['incarnation'],w['application'],w['minimized']) for w in facts['facts']['windows'])
   failure_facts=client.scene_facts('452')
   check('failurePreservesApplicationIdentityAndState',identities(failure_facts)==identities(before))
   check('hostLockFailurePreservesOriginalFile',host_lock_path.stat().st_ino==lock_inode)
   subprocess.run(['grim',str(OUTPUT/'recovery-storage-failure.png')],env=s.env,check=True,timeout=5)
   fcntl.flock(host_lock_fd,fcntl.LOCK_UN);os.close(host_lock_fd);host_lock_fd=None
   observation=time.monotonic()+.5
   while time.monotonic()<observation:
    s.guard();assert not journal() and not any(f.get('kind')=='attached' for f in frames('backend-frame: '));time.sleep(.04)
   check('manualCorrectionDoesNotAutomaticallyRetry',not journal())
   click(projection()['reconnect']);wait(group)
   fresh_binding=[f['binding'] for f in frames('backend-frame: ') if f['kind']=='attached'][-1]
   check('explicitReconnectGetsAuthenticatedCurrentLifetime',fresh_binding['lifetime']==client.bound['lifetime'],binding=fresh_binding)
   check('explicitReconnectKeepsSameOwnedNativeHost',start_time(web_pid)==web_start and supervisor.poll() is None and len(starts())==1)
   check('explicitReconnectDoesNotReplayWindowIntent',not journal())
   check('reconnectPreservesApplicationIdentityAndState',identities(client.scene_facts('453'))==identities(failure_facts))
   check('correctedHostLockFileRemainsPrivateAndUnreplaced',host_lock_path.stat().st_ino==lock_inode and host_lock_path.stat().st_mode&0o777==0o600)
   click(wait(lambda:row('Visible')));wait(lambda:projection()['transaction']=='Committed')
   facts=client.scene_facts('454');check('freshExplicitMinimizeCommitsAfterCorrection',journal()[-1]['intent']['operation']=='minimize' and facts['facts']['windows'][0]['minimized'])
   subprocess.run(['grim',str(OUTPUT/'recovery-storage-corrected.png')],env=s.env,check=True,timeout=5)
   report['storageFailure']={'reason':'unavailable','namespace':str(recovery_dir),'freshBinding':fresh_binding,'noAutomaticRetry':True,'evidencePreserved':True,'fixtureCorrection':'held','fault':'actual host-writer.lock binding refusal'}
   owned=next(row for process,row in s.host.processes if process is supervisor);s.host.stop(owned,supervisor);supervisor.wait(timeout=5)
   check('normalSupervisorStopDoesNotCreateNewGeneration',supervisor.returncode==0 and len(starts())==1)
   report['supervisorEvents']={'starts':starts(),'exits':supervisor_events('supervisor-host-exit: ')};report['cohortCleanup']=supervisor_events('cohort-cleanup: ')
   check('ownedShellScopeHasNoRemainingProcesses',report['cohortCleanup'][-1]['remaining']==[])
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['scope']='Actual host lifetime lock held refusal, preserved instance, explicit same-host reconnect and fresh native effect; full release open'
   report['passed']=True
  finally:
   if host_lock_fd is not None:os.close(host_lock_fd)
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     expected=0
     report['checks'].append({'name':'hostExitMatchesDeclaredFailureOrNormalExit','passed':process.returncode==expected,'exitCode':process.returncode,'expected':expected});report['passed']=report['passed'] and process.returncode==expected
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
