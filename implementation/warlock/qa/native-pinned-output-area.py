"""UI-019: actual pinned native fixture plus original smaller-output/taskbar/client/draft journey; hardware/AT separate."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-area-recovery.py');wrapper=p.read_text()
start="    area_before=root_window();area_monitor=next(m for m in s.data('monitors') if m['id']==area_before['monitor']);area_effects=len(journal())\n"
before=r'''    check('NativePinnedApplicationFixture',s.ctl('dispatch',"hl.dsp.window.pin({window='address:"+area_before['address']+"'})").strip()=='ok')
    wait(lambda:root_window()['pinned'] and (projection() or {}).get('phase')=='Coherent')
    check('PinFixturePreservesWorkspaceSizeAndDraft',root_window()['workspace']==area_before['workspace'] and root_window()['size']==area_before['size'] and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa',before=area_before,after=root_window())
    area_before=root_window()
'''
needle='needle="sys.argv='
assert wrapper.count(needle)==1
inject="""assert journey.count(pinned_start)==1
journey=journey.replace(pinned_start,pinned_start+pinned_before)
journey=journey.replace(\"area_after['workspace']==area_before['workspace'] and\",\"area_after['pinned'] and area_after['workspace']==area_before['workspace'] and\")
journey=journey.replace(\"root_window()['at']==area_after['at'] and\",\"root_window()['pinned'] and root_window()['workspace']==area_before['workspace'] and root_window()['at']==area_after['at'] and\")
journey=journey.replace(\"report['nativeReachableAreaObserved']=True\",\"report['nativeReachableAreaObserved']=True\\n    report['nativePinnedOutputAreaObserved']=True\")
journey += \"    report['pinnedComposition']={'ordinaryAreaRunner':\"+repr(str(pinned_base))+\",'ordinaryAreaRunnerSHA256':sha(pathlib.Path(\"+repr(str(pinned_base))+\")),'setup':'Supported native pin dispatch before reconfigure; no post-failure geometry or focus workaround.'}\\n\"
"""
exec(compile(wrapper.replace(needle,inject+needle),str(p),'exec'),{'__name__':'__main__','__file__':str(pathlib.Path(__file__).resolve()),'pinned_start':start,'pinned_before':before,'pinned_base':p})
