"""ELM-UI-005/search-race on the real catalog, keyboard and AT-SPI path.

Delay one genuine reply before the unchanged bounded writer. Keep the backend
reading so a newer refresh can finish. No synthetic catalog/policy/effect frame.
"""
import hashlib, pathlib, sys

assert sys.argv[1:] in ([], ['--at-actions'])
at_actions = bool(sys.argv[1:])
base = pathlib.Path(__file__).with_name('native-window-feedback.py')
source = base.read_text()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for old, new in [
    ("ACCESSIBILITY=sys.argv[1:]==['--accessibility']", 'ACCESSIBILITY=True'),
    ("SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY", "SWITCHER=sys.argv[1:]==['--switcher']"),
]:
    assert source.count(old) == 1
    source = source.replace(old, new)

# Same narrowly observed diagnostic-only stdout interleaving as the zero-pin
# fixture. Original bytes remain in the raw log; protocol frames are untouched.
needle = "    return raw[:raw.rfind('\\n')+1]"
assert source.count(needle) == 1
source = source.replace(needle, r'''    complete=raw[:raw.rfind('\n')+1];lines=[]
    for line in complete.splitlines():
     if line.startswith(('surface-report: origin=bar ','surface-report: origin=popup ','surface-inspection: ')):
      try:json.loads(line.split(': ',1)[1] if line.startswith('surface-inspection: ') else line.split(' ',2)[2])
      except json.JSONDecodeError:
       if '{mesa ' not in line:raise
       digest=hashlib.sha256(line.encode()).hexdigest();rows=report.setdefault('interleavedReadOnlyDiagnostics',[])
       if not any(r['sha256']==digest for r in rows):rows.append({'sha256':digest,'bytes':len(line.encode()),'scope':'Mesa worker diagnostic interleaving only; raw log retained. No protocol frames filtered.'})
       continue
     lines.append(line)
    return '\n'.join(lines)+'\n' ''')

needle = '   if JUMP or KEYBOARD:'
assert source.count(needle) == 1
fixture = r'''   if SEARCH:
    race_arm=OUTPUT/'race-arm';race_held=OUTPUT/'race-held.json';race_release=OUTPUT/'race-release';race_delivered=OUTPUT/'race-delivered.json'
    race_events=OUTPUT/'race-launch-events.jsonl';race_recorder=OUTPUT/'race-launch-recorder.py'
    race_recorder.write_text('import json,os,sys\nwith open(sys.argv[1],"a") as stream:stream.write(json.dumps({"argv":sys.argv[2:],"pid":os.getpid(),"normalExit":True})+"\\n")\n')
    race_editor=catalog_root/'warlock-editor.desktop'
    def editor_metadata(current):
     return '[Desktop Entry]\nType=Application\nName='+('A Current Editor' if current else 'Editor')+'\nGenericName=Text editor\nExec=/usr/bin/python3 -B '+str(race_recorder)+' '+str(race_events)+' '+('CURRENT_EDITOR' if current else 'OLD_EDITOR')+'\n'
    race_editor.write_text(editor_metadata(False))
    backend_code = 'import importlib.util,json,sys,threading,time\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nspec=importlib.util.spec_from_file_location("real_warlock_backend",'+repr(str(ROOT/'adapter/daemon.py'))+')\ndaemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)\nsys.argv=[str(spec.origin),'+repr(str(broker_config))+']\n'
    backend_code += 'arm=Path('+repr(str(race_arm))+');held=Path('+repr(str(race_held))+');release=Path('+repr(str(race_release))+');delivered=Path('+repr(str(race_delivered))+')\noriginal_send=daemon.send\nstop=threading.Event()\nerrors=[]\ndef store(path,frame):\n temp=path.with_suffix(".tmp");temp.write_text(json.dumps(frame));temp.chmod(0o600);temp.replace(path)\ndef send(frame):\n if frame.get("kind")=="application-catalog" and arm.exists() and not held.exists():\n  store(held,frame);return\n original_send(frame)\ndef delayed():\n try:\n  while not stop.wait(.01):\n   if release.exists() and held.exists():\n    frame=json.loads(held.read_text());original_send(frame);store(delivered,frame);return\n except BaseException as error:errors.append(error)\ndaemon.send=send\nworker=threading.Thread(target=delayed);worker.start()\ntry:code=daemon.run()\nfinally:stop.set();worker.join(timeout=2)\nassert not worker.is_alive() and not errors\nraise SystemExit(code)\n'
    backend_fixture.write_text(backend_code)
    report['catalogFixture']['backendSHA256']=sha(backend_fixture)
    report['searchRaceFixture']={'recorder':str(race_recorder),'recorderSHA256':sha(race_recorder),'desktop':str(race_editor),'oldDesktopSHA256':sha(race_editor),'realDaemonSHA256':sha(ROOT/'adapter/daemon.py'),'scope':'Only one actual catalog receipt delayed before original bounded writer; backend and authority remain unchanged. Owned desktop metadata advances genuine generation; actual GIO argv is journaled.'}
'''
source = source.replace(needle, fixture + needle)

needle = "      if KEYBOARD:selected=button['id']==body['focus']"
assert source.count(needle) == 1
source = source.replace(needle, "      if SEARCH:selected=button['accessibleName'] in ['Refresh applications','Open A Current Editor']\n" + needle)

start = source.index("    else:\n     click(wait(lambda:(projection() or {}).get('openApplications')));wait(lambda:field_value()==''")
end = source.index('   elif DENSEPICKER:', start)
journey = r'''    else:
     report.update(requirements=['ELM-UI-005'],scenarios=['search-race'],scope='Exact original query change while an older genuine catalog refresh is held; newer request/generation remains current after old reply. Physical keyboard or actual AT-SPI result action, actual popup pixels and Orca focus, exactly one current GIO argv. Independent original acceptance remains separate.',popupPresentationAccepted=False)
     report['searchRaceInputs']=race_inputs;report['searchRaceAtActionMode']=race_at_actions
     def frames(kind):return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')==kind]
     def current_body():
      body=popup_body();p=projection()
      return body if body and p and p['phase']=='Coherent' and p['mode']=='applications' and body['publication']==p['publication'] else None
     def ready(label):
      body=current_body()
      return body if body and field_value()=='editor' and any(b['accessibleName']==label and not b['disabled'] for b in body['buttons']) else None
     def events():return [json.loads(l) for l in race_events.read_text().splitlines()] if race_events.exists() else []
     def focus_result():
      body=wait(lambda:ready('Open A Current Editor'));button=next(b for b in body['buttons'] if b['accessibleName']=='Open A Current Editor')
      for _ in range(len(body['buttons'])+2):
       body=wait(lambda:ready('Open A Current Editor'))
       if body['focus']==button['id']:break
       key(15)
      body=wait(lambda:ready('Open A Current Editor'));check('PhysicalKeyboardReachesExactCurrentResult',body['focus']==button['id'],body=body)
      return button
     def observe_result(stage,button):
      def observed():
       value=at_observe();reader=(value.get('reader') or {}).get('focus') or {};nodes=[n for n in value['nodes'] if n.get('pid')==web.pid and n['name']==button['accessibleName'] and n['role'] in ['button','push button','toggle button'] and not any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in n['ancestors'])]
       return (value,nodes[0]) if len(nodes)==1 and {'focused','enabled','sensitive','visible','showing'}<=set(nodes[0]['states']) and reader.get('name')==button['accessibleName'] else None
      value,node=wait(observed);report.setdefault('searchRaceAtSnapshots',[]).append({'stage':stage,**value});return node
     helper([str(keyboard)],'key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100\nsync\n')
     wait(lambda:field_value()=='' and any(b['accessibleName']=='Open Files' for b in (current_body() or {}).get('buttons',[])))
     query([33,23,38,18,31],'files');wait(lambda:any(b['accessibleName']=='Open Files' and not b['disabled'] for b in (current_body() or {}).get('buttons',[])))
     report['raceInitialQueryBody']=current_body();race_arm.write_text('hold');race_arm.chmod(0o600)
     keyboard_button('Refresh applications',28);wait(race_held.exists)
     held=json.loads(race_held.read_text());wait(lambda:field_value()=='files' and (current_body() or {}).get('focusIdentity')=='control:refresh' and 'Loading applications' in current_body()['text'])
     # Refresh retains its current focus. Use actual user navigation to edit
     # the query, rather than a Focus helper or an old automatic-focus premise.
     for _ in range(2):helper([str(keyboard)],'key 42 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 42 0\nsleep 100\nsync\n')
     wait(lambda:(current_body() or {}).get('focus')=='launcher-search')
     query([18,32,23,20,24,19],'editor');key(28)
     check('ChangedQueryDuringHeldRefreshCannotLaunch',not launches() and not events() and not journal() and 'Loading applications' in current_body()['text'],body=current_body(),held=held)
     race_editor.write_text(editor_metadata(True));report['searchRaceFixture']['currentDesktopSHA256']=sha(race_editor)
     keyboard_button('Refresh applications',28);wait(lambda:ready('Open A Current Editor'))
     fresh=frames('application-catalog')[-1];check('NewRefreshHasDifferentRequestAndNewerCatalog',fresh['requestId']!=held['requestId'] and fresh['binding']==held['binding'] and fresh['snapshot']['lifetime']==held['snapshot']['lifetime'] and int(fresh['snapshot']['generation'])>int(held['snapshot']['generation']),held=held,fresh=fresh)
     button=focus_result();observe_result('BeforeOldReply',button);before=current_body()
     race_release.write_text('release');race_release.chmod(0o600);wait(race_delivered.exists);wait(lambda:held in frames('application-catalog'))
     after=wait(lambda:ready('Open A Current Editor'))
     check('ExactOldReplyCannotReplaceCurrentQueryResultsOrSelection',json.loads(race_delivered.read_text())==held and after['publication']==before['publication'] and after['focus']==before['focus'] and field_value()=='editor' and not any(b['accessibleName'] in ['Open Editor','Open Files'] for b in after['buttons']) and not launches() and not events(),before=before,after=after,held=held,fresh=fresh)
     node=observe_result('AfterOldReply',button);popup_capture('current-after-old-reply');capture=report['popupCaptures'][-1]
     check('CurrentNativeResultAndRefreshHaveActualTextPixels',len(capture['controlRegions'])==2 and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     if race_at_actions:
      receipt=OUTPUT/'race-at-action.json';helper(['/usr/bin/python3','-B',str(ROOT/'qa/launcher-at-action.py'),str(web.pid),node['identity'],node['name'],str(receipt)]);report['searchRaceAtAction']=json.loads(receipt.read_text())
     else:key(28)
     wait(lambda:len(launches())==1 and len(events())==1 and frames('application-launch-outcome'))
     request=launches()[0];outcome=frames('application-launch-outcome')[-1]['outcome']
     check('OnlyCurrentQueryCatalogResultActuallyDispatches',request['intent']['entry']=='warlock-editor' and request['intent']['lifetime']==fresh['snapshot']['lifetime'] and request['intent']['generation']==fresh['snapshot']['generation'] and outcome['intent']==request['intent'] and outcome['status']=='Submitted' and events()[0]['argv']==['CURRENT_EDITOR'] and events()[0]['normalExit'] and not journal(),request=request,outcome=outcome,events=events())
     report['searchRaceSchedule']={'held':held,'fresh':fresh,'delivered':json.loads(race_delivered.read_text()),'before':before,'after':after,'request':request,'outcome':outcome,'events':events()}
     report['searchRaceOrcaSpeech']=[json.loads(l) for l in (OUTPUT/'orca-utterances.jsonl').read_text().splitlines()]
     report['nativeSearchRaceKeyboardObserved']=not race_at_actions;report['nativeSearchRaceAtActionObserved']=race_at_actions;report['popupControlsPhysicallyObserved']=True
'''
source = source[:start] + journey + source[end:]
inputs = {base.name: sha(base), pathlib.Path(__file__).name: sha(pathlib.Path(__file__)), **{n: sha(base.with_name(n)) for n in ['accessibility-session.py', 'accessibility-inspector.py', 'accessibility-reader.py', 'launcher-at-action.py']}}
sys.argv = [str(base), '--launcher-search']
exec(compile(source, str(base), 'exec'), {'__name__': '__main__', '__file__': str(base), 'race_inputs': inputs, 'race_at_actions': at_actions})
