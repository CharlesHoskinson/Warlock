"""UI-019 original zero-output journey plus real visible taskbar/application draft recovery; nested, not hardware acceptance."""
import ast,hashlib,pathlib,sys
assert not sys.argv[1:]
qa=pathlib.Path(__file__).resolve().parent;p=qa/'native-window-feedback.py';source=p.read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p.name:sha(p),pathlib.Path(__file__).name:sha(pathlib.Path(__file__))}
for name in ['native-shortcut-output.py','native-output-retirement.py','native-zero-output.py']:
 wrapper=qa/name;tree=ast.parse(wrapper.read_text());values={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('needle','addition')}
 assert source.count(values['needle'])==1
 source=source.replace(values['needle'],values['needle']+'\n'+values['addition']);inputs[name]=sha(wrapper)
# Instrument the actual existing GTK entry only; no alternate input/placement policy.
needle="retirement_fixture=None";assert source.count(needle)==1
fixture=r'''fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
original_placement_fixture=FIXTURE;fixture_source=FIXTURE.read_text();entry_needle='    content.put(entry,8,8)';assert fixture_source.count(entry_needle)==1
fixture_source=fixture_source.replace(entry_needle,entry_needle+"\n    entry.connect('changed',lambda entry:log(name,'draft',text=entry.get_text()))\n    entry.set_text('UNSAVED-WARLOCK-OUTPUT-DRAFT')")
FIXTURE=fixture_inputs/'output-placement-fixture.py';FIXTURE.write_text(fixture_source)
'''
source=source.replace(needle,fixture+'\n'+needle)
needle="    report['nativeZeroOutputReturnObserved']=True";assert source.count(needle)==1
addition=r'''    report['outputPlacementComposition']=placement_inputs
    report['outputPlacementFixture']={'original':str(original_placement_fixture),'originalSHA256':sha(original_placement_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'scope':'Actual original GTK entry receives an unsaved initial draft and changed-text observer; native client Wayland trace observes release. No replacement native focus/input/placement logic.'}
    placement_before=before;placement_after=root_window();monitor=next(m for m in s.data('monitors') if m['id']==placement_after['monitor'])
    x,y=placement_after['at'];width,height=placement_after['size'];ox,oy=monitor['x'],monitor['y'];ow,oh=monitor['width']/monitor['scale'],monitor['height']/monitor['scale']
    check('ReturnedApplicationHasReachableNativeOrigin',ox<=x and x+min(width,32)<=ox+ow and oy+monitor['reserved'][1]<=y and y+min(height,32)<=oy+oh,before=placement_before,after=placement_after,monitor=monitor)
    check('ReturnedApplicationPreservesOriginalSizeAndWorkspace',placement_after['size']==placement_before['size'] and placement_after['workspace']==placement_before['workspace'],before=placement_before,after=placement_after)
    fixture_events=control.with_suffix('.events.jsonl')
    def draft_rows():return [json.loads(l) for l in fixture_events.read_text().splitlines() if l.strip() and json.loads(l).get('kind')=='draft' and json.loads(l).get('window')=='ELM-AUTHORITY-FIXTURE']
    check('ReturnedApplicationKeepsUnsavedDraft',draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFT',events=draft_rows())
    activation=wait(lambda:group('Activate'));effect_count=len(journal());click(activation)
    wait(lambda:facts()['facts']['focused']==target and len(journal())==effect_count+1)
    check('TaskbarActivatesReturnedApplicationExactlyOnce',journal()[-1]['intent']['operation']=='activate' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1],window=root_window())
    native=root_window();entry_x=native['at'][0]+20;entry_y=native['at'][1]+20
    event_start=len(fixture_events.read_text().splitlines());wire_start=len((OUTPUT/'fixture.log').read_text().splitlines());click({'visible':0<=entry_x<800 and 48<=entry_y<600,'point':[entry_x,entry_y]})
    def new_input():return [json.loads(l) for l in fixture_events.read_text().splitlines()[event_start:] if l.strip()]
    def click_wire():
     lines=(OUTPUT/'fixture.log').read_text().splitlines()[wire_start:];buttons=[(i,m.groups()) for i,l in enumerate(lines) if (m:=re.search(r'wl_pointer#(\d+)\.button\((\d+), \d+, 272, ([01])\)',l))]
     if len(buttons)<2:return None
     first,last=buttons[0],buttons[1];proxy=first[1][0]
     return {'proxy':proxy,'pressSerial':first[1][1],'releaseSerial':last[1][1],'lines':lines[first[0]:last[0]+1]} if first[1][2]=='1' and last[1][2]=='0' and last[1][0]==proxy and int(last[1][1])>int(first[1][1]) and not any(re.search(r'wl_pointer#'+proxy+r'\.(enter|leave)\(',l) for l in lines[first[0]+1:last[0]]) else None
    release=wait(click_wire)
    physical('key 107 1\nsleep 50\nkey 107 0\nsleep 100');physical('key 30 1\nsleep 50\nkey 30 0\nsleep 100')
    wait(lambda:draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa')
    check('ReturnedApplicationReceivesActualPointerAndKeyboard',any(e.get('kind')=='pressed' and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_input()) and any(e.get('kind')=='key' and e.get('keyval')==97 and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_input()),events=new_input(),draft=draft_rows()[-1],nativeRelease=release)
    check('ClientInputCannotReplayWindowEffects',len(journal())==effect_count+1)
    image=OUTPUT/'returned-application.png';helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();native=root_window();left=max(0,int(native['at'][0])+12);top=max(0,int(native['at'][1])+48);right=min(pix.get_width(),int(native['at'][0]+native['size'][0])-12);bottom=min(pix.get_height(),int(native['at'][1]+native['size'][1])-12)
    red=sum(1 for py in range(top,bottom) for px in range(left,right) if pixels[py*stride+px*channels]>180 and pixels[py*stride+px*channels+1]<70 and pixels[py*stride+px*channels+2]<70)
    check('ReturnedApplicationActuallyPaints',right>left and bottom>top and red>100,redPixels=red,region=[left,top,right,bottom])
    report['returnedApplicationPixels']={'path':str(image),'sha256':sha(image),'native':native,'redPixels':red}
    report['nativeOutputPlacementObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition)
sys.argv=[str(p),'--shortcut-output']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'placement_inputs':inputs})
