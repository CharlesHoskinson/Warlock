"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,re,shutil,signal,struct,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grant-retirement-runtime-v595';GUI=REPO/'implementation/elm-reconciliation-startup-order-v626'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
RELAY=REPO/'implementation/elm-reconciliation-current-fixture-v634/relay/qa/relay.py'
spec_relay=importlib.util.spec_from_file_location('current_qa_relay',RELAY);relay=importlib.util.module_from_spec(spec_relay);spec_relay.loader.exec_module(relay)
report={'passed':False,'scope':'Actual shared host native pointer context/keyboard navigation and staged native minimize/restore; private owning tuple only, no original137/full recovery/AT/IME/hardware/release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False;observer_loaded=False;controller=None
KIND=json.loads((ROOT/'loss-case.json').read_text())['kind'];assert KIND in ['capability','focus']
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,value,**evidence):
 report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if time.monotonic()>=until:raise RuntimeError('Unchanged observation deadline')
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged observation deadline')
try:
 preflight=json.loads((ROOT/'qa/preflight.json').read_text());assert preflight['passed']
 for path,digest in preflight['inputs'].items():assert host.digest(path)==digest,path
 report['preflightSHA256']=host.digest(ROOT/'qa/preflight.json')
 build_path=Path(json.loads((GUI/'qa/current-build.json').read_text())['report']);build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(GUI/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 assert host.digest(manifest['owningAcceptance'])==manifest['owningAcceptanceSHA256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/grab_guard.py',ROOT/'qa/sampling.py',POINTER,FIXTURE,CORE/'candidate_host.py')})
 for extra in [ROOT/'qa/interactive-client.py',ROOT/'observer-build.json',ROOT/'legacy-client-build.json',ROOT/'loss-case.json',CORE/'parent-probe-build.json']:report['inputs'][str(extra)]=host.digest(extra)
 report['inputs'].update(preflight['inputs']);report['inputs'][str(ROOT/'qa/preflight.json')]=report['preflightSHA256']
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   relay_control=OUTPUT/'relay-actor-1';relay_control.mkdir(mode=0o700)
   relay_config=OUTPUT/'relay-config.json';relay_config.write_text(json.dumps({'profile':'broker','authorityConfig':str(config_path),'controlDirectory':str(relay_control),'runtime':config['runtime'],'instance':config['instance']}));relay_config.chmod(0o600)
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(RELAY),'--authority-config',str(relay_config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client'));apps.append(web)
   sys.path.insert(0,str(ROOT/'qa'))
   from inspection import Collector
   collector=Collector()
   def projection():return collector.read((OUTPUT/'elm-webview.log').read_text(errors='replace'))
   def row(state):
    p=projection()
    action='Restore ' if state=='Minimized' else 'Minimize '
    return next((g for g in p['groups'] if g['label'].startswith(action) and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():
    return [json.loads(line.split('frontend-request: ',1)[1]) for line in (OUTPUT/'elm-webview.log').read_text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='window-effect']
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
   initial=wait(group);check('sharedNativeTaskbarReady',initial['label'].startswith('Choose a window from '),group=initial)
   KEYBOARD=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
   report['inputs'][str(KEYBOARD)]=host.digest(KEYBOARD)
   def log():return (OUTPUT/'elm-webview.log').read_text(errors='replace')
   def inspections():
    return [json.loads(line.split(': ',1)[1]) for line in log().splitlines() if line.startswith('surface-inspection: ')]
   def native_menu():
    values=inspections()
    if not values:return None
    model=values[-1]
    return model if model['body']['mode']=='menu' and model['body']['phase']=='Coherent' and model['body']['menu'] else None
   def keys(commands):
    result=subprocess.run([str(KEYBOARD)],input=commands+'sleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedNativeKeyboardNormalExit',result.returncode==0,stderr=result.stderr,commands=commands)
   def right(item):
    assert item.get('visible',True),'Target outside fixed viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<600
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedNativeContextPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   before_journal=journal();right(initial)
   item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   check('multifamilyContextOpensNativePickerWithoutEffect',journal()==before_journal,selection=item)
   right(item);opened=wait(native_menu)
   check('realPopupPointerContextOpensElmWindowMenu',opened['body']['menu']['incarnation']==item['incarnation'],inspection=opened)
   check('nativeContextProofIdentifiesActualOutput','surface-context-admitted: view=1 generation=1 origin=popup trigger=pointer' in log())
   check('menuOpenDoesNotMutateNativeWindows',journal()==before_journal)
   keys('key 1 1\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('realEscapeClosesMenuWithoutNativeEffect',journal()==before_journal)
   # Open the ordinary picker again, retaining its native focused selection.
   click(wait(group));wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   keys('key 127 1\nkey 127 0\n');opened=wait(native_menu)
   check('realMenuKeyOpensWindowMenu','surface-context-admitted: view=1 generation=1 origin=popup trigger=keyboard' in log(),inspection=opened)
   selected=opened['body']['menu']['selected'];enabled=[i for i,a in enumerate(opened['body']['menu']['actions']) if a['enabled']]
   assert enabled==[selected], 'This tiled fixture has exactly one enabled action; multi-action navigation needs a separate floating fixture'
   count=len(inspections());keys('key 108 1\nkey 108 0\n')
   navigated=wait(lambda:native_menu() if len(inspections())>count and native_menu() and native_menu()['body']['menu']['id']==opened['body']['menu']['id'] else None)
   check('realArrowDownSkipsDisabledRowsAndRetainsSoleEnabledAction',navigated['body']['menu']['selected']==selected and journal()==before_journal,inspection=navigated)
   keys('key 1 1\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   click(wait(group));wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   keys('key 42 1\nkey 68 1\nkey 68 0\nkey 42 0\n');shift=wait(native_menu)
   check('realShiftF10OpensElmMenu',shift['body']['menu'] is not None,inspection=shift)
   keys('key 1 1\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('allNativeOpenNavigateCancelRoutesKeepEffectsInert',journal()==before_journal)
   # Additive real parent-key loss with an actual open shared Elm menu.
   def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
   interactive=module('shared_held_parent_controller',ROOT/'qa/interactive-client.py')
   probe_desc=json.loads((CORE/'parent-probe-build.json').read_text());probe_report=Path(probe_desc['buildReport'])
   assert host.digest(probe_report)==probe_desc['buildReportSHA256'];probe=json.loads(probe_report.read_text());assert probe['passed']
   observer_desc=json.loads((ROOT/'observer-build.json').read_text());observer_path=Path(observer_desc['buildReport'])
   assert host.digest(observer_path)==observer_desc['buildReportSHA256'];observer=json.loads(observer_path.read_text())
   assert observer['passed'] and not observer['missingSymbols'] and observer['core']['sha256']==pair['core']['sha256']
   assert host.digest(observer['binary'])==observer['binarySHA256']
   check('owningInputObserverLoaded',s.ctl('plugin','load',observer['binary']).strip()=='ok');observer_loaded=True
   mapped=host.original.mapped_files(s.child.pid)['files']
   check('exactInputObserverMapped',mapped.get(str(Path(observer['binary']).resolve()))==observer['binarySHA256'])
   check('exactProtocol8ParentModuleMapped',s.evidence['westonMaps']['files'].get(str(Path(probe['module']).resolve()))==probe['moduleSHA256'])
   def held_state():
    value=json.loads(s.ctl('elm_held_state'));assert value['schema']==1 and value['pid']==s.child.pid
    return value
   def gtk_keys():
    result=[]
    for line in log().splitlines():
     if not line.startswith('context-key-event: '):continue
     values=dict(field.split('=',1) for field in line.split(': ',1)[1].split())
     assert set(values)=={'type','hardware','key','state','time','send','view','generation','popup','engine','window','device','held'}
     for field in ['type','hardware','key','state','time','send','view','generation','popup','held']:values[field]=int(values[field])
     assert values['type'] in [8,9] and values['send']==0 and values['view']>0 and values['generation']>0 and values['popup'] in [0,1]
     for field in ['engine','window','device']:assert re.fullmatch(r'0x[0-9a-f]+',values[field]) and int(values[field],16)>0
     result.append(values)
    return result
   def parent_point(item):
    assert item.get('visible',True) and len(item['point'])==2
    monitors=s.data('monitors');assert len(monitors)==1
    monitor=monitors[0];assert monitor['name']=='WAYLAND-1' and monitor.get('transform',0)==0 and monitor['x']==monitor['y']==0 and monitor['scale']==1
    x,y=item['point'];assert 0<x<800 and 0<y<420
    return [round(x*1600/(monitor['width']/monitor['scale'])),round(y*1000/(monitor['height']/monitor['scale']))]
   initial_held=held_state();check('noStaleStateBeforeHeldMenu',initial_held['keys']==initial_held['bindKeys']==[] and initial_held['mods']==0,state=initial_held)
   def focus_picker_target():
    item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
    if projection()['focus']!=item['domId']:keys('key 15 1\nkey 15 0\n')
    focused=wait(lambda:projection() if projection() and projection()['picker'] and projection()['focus']==item['domId'] else None)
    check('actualDOMKeyboardFocusMatchesTargetSelection',focused['phase']=='Coherent' and focused['focus']==item['domId'],selection=item,projection=focused)
    return item
   click(wait(group));focused_picker=focus_picker_target()
   px,py=parent_point(focused_picker);base_events=len(gtk_keys())
   legacy_report=Path(json.loads((ROOT/'legacy-client-build.json').read_text())['buildReport']);legacy=json.loads(legacy_report.read_text());assert legacy['passed']
   negative=subprocess.run([legacy['client']],input=f'motion {px} {py}\nkey-press 30\nkey-release 30\nkey-press 68\nquit\n',text=True,capture_output=True,env=dict(s.host.env,ELM_PARENT_INPUT_QA='1'),cwd=s.host.runtime,timeout=5)
   messages=[json.loads(line) for line in negative.stdout.splitlines()]
   check('protocol7F10RefusedAfterEligibleAPair',negative.returncode==6 and len(messages)==5 and messages[0]=={'ready':True,'scope':'parent-notify-only'} and [m['sequence'] for m in messages[1:]]==[1,2,3,4] and [m['accepted'] for m in messages[1:]]==[True,True,True,False],messages=messages,stderr=negative.stderr)
   legacy_delivered=wait(lambda:gtk_keys()[base_events:] if any(v['type']==9 and v['hardware']==38 for v in gtk_keys()[base_events:]) else None)
   check('legacyAPairDeliveredToActualPopup',len(legacy_delivered)==2 and [v['type'] for v in legacy_delivered]==[8,9] and all(v['hardware']==38 and v['popup']==1 for v in legacy_delivered),events=legacy_delivered)
   check('legacyPairLeavesLedgersBalanced',held_state()['keys']==held_state()['bindKeys']==[] and held_state()['mods']==0)
   controller=interactive.InteractiveClient(s.host,host.original,probe_report,probe_desc['buildReportSHA256'],guard=s.guard,name='shared-held-menu-controller')
   report['interactiveParent']=controller.evidence
   controller.send(f'motion {px} {py}');held_start=len(gtk_keys());held_journal=journal();before_devices=s.data('devices');before_monitors=s.data('monitors')
   check('exactInitialKeyboardPointerDevices',len(before_devices['mice'])==len(before_devices['keyboards'])==1,devices=before_devices)
   controller.send('key-press 42');controller.send('key-press 68')
   held_menu=wait(native_menu)
   def held_receipts():
    events=gtk_keys()[held_start:];state=held_state()
    return {'events':events,'state':state} if all(any(v['type']==8 and v['hardware']==code and v['popup']==1 for v in events) for code in [50,76]) and sorted(state['keys'])==[42,68] and sorted(state['bindKeys'])==[50,76] and state['mods']==1 else None
   before=wait(held_receipts);physical={code:next(v for v in before['events'] if v['type']==8 and v['hardware']==code) for code in [50,76]}
   check('realShiftF10HeldOnExactWebKitEngine',physical[50]['engine']==physical[76]['engine'] and physical[50]['view']==physical[76]['view']==1 and physical[50]['generation']==physical[76]['generation']==1 and not any(v['type']==9 for v in before['events']),events=before['events'],state=before['state'])
   check('heldF10ActuallyOpensCoherentElmMenu',held_menu['body']['menu']['incarnation']==focused_picker['incarnation'] and journal()==held_journal,inspection=held_menu)
   report['beforeKeyboardLoss']={'state':before['state'],'events':before['events'],'menu':held_menu,'devices':before_devices,'monitors':before_monitors,'child':s.child_identity}
   loss_offset=len(gtk_keys());loss=controller.send('keyboard-capability 0' if KIND=='capability' else 'keyboard-focus 0')
   check('actualHeldMenuKeyboardLossAdmitted',loss['accepted'] is True,kind=KIND)
   def cancellation():
    value=held_state();report['lastHeldState']=value
    return value if value['keys']==value['bindKeys']==[] and value['mods']==0 else None
   cancelled_state=wait(cancellation);check('actualHeldMenuCoreLedgersCancelled',cancelled_state['keys']==cancelled_state['bindKeys']==[] and cancelled_state['mods']==0,state=cancelled_state)
   expected_keyboards=0 if KIND=='capability' else 1
   lost_devices=wait(lambda:s.data('devices') if len(s.data('devices')['keyboards'])==expected_keyboards else None)
   check('onlyExpectedSharedKeyboardCapabilityChanges',len(lost_devices['mice'])==1 and len(lost_devices['keyboards'])==expected_keyboards,devices=lost_devices)
   check('sharedOutputAndChildSurviveKeyboardLoss',s.data('monitors')==before_monitors and host.original.same_process(s.child_identity) and bool(s.data('version')))
   def released():
    values=gtk_keys()[loss_offset:]
    return values if all(any(v['type']==9 and v['hardware']==code for v in values) for code in [50,76]) else None
   releases=wait(released)
   check('exactGTKCancelReleaseOnSameWebKitEngine',len(releases)==2 and all(sum(v['type']==9 and v['hardware']==code and v['engine']==physical[code]['engine'] and v['device']==physical[code]['device'] and v['view']==physical[code]['view'] and v['generation']==physical[code]['generation'] and v['popup']==1 for v in releases)==1 for code in [50,76]),events=releases,physicalPresses=physical)
   check('actualF10ReleaseReachesHeldContextLedger',next(v for v in releases if v['hardware']==76)['held']&2==2,events=releases)
   cancel_end=len(gtk_keys())
   def parent_click(item):
    x,y=parent_point(item)
    controller.send(f'motion {x} {y}');controller.send('press 272');controller.send('release 272')
   parent_click(wait(group))
   def dismissed():
    values=inspections();return values[-1] if values and values[-1]['body']['phase']=='Coherent' and values[-1]['body']['mode'] in ['closed','picker'] else None
   lost_mode=wait(dismissed)
   check('parentPointerDismissesHeldMenuWithoutEffect',journal()==held_journal,inspection=lost_mode)
   if lost_mode['body']['mode']=='closed':parent_click(wait(group))
   lost_picker=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   check('parentPointerOpensActualPickerWhileKeyboardLost',lost_picker['incarnation']==focused_picker['incarnation'] and journal()==held_journal,selection=lost_picker)
   if KIND=='capability':controller.send('keyboard-capability 1')
   else:
    controller.send('key-release 68');controller.send('key-release 42');controller.send('keyboard-focus 1')
   restored=wait(lambda:s.data('devices') if len(s.data('devices')['keyboards'])==len(s.data('devices')['mice'])==1 else None)
   check('sharedKeyboardRestoredAndBalanced',held_state()['keys']==held_state()['bindKeys']==[] and held_state()['mods']==0,devices=restored,state=held_state())
   check('parentBalanceAddsNoGTKKeyDelivery',len(gtk_keys())==cancel_end,events=gtk_keys()[cancel_end:])
   restored_target=focus_picker_target();assert restored_target['incarnation']==focused_picker['incarnation']
   fresh_offset=len(gtk_keys());fresh_log_offset=len(log());px,py=parent_point(restored_target);controller.send(f'motion {px} {py}')
   controller.send('key-press 42');controller.send('key-press 68');controller.send('key-release 68');controller.send('key-release 42')
   fresh_menu=wait(native_menu)
   fresh=wait(lambda:gtk_keys()[fresh_offset:] if any(v['type']==9 and v['hardware']==50 for v in gtk_keys()[fresh_offset:]) else None)
   check('freshPhysicalShiftF10PairAfterRestoration',len(fresh)==4 and all(sum(v['hardware']==code and v['type']==kind and v['popup']==1 for v in fresh)==1 for code in [50,76] for kind in [8,9]),events=fresh)
   check('restoredF10ContextIsFreshAndAdmitted',bool(re.search(r'context-key-report: key=65479 state=1 hardware=76 time=[0-9]+ fresh=1 available=1 popup=1',log()[fresh_log_offset:])) and 'surface-context-admitted: view=1 generation=1 origin=popup trigger=keyboard' in log()[fresh_log_offset:],log=log()[fresh_log_offset:])
   check('restoredShiftF10ActuallyReopensElmMenu',fresh_menu['body']['menu']['incarnation']==focused_picker['incarnation'] and journal()==held_journal,inspection=fresh_menu)
   check('allSharedHeldInputLedgersBalancedAfterFreshPair',held_state()['keys']==held_state()['bindKeys']==[] and held_state()['mods']==0,state=held_state())
   controller.quit();controller=None
   renderer=(OUTPUT/'weston-renderer.log').read_text(errors='replace');marker='keyboard-removal-before-parent-key-balance mask=6' if KIND=='capability' else 'keyboard-focus requested=0 before-parent-key-balance mask=6'
   check('heldContextLossPrecedesParentKeyBalance',marker in renderer,marker=marker)
   report['heldMenuLoss']={'kind':KIND,'cancellation':cancelled_state,'gtkReleases':releases,'lostDevices':lost_devices,'restoredDevices':restored,'freshPair':fresh,'freshMenu':fresh_menu}
   keys('key 1 1\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('freshMenuNormallyDismissesWithoutEffect',journal()==held_journal)
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);close_menu=wait(native_menu)
   keys('key 15 1\nkey 15 0\n')
   def close_focus():
    reports=[json.loads(line.split('surface-report: origin=popup ',1)[1])['body'] for line in log().splitlines() if line.startswith('surface-report: origin=popup ')]
    return reports[-1] if reports and reports[-1]['focus']==close_menu['body']['menu']['closeId'] else None
   focused_close=wait(close_focus);check('realTabFocusesMenuCloseControl',focused_close['focus']==close_menu['body']['menu']['closeId'],dom=focused_close)
   keys('key 28 1\nkey 28 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('realEnterOnCloseDismissesWithoutEffect',journal()==before_journal)
   check('keyboardCloseUsesAdmittedTerminalRelease',log().count('surface-terminal-released: key=65293 ')==1)
   observation=1
   def facts():
    global observation
    observation+=1
    return client.scene_facts(str(observation))
   identities=client.snapshot('1');inc=next(w['incarnation'] for w in identities['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')
   baseline=facts();target=next(w for w in baseline['facts']['windows'] if w['incarnation']==inc)
   def pixels(name,expected_red,expected):
    geometry=expected['geometry'];x,y,w,h=geometry
    points=[(round(x+w*f),round(y+h*f)) for f in [.5,.7,.3]];attempts=[];deadline=time.monotonic()+6
    def capture():
     s.guard();remaining=deadline-time.monotonic()
     if remaining<=0:raise RuntimeError('Unchanged observation deadline')
     picture=OUTPUT/(name+'-'+str(len(attempts))+'.png')
     process=subprocess.run(['/usr/bin/grim',str(picture)],env=s.env,capture_output=True,timeout=min(5,remaining));assert process.returncode==0,process.stderr
     raw=picture.read_bytes();assert raw[:8]==bytes.fromhex('89504e470d0a1a0a') and raw[12:16]==b'IHDR' and struct.unpack('>II',raw[16:24])==(800,600)
     remaining=deadline-time.monotonic()
     if remaining<=0:raise RuntimeError('Unchanged observation deadline')
     converted=subprocess.run(['/usr/bin/magick',str(picture),'-depth','8','rgb:-'],capture_output=True,timeout=min(5,remaining));assert converted.returncode==0 and len(converted.stdout)==800*600*3
     samples=[]
     for px,py in points:
      assert 0<px<800 and 48<py<600
      offset=(py*800+px)*3;samples.append(list(converted.stdout[offset:offset+3]))
     current=next(v for v in facts()['facts']['windows'] if v['incarnation']==inc)
     assert all(current[k]==expected[k] for k in ['incarnation','geometry','workspace','monitor','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput']), 'Native state changed during pixel observation'
     row={'path':str(picture),'sha256':host.digest(picture),'points':points,'samples':samples};attempts.append(row);report.setdefault('pixelAttempts',[]).append(row)
     matched=all(v==[255,0,0] for v in samples) if expected_red else all(v!=[255,0,0] for v in samples)
     return row if matched else None
    observed=wait(capture)
    if time.monotonic()>=deadline:raise RuntimeError('Unchanged observation deadline')
    check(name,True,capture=observed,expectedRed=expected_red)
   pixels('initialNativeFixturePixelsAreRed',True,target)
   def state(minimized):
    current=facts();window=next((w for w in current['facts']['windows'] if w['incarnation']==inc),None)
    return {'facts':current,'window':window} if window and window['minimized']==minimized else None
   def outcomes():
    return [json.loads(line.split('backend-frame: ',1)[1]) for line in log().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split('backend-frame: ',1)[1]).get('kind')=='effect-outcome']
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);chosen=wait(native_menu)
   check('nativeTiledMenuSelectsMinimize',chosen['body']['menu']['incarnation']==inc and chosen['body']['menu']['selected']==1 and chosen['body']['menu']['actions'][1]['enabled'])
   keys('key 28 1\nkey 28 0\n');hidden=wait(lambda:state(True));wait(lambda:len(outcomes())==1)
   minimized_request=journal()
   check('realElmMenuMinimizeSubmitsExactlyOnce',len(minimized_request)==1 and minimized_request[0]['intent']['incarnation']==inc and minimized_request[0]['intent']['operation']=='minimize',requests=minimized_request)
   check('nativeMinimizeUsesAdmittedTerminalRelease',log().count('surface-terminal-released: key=65293 ')==2)
   check('minimizeNativeReceiptIsCorrelatedCommitted',outcomes()[0]['status']=='Committed' and outcomes()[0]['intent']==minimized_request[0]['intent'],outcome=outcomes()[0])
   check('minimizeNativeRenderAndInputSuppressionKeepsOriginalWorkspace',not hidden['window']['shouldRenderAny'] and not hidden['window']['shouldRenderOwnMonitor'] and not hidden['window']['acceptsInput'] and hidden['window']['workspace']==target['workspace'] and hidden['window']['monitor']==target['monitor'],before=target,after=hidden['window'])
   pixels('minimizedNativeFixturePixelsDisappear',False,hidden['window'])
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);restoring=wait(native_menu)
   check('nativeMinimizedMenuSelectsRestore',restoring['body']['menu']['incarnation']==inc and restoring['body']['menu']['selected']==0 and restoring['body']['menu']['actions'][0]['enabled'])
   keys('key 28 1\nkey 28 0\n');shown=wait(lambda:state(False));wait(lambda:len(outcomes())==2)
   restored_requests=journal()
   check('realElmMenuRestoreSubmitsExactlyOnce',len(restored_requests)==2 and restored_requests[1]['intent']['incarnation']==inc and restored_requests[1]['intent']['operation']=='restore',requests=restored_requests)
   check('nativeRestoreUsesAdmittedTerminalRelease',log().count('surface-terminal-released: key=65293 ')==3)
   check('restoreNativeReceiptIsCorrelatedCommitted',outcomes()[1]['status']=='Committed' and outcomes()[1]['intent']==restored_requests[1]['intent'],outcome=outcomes()[1])
   check('restoreNativeRenderAndInputEligibilityKeepsOriginalWorkspace',shown['window']['shouldRenderAny'] and shown['window']['shouldRenderOwnMonitor'] and shown['window']['acceptsInput'] and shown['window']['workspace']==target['workspace'] and shown['window']['monitor']==target['monitor'],before=target,after=shown['window'])
   pixels('restoredNativeFixturePixelsReturn',True,shown['window'])
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['passed']=True
  finally:
   if controller is not None:controller.eof();controller=None
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
   relay_exit=relay.exit_status(relay_control);check('currentSchema5RelayAndBrokerExitNormallyOnEOF',relay_exit['childExit']==0 and relay_exit['stdinClosed'],actor=relay_exit)
   empty_clients=s.data('clients');check('nativeClientsEmptyBeforePluginUnload',empty_clients==[],clients=empty_clients)
   if observer_loaded:
    s.guard();check('inputObserverNormallyUnloaded',s.ctl('plugin','unload',observer['binary']).strip()=='ok');observer_loaded=False
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
report['inputChanges']=[path for path,digest in report.get('inputs',{}).items() if host.digest(path)!=digest]
report['passed']=report['passed'] and not report['inputChanges']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
