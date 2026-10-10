"""REN-018 real draft/unrelated click and no-focus exclusion; original modal/MAX retained."""
import pathlib,sys
assert not sys.argv[1:]
def adapt_draft(source):
    needle="    check('MappedBlockingModalOnMAXOwner'"
    assert source.count(needle)==1
    setup="""    fixture_control('set-modal-draft')
    wait(lambda:any(e['kind']=='draft' and e.get('text')=='Warlock unsaved draft Ω' for e in events()))
"""
    source=source.replace(needle,setup+needle)
    needle="    fixture_control('retire-modal');"
    assert source.count(needle)==1
    addition=r'''    def draft():
     before=len([e for e in events() if e['kind']=='draft'])
     fixture_control('query-modal-draft')
     rows=wait(lambda:[e for e in events() if e['kind']=='draft'] if len([e for e in events() if e['kind']=='draft'])==before+1 else None)
     return rows[-1]
    saved=draft();check('RealGTKModalContainsUnsavedTypedDraft',saved['visible'] and saved['text']=='Warlock unsaved draft Ωa',draft=saved)
    modal_before=root(modal);journal_before=len(journal())
    # Preserve the original actual wl_surface input mask: MAX paint extends
    # farther than its intentionally retained 320x240 eligible input region.
    hit('UnrelatedEligibleWindowWithDraftModal',[200,180],'ELM-ACTIVATION-PEER')
    check('UnrelatedClickPreservesModalIncarnationAndPlacement',root(modal)['incarnation']==modal_before['incarnation'] and root(modal)['owner']==primary and root(modal)['geometry']==modal_before['geometry'] and root(modal)['acceptsInput'],before=modal_before,after=root(modal))
    before_keys=len([e for e in events() if e['kind']=='key'])
    helper([str(keyboard)],'key 48 1\nsleep 50\nkey 48 0\nsleep 100\nsync\n')
    keys=wait(lambda:[e for e in events() if e['kind']=='key'] if len([e for e in events() if e['kind']=='key'])==before_keys+1 else None)
    after=draft();check('UnrelatedWindowReceivesActualGTKKeyWithoutDraftLoss',keys[-1]['window']=='ELM-ACTIVATION-PEER' and keys[-1]['keyval']==98 and after==saved,key=keys[-1],before=saved,after=after)
    check('PhysicalUnrelatedDraftClickNeverAddsShellEffect',len(journal())==journal_before)
    report['nativeUnrelatedDraftObservation']={'modal':modal_before,'before':saved,'after':after,'actualGTKKey':keys[-1],'native':facts()}
    # The unrelated physical click legitimately raises its app over the modal.
    # Use the actual taskbar family action to expose the modal before testing
    # exclusion of a painted no-focus surface; never rearrange the stack by hand.
    select(primary,False);wait(lambda:facts()['facts']['focused']==modal)
    row=next(w for w in s.data('clients') if w['title']=='SCENE-MODAL');address='address:'+row['address']
    check('ApplyActualNativeNoFocusRule',s.ctl('dispatch',"hl.dsp.window.set_prop({prop='no_focus',value='1',window='"+address+"'})").strip()=='ok')
    box=root(modal)['geometry'];mx,my=round(box[0]+30),round(box[1]+50)
    peer_box=root(peer)['geometry'];check('NoFocusPointWithinActualOriginalPeerInputShape',peer_box[0]+130<mx<peer_box[0]+320 and peer_box[1]+120<my<peer_box[1]+240,point=[mx,my],peer=peer_box,modal=box)
    helper([str(POINTER),'800','600'],f'move {mx} {my}\nsleep 100\n')
    image=OUTPUT/'NoFocusModalPaint.png';helper(['/usr/bin/grim',str(image)])
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));offset=my*pix.get_rowstride()+mx*pix.get_n_channels();rgb=list(pix.get_pixels()[offset:offset+3]);check('NoFocusModalRemainsPainted',rgb[2]>180 and rgb[0]<80 and rgb[1]<80,image=str(image),sha256=sha(image),point=[mx,my],rgb=rgb)
    before_press=len([e for e in events() if e['kind']=='pressed']);before_release=len([e for e in events() if e['kind']=='released'])
    helper([str(POINTER),'800','600'],f'button 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    pressed=wait(lambda:[e for e in events() if e['kind']=='pressed'] if len([e for e in events() if e['kind']=='pressed'])==before_press+1 else None)
    released=wait(lambda:[e for e in events() if e['kind']=='released'] if len([e for e in events() if e['kind']=='released'])==before_release+1 else None)
    check('NativeNoFocusModalExcludedFromActualGTKClick',pressed[-1]['window']==released[-1]['window']=='ELM-ACTIVATION-PEER' and facts()['facts']['focused']==peer,pressed=pressed[-1],released=released[-1],native=facts())
    before_keys=len([e for e in events() if e['kind']=='key']);helper([str(keyboard)],'key 46 1\nsleep 50\nkey 46 0\nsleep 100\nsync\n')
    keys=wait(lambda:[e for e in events() if e['kind']=='key'] if len([e for e in events() if e['kind']=='key'])==before_keys+1 else None)
    after=draft();check('ActualNoFocusKeepsEligibleKeyboardAndDraft',keys[-1]['window']=='ELM-ACTIVATION-PEER' and keys[-1]['keyval']==99 and after==saved,key=keys[-1],draft=after)
    check('ClearActualNativeNoFocusRule',s.ctl('dispatch',"hl.dsp.window.set_prop({prop='no_focus',value='0',window='"+address+"'})").strip()=='ok')
    report['nativeNoFocusModalObservation']={'point':[mx,my],'image':str(image),'sha256':sha(image),'rgb':rgb,'pressed':pressed[-1],'released':released[-1],'actualGTKKey':keys[-1],'draft':after,'native':facts(),'allowsInputFalseUsedAsBlocker':False}
    report['nativeModalDraftFocusObserved']=True
'''
    source=source.replace(needle,addition+needle)
    source=source.replace("'native-max-modal-focus-' if FOCUS","'native-modal-draft-focus-' if FOCUS")
    source=source.replace("requirements=['ELM-REN-015','ELM-GNO-006'],scenarios=['max-input-region','max-modal-focus','hit-modal-redirect']","requirements=['ELM-REN-018'],scenarios=['ren-018']")
    needle='adapted=original[:start]+branch+original[end:]'
    assert source.count(needle)==1
    fixture="""adapted=original[:start]+branch+original[end:]
fixture_needle="FIXTURE=RUNTIME/'fixture.py'"
assert adapted.count(fixture_needle)==1
adapted=adapted.replace(fixture_needle,"FIXTURE=ROOT/'qa/modal-draft-fixture.py'")
"""
    return source.replace(needle,fixture)
p=pathlib.Path(__file__).with_name('native-max-modal-focus.py');source=p.read_text()
needle='source=adapt_modal(p.read_text())';assert source.count(needle)==1
source=source.replace(needle,'source=adapt_draft(adapt_modal(p.read_text()))')
exec(compile(source,str(p),'exec'),globals())
