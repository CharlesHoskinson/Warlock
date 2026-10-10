"""Actual nested output removal/replacement with focused launcher and surviving keyboard recovery; physical hardware separate."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-shortcut-output.py');source=p.read_text()
needle="    report['nativeShortcutCurrentOutputObserved']=True"
assert source.count(needle)==1
addition=r'''    report.update(requirements=['ELM-UI-019'],scenarios=['output-remove'],scope='Actual nested Wayland output removal with a focused Apps query, declared surviving scope/keyboard recovery, workspace preservation, replacement view identity and no stale effect replay. Physical hotplug/AT/independent acceptance remain separate.')
    # Begin from the unchanged shortcut/drag/no-match journey above, now closed.
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and b)
    for code in [44,44]:physical(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100')
    body=wait(lambda:(b:=shortcut_popup_body()) and any(f['value']=='zzzzqvzz' for f in b.get('fields',[])) and b)
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    def latest_shortcut():
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')=='shell-shortcuts'];return rows[-1] if rows else None
    current=wait(lambda:(r:=latest_shortcut()) and int(r['serial'])>=5 and r)
    before=root_window();before_journal=len(journal());old_scope=location['scope'];old_serial=current['serial']
    check('LayerAndPopupChordsRetainKeyboardOutput',current['events'][-1]['output']==box and int(re.search(r'popup=(\d+)',[l for l in text().splitlines() if l.startswith('view-commit: popup=')][-1]).group(1))==int(old_scope['id']),event=current['events'][-1])
    removed=next(m for m in s.data('monitors') if m['id']==before['monitor'])
    check('FocusedPopupBeforeOutputRemoval',body['focus']=='launcher-search' and body['documentFocused'] and removed['name']=='WAYLAND-2',body=body,output=removed)
    check('RemoveActualNativeOutput',s.ctl('output','remove',removed['name']).strip()=='ok')
    monitors=wait(lambda:(ms:=s.data('monitors')) and len(ms)==1 and ms[0]['name']=='WAYLAND-1' and ms)
    wait(lambda:'view-retired: id='+old_scope['id'] in text())
    wait(lambda:(p:=projection()) and p.get('mode')=='closed' and p.get('phase')=='Coherent')
    after=root_window();topology=json.loads([l.split(': ',1)[1] for l in text().splitlines() if l.startswith('view-topology: ')][-1])
    check('RemovedPopupScopeAbsentFromCurrentTopology',old_scope not in topology['views'] and len(topology['views'])==1,topology=topology,removed=old_scope)
    check('OutputRemovalPreservesWorkspaceIdentity',after['workspace']['id']==before['workspace']['id'] and after['monitor']==monitors[0]['id'],before=before,after=after)
    check('RemovalNeverReplaysWindowMutation',len(journal())==before_journal)
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    recovered=wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and any(x['accessibleName']=='Refresh applications' and not x['disabled'] for x in b['buttons']) and b)
    history=wait(lambda:(r:=latest_shortcut()) and int(r['serial'])>int(old_serial) and r);retired_event=next(e for e in history['events'] if e['serial']==old_serial)
    check('RemovedNativeShortcutDestinationBecomesUnavailable',retired_event['output'] is None,event=retired_event)
    owner=int(re.search(r'popup=(\d+)',[l for l in text().splitlines() if l.startswith('view-commit: popup=')][-1]).group(1))
    check('SurvivingOutputKeyboardRecovery',str(owner)==topology['views'][0]['id'] and owner!=int(old_scope['id']),body=recovered,surviving=topology['views'][0])
    # Tab reaches an actual recovery button, and Enter operates it without launch.
    physical('key 15 1\nsleep 50\nkey 15 0\nsleep 100');physical('key 15 1\nsleep 50\nkey 15 0\nsleep 100')
    refresh=wait(lambda:(b:=shortcut_popup_body()) and b.get('documentFocused') and any(x['id']==b.get('focus') and x['accessibleName']=='Refresh applications' for x in b['buttons']) and b)
    def catalog_reads():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='catalog-request']
    read_count=len(catalog_reads());physical('key 28 1\nsleep 50\nkey 28 0\nsleep 100')
    wait(lambda:len(catalog_reads())>read_count)
    check('ActualSurvivingKeyboardRefreshRead',len(catalog_reads())>read_count,before=read_count,after=len(catalog_reads()))
    wait(lambda:(b:=shortcut_popup_body()) and b.get('documentFocused') and b)
    check('SurvivingRecoveryNeverLaunchesOrMutates',len(journal())==before_journal and not any(json.loads(l.split(': ',1)[1])['kind']=='application-launch' for l in text().splitlines() if l.startswith('frontend-request: ')))
    image=OUTPUT/'output-survivor.png';helper(['/usr/bin/grim',str(image)]);report['outputSurvivorPixels']={'path':str(image),'sha256':sha(image)}
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    check('RecreateActualNativeOutput',s.ctl('output','create','wayland').strip()=='ok')
    wait(lambda:len(s.data('monitors'))==2)
    replacement_output=next(m for m in s.data('monitors') if m['name']!=monitors[0]['name'])
    command='hl.monitor({output="'+replacement_output['name']+'",mode="800x600@60",position="800x0",scale=1})'
    check('ConfigureReplacementAtRetiredLogicalBounds',s.ctl('eval',command).strip()=='ok')
    wait(lambda:any(m['name']==replacement_output['name'] and m['x']==box[0] and m['y']==box[1] and m['width']==box[2] and m['height']==box[3] and m['scale']==1 for m in s.data('monitors')))
    def replacement_topology():
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('view-topology: ')];return rows[-1] if rows and len(rows[-1]['views'])==2 and any(loc['scope'] not in topology['views'] and loc['box']==box for loc in rows[-1]['locations']) else None
    replaced=wait(replacement_topology);replacement=next(v for v in replaced['views'] if v not in topology['views'])
    check('ReplacementGetsFreshViewIdentity',old_scope not in replaced['views'] and int(replacement['id'])>int(old_scope['id']),removed=old_scope,replacement=replacement,topology=replaced)
    wait(lambda:(projection() or {}).get('phase')=='Coherent')
    check('ReplacementCannotReplayOldPopupOrEffect',(projection() or {}).get('mode')=='closed' and len(journal())==before_journal)
    prior_serial=latest_shortcut()['serial']
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    history=wait(lambda:(r:=latest_shortcut()) and int(r['serial'])>int(prior_serial) and r);retired_event=next(e for e in history['events'] if e['serial']==old_serial)
    check('ReplacementCannotAdoptRetiredNativeShortcut',retired_event['output'] is None,event=retired_event)
    wait(lambda:(b:=shortcut_popup_body()) and b.get('documentFocused') and b)
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    report['nativeOutputRetirementObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition)
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
