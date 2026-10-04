"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grab-safe-background-v89';GUI=ROOT
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'qa/fixture.py'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False
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
 report['originalScenario']={'path':'implementation/elm-surface-regression-qa-v93/qa/regression.py','sha256':host.digest(REPO/'implementation/elm-surface-regression-qa-v93/qa/regression.py'),'changes':'candidate path and frozen backend/fixture location only; scenarios and deadlines retained'}
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/grab_guard.py',POINTER,FIXTURE,CORE/'candidate_host.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
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
   before_keyboard=journal();click(wait(group))
   opened=wait(lambda:projection() if projection()['picker'] and projection()['focus'].startswith('picker:') else None)
   check('pickerOpeningFocusesFirstAvailableControl',opened['focus'].endswith(':'+opened['picker']['selections'][0]['incarnation']) and opened['picker']['close']['visible'],projection=opened)
   press_key(1)
   dismissed=wait(lambda:projection() if projection()['picker'] is None and projection()['focus'].startswith('group:') else None)
   check('escapeRestoresScopedOpenerWithoutNativeEffect',journal()==before_keyboard,projection=dismissed)
   click(wait(group));wait(lambda:projection()['picker'] and projection()['focus'].startswith('picker:'))
   opened=projection();second=opened['picker']['selections'][1]
   press_key(15);wait(lambda:projection()['focus'].endswith(':'+second['incarnation']))
   press_key(28);wait(lambda:projection()['picker'] is None and projection()['transaction']=='Committed' and projection()['phase']=='Coherent')
   check('tabEnterPickerSelectionActivatesActualKeyboardRecipient',journal()[-1]['intent']['operation']=='activate' and journal()[-1]['intent']['incarnation']==second['incarnation'] and key_recipient(second['title']))
   before_close=journal();click(wait(group));opened=wait(lambda:projection() if projection()['picker'] and projection()['focus'].startswith('picker:') else None)
   click(opened['picker']['close']);wait(lambda:projection()['picker'] is None and projection()['focus'].startswith('group:'))
   check('visiblePointerCloseRestoresOpenerWithoutNativeEffect',journal()==before_close)
   identity=choose('ELM-AUTHORITY-FIXTURE')
   check('pointerElmPickerOwnerActivationKeyboard',client.scene_facts('201')['facts']['focused']==identity and key_recipient('ELM-AUTHORITY-FIXTURE'))
   peer_identity=choose('ELM-ACTIVATION-PEER')
   check('pointerElmPickerPeerActivationKeyboard',client.scene_facts('202')['facts']['focused']==peer_identity and key_recipient('ELM-ACTIVATION-PEER'))
   choose('ELM-ACTIVATION-PEER')
   check('activePickerSelectionDoesNotMinimize',not next(w for w in client.scene_facts('203')['facts']['windows'] if w['incarnation']==peer_identity)['minimized'])
   # Separate supervisor PID/session supplies an explicit native setup effect.
   setup_facts=client.scene_facts('220')
   setup_intent={'request':'900','generation':'900','incarnation':peer_identity,'operation':'minimize','context':client.context(setup_facts)}
   setup_outcome=client.effect(setup_intent)
   check('ownedFocusedPeerMinimizedForPickerRestore',setup_outcome['status']=='Committed',intent=setup_intent,outcome=setup_outcome)
   click(wait(group));item=wait(lambda:selection('ELM-ACTIVATION-PEER') if selection('ELM-ACTIVATION-PEER') and selection('ELM-ACTIVATION-PEER')['state']=='Minimized' else None)
   check('minimizedFamilyRetainedAsLabeledPickerChoice',item['label'].startswith('Restore '),projection=projection())
   click(item);wait(lambda:projection()['picker'] is None and projection()['transaction']=='Committed' and projection()['phase']=='Coherent')
   check('pickerRestoreUsesExplicitRestoreAndActualKeyboard',journal()[-1]['intent']['operation']=='restore' and not next(w for w in client.scene_facts('221')['facts']['windows'] if w['incarnation']==peer_identity)['minimized'] and key_recipient('ELM-ACTIVATION-PEER'))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'add-modal'}));temp.replace(control)
   wait(lambda:any(w['title']=='SCENE-MODAL' for w in s.data('clients')))
   click(wait(group));opened=wait(lambda:projection() if projection()['picker'] and projection()['focus'].startswith('picker:') else None)
   check('modalChildNotDuplicatedInPicker',len(opened['picker']['selections'])==2 and not any(item['title']=='SCENE-MODAL' for item in opened['picker']['selections']),projection=opened)
   screenshot=OUTPUT/'elm-family-picker.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['pickerScreenshotSHA256']=host.digest(screenshot)
   item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));click(item)
   wait(lambda:projection()['picker'] is None and projection()['transaction']=='Committed' and projection()['phase']=='Coherent')
   modal_id=next(w['incarnation'] for w in client.snapshot('222')['windows'] if w['label']=='SCENE-MODAL')
   check('rootPickerActivationSelectsActualModalKeyboard',journal()[-1]['intent']['incarnation']==identity and client.scene_facts('222')['facts']['focused']==modal_id and key_recipient('SCENE-MODAL'))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'retire-modal'}));temp.replace(control)
   wait(lambda:not any(w['title']=='SCENE-MODAL' for w in s.data('clients')))
   choose('ELM-ACTIVATION-PEER')
   click(wait(group));wait(lambda:projection()['picker'] and projection()['focus'].startswith('picker:'))
   before_external=client.scene_facts('230');before_external_projection=projection();before_external_journal=journal()
   guard=subprocess.run(['/usr/bin/python3','-B',str(ROOT/'qa/grab_guard.py'),str(GUI/'adapter'),str(config_path),peer_identity],env=s.env,capture_output=True,text=True,timeout=5)
   assert guard.returncode==0,guard.stderr
   focused_outcome=json.loads(guard.stdout)
   check('focusedMinimizeStillRefusesActivePopupGrab',focused_outcome['status']=='Refused' and focused_outcome['reason']=='seat-grab',outcome=focused_outcome)
   external_intent={'request':'901','generation':'901','incarnation':identity,'operation':'minimize','context':client.context(before_external)}
   external_outcome=client.effect(external_intent);after_external=client.scene_facts('231')
   report['externalUnfocusedMutation']={'before':before_external,'beforeProjection':before_external_projection,'intent':external_intent,'outcome':external_outcome,'after':after_external}
   check('externalUnfocusedMinimizePreservesPeerFocus',external_outcome['status']=='Committed' and after_external['facts']['focused']==peer_identity and next(w for w in after_external['facts']['windows'] if w['incarnation']==identity)['minimized'])
   changed=wait(lambda:projection() if projection()['picker'] is None and projection()['phase']=='Coherent' else None)
   check('externalUnfocusedChangeAutomaticallyRetiresStalePicker',journal()==before_external_journal,projection=changed)
   click(wait(group));item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE') if selection('ELM-AUTHORITY-FIXTURE') and selection('ELM-AUTHORITY-FIXTURE')['state']=='Minimized' else None)
   click(item);wait(lambda:projection()['picker'] is None and projection()['phase']=='Coherent' and projection()['transaction']=='Committed')
   check('externalStateReconciliationLeavesExplicitRestoreUsable',journal()[-1]['intent']['operation']=='restore' and key_recipient('ELM-AUTHORITY-FIXTURE'))
   choose('ELM-ACTIVATION-PEER')
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'retire-peer'}));temp.replace(control)
   wait(lambda:len(s.data('clients'))==1)
   single=wait(lambda:row('Open'))
   check('retiredActivePeerSelectsRemainingNativeMRU',client.scene_facts('204')['facts']['focused']==identity and single['active'] and key_recipient('ELM-AUTHORITY-FIXTURE'))
   initial=wait(lambda:row('Open'))

   click(initial)
   minimized=wait(lambda:row('Minimized'))
   facts=client.scene_facts('1');native_window=next(w for w in facts['facts']['windows'] if w['incarnation']==identity)
   check('pointerElmMinimizeNativeState',native_window['minimized'] and not native_window['acceptsInput'] and not native_window['shouldRenderAny'],window=native_window)
   check('minimizeReceiptThenAuthoritativeDOM',minimized['label'].startswith('Restore ') and projection()['transaction']=='Committed',projection=projection())
   click(minimized)
   restored=wait(lambda:row('Open'));facts=client.scene_facts('2');native_window=next(w for w in facts['facts']['windows'] if w['incarnation']==identity)
   check('pointerElmRestoreNativeState',not native_window['minimized'] and native_window['acceptsInput'] and facts['facts']['focused']==identity,window=native_window)
   check('restoreReceiptThenAuthoritativeDOM',restored['label'].startswith('Minimize ') and projection()['transaction']=='Committed',projection=projection())
   def backend():
    def is_backend(p):
     try:args=Path(f"/proc/{p['pid']}/cmdline").read_bytes().split(b'\0')
     except FileNotFoundError:return False
     return args[:3]==[b'/usr/bin/python3',b'-B',str(build_path.parent/'inputs/adapter/daemon.py').encode()]
    return next((p for p in s.host.descendants() if is_backend(p)),None)
   def frames(prefix):
    return [json.loads(line.split(prefix,1)[1]) for line in (OUTPUT/'elm-webview.log').read_text().splitlines() if line.startswith(prefix)]
   old_backend=wait(backend)
   old_binding=[frame['binding'] for frame in frames('backend-frame: ') if frame['kind']=='attached'][-1]
   report['faultInjection']={'oldBackend':old_backend,'oldBinding':old_binding,'signal':'SIGSTOP then SIGKILL after actual Pending UI'}
   os.kill(old_backend['pid'],signal.SIGSTOP)
   click(restored)
   pending_projection=wait(lambda:projection() if projection() and projection()['transaction']=='Pending' else None)
   check('pendingRequestDisablesAllWindowActions',all(g['disabled'] for g in pending_projection['groups']) and pending_projection['picker'] is None,projection=pending_projection)
   check('pendingRequestHasNoOptimisticMinimize',not next(w for w in client.scene_facts('3')['facts']['windows'] if w['incarnation']==identity)['minimized'])
   interrupted_journal=[frame for frame in frames('frontend-request: ') if frame['kind']=='window-effect']
   report['interruptedJournal']=interrupted_journal
   os.kill(old_backend['pid'],signal.SIGKILL)
   lost=wait(lambda:projection() if projection() and projection()['phase']=='Detached' and projection()['transaction']=='Unknown' and projection()['reconnect'] else None)
   check('backendLossPreservesUnknownAndDisablesActions',all(g['disabled'] for g in lost['groups']) and lost['picker'] is None,projection=lost)
   wait(lambda:'backend-exit: waited=1 normal=0 code=-1' in (OUTPUT/'elm-webview.log').read_text())
   click(lost['reconnect'])
   recovered=wait(lambda:row('Open'))
   fresh_binding=[frame['binding'] for frame in frames('backend-frame: ') if frame['kind']=='attached'][-1]
   check('explicitReconnectUsesFreshNativeBinding',fresh_binding!=old_binding,old=old_binding,new=fresh_binding)
   check('freshSnapshotPrecedesAdmissionWithoutReplay',projection()['transaction']=='Unknown' and [f for f in frames('frontend-request: ') if f['kind']=='window-effect']==interrupted_journal and not next(w for w in client.scene_facts('4')['facts']['windows'] if w['incarnation']==identity)['minimized'],projection=projection())
   requests=[frame for frame in frames('frontend-request: ') if frame['kind']=='window-effect'];stale=dict(requests[-1]);stale['binding']=old_binding
   try:stale_result=client.request(stale)
   except Refused as refusal:stale_result={'kind':'authenticated-native-refusal','reason':str(refusal)}
   report['staleBindingOutcome']=stale_result
   check('retiredBackendBindingRefusedNatively',stale_result=={'kind':'authenticated-native-refusal','reason':'binding-mismatch'} and not next(w for w in client.scene_facts('5')['facts']['windows'] if w['incarnation']==identity)['minimized'])
   click(recovered);recovered_min=wait(lambda:row('Minimized'))
   request=[frame for frame in frames('frontend-request: ') if frame['kind']=='window-effect'][-1]
   check('freshExplicitIntentAfterReconnect',int(request['intent']['request'])==int(interrupted_journal[-1]['intent']['request'])+1 and request['binding']==fresh_binding and projection()['transaction']=='Committed',request=request)
   click(recovered_min);wait(lambda:row('Open'))
   check('freshRestoreAfterReconnect',client.scene_facts('6')['facts']['focused']==identity and projection()['transaction']=='Committed')
   screenshot=OUTPUT/'elm-effects-restored.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['screenshotSHA256']=host.digest(screenshot)
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'many-documents'}));temp.replace(control)
   wait(lambda:len(s.data('clients'))==9)
   wait(lambda:group() if group() and group()['label'].startswith('Choose a window from ') else None)
   click(wait(group));many=wait(lambda:projection() if projection()['picker'] and len(projection()['picker']['selections'])==9 and projection()['focus'].startswith('picker:') else None)
   report['manyEntryProjection']=many
   screenshot=OUTPUT/'elm-many-picker.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['manyScreenshotSHA256']=host.digest(screenshot)
   check('manyEntryCloseRemainsVisible',many['picker']['close']['visible'],projection=many)
   for item in many['picker']['selections'][1:]:
    press_key(15);focused=wait(lambda:projection() if projection()['focus'].endswith(':'+item['incarnation']) else None)
    selected=next(row for row in focused['picker']['selections'] if row['incarnation']==item['incarnation'])
    check('keyboardChoiceRevealedInViewport',selected['visible'],selection=selected)
   target=many['picker']['selections'][-1]
   press_key(28);wait(lambda:projection()['picker'] is None and projection()['phase']=='Coherent' and projection()['transaction']=='Committed')
   check('longLabelLastChoiceActualKeyboardRecipient',journal()[-1]['intent']['incarnation']==target['incarnation'] and key_recipient(target['title']))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['passed']=True
  finally:
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
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
