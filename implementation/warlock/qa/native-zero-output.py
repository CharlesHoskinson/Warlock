"""Original UI-019 outputs-return: actual nested zero-output suspension and keyboard recovery; physical displays separate."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-output-retirement.py');source=p.read_text()
needle="    report['nativeOutputRetirementObserved']=True"
assert source.count(needle)==1
addition=r'''    report.update(requirements=['ELM-UI-019'],scenarios=['outputs-return'],scope='Actual nested Wayland all-output disappearance, zero presentable outputs/empty host topology, live suspended GUI, fresh returned view and physical keyboard recovery. Prior removal/replacement/drag journey retained. Physical displays/AT/independent acceptance remain separate.')
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    focused=wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and b)
    old_topology=replacement_topology();old_views=old_topology['views'];old_serial=latest_shortcut()['serial'];before=root_window();before_effects=len(journal())
    live_outputs=s.data('monitors');report['zeroOutputAttempt']={'nativeBefore':live_outputs,'hostBefore':old_topology,'focusedBody':focused,'workspaceBefore':before['workspace'],'effectsBefore':before_effects}
    for native_output in live_outputs:
     check('RemoveZeroOutput'+native_output['name'],s.ctl('output','remove',native_output['name']).strip()=='ok')
    def empty_native():
     outputs=s.data('monitors');report['zeroOutputAttempt']['lastNativeOutputs']=outputs;return all(output['name']=='FALLBACK' for output in outputs)
    wait(empty_native)
    def last_topology():
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('view-topology: ')];return rows[-1] if rows else None
    empty=wait(lambda:(t:=last_topology()) and t['views']==[] and t)
    def zero_inspection():
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('surface-inspection: ')];return rows[-1] if rows else None
    suspended=wait(lambda:(r:=zero_inspection()) and r['body']['mode']=='closed' and any(l=='view-commit: popup=0 focus=0 publication='+r['publication'] for l in text().splitlines()) and r)
    report['zeroOutputAttempt']['suspendedInspection']=suspended
    check('ZeroOutputsSuspendWithLiveNativeAndGUI',web.poll() is None and s.host.processes and empty['locations']==[] and len(journal())==before_effects,topology=empty,nativeInternal=report['zeroOutputAttempt']['lastNativeOutputs'])
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    check('NoPopupPresentationOnInternalFallback',zero_inspection()['body']['mode']=='closed' and last_topology()['views']==[] and len(journal())==before_effects)
    check('CreateReturnedNativeOutput',s.ctl('output','create','wayland').strip()=='ok')
    returned=wait(lambda:(outputs:=[o for o in s.data('monitors') if o['name']!='FALLBACK']) and len(outputs)==1 and outputs)
    command='hl.monitor({output="'+returned[0]['name']+'",mode="800x600@60",position="0x0",scale=1})'
    check('ConfigureReturnedNativeOutput',s.ctl('eval',command).strip()=='ok')
    current=wait(lambda:(t:=last_topology()) and len(t['views'])==1 and t['locations'][0]['box']==[0,0,800,600] and t)
    reconciled=wait(lambda:(p:=projection()) and p.get('phase')=='Coherent' and p.get('mode')=='closed' and p)
    check('ReturnedOutputHasFreshIssuedIdentity',current['views'][0] not in old_views and int(current['views'][0]['id'])>max(int(v['id']) for v in old_views),before=old_topology,returned=current)
    check('ReturnedOutputCannotReplayOldPopupOrEffect',reconciled['mode']=='closed' and zero_inspection()['body']['mode']=='closed' and len(journal())==before_effects,projection=reconciled)
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    recovered=wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and any(x['accessibleName']=='Refresh applications' and not x['disabled'] for x in b['buttons']) and b)
    history=wait(lambda:(r:=latest_shortcut()) and int(r['serial'])>int(old_serial) and r)
    check('FallbackChordCannotMintShortcut',int(history['serial'])==int(old_serial)+1,before=old_serial,after=history['serial'])
    check('AllRetiredNativeShortcutDestinationsStayUnavailable',all(e['output'] is None for e in history['events'] if int(e['serial'])<=int(old_serial)),history=history)
    owner=int(re.search(r'popup=(\d+)',[l for l in text().splitlines() if l.startswith('view-commit: popup=')][-1]).group(1))
    check('ReturnedOutputOwnsActualKeyboardPopup',str(owner)==current['views'][0]['id'],body=recovered,view=current['views'][0])
    after=root_window();check('ReturnedOutputPreservesWorkspaceIdentity',after['workspace']['id']==before['workspace']['id'],before=before,after=after)
    physical('key 15 1\nsleep 50\nkey 15 0\nsleep 100');physical('key 15 1\nsleep 50\nkey 15 0\nsleep 100')
    wait(lambda:(b:=shortcut_popup_body()) and b.get('documentFocused') and any(x['id']==b.get('focus') and x['accessibleName']=='Refresh applications' for x in b['buttons']) and b)
    count=len(catalog_reads());physical('key 28 1\nsleep 50\nkey 28 0\nsleep 100');wait(lambda:len(catalog_reads())>count)
    check('ReturnedKeyboardRecoveryIssuesOnlyRead',len(journal())==before_effects and len(catalog_reads())>count,before=count,after=len(catalog_reads()))
    image=OUTPUT/'zero-output-return.png';helper(['/usr/bin/grim',str(image)]);report['zeroOutputPixels']={'path':str(image),'sha256':sha(image)}
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    check('ReturnedEscapeDismissesWithoutEffectReplay',len(journal())==before_effects)
    report['nativeZeroOutputReturnObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition)
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
