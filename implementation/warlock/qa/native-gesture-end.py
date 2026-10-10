"""UX-021 actual caption/edge cancellation and captured owner retirement.

Retain the current caption admission journey and original protected host/clocks.
Floating rollback/retirement addition; original two-output capture and wider
fullscreen/tiled/snap/device/AT acceptance remain open.
"""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-caption-gesture.py');source=p.read_text()
needle="    image=OUTPUT/'caption-gesture.png'";assert source.count(needle)==1
addition=r'''    def peer_draft():
     before=len(events());fixture_control('query-peer-draft')
     return wait(lambda:next((e['text'] for e in events()[before:] if e['kind']=='peer-draft' and e['window']=='ELM-ACTIVATION-PEER'),None))
    peer_saved=peer_draft();peer_geometry=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
    def peer_unchanged():
     w=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
     return w['at']==peer_geometry['at'] and w['size']==peer_geometry['size'] and peer_draft()==peer_saved
    def box(w):return [*w['at'],*w['size']]
    for label,state,offset,end in [('CaptionMoveCancel','move',(180,24),(400,450)),('EdgeResizeCancel','resize',(300,216),(600,450))]:
     mode(state);old=root_window();before=ownership();x,y=round(old['at'][0]+offset[0]),round(old['at'][1]+offset[1])
     pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n)
     active=wait(lambda:owned(state));wait(lambda:received_owner(state,active['serial']))
     check(label+'OriginalCapturedOwner',active['owner']==target and int(active['serial'])==int(before['serial'])+1)
     pointer(f'move {end[0]} {end[1]}\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':end[0],'y':end[1]})
     moved=wait(lambda:root_window() if box(root_window())!=box(old) else None)
     physical('key 1 1\nsleep 50');ended=wait(lambda:owned('idle'));wait(lambda:received_owner('idle',ended['serial']))
     check(label+'EscapeRestoresCapturedFloatingGeometry',box(root_window())==box(old),before=old,moved=moved,after=root_window())
     check(label+'EndsOnceWithoutFocusOrDraftTheft',int(ended['serial'])==int(active['serial'])+1 and ended['owner'] is None and client.scene_facts('473')['facts']['focused']==target and draft()==saved and peer_unchanged())
     pointer('button 272 0\nsleep 100');check(label+'MouseReleaseCannotEndAgain',ownership()==ended)
     # Start another real resize while Escape remains physically held. Its old
     # key release is not cancellation of this new native gesture.
     mode('resize');old2=root_window();x,y=round(old2['at'][0]+300),round(old2['at'][1]+216)
     pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n)
     second=wait(lambda:owned('resize'));physical('key 1 0\nsleep 100')
     check(label+'EscapeReleaseKeepsNewOwner',ownership()==second and second['owner']==target)
     pointer('button 272 0\nsleep 100');second_end=wait(lambda:owned('idle'))
     check(label+'NewGestureEndsOnce',int(second_end['serial'])==int(second['serial'])+1 and box(root_window())==box(old2))
     report['gestures'].append({'name':label,'before':before,'active':active,'end':ended,'windowBefore':old,'windowMoved':moved,'windowAfter':root_window(),'secondActive':second,'secondEnd':second_end})
    # Retire the actual captured window while held, then map a fresh incarnation
    # with the same title. Neither old Gdk request nor release may act on it.
    mode('move');old=root_window();x,y=round(old['at'][0]+180),round(old['at'][1]+24)
    pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n)
    active=wait(lambda:owned('move'));pointer('move 600 450\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':600,'y':450})
    fixture_control('retire-primary');wait(lambda:not any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
    retired=wait(lambda:owned('idle'));check('CapturedOwnerRetirementEndsExactlyOnce',int(retired['serial'])==int(active['serial'])+1 and retired['owner'] is None and peer_unchanged(),before=active,after=retired)
    mode('deferred');fixture_control('replace-primary');replacement=wait(lambda:next((w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE'),None))
    replacement_id=wait(lambda:next((w['incarnation'] for w in client.snapshot('474')['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE' and w['incarnation']!=target),None))
    check('ReplacementHasNewNativeIncarnation',replacement_id!=target,oldIncarnation=target,newIncarnation=replacement_id)
    old_request=request('move');check('RetiredPressCannotStartReplacementGesture',ownership()==retired,request=old_request)
    pointer('button 272 0\nsleep 100');physical('key 1 0\nsleep 100')
    check('OldReleaseCannotMutateReplacementOrPeer',ownership()==retired and box(root_window())==box(replacement) and peer_unchanged())
    report['nativeGestureTerminalObserved']=True
    report['terminalScope']='Actual floating caption/edge Escape rollback, exact one native end, old Escape release during a new gesture and captured owner retirement/replacement. Full original two-output/native fullscreen/tiled/snap/device/AT acceptance remains open.'
'''
source=source.replace(needle,addition+needle).replace("'native-caption-gesture-' if DRAG","'native-gesture-end-' if DRAG")
exec(compile(source,str(p),'exec'),globals())
