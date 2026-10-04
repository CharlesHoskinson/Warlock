"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,re,re,shutil,signal,struct,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grant-retirement-runtime-v595';GUI=REPO/'implementation/elm-recovery-delivery-integrated-gui-v640'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Actual shared menu zero-dwell native keyboard presses, staged minimize/restore and pixels; no held-loss/repeat/AT/IME/physical/full-release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False;observer_loaded=False;controller=None
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
 report['inputs'].update(preflight['inputs']);report['inputs'][str(ROOT/'qa/preflight.json')]=report['preflightSHA256']
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   observer_descriptor=json.loads((ROOT/'observer-build.json').read_text());assert host.digest(observer_descriptor['buildReport'])==observer_descriptor['buildReportSHA256']
   observer_build=json.loads(Path(observer_descriptor['buildReport']).read_text());assert observer_build['passed'] and observer_build['core']['sha256']==pair['core']['sha256'] and not observer_build['missingSymbols'];observer_plugin=observer_build['binary'];assert host.digest(observer_plugin)==observer_build['binarySHA256']
   assert s.ctl('plugin','load',observer_plugin).strip()=='ok';observer_loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=dict(env,WAYLAND_DEBUG='client'));apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(build_path.parent/'inputs/adapter/daemon.py'),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client'));apps.append(web)
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
   from importlib.util import spec_from_file_location,module_from_spec
   ci=spec_from_file_location('actual_parent_control',ROOT/'qa/interactive-client.py');im=module_from_spec(ci);ci.loader.exec_module(im)
   pd=json.loads((CORE/'parent-probe-build.json').read_text());controller=im.InteractiveClient(s.host,host.original,pd['buildReport'],pd['buildReportSHA256'],guard=s.guard)
   def held_state():
    value=json.loads(s.ctl('elm_held_state'));assert value['schema']==1 and value['pid']==native['pid'];return value
   def transport_keys():
    return [(int(k),int(state)) for k,state in re.findall(r'wl_keyboard(?:[#@]\d+)?\.key\(\d+, \d+, (\d+), (\d+)\)',log())]
   for loss_kind in ['focus','capability']:
    menu_before=wait(native_menu);snapshot_journal=journal();monitors=s.data('monitors');devices=s.data('devices')
    rect=tuple(map(int,re.findall(r'xdg_popup[#@]\d+\.configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',log())[-1]));px,py=rect[0]+20,rect[1]+14
    controller.send(f'motion {px} {py}');controller.send('press 272');controller.send('release 272');wait(native_menu)
    baseline_keys=transport_keys();controller.send('key-press 42');controller.send('key-press 30')
    state=wait(lambda:held_state() if sorted(held_state()['keys'])==[30,42] and sorted(held_state()['bindKeys'])==[38,50] and held_state()['mods']!=0 else None)
    report.setdefault('focusDiagnostics',[]).append({'kind':loss_kind,'phase':'heldBeforeLoss','state':held_state()})
    check(loss_kind+':sharedMenuKeysActuallyHeld',native_menu() is not None and journal()==snapshot_journal,state=state)
    key_start=len(transport_keys());deadline=time.monotonic()+6;controller.send('keyboard-'+loss_kind+' 0')
    def cleared():
     if time.monotonic()>=deadline:raise RuntimeError('Original six-second loss deadline')
     value=held_state();return value if value['keys']==[] and value['bindKeys']==[] and value['mods']==0 else None
    state=wait(cleared,seconds=max(.001,deadline-time.monotonic()))
    check(loss_kind+':nativeInputShortcutModifiersCleared',state['keys']==state['bindKeys']==[] and state['mods']==0 and time.monotonic()<deadline,state=state)
    releases=wait(lambda:transport_keys()[key_start:] if all(transport_keys()[key_start:].count((key,0))==1 for key in [30,42]) else None,seconds=max(.001,deadline-time.monotonic()))
    check(loss_kind+':sharedHostReceivesExactlyOneCancellationRelease',releases.count((30,0))==releases.count((42,0))==1 and not any(state==1 for _,state in releases),transportEvents=releases)
    report['focusDiagnostics'].append({'kind':loss_kind,'phase':'cancelled','state':held_state()})
    changed=s.data('devices');check(loss_kind+':onlyExpectedKeyboardChanges',len(changed['mice'])==len(devices['mice']) and len(changed['keyboards'])==(0 if loss_kind=='capability' else len(devices['keyboards'])),before=devices,after=changed)
    check(loss_kind+':sameOutputAndNoEffect',s.data('monitors')==monitors and journal()==snapshot_journal and host.original.same_process(native))
    controller.send(f'motion {px} {py}')
    if loss_kind=='capability':controller.send('keyboard-capability 1')
    else:
     controller.send('key-release 30');controller.send('key-release 42');controller.send('keyboard-focus 1')
    wait(lambda:len(s.data('devices')['keyboards'])==len(devices['keyboards']))
    if native_menu() is None:
     right(wait(group));right(wait(lambda:selection('ELM-AUTHORITY-FIXTURE')));wait(native_menu)
    recovered_start=len(transport_keys());controller.send('key-press 30');controller.send('key-release 30')
    report['focusDiagnostics'].append({'kind':loss_kind,'phase':'freshParentPairIssued','state':held_state()})
    recovered=wait(lambda:transport_keys()[recovered_start:] if transport_keys()[recovered_start:].count((30,1))==1 and transport_keys()[recovered_start:].count((30,0))==1 else None)
    check(loss_kind+':restoredParentAPairReceivedBySharedHost',recovered.count((30,1))==recovered.count((30,0))==1 and held_state()['keys']==held_state()['bindKeys']==[] and held_state()['mods']==0,transportEvents=recovered)
    keys('key 1 1\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
    check(loss_kind+':restoredNativeEscapeClosesMenuWithoutReplay',held_state()['keys']==held_state()['bindKeys']==[] and held_state()['mods']==0 and journal()==snapshot_journal)
    right(wait(group));right(wait(lambda:selection('ELM-AUTHORITY-FIXTURE')));opened=wait(native_menu)
   report['parentKeyboardLossController']=controller.quit();controller=None
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
    observed=wait(capture);check(name,True,capture=observed,expectedRed=expected_red)
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
   check('minimizeNativeReceiptIsCorrelatedCommitted',outcomes()[0]['status']=='Committed' and outcomes()[0]['intent']==minimized_request[0]['intent'],outcome=outcomes()[0])
   check('minimizeNativeRenderAndInputSuppressionKeepsOriginalWorkspace',not hidden['window']['shouldRenderAny'] and not hidden['window']['shouldRenderOwnMonitor'] and not hidden['window']['acceptsInput'] and hidden['window']['workspace']==target['workspace'] and hidden['window']['monitor']==target['monitor'],before=target,after=hidden['window'])
   pixels('minimizedNativeFixturePixelsDisappear',False,hidden['window'])
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);restoring=wait(native_menu)
   check('nativeMinimizedMenuSelectsRestore',restoring['body']['menu']['incarnation']==inc and restoring['body']['menu']['selected']==0 and restoring['body']['menu']['actions'][0]['enabled'])
   keys('key 28 1\nkey 28 0\n');shown=wait(lambda:state(False));wait(lambda:len(outcomes())==2)
   restored_requests=journal()
   check('realElmMenuRestoreSubmitsExactlyOnce',len(restored_requests)==2 and restored_requests[1]['intent']['incarnation']==inc and restored_requests[1]['intent']['operation']=='restore',requests=restored_requests)
   check('restoreNativeReceiptIsCorrelatedCommitted',outcomes()[1]['status']=='Committed' and outcomes()[1]['intent']==restored_requests[1]['intent'],outcome=outcomes()[1])
   check('restoreNativeRenderAndInputEligibilityKeepsOriginalWorkspace',shown['window']['shouldRenderAny'] and shown['window']['shouldRenderOwnMonitor'] and shown['window']['acceptsInput'] and shown['window']['workspace']==target['workspace'] and shown['window']['monitor']==target['monitor'],before=target,after=shown['window'])
   pixels('restoredNativeFixturePixelsReturn',True,shown['window'])
   # Additive actual floating-window multi-action/maximize/restore route.
   floating_deadline=time.monotonic()+6
   def floating_remaining():
    value=floating_deadline-time.monotonic()
    if value<=0:raise RuntimeError('Unchanged observation deadline')
    return value
   def floating_wait(predicate):return wait(predicate,seconds=floating_remaining())
   placement=next(w for w in s.data('clients') if w['pid']==fixture.pid and w['title']=='ELM-AUTHORITY-FIXTURE')
   check('floatingPlacementTargetsExactAuthorityIncarnation',placement['pid']==fixture.pid and inc==next(w['incarnation'] for w in client.snapshot('3')['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE'))
   selector=json.dumps('address:'+placement['address'])
   check('floatingFixturePlacementAdmitted',s.ctl('eval','local r=hl.dispatch(hl.dsp.window.float({action="enable",window='+selector+'}));if type(r)~="table" or r.ok~=true then error("placement refused") end').strip()=='ok')
   floating_wait(lambda:next((w for w in s.data('clients') if w['pid']==fixture.pid and w['address']==placement['address'] and w['title']=='ELM-AUTHORITY-FIXTURE' and w['floating']),None))
   # Native observed geometry is captured before the first UI geometry operation.
   ordinary=floating_wait(lambda:state(False))['window']
   prior=journal();click(floating_wait(group));right(floating_wait(lambda:selection('ELM-AUTHORITY-FIXTURE')))
   floating_menu=floating_wait(native_menu)
   enabled=[(i,a) for i,a in enumerate(floating_menu['body']['menu']['actions']) if a['enabled']]
   native_log=(OUTPUT/'fixture.log').read_text(errors='replace')
   identities=set(re.findall(r'xdg_toplevel([#@]\d+)\.set_title\("ELM-AUTHORITY-FIXTURE"\)',native_log))
   requests=[]
   if len(identities)==1:
    protocol_id=next(iter(identities))
    requests=[{'kind':kind,'width':int(width),'height':int(height)} for kind,width,height in re.findall(r'xdg_toplevel'+re.escape(protocol_id)+r'\.set_(min|max)_size\((\d+), (\d+)\)',native_log)]
   broker_geometry=[json.loads(line.split('backend-frame: ',1)[1]) for line in log().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split('backend-frame: ',1)[1]).get('kind')=='geometry-facts']
   report['latestBrokerGeometryFacts']=broker_geometry[-1] if broker_geometry else None
   report['constraintDiagnostic']={'pid':fixture.pid,'address':placement['address'],'incarnation':inc,'targetProtocolObjects':sorted(identities),'actualClientSizeRequests':requests,'rawLayoutBoundsObserved':bool(broker_geometry),'geometryFact':ordinary,'menu':floating_menu,'nativeLogSHA256':host.digest(OUTPUT/'fixture.log')}
   check('nativeConstraintDiagnosticBindsExactGTKTarget',len(identities)==1 and any(v['kind']=='min' for v in requests),diagnostic=report['constraintDiagnostic'])
   check('floatingMenuHasMultipleActualEnabledActions',floating_menu['body']['menu']['incarnation']==inc and len(enabled)>=2,actions=enabled)
   max_index=next(i for i,a in enabled if a['label']=='Maximize')
   original_selected=floating_menu['body']['menu']['selected'];count=len(inspections())
   keys('key 108 1\nkey 108 0\n')
   moved=floating_wait(lambda:native_menu() if len(inspections())>count and native_menu() else None)
   next_index=next((i for i,a in enabled if i>original_selected),enabled[0][0])
   check('floatingArrowMovesToNextEnabledActionWithoutEffect',moved['body']['menu']['selected']==next_index and journal()==prior,inspection=moved)
   # End selects the last enabled action, which must be Maximize for this fixture.
   check('floatingMaximizeIsLastEnabledAction',max_index==enabled[-1][0])
   keys('key 107 1\nkey 107 0\n')
   selected_max=floating_wait(lambda:native_menu() if native_menu() and native_menu()['body']['menu']['selected']==max_index else None)
   check('floatingEndSelectsMaximizeWithoutEffect',journal()==prior,inspection=selected_max)
   keys('key 28 1\nkey 28 0\n')
   floating_wait(lambda:len(outcomes())==3)
   request=journal();receipt=outcomes()[-1]
   check('floatingMaximizeHasOneActualCorrelatedCommittedReceipt',len(request)==len(prior)+1 and request[-1]['intent']['incarnation']==inc and request[-1]['intent']['operation']=='maximize' and request[-1]['effectProtocol']==2 and receipt['effectProtocol']==2 and receipt['status']=='Committed' and receipt['binding']==request[-1]['binding'] and receipt['intent']==request[-1]['intent'],request=request[-1],receipt=receipt)
   maximized=floating_wait(lambda:state(False) if state(False) and state(False)['window']['geometry']!=ordinary['geometry'] else None)['window']
   floating_remaining()
   check('floatingMaximizeChangesNativeGeometryPreservingOwnership',maximized['workspace']==ordinary['workspace'] and maximized['monitor']==ordinary['monitor'] and maximized['shouldRenderAny'] and maximized['acceptsInput'],before=ordinary,after=maximized)
   # Restore uses its own original six-second whole-transition budget.
   floating_deadline=time.monotonic()+6
   click(floating_wait(group));right(floating_wait(lambda:selection('ELM-AUTHORITY-FIXTURE')))
   restored_menu=floating_wait(native_menu)
   check('floatingRestoreMenuTargetsOriginalIncarnation',restored_menu['body']['menu']['incarnation']==inc)
   restore_index=next(i for i,a in enumerate(restored_menu['body']['menu']['actions']) if a['label']=='Restore' and a['enabled'])
   keys('key 102 1\nkey 102 0\n')
   floating_wait(lambda:native_menu() if native_menu() and native_menu()['body']['menu']['selected']==restore_index else None)
   keys('key 28 1\nkey 28 0\n');floating_wait(lambda:len(outcomes())==4)
   request=journal();receipt=outcomes()[-1]
   check('floatingGeometryRestoreHasOneActualCorrelatedCommittedReceipt',len(request)==len(prior)+2 and request[-1]['intent']['incarnation']==inc and request[-1]['intent']['operation']=='restore-geometry' and request[-1]['effectProtocol']==2 and receipt['effectProtocol']==2 and receipt['status']=='Committed' and receipt['binding']==request[-1]['binding'] and receipt['intent']==request[-1]['intent'],request=request[-1],receipt=receipt)
   geometry_restored=floating_wait(lambda:state(False) if state(False) and state(False)['window']['geometry']==ordinary['geometry'] else None)['window']
   floating_remaining()
   check('floatingGeometryRestoreReturnsOriginalPlacementAndOwnership',geometry_restored['workspace']==ordinary['workspace'] and geometry_restored['monitor']==ordinary['monitor'] and geometry_restored['shouldRenderAny'] and geometry_restored['acceptsInput'],before=ordinary,after=geometry_restored)
   report['floatingExtension']={'nativeClientACKQualified':False,'fullGeometryCampaignAccepted':False,'deadlineSecondsPerTransition':6}
   # One absolute six-second window for retirement and same-title replacement.
   retirement_deadline=time.monotonic()+6
   def remaining():
    value=retirement_deadline-time.monotonic()
    if value<=0:raise RuntimeError('Unchanged observation deadline')
    return value
   def retirement_wait(predicate):return wait(predicate,seconds=remaining())
   retirement_journal=journal();old_pid=fixture.pid
   click(retirement_wait(group));right(retirement_wait(lambda:selection('ELM-AUTHORITY-FIXTURE')))
   retiring=retirement_wait(native_menu)
   check('retirementMenuTargetsOriginalIncarnation',retiring['body']['menu']['incarnation']==inc and journal()==retirement_journal)
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control)
   fixture.wait(timeout=remaining());check('retiredOwnedFixtureNormalExit',fixture.returncode==0)
   def retired_coherent():
    current=facts();values=inspections();body=values[-1]['body'] if values else None
    return {'facts':current,'inspection':values[-1]} if not any(w['incarnation']==inc for w in current['facts']['windows']) and body and body['phase']=='Coherent' and body['menu'] is None and body['mode']=='closed' else None
   retired=retirement_wait(retired_coherent)
   check('retirementClosesMenuAndRefreshesCoherentFacts',journal()==retirement_journal and retired['inspection']['body']['outstanding']==0 and retired['inspection']['body']['registry']==0,evidence=retired)
   fixture=s.host.launch('replacement-fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=dict(env,WAYLAND_DEBUG='client'));apps.append(fixture)
   replacement=retirement_wait(lambda:next((w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE' and w['pid']==fixture.pid),None))
   replacement_snapshot=client.snapshot('2');replacement_inc=next(w['incarnation'] for w in replacement_snapshot['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')
   replacement_facts=next(w for w in facts()['facts']['windows'] if w['incarnation']==replacement_inc)
   retirement_wait(group);remaining()
   check('sameTitleReplacementKeepsDistinctNativeIdentity',fixture.pid!=old_pid and replacement_inc!=inc,replacement=replacement,oldIncarnation=inc,newIncarnation=replacement_inc)
   check('retiredMenuNeverMutatesSameTitleReplacement',not replacement_facts['minimized'] and replacement_facts['shouldRenderAny'] and replacement_facts['acceptsInput'] and journal()==retirement_journal and inspections()[-1]['body']['menu'] is None,geometry=replacement_facts,requests=journal())
   report['retirementExtension']={'deadlineSeconds':6,'remainingSeconds':remaining(),'oldPID':old_pid,'replacementPID':fixture.pid,'oldIncarnation':inc,'replacementIncarnation':replacement_inc,'originalGeometryMenu10Accepted':False}
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['passed']=True
  finally:
   if controller is not None:report['parentKeyboardLossController']=controller.eof();controller=None
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
   empty_clients=s.data('clients');check('nativeClientsEmptyBeforePluginUnload',empty_clients==[],clients=empty_clients)
   if observer_loaded:s.guard();assert s.ctl('plugin','unload',observer_plugin).strip()=='ok';observer_loaded=False
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
