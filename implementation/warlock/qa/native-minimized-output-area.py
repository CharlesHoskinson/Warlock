"""UI-019: actual taskbar minimize before output reconfigure, then restore/input/draft/pixels; native hardware/AT acceptance separate."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-area-recovery.py');wrapper=p.read_text()
start="    area_before=root_window();area_monitor=next(m for m in s.data('monitors') if m['id']==area_before['monitor']);area_effects=len(journal())\n"
before=r'''    minimize=wait(lambda:group('Minimize'));click(minimize)
    wait(lambda:current_window()['minimized'] and transaction_state()=='Committed' and len(journal())==area_effects+1)
    check('TaskbarMinimizesBeforeOutputChangeExactlyOnce',journal()[-1]['intent']['operation']=='minimize' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1],window=root_window())
'''
opening="    check('SmallerOutputKeepsApplicationInputRegionReachable'"
closing="    wire_start=len((OUTPUT/'fixture.log').read_text().splitlines());"
after=r'''    check('OutputChangeKeepsApplicationMinimizedAndDraft',current_window()['minimized'] and len(journal())==area_effects+1 and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa',window=root_window(),draft=draft_rows()[-1])
    def area_click(x,y):
     helper([str(POINTER),'400','200'],input_text=f'move {int(x)} {int(y)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    restore=wait(lambda:group('Restore'));area_click(*restore['point'])
    wait(lambda:not current_window()['minimized'] and facts()['facts']['focused']==target and transaction_state()=='Committed' and len(journal())==area_effects+2)
    area_after=root_window();ax,ay=area_after['at'];aw,ah=area_after['size']
    check('PreviouslyMinimizedApplicationRestoresReachably',mx+area_monitor['reserved'][0]<=ax and ax+min(aw,32)<=mx+mw-area_monitor['reserved'][2] and my+area_monitor['reserved'][1]<=ay and ay+min(ah,32)<=my+mh-area_monitor['reserved'][3],before=area_before,after=area_after,monitor=area_monitor)
    check('PreviouslyMinimizedRestorePreservesWorkspaceSizeAndDraft',area_after['workspace']==area_before['workspace'] and area_after['size']==area_before['size'] and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa',before=area_before,after=area_after,draft=draft_rows()[-1])
    check('PreviouslyMinimizedRestoreCommitsExactlyOnce',journal()[-1]['intent']['operation']=='restore' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1],window=root_window())
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused'))
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
'''
needle='needle="sys.argv='
assert wrapper.count(needle)==1
inject="""assert journey.count(minimized_start)==1
journey=journey.replace(minimized_start,minimized_start+minimized_before)
begin=journey.index(minimized_opening);end=journey.index(minimized_closing,begin)
journey=journey[:begin]+minimized_after+journey[end:]
journey=journey.replace(\"report['nativeReachableAreaObserved']=True\",\"report['nativeReachableAreaObserved']=True\\n    report['nativeMinimizedOutputAreaObserved']=True\")
journey += \"    report['minimizedComposition']={'ordinaryAreaRunner':\"+repr(str(minimized_base))+\",'ordinaryAreaRunnerSHA256':sha(pathlib.Path(\"+repr(str(minimized_base))+\"))}\\n\"
"""
exec(compile(wrapper.replace(needle,inject+needle),str(p),'exec'),{'__name__':'__main__','__file__':str(pathlib.Path(__file__).resolve()),'minimized_start':start,'minimized_before':before,'minimized_opening':opening,'minimized_closing':closing,'minimized_after':after,'minimized_base':p})
