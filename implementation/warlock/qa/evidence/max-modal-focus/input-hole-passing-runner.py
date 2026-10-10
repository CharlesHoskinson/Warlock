"""Original two-MAX scene journey extended with declared modal-no-click policy.

Use the frozen GTK modal/retirement operations and real shell activation;
retain private host, exact tuple, original six-second waits and input cadence.
"""
import pathlib,sys
assert not sys.argv[1:]
def adapt_modal(source):
    needle="    action(peer,'Restore');wait(lambda:root(peer)['fullscreenMode']==0)"
    assert source.count(needle)==1
    addition=r'''    modal_policy=json.loads(s.ctl('-j','getoption','general:modal_parent_blocking'))
    check('NativeModalBlockingPolicyEnabled',modal_policy['bool'] is True,option=modal_policy)
    fixture_control('add-modal')
    modal=wait(lambda:next((row['incarnation'] for row in client.snapshot('600')['windows'] if row['label']=='SCENE-MODAL'),None))
    wait(lambda:any(w['incarnation']==modal and w['owner']==primary and w['acceptsInput'] and w['shouldRenderOwnMonitor'] for w in facts()['facts']['windows']))
    check('MappedBlockingModalOnMAXOwner',root(primary)['fullscreenMode']==1 and root(modal)['owner']==primary,owner=root(primary),modal=root(modal))
    select(peer,False);wait(lambda:facts()['facts']['focused']==peer)
    x,y=round(second[0]+100),round(second[1]+90)
    box=root(modal)['geometry'];check('ParentClickOutsideModalGeometry',not(box[0]<=x<box[0]+box[2] and box[1]<=y<box[1]+box[3]),point=[x,y],modal=box)
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\n')
    committed=wait(lambda:next((scene for scene in [ready_scene()] if scene and modal in scene['order']),None))
    before_facts=facts();before_events=[e for e in events() if e['kind'] in ['pressed','released']];before_journal=len(journal())
    check('ParentClickStartsOnUnrelatedRoot',before_facts['facts']['focused']==peer,before=before_facts)
    image=OUTPUT/'ModalParentPointBefore.png';helper(['/usr/bin/grim',str(image)])
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));offset=y*pix.get_rowstride()+x*pix.get_n_channels();red,green,blue=pix.get_pixels()[offset:offset+3]
    check('ParentPointPreservesOriginalUpperInputHolePixels',green>180 and red<80 and blue<80,point=[x,y],rgb=[red,green,blue],image=str(image),sha256=sha(image))
    before_packet=scene_packet();before_hit=max([int(hit['sequence']) for hit in before_packet['hits']] or [0])
    report['modalActivationAttempt']={'declaredPolicy':'Eligible modal keyboard focus; never forward parent coordinates as a modal click.','owner':primary,'modal':modal,'point':[x,y],'before':before_facts,'paintScene':committed,'image':str(image),'sha256':sha(image)}
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    report['modalActivationAttempt']['afterPress']=facts()
    wait(lambda:facts()['facts']['focused']==modal)
    after_facts=facts();after_scene=wait(ready_scene);observed=scene_packet()
    activation_hits=[hit for hit in observed['hits'] if int(hit['sequence'])>before_hit and hit['ready'] and hit['sceneRevision']==committed['sceneRevision'] and hit['recipient']==primary and hit['point']==[x,y] and (hit['properties'] & (1<<15))]
    check('BlockedOwnerActivationConsumesCommittedScene',bool(activation_hits),paintScene=committed,hitReceipts=activation_hits)
    check('ParentActivationFocusesAcceptedNativeModal',after_facts['facts']['focused']==modal,before=before_facts,after=after_facts)
    check('ParentCoordinatesNeverBecomeGTKModalClick',[e for e in events() if e['kind'] in ['pressed','released']]==before_events,before=before_events,after=events())
    check('ModalActivationPreservesMAXRootOrderAndGeometry',[i for i in after_scene['order'] if i in [primary,peer]]==[i for i in committed['order'] if i in [primary,peer]] and after_scene['order'].index(modal)>after_scene['order'].index(primary) and root(primary)['fullscreenMode']==root(peer)['fullscreenMode']==1 and root(primary)['geometry']==first and root(peer)['geometry']==second,paintBefore=committed,paintAfter=after_scene)
    check('PhysicalModalActivationAddsNoShellEffectReplay',len(journal())==before_journal)
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');before_keys=len([e for e in events() if e['kind']=='key'])
    helper([str(keyboard)],'key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n')
    keys=wait(lambda:[e for e in events() if e['kind']=='key'] if len([e for e in events() if e['kind']=='key'])==before_keys+1 else None)
    check('ActualGTKKeyboardReachesAcceptedModal',keys[-1]['window']=='SCENE-MODAL' and keys[-1]['keyval']==97,key=keys[-1])
    box=root(modal)['geometry'];mx,my=round(box[0]+200),round(box[1]+180);image_after=OUTPUT/'ModalRecipientAfter.png';helper(['/usr/bin/grim',str(image_after)])
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image_after));offset=my*pix.get_rowstride()+mx*pix.get_n_channels();mr,mg,mb=pix.get_pixels()[offset:offset+3]
    check('AcceptedModalHasNativePixelsAboveOwner',mb>180 and mr<80 and mg<80,point=[mx,my],rgb=[mr,mg,mb],image=str(image_after),sha256=sha(image_after))
    report['modalActivationObservation']={'owner':primary,'recipient':modal,'point':[x,y],'paintSceneBefore':committed,'paintSceneAfter':after_scene,'hitReceipts':activation_hits,'before':before_facts,'after':after_facts,'actualGTKKey':keys[-1],'images':[{'path':str(image),'sha256':sha(image)},{'path':str(image_after),'sha256':sha(image_after)}],'noSyntheticClick':True}
    before_events=[e for e in events() if e['kind'] in ['pressed','released']]
    select(peer,False);wait(lambda:facts()['facts']['focused']==peer)
    before=len(journal());select(primary,False);wait(lambda:facts()['facts']['focused']==modal)
    check('SharedSelectorTaskbarMAXFamilyActivation',len(journal())==before+1 and journal()[-1]['intent']['incarnation']==primary,receipt=journal()[-1],native=facts())
    check('TaskbarModalActivationNeverSynthesizesGTKClick',[e for e in events() if e['kind'] in ['pressed','released']]==before_events,before=before_events,after=events())
    report['taskbarModalActivationObservation']={'intent':journal()[-1],'native':facts(),'recipient':modal,'noSyntheticClick':True}
    fixture_control('retire-modal');wait(lambda:not any(w['incarnation']==modal for w in facts()['facts']['windows']))
    select(peer,False);wait(lambda:facts()['facts']['focused']==peer)
    hit('RetiredModalParentEligibleAgain',[100,90],'ELM-AUTHORITY-FIXTURE')
    report['nativeMAXModalFocusObserved']=True
'''
    source=source.replace(needle,addition+needle)
    source=source.replace("'native-max-input-region-' if FOCUS","'native-max-modal-focus-' if FOCUS")
    needle="requirements=['ELM-REN-015'],scenarios=['max-input-region']"
    assert source.count(needle)==1
    return source.replace(needle,"requirements=['ELM-REN-015','ELM-GNO-006'],scenarios=['max-input-region','max-modal-focus','hit-modal-redirect']")
p=pathlib.Path(__file__).with_name('native-committed-max.py');source=p.read_text()
needle='source=p.read_text()';assert source.count(needle)==1
source=source.replace(needle,'source=adapt_modal(p.read_text())')
exec(compile(source,str(p),'exec'),globals())
