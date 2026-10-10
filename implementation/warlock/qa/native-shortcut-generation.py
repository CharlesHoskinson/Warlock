"""Original output/placement journey plus a held actual native shortcut reply across same-bound replacement. No hardware/AT acceptance."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-output-placement.py')
wrapper=p.read_text()
launch="   web=s.host.launch('warlock'"
setup=r'''   generation_arm=OUTPUT/'shortcut-hold.arm';generation_held=OUTPUT/'shortcut-hold.json';generation_release=OUTPUT/'shortcut-hold.release';generation_delivered=OUTPUT/'shortcut-hold.delivered'
   generation_backend=OUTPUT/'shortcut-generation-backend.py'
   generation_backend.write_text("import sys,json,threading,time\nfrom pathlib import Path\nsys.path.insert(0,"+repr(str(ROOT/'adapter'))+")\nimport daemon\noriginal=daemon.send\narm=Path("+repr(str(generation_arm))+");held=Path("+repr(str(generation_held))+");release=Path("+repr(str(generation_release))+");delivered=Path("+repr(str(generation_delivered))+")\nlock=threading.Lock();stopped=threading.Event()\ndef send(frame):\n with lock:\n  if frame.get('kind')=='shell-shortcuts' and arm.exists() and int(frame['serial'])>int(arm.read_text()):\n   if not held.exists():held.write_text(json.dumps(frame))\n   return\n  original(frame)\ndef dispatch():\n while not stopped.wait(.01):\n  if release.exists():\n   with lock:\n    frame=json.loads(held.read_text());original(frame);arm.unlink();release.unlink();delivered.write_text(json.dumps(frame))\n   return\ndaemon.send=send\nthread=threading.Thread(target=dispatch,daemon=True);thread.start()\ntry:result=daemon.run()\nfinally:stopped.set();thread.join(1)\nraise SystemExit(result)\n")
   report['shortcutGenerationTransport']={'path':str(generation_backend),'sha256':sha(generation_backend),'scope':'Hold only an actual validated native shortcut reply after read; unchanged production daemon handles all other requests/effects. Re-deliver that same frame through the original bounded serialized OutputWriter. No fabricated generation, focus or native state.'}
'''
journey=r'''    report['shortcutGenerationComposition']={'placementRunner':str(generation_placement_path),'placementRunnerSHA256':sha(generation_placement_path),'runner':str(generation_runner_path),'runnerSHA256':sha(generation_runner_path)}
    generation_before=root_window();generation_monitor=next(m for m in s.data('monitors') if m['id']==generation_before['monitor']);generation_box=[generation_monitor['x'],generation_monitor['y'],int(generation_monitor['width']/generation_monitor['scale']),int(generation_monitor['height']/generation_monitor['scale'])]
    generation_topology=json.loads([l.split(': ',1)[1] for l in text().splitlines() if l.startswith('view-topology: ')][-1]);generation_scope=next(loc['scope'] for loc in generation_topology['locations'] if loc['box']==generation_box)
    def generation_rows():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')=='shell-shortcuts']
    generation_baseline=generation_rows()[-1];generation_arm.write_text(generation_baseline['serial']);generation_effects=len(journal())
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    wait(lambda:generation_held.exists());generation_receipt=json.loads(generation_held.read_text());generation_event=generation_receipt['events'][-1]
    check('HeldActualFreshShortcutBeforeRetirement',generation_receipt['shortcutProtocol']==3 and int(generation_receipt['serial'])==int(generation_baseline['serial'])+1 and generation_event['output']==generation_box and generation_rows()[-1]['serial']==generation_baseline['serial'] and (projection() or {}).get('mode')=='closed',receipt=generation_receipt,baseline=generation_baseline)
    check('RetireActualHeldShortcutOutput',s.ctl('output','remove',generation_monitor['name']).strip()=='ok')
    wait(lambda:'view-retired: id='+generation_scope['id'] in text());wait(lambda:json.loads([l.split(': ',1)[1] for l in text().splitlines() if l.startswith('view-topology: ')][-1])['views']==[])
    check('RecreateActualHeldShortcutOutput',s.ctl('output','create','wayland').strip()=='ok')
    generation_created=wait(lambda:next((m for m in s.data('monitors') if m['name']!='FALLBACK'),None))
    generation_config='hl.monitor({output="'+generation_created['name']+'",mode="800x600@60",position="0x0",scale=1})'
    check('ConfigureHeldReplacementAtOriginalLogicalBounds',s.ctl('eval',generation_config).strip()=='ok')
    def generation_returned():
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('view-topology: ')]
     return rows[-1] if rows and len(rows[-1]['views'])==1 and rows[-1]['locations'][0]['box']==generation_box and rows[-1]['views'][0]!=generation_scope else None
    generation_new=wait(generation_returned);wait(lambda:(projection() or {}).get('phase')=='Coherent' and (projection() or {}).get('mode')=='closed')
    generation_facts=facts();check('ReplacementRetiresNativeGenerationAtIdenticalBounds',int(generation_facts['outputGeneration'])>int(generation_event['outputGeneration']) and generation_new['locations'][0]['box']==generation_event['output'],before=generation_event,after=generation_facts,topology=generation_new)
    generation_release_offset=len(text());generation_release.write_text('release');wait(lambda:generation_delivered.exists());wait(lambda:generation_rows()[-1]['serial']==generation_receipt['serial'])
    # Wait for the actual Elm publication following this backend receipt, not a
    # quiet interval. Original six-second observation bound remains unchanged.
    wait(lambda:'Shell shortcut output is unavailable. Press the shortcut again.' in text()[generation_release_offset:])
    check('DelayedOldShortcutCannotOpenReplacementPopup',(projection() or {}).get('mode')=='closed' and len(journal())==generation_effects and json.loads(generation_delivered.read_text())==generation_receipt,receipt=generation_receipt,projection=projection(),topology=generation_new)
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    generation_fresh=wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and b)
    current=generation_rows()[-1];check('FreshReplacementShortcutWorksAfterStaleConsumed',int(current['serial'])==int(generation_receipt['serial'])+1 and current['events'][-1]['outputGeneration']==facts()['outputGeneration'] and len(journal())==generation_effects,event=current['events'][-1],body=generation_fresh)
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    check('SecondReturnPreservesApplicationWorkspaceSizeAndDraft',root_window()['workspace']==generation_before['workspace'] and root_window()['size']==generation_before['size'] and draft_rows()[-1]['text']=='UNSAVED-WARLOCK-OUTPUT-DRAFTa',before=generation_before,after=root_window(),draft=draft_rows()[-1])
    report['nativeShortcutGenerationObserved']=True
'''
# Reuse the existing composition; change only the QA backend transport and add
# the new journey after every original placement/output assertion has passed.
needle="sys.argv=[str(p),'--shortcut-output']\nexec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'placement_inputs':inputs})"
assert wrapper.count(needle)==1
replacement="""assert source.count(generation_launch)==1
source=source.replace(generation_launch,generation_setup+'\\n'+generation_launch)
backend=\"'--backend',str(backend_fixture if CATALOG or CHORD else ROOT/'adapter/daemon.py')\"
assert source.count(backend)==1
source=source.replace(backend,\"'--backend',str(generation_backend)\")
end=\"    report['nativeOutputPlacementObserved']=True\"
assert source.count(end)==1
source=source.replace(end,end+'\\n'+generation_journey)
sys.argv=[str(p),'--shortcut-output']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'placement_inputs':inputs,'generation_placement_path':generation_placement_path,'generation_runner_path':generation_runner_path})
"""
exec(compile(wrapper.replace(needle,replacement),str(p),'exec'),{'__name__':'__main__','__file__':str(p),'generation_launch':launch,'generation_setup':setup,'generation_journey':journey,'generation_placement_path':p,'generation_runner_path':pathlib.Path(__file__).resolve()})
