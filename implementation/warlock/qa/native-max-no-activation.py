"""Original committed two-MAX journey plus a both-excluded no-activation case.

Add a private, source-bound GTK shape control; preserve frozen fixture, host,
original positive oracles, six-second deadlines, pointer cadence and cleanup.
No claim that the shape commit retained cached pointer focus or raced a button.
"""
import pathlib,sys
assert not sys.argv[1:]

def add_fixture(original):
    needle="retirement_fixture=None\n"
    assert original.count(needle)==1
    addition=r'''no_activation_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');no_activation_inputs.mkdir(mode=0o700,exist_ok=True)
original_no_activation_fixture=FIXTURE
no_activation_fixture_source=FIXTURE.read_text()
no_activation_fixture_needle="        elif request['op'] == 'input-full':"
assert no_activation_fixture_source.count(no_activation_fixture_needle)==1
no_activation_fixture_addition="""        elif request['op'] == 'both-input-holes':
            for name in ['ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER']:
                surface=windows[name].get_surface()
                assert surface.get_display().supports_input_shapes()
                region=cairo.Region()
                rectangles=[(0,0,320,60),(0,60,70,60),(130,60,190,60),(0,120,320,120)]
                for rectangle in rectangles:region.union(cairo.RectangleInt(*rectangle))
                surface.set_input_region(region)
                windows[name].queue_draw()
                log(name,'mask',rectangles=rectangles,both=True)
        elif request['op'] == 'primary-input-full':
            windows['ELM-AUTHORITY-FIXTURE'].get_surface().set_input_region(None)
            windows['ELM-AUTHORITY-FIXTURE'].queue_draw()
            log('ELM-AUTHORITY-FIXTURE','mask',full=True)
"""
FIXTURE=no_activation_inputs/'no-activation-fixture.py'
FIXTURE.write_text(no_activation_fixture_source.replace(no_activation_fixture_needle,no_activation_fixture_addition+no_activation_fixture_needle))
no_activation_fixture={'originalPath':str(original_no_activation_fixture),'originalSHA256':sha(original_no_activation_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'Additional both-root input holes and primary full-region recovery; existing controls/controllers/colors/roots unchanged.'}
'''
    original=original.replace(needle,addition+needle)
    needle="if focus_host:report['focusHostAdaptation']=focus_host"
    assert original.count(needle)==1
    return original.replace(needle,"report['noActivationFixture']=no_activation_fixture\n"+needle)

def adapt_no_activation(source):
    needle='original=path.read_text()'
    assert source.count(needle)==1
    source=source.replace(needle,'original=add_fixture(path.read_text())')
    source=source.replace('hashlib.sha256(original.encode()).hexdigest()',
                          'hashlib.sha256(path.read_bytes()).hexdigest()')
    needle="    action(peer,'Restore');wait(lambda:root(peer)['fullscreenMode']==0)"
    assert source.count(needle)==1
    addition=r'''    prior_scene=wait(ready_scene)
    fixture_control('both-input-holes')
    wait(lambda:len([e for e in events() if e['kind']=='mask' and e.get('both')])==2)
    x,y=round(second[0]+100),round(second[1]+90)
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\n')
    no_hit_scene=wait(lambda:next((scene for scene in [ready_scene()] if scene and scene['sceneRevision']!=prior_scene['sceneRevision']),None))
    before_facts=facts();before_events=[e for e in events() if e['kind'] in ['pressed','released']];before_journal=len(journal())
    before_packet=scene_packet();before_hit=max([int(hit['sequence']) for hit in before_packet['hits']] or [0])
    image=OUTPUT/'BothExcludedPoint.png';helper(['/usr/bin/grim',str(image)])
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));offset=y*pix.get_rowstride()+x*pix.get_n_channels();red,green,blue=pix.get_pixels()[offset:offset+3]
    top=[id for id in no_hit_scene['order'] if id in [primary,peer]][-1]
    check('BothExcludedPaintRetainsTopMAXPixels',(red>180 and green<80 and blue<80) if top==primary else (green>180 and red<80 and blue<80),point=[x,y],rgb=[red,green,blue],paintScene=no_hit_scene,image=str(image),sha256=sha(image))
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    # Observe absence through the original six-second deadline; no extended wait.
    until=time.monotonic()+6
    while time.monotonic()<until:
     assert [e for e in events() if e['kind'] in ['pressed','released']]==before_events,'Ineligible MAX received a press or release'
     time.sleep(.02)
    observed=scene_packet();after_facts=facts()
    no_hit_receipts=[hit for hit in observed['hits'] if int(hit['sequence'])>before_hit and hit['ready'] and hit['sceneRevision']==no_hit_scene['sceneRevision'] and hit['recipient'] is None and hit['point']==[x,y]]
    check('BothExcludedConsumesCommittedSceneWithoutRecipient',bool(no_hit_receipts),paintScene=no_hit_scene,hitReceipts=no_hit_receipts,after=observed)
    check('BothExcludedNoGTKPressOrOrphanRelease',[e for e in events() if e['kind'] in ['pressed','released']]==before_events,eventsBefore=before_events,eventsAfter=events(),observationSeconds=6)
    check('BothExcludedNoActivationOrRaise',after_facts['facts']['focused']==before_facts['facts']['focused'] and [(w['incarnation'],w['stackPosition']) for w in after_facts['facts']['windows']]==[(w['incarnation'],w['stackPosition']) for w in before_facts['facts']['windows']],before=before_facts,after=after_facts)
    check('BothExcludedNoWindowEffectReplay',len(journal())==before_journal)
    check('BothExcludedPreservesBothMAXGeometry',root(primary)['fullscreenMode']==root(peer)['fullscreenMode']==1 and root(primary)['geometry']==first and root(peer)['geometry']==second)
    report['noActivationObservation']={'paintScene':no_hit_scene,'hitReceipts':no_hit_receipts,'image':str(image),'sha256':sha(image),'point':[x,y],'rgb':[red,green,blue],'before':before_facts,'after':after_facts,'cachedPointerRetainedObserved':False,'buttonCommitRaceAccepted':False}
    fixture_control('primary-input-full')
    wait(lambda:any(e['kind']=='mask' and e['window']=='ELM-AUTHORITY-FIXTURE' and e.get('full') for e in events()))
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\n')
    recovery_scene=wait(lambda:next((scene for scene in [ready_scene()] if scene and scene['sceneRevision']!=no_hit_scene['sceneRevision']),None))
    before_packet=scene_packet();before_hit=max([int(hit['sequence']) for hit in before_packet['hits']] or [0]);before=len([e for e in events() if e['kind']=='pressed'])
    helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    pressed=wait(lambda:[e for e in events() if e['kind']=='pressed'] if len([e for e in events() if e['kind']=='pressed'])==before+1 else None)
    released=wait(lambda:[e for e in events() if e['kind']=='released'] if len([e for e in events() if e['kind']=='released'])==before+1 else None)
    wait(lambda:facts()['facts']['focused']==primary)
    check('EligibleRecoveryActualPressReleaseOwner',pressed[-1]['window']==released[-1]['window']=='ELM-AUTHORITY-FIXTURE',pressed=pressed[-1],released=released[-1])
    observed=scene_packet();recovery_receipts=[hit for hit in observed['hits'] if int(hit['sequence'])>before_hit and hit['ready'] and hit['sceneRevision']==recovery_scene['sceneRevision'] and hit['recipient']==primary and hit['point']==[x,y]]
    check('EligibleRecoveryConsumesCommittedScene',bool(recovery_receipts),paintScene=recovery_scene,hitReceipts=recovery_receipts)
    report['eligibleRecoveryObservation']={'paintScene':recovery_scene,'hitReceipts':recovery_receipts,'pressed':pressed[-1],'released':released[-1]}
    report['nativeMAXNoActivationObserved']=True
'''
    source=source.replace(needle,addition+needle)
    source=source.replace("'native-max-input-region-' if FOCUS","'native-max-no-activation-' if FOCUS")
    return source

p=pathlib.Path(__file__).with_name('native-committed-max.py')
source=p.read_text()
needle="source=p.read_text()"
assert source.count(needle)==1
source=source.replace(needle,"source=adapt_no_activation(p.read_text())")
exec(compile(source,str(p),'exec'),globals())
