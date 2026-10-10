"""UI-004 native inactive/active taskbar after real output retirement; AT/independent acceptance separate."""
import ast,hashlib,pathlib,sys
assert not sys.argv[1:]
qa=pathlib.Path(__file__).resolve().parent;p=qa/'native-window-feedback.py';source=p.read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p.name:sha(p),pathlib.Path(__file__).name:sha(pathlib.Path(__file__))}
for name in ['native-shortcut-output.py','native-output-retirement.py']:
 wrapper=qa/name;tree=ast.parse(wrapper.read_text());values={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('needle','addition')}
 assert source.count(values['needle'])==1
 source=source.replace(values['needle'],values['needle']+'\n'+values['addition']);inputs[name]=sha(wrapper)
needle="retirement_fixture=None";assert source.count(needle)==1
fixture=r'''fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
original_taskbar_fixture=FIXTURE;fixture_source=FIXTURE.read_text();entry_needle='    content.put(entry,8,8)';assert fixture_source.count(entry_needle)==1
fixture_source=fixture_source.replace(entry_needle,entry_needle+"\n    entry.connect('changed',lambda entry:log(name,'draft',text=entry.get_text()))\n    entry.set_text('UNSAVED-WARLOCK-TASKBAR-DRAFT')")
FIXTURE=fixture_inputs/'taskbar-output-fixture.py';FIXTURE.write_text(fixture_source)
'''
source=source.replace(needle,fixture+'\n'+needle)
needle="    report['nativeOutputRetirementObserved']=True";assert source.count(needle)==1
addition=r'''    report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-inactive','taskbar-active'],scope='Real native output removal/replacement, raw native focus/visibility and actual taskbar primary pointer activation/minimize/restore with draft preservation. Original deadlines; no native focus workaround. AT/independent acceptance separate.')
    report['taskbarOutputComposition']=taskbar_inputs
    report['taskbarOutputFixture']={'original':str(original_taskbar_fixture),'originalSHA256':sha(original_taskbar_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'scope':'Original GTK entry with unsaved draft and text observer; no alternate focus/input/placement policy.'}
    taskbar_before=root_window();taskbar_facts=facts();taskbar_member=next(w for w in taskbar_facts['facts']['windows'] if w['incarnation']==target);taskbar_group=wait(lambda:group('Activate') or group('Minimize'))
    report['taskbarOutputAttempt']={'native':taskbar_before,'facts':taskbar_facts,'group':taskbar_group,'projection':projection()}
    check('InvisibleNativeMemberOffersActivate',not taskbar_member['workspaceVisible'] and not taskbar_member['pinned'] and not taskbar_member['minimized'] and taskbar_group['label'].startswith('Activate '),facts=taskbar_facts,group=taskbar_group)
    # The unchanged replacement schedule has two live 800x600 outputs. Use
    # actual native desktop extent, not the single-output click convenience.
    def taskbar_click(item):
     check('TaskbarPointerTargetWithinActualView',item['visible'],item=item)
     monitors=s.data('monitors');owner=next(m for m in monitors if m['id']==root_window()['monitor']);x,y=item['point'];x+=owner['x'];y+=owner['y'];vw=max(m['x']+m['width']/m['scale'] for m in monitors);vh=max(m['y']+m['height']/m['scale'] for m in monitors)
     helper([str(POINTER),str(int(vw)),str(int(vh))],input_text=f'move {round(x)} {round(y)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    def taskbar_picture(stage,minimized):
     image=OUTPUT/(stage+'.png');helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();native=root_window();left=max(0,int(native['at'][0])+12);top=max(0,int(native['at'][1])+48);right=min(pix.get_width(),int(native['at'][0]+native['size'][0])-12);bottom=min(pix.get_height(),int(native['at'][1]+native['size'][1])-12)
     red=sum(1 for py in range(top,bottom) for px in range(left,right) if pixels[py*stride+px*channels]>180 and pixels[py*stride+px*channels+1]<70 and pixels[py*stride+px*channels+2]<70)
     check(stage+'ActualWindowPresentation',red==0 if minimized else red>1000,redPixels=red,region=[left,top,right,bottom],image=str(image),sha256=sha(image))
     receipt={'path':str(image),'sha256':sha(image),'native':native,'redPixels':red};report.setdefault('taskbarOutputImages',[]).append(receipt);return receipt
    taskbar_effects=len(journal());taskbar_click(taskbar_group)
    wait(lambda:current_window()['workspaceVisible'] and facts()['facts']['focused']==target and transaction_state()=='Committed' and len(journal())==taskbar_effects+1)
    check('RetiredOutputTaskbarActivationCommitsOnce',journal()[-1]['intent']['operation']=='activate' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1])
    taskbar_picture('taskbar-output-activated',False)
    fixture_events=control.with_suffix('.events.jsonl')
    def taskbar_drafts():return [json.loads(l) for l in fixture_events.read_text().splitlines() if l.strip() and json.loads(l).get('kind')=='draft' and json.loads(l).get('window')=='ELM-AUTHORITY-FIXTURE']
    check('ActivationPreservesOriginalWorkspaceSizeDraft',root_window()['workspace']==taskbar_before['workspace'] and root_window()['size']==taskbar_before['size'] and taskbar_drafts()[-1]['text']=='UNSAVED-WARLOCK-TASKBAR-DRAFT',before=taskbar_before,after=root_window(),draft=taskbar_drafts()[-1])
    active_group=wait(lambda:group('Minimize'));taskbar_click(active_group)
    wait(lambda:current_window()['minimized'] and facts()['facts']['focused']!=target and transaction_state()=='Committed' and len(journal())==taskbar_effects+2)
    check('VisibleActiveMemberMinimizesOnce',journal()[-1]['intent']['operation']=='minimize' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1],facts=facts())
    taskbar_picture('taskbar-output-minimized',True)
    restored_group=wait(lambda:group('Restore'));taskbar_click(restored_group)
    wait(lambda:not current_window()['minimized'] and current_window()['workspaceVisible'] and facts()['facts']['focused']==target and transaction_state()=='Committed' and len(journal())==taskbar_effects+3)
    check('MinimizedMemberRestoresOnce',journal()[-1]['intent']['operation']=='restore' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1])
    native=root_window();entry_x=native['at'][0]+20;entry_y=native['at'][1]+20;event_start=len(fixture_events.read_text().splitlines())
    taskbar_click({'visible':0<=entry_x<800 and 48<=entry_y<600,'point':[entry_x,entry_y]})
    physical('key 107 1\nsleep 50\nkey 107 0\nsleep 100');physical('key 30 1\nsleep 50\nkey 30 0\nsleep 100')
    wait(lambda:taskbar_drafts()[-1]['text']=='UNSAVED-WARLOCK-TASKBAR-DRAFTa')
    new_events=[json.loads(l) for l in fixture_events.read_text().splitlines()[event_start:] if l.strip()]
    check('ActualClientPointerKeyboardAndDraftAfterRecovery',any(e.get('kind')=='pressed' and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_events) and any(e.get('kind')=='key' and e.get('keyval')==97 and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_events) and len(journal())==taskbar_effects+3,events=new_events,draft=taskbar_drafts()[-1])
    report['taskbarOutputPixels']=taskbar_picture('taskbar-output-recovered',False)
    report['nativeTaskbarOutputFocusObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition)
sys.argv=[str(p),'--shortcut-output']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'taskbar_inputs':inputs})
