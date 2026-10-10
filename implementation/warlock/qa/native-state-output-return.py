"""UI-019: actual zero-output retirement/return with a pinned or minimized application before retirement; hardware/AT separate."""
import pathlib,sys
assert sys.argv[1:] in ([],['--pinned'],['--minimized'],['--guards'])
minimized=sys.argv[1:]==['--minimized'];guards=sys.argv[1:]==['--guards'];sys.argv=sys.argv[:1]
p=pathlib.Path(__file__).with_name('native-output-placement.py');wrapper=p.read_text()
activate_fixture=r'''    # Establish fixture focus through the real taskbar so the frontend also
    # retires its popup/bar keyboard custody before pinning or minimizing.
    state_activation=wait(lambda:group('Activate') or group('Minimize'))
    if state_activation['label'].startswith('Activate '):
     state_activate_effects=len(journal());sx,sy=state_activation['point'];state_monitor=next(m for m in s.data('monitors') if m['id']==root_window()['monitor']);sx+=state_monitor['x'];sy+=state_monitor['y']
     helper([str(POINTER),'1600','600'],input_text=f'move {int(sx)} {int(sy)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     wait(lambda:facts()['facts']['focused']==target and current_window()['workspaceVisible'] and transaction_state()=='Committed' and len(journal())==state_activate_effects+1)
     check('ActualTaskbarEstablishesRetirementFixtureFocusOnce',journal()[-1]['intent']['operation']=='activate' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1])
    state_before=root_window();state_effects=len(journal())
'''
setup=activate_fixture+r'''
    check('NativePinnedBeforeRetirementFixture',s.ctl('dispatch',"hl.dsp.window.pin({window='address:"+state_before['address']+"'})").strip()=='ok')
    wait(lambda:root_window()['pinned'] and (projection() or {}).get('phase')=='Coherent')
    check('PinnedFixturePreservesOriginalPlacement',root_window()['workspace']==state_before['workspace'] and root_window()['size']==state_before['size'] and root_window()['at']==state_before['at'] and len(journal())==state_effects,before=state_before,after=root_window())
'''
if minimized:
 setup=activate_fixture+r'''
    state_minimize=wait(lambda:group('Minimize'));sx,sy=state_minimize['point'];state_minimize_effects=len(journal());state_monitor=next(m for m in s.data('monitors') if m['id']==root_window()['monitor']);sx+=state_monitor['x'];sy+=state_monitor['y']
    helper([str(POINTER),'1600','600'],input_text=f'move {int(sx)} {int(sy)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    wait(lambda:current_window()['minimized'] and transaction_state()=='Committed' and len(journal())==state_minimize_effects+1 and (projection() or {}).get('phase')=='Coherent')
    check('TaskbarMinimizesRetirementFixtureOnce',journal()[-1]['intent']['operation']=='minimize' and journal()[-1]['intent']['incarnation']==target,request=journal()[-1])
    check('NativeMinimizedBeforeRetirementFixture',root_window()['workspace']==state_before['workspace'] and root_window()['size']==state_before['size'] and root_window()['at']==state_before['at'],before=state_before,after=root_window(),facts=current_window())
'''
marker='    report[\'nativeShortcutCurrentOutputObserved\']=True'
inject="""assert source.count(state_marker)==1
inputs[state_base.name]=sha(state_base)
source=source.replace(state_marker,state_marker+'\\n'+state_setup)
"""
needle='# Instrument the actual existing GTK entry only;'
assert wrapper.count(needle)==1
wrapper=wrapper.replace(needle,inject+needle)
final="sys.argv=[str(p),'--shortcut-output']"
assert wrapper.count(final)==1
tail="""assert source.count(\"    report['nativeOutputPlacementObserved']=True\")==1
source=source.replace(\"    report['nativeOutputPlacementObserved']=True\",\"    check('ReturnedApplicationPreservesRetiredState',root_window()['pinned']==state_expected_pin and not current_window()['minimized'],window=root_window(),facts=current_window())\\n    report['nativeOutputPlacementObserved']=True\\n    report['nativeStateOutputReturnObserved']=True\".replace('state_expected_pin',str(not state_minimized)))
if state_minimized:
 source=source.replace(\"activation=wait(lambda:group('Activate'));effect_count=\",\"activation=wait(lambda:group('Restore'));effect_count=\")
 source=source.replace(\"check('TaskbarActivatesReturnedApplicationExactlyOnce',journal()[-1]['intent']['operation']=='activate'\",\"check('TaskbarRestoresReturnedApplicationExactlyOnce',journal()[-1]['intent']['operation']=='restore'\")
source=source.replace(\"wait(lambda:facts()['facts']['focused']==target and len(journal())==effect_count+1)\",\"wait(lambda:facts()['facts']['focused']==target and len(journal())==effect_count+1 and transaction_state()=='Committed' and not current_window()['minimized'])\")
"""
guard_checks=r'''    guard_before=root_window();guard_owner=next(m for m in s.data('monitors') if m['id']==guard_before['monitor']);guard_journal=len(journal())
    check('CreateLiveGuardOutput',s.ctl('output','create','wayland').strip()=='ok')
    guard_monitors=wait(lambda:(ms:=s.data('monitors')) and len(ms)==2 and ms);guard_other=next(m for m in guard_monitors if m['id']!=guard_owner['id'])
    check('ConfigureLiveGuardOutput',s.ctl('eval','hl.monitor({output="'+guard_other['name']+'",mode="800x600@60",position="800x0",scale=1})').strip()=='ok')
    wait(lambda:any(m['name']==guard_other['name'] and m['x']==800 and m['width']==800 for m in s.data('monitors')) and (projection() or {}).get('phase')=='Coherent')
    check('FocusOtherOutputForPinGuard',s.ctl('dispatch','hl.dsp.focus({monitor="'+guard_other['name']+'"})').strip()=='ok')
    wait(lambda:any(m['name']==guard_other['name'] and m['focused'] for m in s.data('monitors')))
    guard_focus=facts()['facts']['focused'];guard_result=private_effect('activate',expected_status='Refused');guard_after=root_window()
    check('CrossOutputPinnedActivationRefusesWithoutTransfer',guard_result['reason']=='implicit-transfer-required' and guard_after['pinned'] and all(guard_after[k]==guard_before[k] for k in ['workspace','monitor','at','size']) and facts()['facts']['focused']==guard_focus and len(journal())==guard_journal,result=guard_result,before=guard_before,after=guard_after)
    check('SelectLivePinOwnerForWorkspaceMove',s.ctl('dispatch','hl.dsp.focus({monitor="'+guard_owner['name']+'"})').strip()=='ok')
    wait(lambda:any(m['name']==guard_owner['name'] and m['focused'] and m['activeWorkspace']['id']==guard_before['workspace']['id'] for m in s.data('monitors')))
    command='hl.dsp.workspace.move({workspace="'+str(guard_before['workspace']['id'])+'",monitor="'+guard_other['name']+'"})'
    check('MoveWorkspaceBetweenLiveOutputs',s.ctl('dispatch',command).strip()=='ok')
    wait(lambda:any(w['id']==guard_before['workspace']['id'] and w['monitor']==guard_other['name'] for w in s.data('workspaces')))
    guard_after=root_window()
    check('LiveWorkspaceMoveKeepsPinOnOldOutput',guard_after['pinned'] and guard_after['monitor']==guard_before['monitor'] and guard_after['workspace']['id']!=guard_before['workspace']['id'] and guard_after['at']==guard_before['at'] and guard_after['size']==guard_before['size'] and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa' and len(journal())==guard_journal,before=guard_before,after=guard_after)
    report['nativePinnedMigrationGuardsObserved']=True
'''
tail+="""if state_guards:
 guard_marker=\"    report['nativeStateOutputReturnObserved']=True\"
 assert source.count(guard_marker)==1
 source=source.replace(guard_marker,guard_marker+'\\n'+state_guard_checks)
"""
wrapper=wrapper.replace(final,tail+final)
exec(compile(wrapper,str(p),'exec'),{'__name__':'__main__','__file__':str(pathlib.Path(__file__).resolve()),'state_marker':marker,'state_setup':setup,'state_minimized':minimized,'state_base':p,'state_guards':guards,'state_guard_checks':guard_checks})
