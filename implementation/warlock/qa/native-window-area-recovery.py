"""Original output/application recovery plus actual smaller, negatively shifted usable-area recovery; wider hardware/AT acceptance separate."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-output-placement.py');wrapper=p.read_text()
journey=r'''    area_before=root_window();area_monitor=next(m for m in s.data('monitors') if m['id']==area_before['monitor']);area_effects=len(journal())
    command='hl.monitor({output="'+area_monitor['name']+'",mode="400x200@60",position="-400x-200",scale=1})'
    check('ConfigureActualSmallerNegativeOriginOutput',s.ctl('eval',command).strip()=='ok')
    area_monitor=wait(lambda:next((m for m in s.data('monitors') if m['name']==area_monitor['name'] and m['x']==-400 and m['y']==-200 and m['width']==400 and m['height']==200),None))
    wait(lambda:(projection() or {}).get('phase')=='Coherent');area_after=root_window();ax,ay=area_after['at'];aw,ah=area_after['size'];mx,my=area_monitor['x'],area_monitor['y'];mw,mh=area_monitor['width']/area_monitor['scale'],area_monitor['height']/area_monitor['scale']
    check('SmallerOutputKeepsApplicationInputRegionReachable',mx+area_monitor['reserved'][0]<=ax and ax+min(aw,32)<=mx+mw-area_monitor['reserved'][2] and my+area_monitor['reserved'][1]<=ay and ay+min(ah,32)<=my+mh-area_monitor['reserved'][3],before=area_before,after=area_after,monitor=area_monitor)
    check('SmallerOutputPreservesWorkspaceSizeAndDraft',area_after['workspace']==area_before['workspace'] and area_after['size']==area_before['size'] and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa',before=area_before,after=area_after,draft=draft_rows()[-1])
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused'))
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    minimize=wait(lambda:group('Minimize'))
    def area_click(x,y):
     helper([str(POINTER),'400','200'],input_text=f'move {int(x)} {int(y)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    area_click(*minimize['point']);restore=wait(lambda:group('Restore'))
    check('TaskbarMinimizesSmallerOutputApplicationOnce',len(journal())==area_effects+1 and journal()[-1]['intent']['operation']=='minimize' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1])
    area_click(*restore['point']);wait(lambda:facts()['facts']['focused']==target and len(journal())==area_effects+2)
    check('TaskbarRestoresSmallerOutputApplicationOnce',journal()[-1]['intent']['operation']=='restore' and journal()[-1]['intent']['incarnation']==target and root_window()['at']==area_after['at'] and root_window()['size']==area_before['size'],request=journal()[-1],window=root_window())
    wire_start=len((OUTPUT/'fixture.log').read_text().splitlines());event_start=len(fixture_events.read_text().splitlines());area_click(ax-mx+20,ay-my+20);release=wait(click_wire)
    physical('key 107 1\nsleep 50\nkey 107 0\nsleep 100');physical('key 48 1\nsleep 50\nkey 48 0\nsleep 100')
    wait(lambda:draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTab')
    check('SmallerOutputReceivesActualClientPointerAndKeyboard',any(e.get('kind')=='pressed' and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_input()) and any(e.get('kind')=='key' and e.get('keyval')==98 and e.get('window')=='ELM-AUTHORITY-FIXTURE' for e in new_input()) and len(journal())==area_effects+2,events=new_input(),nativeRelease=release,draft=draft_rows()[-1])
    area_image=OUTPUT/'smaller-output-application.png';helper(['/usr/bin/grim',str(area_image)])
    area_pix=GdkPixbuf.Pixbuf.new_from_file(str(area_image));area_pixels=area_pix.get_pixels();area_stride=area_pix.get_rowstride();area_channels=area_pix.get_n_channels()
    left=max(0,int(ax-mx)+2);right=min(area_pix.get_width(),int(ax-mx+aw)-2);top=max(0,int(ay-my)+2);bottom=min(area_pix.get_height(),int(ay-my+ah)-2)
    red=sum(1 for py in range(top,bottom) for px in range(left,right) if area_pixels[py*area_stride+px*area_channels]>180 and area_pixels[py*area_stride+px*area_channels+1]<70 and area_pixels[py*area_stride+px*area_channels+2]<70)
    check('SmallerOutputApplicationActuallyPaints',area_pix.get_width()==400 and area_pix.get_height()==200 and red>50,redPixels=red,region=[left,top,right,bottom])
    report['reachableAreaPixels']={'path':str(area_image),'sha256':sha(area_image),'native':root_window(),'redPixels':red}
    report['nativeReachableAreaObserved']=True
    report['reachableAreaComposition']={'placementRunner':str(area_placement_path),'placementRunnerSHA256':sha(area_placement_path),'runner':str(area_runner_path),'runnerSHA256':sha(area_runner_path)}
'''
needle="sys.argv=[str(p),'--shortcut-output']\nexec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'placement_inputs':inputs})"
assert wrapper.count(needle)==1
replacement="""end=\"    report['nativeOutputPlacementObserved']=True\"
assert source.count(end)==1
source=source.replace(end,end+'\\n'+area_journey)
sys.argv=[str(p),'--shortcut-output']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'placement_inputs':inputs,'area_placement_path':area_placement_path,'area_runner_path':area_runner_path})
"""
exec(compile(wrapper.replace(needle,replacement),str(p),'exec'),{'__name__':'__main__','__file__':str(p),'area_journey':journey,'area_placement_path':p,'area_runner_path':pathlib.Path(__file__).resolve()})
