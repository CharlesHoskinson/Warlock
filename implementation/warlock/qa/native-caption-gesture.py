"""UX-021 actual GTK/Gdk caption/edge requests and current recipient admission.

Bounded one-output addition. The original two-output drag capture remains failed;
no original crossing, caption cancellation/rollback, AT or release acceptance.
"""
import pathlib,sys
assert not sys.argv[1:]
root=pathlib.Path(__file__).resolve().parents[1]
source=(root/'qa/native-window-feedback.py').read_text()
source=source.replace("FIXTURE=RUNTIME/'fixture.py'","FIXTURE=ROOT/'qa/caption-gesture-fixture.py'")
source=source.replace("'native-drag-ownership-' if DRAG","'native-caption-gesture-' if DRAG")
source=source.replace("str(POINTER),'1600','600'","str(POINTER),'800','600'")
source=source.replace("if not (FOCUS or TASKVIEW or PRIMARY or SWITCHER or CHORD):fixture_control('hide-peer')","if not (FOCUS or TASKVIEW or PRIMARY or SWITCHER or CHORD or DRAG):fixture_control('hide-peer')")
start=source.index('   if DRAG:\n    check(\'CreateSecondWaylandOutput\'');end=source.index('   native=next',start)
source=source[:start]+'''   if DRAG:
    check('CaptionFixtureUsesActualOriginalOutput',[(m['name'],m['width'],m['height']) for m in s.data('monitors')]==[('WAYLAND-1',800,600)])
'''+source[end:]
start=source.index("if DRAG:\n LUA+=b'hl.monitor");end=source.index('if ACCESSIBILITY:',start)
source=source[:start]+'''if DRAG:
 report.update(requirements=['ELM-UX-021'],scenarios=['ux-021'],scope='Bounded actual one-output GTK/Gdk caption/edge input and current no-focus/modal/one-use press admission. Original two-output capture, wider cancellation/close, AT and acceptance remain open.')
'''+source[end:]
start=source.index('    wait(lambda:(projection() or {}).get(\'phase\')==\'Coherent\' and received_owner');end=source.index('   elif ATTENTION:',start)
branch=r'''    def events():
     path=control.with_suffix('.events.jsonl');return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    def wait_event(kind,before=0):return wait(lambda:next((e for e in events()[before:] if e['kind']==kind and e['window']=='ELM-AUTHORITY-FIXTURE'),None))
    def mode(value):
     before=len(events());fixture_control('gesture-mode-'+value);wait_event('gesture-mode',before)
    def draft():
     before=len(events());fixture_control('query-caption-draft');return wait_event('draft',before)['text']
    def request(value):
     before=len(events());fixture_control('gesture-request-'+value);return wait_event('native-request',before)
    peer_window=wait(lambda:next((w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER'),None));peer_selector='address:'+peer_window['address']
    if not peer_window['floating']:check('CaptionPeerFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
    check('CaptionPeerSize',s.ctl('dispatch',"hl.dsp.window.resize({x=260,y=220,window='"+peer_selector+"'})").strip()=='ok')
    check('CaptionPeerPosition',s.ctl('dispatch',"hl.dsp.window.move({x=480,y=300,window='"+peer_selector+"'})").strip()=='ok')
    wait(lambda:(projection() or {}).get('phase')=='Coherent' and received_owner('idle',ownership()['serial']))
    report['gestures']=[];saved=draft();check('ActualCaptionDraftIsPresent',saved=='Warlock caption draft Ω')
    for label,state,offset,delta in [('NativeCaptionMove','move',(180,24),(80,70)),('NativeEdgeResize','resize',(300,216),(50,40))]:
     mode(state);old=root_window();before=ownership();x,y=map(round,[old['at'][0]+offset[0],old['at'][1]+offset[1]]);delta=((400-x,300-y) if state=='move' else (600-x,450-y))
     pointer(f'move {x} {y}\nsleep 100');before_events=len(events());pointer('button 272 1\nsleep 50')
     wait_event('native-request',before_events);active=wait(lambda:owned(state));wait(lambda:received_owner(state,active['serial']))
     check(label+'UsesOriginalNativeRecipient',active['owner']==target and int(active['serial'])==int(before['serial'])+1,observation=active)
     pointer(f'move {x+delta[0]} {y+delta[1]}\nsleep 100');wait(lambda:report.setdefault('cursorObservations',[]).append(s.data('cursorpos')) or report['cursorObservations'][-1]=={'x':x+delta[0],'y':y+delta[1]})
     check(label+'KeepsOwnerWithoutShellPopup',ownership()==active and (projection() or {}).get('mode')=='closed')
     pointer('button 272 0\nsleep 100');ended=wait(lambda:owned('idle'));wait(lambda:received_owner('idle',ended['serial']))
     after=root_window();check(label+'ChangesNativeGeometry',after['at']!=old['at'] if state=='move' else after['size']!=old['size'],before=old,after=after)
     check(label+'EndsExactlyOnce',int(ended['serial'])==int(active['serial'])+1 and ended['owner'] is None)
     check(label+'PreservesUnsavedDraft',draft()==saved)
     report['gestures'].append({'name':label,'before':before,'active':active,'end':ended,'windowBefore':old,'windowAfter':after})
    # A real press remains held while native no-focus policy changes. Its Gdk
    # request retains the real seat/surface serial, not an injected grant.
    mode('deferred');old=root_window();x,y=round(old['at'][0]+180),round(old['at'][1]+24)
    pointer(f'move {x} {y}\nsleep 100');before_events=len(events());pointer('button 272 1\nsleep 50');wait_event('pressed',before_events)
    check('ApplyCurrentNativeNoFocusAfterPress',s.ctl('dispatch',"hl.dsp.window.set_prop({prop='no_focus',value='1',window='"+selector+"'})").strip()=='ok')
    before=ownership();before_facts=client.scene_facts('471')['facts'];req=request('move');after=ownership()
    check('NoFocusAfterPressCannotStartCaptionGesture',after['state']=='idle' and after==before,request=req,before=before,after=after)
    pointer('move 400 450\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':400,'y':450})
    check('RefusedCaptionPreservesNativeGeometryFocusAndDraft',root_window()['at']==old['at'] and root_window()['size']==old['size'] and client.scene_facts('471')['facts']['focused']==before_facts['focused'] and draft()==saved)
    check('ClearCurrentNativeNoFocus',s.ctl('dispatch',"hl.dsp.window.set_prop({prop='no_focus',value='0',window='"+selector+"'})").strip()=='ok')
    req=request('move');check('ConsumedNoFocusPressCannotReplayWhenEligible',ownership()==before,request=req)
    pointer('button 272 0\nsleep 100')
    # A mapped modal changes the family's recipient after the accepted press.
    old=root_window();x,y=round(old['at'][0]+180),round(old['at'][1]+24)
    pointer(f'move {x} {y}\nsleep 100');before_events=len(events());pointer('button 272 1\nsleep 50');wait_event('pressed',before_events)
    fixture_control('add-modal');modal=wait(lambda:next((w for w in s.data('clients') if w['title']=='SCENE-MODAL'),None))
    modal_id=wait(lambda:next((w['incarnation'] for w in client.snapshot('472')['windows'] if w['label']=='SCENE-MODAL'),None))
    modal_facts=wait(lambda:next((w for w in client.scene_facts('471')['facts']['windows'] if w['incarnation']==modal_id and w['owner']==target and w['workspaceVisible'] and not w['hidden']),None))
    check('ActualMappedModalBelongsToPressedParent',modal_facts['owner']==target,observation=modal_facts)
    before=ownership();before_facts=client.scene_facts('471')['facts'];req=request('resize');after=ownership()
    check('MappedModalAfterPressCannotStartParentEdgeResize',after==before and after['state']=='idle',request=req,before=before,after=after,modal=modal)
    fixture_control('retire-modal');wait(lambda:not any(w['title']=='SCENE-MODAL' for w in s.data('clients')))
    req=request('resize');check('ConsumedModalPressCannotReplayAfterRetirement',ownership()==before,request=req)
    pointer('button 272 0\nsleep 100');check('ModalRefusalPreservesCaptionDraft',draft()==saved)
    image=OUTPUT/'caption-gesture.png';helper(['/usr/bin/grim',str(image)]);report['captionPixels']={'path':str(image),'sha256':sha(image)}
    report['nativeCaptionGestureObserved']=True
'''
source=source[:start]+branch+source[end:]
sys.argv=[sys.argv[0],'--drag-ownership']
exec(compile(source,str(root/'qa/native-window-feedback.py'),'exec'))
