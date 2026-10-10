"""Original UI-004 zero-window pin: real keyboard/AT launch and running-family routing."""
import hashlib, pathlib, sys

assert sys.argv[1:] in ([], ['--at-actions'])
at_actions = bool(sys.argv[1:])
p = pathlib.Path(__file__).with_name('native-window-feedback.py')
source = p.read_text()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for old, new in [
    ("ACCESSIBILITY=sys.argv[1:]==['--accessibility']", 'ACCESSIBILITY=True'),
    ("SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY", "SWITCHER=sys.argv[1:]==['--switcher']"),
]:
    assert source.count(old) == 1
    source = source.replace(old, new)

needle = "   if JUMP or KEYBOARD:"
assert source.count(needle) == 1
fixture = r'''   if PINS:
    zero_control=OUTPUT/'zero-editor-control.json';zero_fixture=OUTPUT/'zero-editor-fixture.py'
    original_zero_source=FIXTURE.read_text();initial="create('ELM-AUTHORITY-FIXTURE', 'red')\ncreate('ELM-ACTIVATION-PEER', 'green')"
    assert original_zero_source.count(initial)==1 and original_zero_source.count('control = Path(sys.argv[1])')==1 and original_zero_source.count('loop.run()')==1
    zero_source=original_zero_source.replace('control = Path(sys.argv[1])',"import os\nGLib.set_prgname('warlock-zero-editor')\ncontrol = Path(sys.argv[1])")
    zero_source=zero_source.replace(initial,"log('WARLOCK-ZERO-EDITOR','process-start',pid=os.getpid())\ncreate('WARLOCK-ZERO-EDITOR','green')")
    zero_source=zero_source.replace('loop.run()',"loop.run()\nlog('WARLOCK-ZERO-EDITOR','normal-exit',exitCode=0)")
    zero_fixture.write_text(zero_source)
    zero_desktop=catalog_root/'warlock-editor.desktop'
    zero_desktop.write_text('[Desktop Entry]\nType=Application\nName=Editor\nGenericName=Text editor\nStartupWMClass=warlock-zero-editor\nExec=/usr/bin/python3 -B '+str(zero_fixture)+' '+str(zero_control)+'\n')
    report['zeroEditorFixture']={'originalSHA256':sha(FIXTURE),'fixture':str(zero_fixture),'fixtureSHA256':sha(zero_fixture),'desktop':str(zero_desktop),'desktopSHA256':sha(zero_desktop),'scope':'Real original green GTK root only, matching declared startup class, actual process/key/normal-exit events. Launched solely through the existing catalog/GIO authority.'}
'''
source = source.replace(needle, fixture + needle)

needle = "     chosen=buttons[0];click({'visible':0<=chosen['x']<800 and 0<=chosen['y']<48,'point':[chosen['x']+chosen['width']/2,chosen['y']+chosen['height']/2]})"
assert source.count(needle) == 1
primary = r'''     report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-zero'],scope='Actual persistent pin/reorder/restart with physical keyboard or actual AT-SPI zero-window primary launch, native resulting GTK application, current running-pin routing without duplicate launch. Exact AT tree/Orca and client keyboard/pixels observed; independent original acceptance remains separate.')
     report['zeroKeyboardInputs']=zero_inputs;report['zeroAtActionMode']=zero_at_actions
     def zero_body():
      body=bar_body();p=projection()
      return body if body and p and p['phase']=='Coherent' and p['mode']=='closed' and body['publication']==p['publication'] else None
     def zero_focus():
      body=zero_body()
      return body if body and body.get('documentFocused') and any(b['id']==body['focus'] and not b['disabled'] for b in body['buttons']) else None
     def editor_at(stage,chosen):
      def observed():
       value=at_observe();focus=(value.get('reader') or {}).get('focus') or {};nodes=[n for n in value['nodes'] if n.get('pid')==web.pid and n['name']==chosen['accessibleName'] and n['role'] in ['button','push button','toggle button'] and any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in n['ancestors'])]
       return (value,nodes[0]) if len(nodes)==1 and {'enabled','sensitive','visible','showing','focused'}<=set(nodes[0]['states']) and focus.get('name')==chosen['accessibleName'] else None
      value,node=wait(observed);report.setdefault('zeroAtSnapshots',[]).append({'stage':stage,**value});check(stage+'ActualAtAndOrcaFocusedEditorAgree',node['name']==chosen['accessibleName'],node=node,reader=value['reader']);return node
     def editor_primary(stage,at=False):
      helper([str(keyboard)],'key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100\nsync\n')
      wait(lambda:(projection() or {}).get('mode')=='applications');key(1);wait(zero_focus);key(102)
      body=wait(zero_focus);chosen=next(b for b in body['buttons'] if b['identity']=='bar:pin:warlock-editor' and not b['disabled'])
      for _ in range(len(body['buttons'])+1):
       current=wait(zero_focus)
       if any(b['id']==current['focus'] and b['identity']==chosen['identity'] for b in current['buttons']):break
       prior=current['focus'];key(106);wait(lambda:(b:=zero_focus()) and b['focus']!=prior)
      body=wait(zero_focus);check(stage+'PhysicalKeyboardReachesCurrentPin',any(b['id']==body['focus'] and b['identity']==chosen['identity'] for b in body['buttons']),body=body)
      node=editor_at(stage,chosen)
      report.setdefault('zeroPrimaryControls',[]).append({'stage':stage,'chosen':chosen,'body':body})
      if at:
       receipt=OUTPUT/'zero-at-action.json';helper(['/usr/bin/python3','-B',str(ROOT/'qa/taskbar-at-action.py'),str(web.pid),node['identity'],node['name'],str(receipt)])
       value=json.loads(receipt.read_text());check('ActualAtSpiZeroPrimaryInvoked',value['passed'] and value['source']=='actual-at-spi-action',receipt=value);report['zeroAtAction']=value
      else:key(28)
     check('PinnedEditorInitiallyHasZeroNativeMembers',not any(w['application']=='warlock-zero-editor' for w in facts()['facts']['windows']) and buttons[0]['accessibleName']=='Open Editor',facts=facts(),button=buttons[0])
     editor_primary('ZeroWindowLaunch',zero_at_actions)
'''
source = source.replace(needle, primary)

needle = "     report['afterRestartOrder']=saved_order();report['afterRestartLaunches']=launches();report['nativePinJourneyObserved']=True"
assert source.count(needle) == 1
after = r'''     zero_events=zero_control.with_suffix('.events.jsonl')
     def editor_events():return [json.loads(l) for l in zero_events.read_text().splitlines()] if zero_events.exists() else []
     started=wait(lambda:next((e for e in editor_events() if e['kind']=='process-start'),None));zero_editor_pid=started['pid'];zero_editor_start=start_time(zero_editor_pid);zero_editor_pidfd=os.pidfd_open(zero_editor_pid)
     def editor_window():return next((w for w in facts()['facts']['windows'] if w['application']=='warlock-zero-editor'),None)
     window=wait(editor_window);zero_incarnation=window['incarnation'];check('LaunchedApplicationUsesExactCatalogStartupIdentity',len([w for w in facts()['facts']['windows'] if w['application']=='warlock-zero-editor'])==1 and any(w['incarnation']==zero_incarnation and w['label']=='WARLOCK-ZERO-EDITOR' for w in client.snapshot('899')['windows']) and saved_order()==report['beforeRestartOrder'],window=window,events=editor_events())
     before=len(journal());editor_primary('RunningPinActivation');wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and facts()['facts']['focused']==zero_incarnation)
     submitted=journal()[-1];check('RunningPinUsesNativeActivationWithoutDuplicateLaunch',submitted['intent']['incarnation']==zero_incarnation and submitted['intent']['operation']=='activate' and len(launches())==1 and saved_order()==report['beforeRestartOrder'],request=submitted,facts=facts())
     event_before=len(editor_events());key(30);delivered=editor_events()[event_before:];check('LaunchedEditorActuallyReceivesKeyboard',any(e['kind']=='key' and e['keyval']==97 for e in delivered),events=delivered)
     image=OUTPUT/'zero-editor-active.png';helper(['/usr/bin/grim',str(image)])
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();green=sum(1 for y in range(100,min(600,pix.get_height())) for x in range(min(800,pix.get_width())) if pixels[y*stride+x*channels+1]>100 and pixels[y*stride+x*channels+1]>pixels[y*stride+x*channels]+30 and pixels[y*stride+x*channels+1]>pixels[y*stride+x*channels+2]+30)
     check('LaunchedEditorHasActualNativeGreenPixels',green>1000,greenPixels=green,image=str(image),sha256=sha(image));report['zeroEditorPixels']={'path':str(image),'sha256':sha(image),'greenPixels':green,'facts':facts(),'body':zero_body()}
     before=len(journal());editor_primary('ActivePinMinimize');wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and editor_window()['minimized'])
     check('ActiveRunningPinMinimizesWithoutNewLaunch',journal()[-1]['intent']['operation']=='minimize' and journal()[-1]['intent']['incarnation']==zero_incarnation and len(launches())==1 and saved_order()==report['beforeRestartOrder'],request=journal()[-1],facts=facts())
     report['zeroEditorEvents']=editor_events();report['zeroOrcaSpeech']=[json.loads(l) for l in (OUTPUT/'orca-utterances.jsonl').read_text().splitlines()]
     report['nativeTaskbarZeroKeyboardObserved']=not zero_at_actions;report['nativeTaskbarZeroAtActionObserved']=zero_at_actions
'''
source = source.replace(needle, after + '\n' + needle)

needle = "   if MOTION and 'motion_socket' in globals():motion_socket.close()"
assert source.count(needle) == 1
cleanup = r'''   if 'zero_editor_pidfd' in locals():
    import select
    if not select.select([zero_editor_pidfd],[],[],0)[0]:
     assert start_time(zero_editor_pid)==zero_editor_start
     zero_control.write_text(json.dumps({'op':'quit'}));wait(lambda:bool(select.select([zero_editor_pidfd],[],[],0)[0]))
    check('GioLaunchedOwnedEditorExitsNormally',any(e['kind']=='normal-exit' and e['exitCode']==0 for e in editor_events()),events=editor_events(),pid=zero_editor_pid,start=zero_editor_start)
    os.close(zero_editor_pidfd)
'''
source = source.replace(needle, cleanup + needle)
inputs = {p.name: sha(p), pathlib.Path(__file__).name: sha(pathlib.Path(__file__)), **{n: sha(p.with_name(n)) for n in ['accessibility-session.py', 'accessibility-inspector.py', 'accessibility-reader.py', 'taskbar-at-action.py']}}
sys.argv = [str(p), '--taskbar-pins']
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': str(p), 'zero_inputs': inputs, 'zero_at_actions': at_actions})
