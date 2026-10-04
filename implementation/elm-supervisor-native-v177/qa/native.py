"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grab-safe-background-v89';GUI=REPO/'implementation/elm-native-recovery-v169'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py';SUP=REPO/'implementation/elm-host-supervisor-v176'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False;failed_web=None
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
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/sampling.py',POINTER,FIXTURE,CORE/'candidate_host.py',SUP/'supervisor.py',SUP/'runtime-manifest.json')})
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
   supervisor=s.host.launch('elm-supervisor',['/usr/bin/python3','-B',str(SUP/'supervisor.py'),'--manifest',str(SUP/'runtime-manifest.json'),'--authority-config',str(config_path),'--qa','--qa-log-directory',str(OUTPUT)],env=dict(env));apps.append(supervisor)
   def supervisor_events(prefix):
    log=OUTPUT/'elm-supervisor.log'
    return [json.loads(line[len(prefix):]) for line in log.read_text().splitlines() if line.startswith(prefix)]
   def starts():return supervisor_events('supervisor-host-start: ')
   first=wait(lambda:starts()[-1] if starts() else None);web_pid=first['pid'];web_start=first['start'];failed_pid=web_pid
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
   initial=wait(group);check('actualElmGroupedControl',initial['label'].startswith('Choose a window from '),group=initial)
   keyboard=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
   report['inputs'][str(keyboard)]=host.digest(keyboard);report['inputs'][str(keyboard.with_suffix('.c'))]=host.digest(keyboard.with_suffix('.c'))
   def key_recipient(label):
    events=control.with_suffix('.events.jsonl');before=events.read_text().splitlines() if events.exists() else []
    s.guard();process=subprocess.run([str(keyboard)],input='sleep 100\nkey 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    assert process.returncode==0,process.stderr
    delivered=[json.loads(line) for line in events.read_text().splitlines()[len(before):]]
    report.setdefault('activationKeyboardReceipts',[]).append({'expected':label,'events':delivered,'exitCode':process.returncode})
    keys=[e for e in delivered if e['kind']=='key' and e['keyval']==97]
    return len(keys)==1 and keys[0]['window']==label
   def choose(label):
    control_group=wait(group);before_journal=journal();click(control_group)
    item=wait(lambda:selection(label))
    check('multipleFamilyPrimaryOpensPickerWithoutEffect',journal()==before_journal,projection=projection())
    click(item)
    wait(lambda:projection()['transaction']=='Committed' and projection()['phase']=='Coherent' and projection()['picker'] is None)
    request=journal()[-1]
    check('pickerSelectionEmitsActivate',request['intent']['operation']=='activate' and request['intent']['incarnation']==item['incarnation'],request=request)
    return item['incarnation']
   def press_key(code):
    s.guard();process=subprocess.run([str(keyboard)],input=f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedKeyboardCommandNormalExit',process.returncode==0,code=code,stderr=process.stderr)
   from sampling import sample_tree
   def frames(prefix):return [json.loads(line[len(prefix):]) for line in current_log.read_text().splitlines() if line.startswith(prefix)]
   target=choose('ELM-AUTHORITY-FIXTURE');check('beforeFailureActualApplicationKeyboardRecipient',key_recipient('ELM-AUTHORITY-FIXTURE'))
   old_request=journal()[-1];old_binding=old_request['binding'];before=client.scene_facts('451')
   native_identity={'pid':native['pid'],'start':start_time(native['pid'])}
   click(wait(group));wait(lambda:projection()['picker'] and projection()['focus'].startswith('picker:'))
   processes=sample_tree(web_pid,start_time(web_pid));renderers=[p for p in processes['processes'] if p['name'].startswith('WebKitWebProces')]
   check('oneRelatedRendererOwnsAllGUIViews',len(renderers)==1,processes=processes)
   renderer=renderers[0];check('rendererPIDIdentityVerifiedBeforeSignal',start_time(renderer['pid'])==renderer['start'])
   report['faultInjection']={'renderer':renderer,'hostPID':web_pid,'signal':'SIGKILL','oldBinding':old_binding,'openPopup':projection()['picker']}
   s.guard();os.kill(renderer['pid'],signal.SIGKILL)
   wait(lambda:'native-recovery-ready:' in current_log.read_text())
   check('rendererFailureKeepsTrustedNativeRecoveryHost',supervisor.poll() is None)
   check('hostReportsRendererTermination','Web process terminated:' in current_log.read_text())
   check('failedRendererBackendExitsNormally','backend-exit: waited=1 normal=1 code=0' in current_log.read_text())
   recovery_layers=[row for output in s.data('layers').values() for rows in output['levels'].values() for row in rows if row['pid']==failed_pid]
   check('nativeRecoveryRetainsOriginalBarReservation',len(recovery_layers)==1 and recovery_layers[0]['h']==48 and s.data('monitors')[0]['reserved'][1]==48,layers=recovery_layers)
   after=client.scene_facts('452');report['applicationFacts']={'beforeFailure':before,'afterFailure':after}
   def application_state(facts):return sorted((w['incarnation'],w['application'],w['minimized'],tuple(w['geometry'])) for w in facts['facts']['windows'])
   check('rendererFailurePreservesApplicationIncarnationsAndGeometry',application_state(before)==application_state(after),before=before,after=after)
   check('compositorIdentitySurvivesRendererFailure',start_time(native['pid'])==native_identity['start'])
   check('applicationReceivesRealKeyboardAfterShellFailure',key_recipient('ELM-AUTHORITY-FIXTURE'))
   import re
   def recovery_control():
    values=[tuple(map(int,m.groups())) for m in re.finditer(r'recovery-control: id=1 x=(\d+) y=(\d+) w=(\d+) h=(\d+)',current_log.read_text())]
    return values[-1] if values else None
   rectangle=wait(recovery_control);x,y,width,height=rectangle
   subprocess.run(['grim',str(OUTPUT/'native-recovery.png')],env=s.env,check=True,timeout=5)
   click({'point':[x+width/2,y+height/2],'visible':True})
   wait(lambda:any(row['generation']==1 for row in supervisor_events('supervisor-host-exit: ')))
   old_exit=next(row for row in supervisor_events('supervisor-host-exit: ') if row['generation']==1)
   check('nativeRestartButtonEmitsExplicitRestartExit',old_exit['exitCode']==3 and 'recovery-restart-requested' in current_log.read_text(),exitCode=old_exit['exitCode'],control=rectangle)
   report['recoveryScreenshot']=str(OUTPUT/'native-recovery.png')
   old_log=current_log;second=wait(lambda:starts()[-1] if len(starts())==2 else None)
   web_pid=second['pid'];web_start=second['start'];current_log=Path(second['log']);collector=Collector()
   check('sameLiveSupervisorOwnsReplacementHost',supervisor.poll() is None and web_pid!=failed_pid and start_time(web_pid)==web_start and Path('/proc/'+str(web_pid)+'/exe').resolve()==(build_path.parent/'elm-host').resolve(),first=first,second=second)
   wait(group);fresh_binding=wait(lambda:frames('backend-frame: ') if any(f['kind']=='attached' for f in frames('backend-frame: ')) else None)
   fresh_binding=[f['binding'] for f in fresh_binding if f['kind']=='attached'][-1]
   check('explicitHostRestartGetsFreshAuthorityBinding',fresh_binding!=old_binding and fresh_binding['lifetime']==old_binding['lifetime'],old=old_binding,new=fresh_binding)
   check('freshCoherentSnapshotPrecedesNewEffects',projection()['phase']=='Coherent' and not journal(),projection=projection())
   try:stale_result=client.request(old_request)
   except Refused as refusal:stale_result={'kind':'authenticated-native-refusal','reason':str(refusal)}
   check('oldHostEffectPacketRefusedAfterRestart',stale_result=={'kind':'authenticated-native-refusal','reason':'binding-mismatch'},outcome=stale_result)
   check('stalePacketDoesNotChangeApplicationState',application_state(client.scene_facts('453'))==application_state(after))
   choose('ELM-ACTIVATION-PEER');check('freshHostExplicitActivationGetsActualKeyboardRecipient',key_recipient('ELM-ACTIVATION-PEER'))
   final_facts=wait(lambda:client.scene_facts('454') if application_state(client.scene_facts('454'))==application_state(after) else None)
   check('restartPreservesApplicationsAndCompositor',application_state(final_facts)==application_state(after) and start_time(native['pid'])==native_identity['start'])
   report['recovery']={'mode':'actual sealed supervisor follows real native Restart; no fixture host replacement or compositor restart','freshBinding':fresh_binding,'oldBinding':old_binding,'oldHostExit':old_exit['exitCode'],'oldLog':str(old_log),'freshHostPID':web_pid,'supervisorPID':supervisor.pid}
   second_tree=sample_tree(web_pid,web_start);second_renderers=[p for p in second_tree['processes'] if p['name'].startswith('WebKitWebProces')]
   check('replacementHostStillHasOneOwnedRenderer',len(second_renderers)==1 and start_time(second_renderers[0]['pid'])==second_renderers[0]['start'])
   s.guard();os.kill(second_renderers[0]['pid'],signal.SIGKILL)
   wait(lambda:'native-recovery-ready:' in current_log.read_text())
   check('replacementFailureStillReturnsApplicationKeyboard',key_recipient('ELM-ACTIVATION-PEER'))
   owned_supervisor=next(row for process,row in s.host.processes if process is supervisor)
   s.host.stop(owned_supervisor,supervisor);supervisor.wait(timeout=5)
   check('supervisorStopCancelsRecoveryWithoutRestart',supervisor.returncode==0 and len(starts())==2 and len(supervisor_events('supervisor-host-exit: '))==2)
   last_exit=supervisor_events('supervisor-host-exit: ')[-1]
   check('cancelledRecoveryHostExitsWithoutForce',last_exit['stopping'] and not last_exit['forced'] and last_exit['exitCode']==1,exit=last_exit)
   check('cancelledRecoveryPreservesApplicationConnectionsAndCompositor',{w['incarnation'] for w in client.scene_facts('455')['facts']['windows']}=={w['incarnation'] for w in before['facts']['windows']} and start_time(native['pid'])==native_identity['start'])
   report['supervisorEvents']={'starts':starts(),'exits':supervisor_events('supervisor-host-exit: ')}
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['scope']='Private actual sealed supervisor restart/cancellation through native recovery controls; failure/final geometry and real application keyboard preserved; pending-intent/AT/hotplug/atomic restart/full release remain open'
   report['passed']=True
  finally:
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
