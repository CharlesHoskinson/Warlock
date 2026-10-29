     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     def settings_body():return body_for('settings')
     def button(label):
      body=settings_body();return next((b for b in body['buttons'] if b['accessibleName']==label),None) if body else None
     def existing():return [r for r in s.data('binds') if r.get('description') in ['Existing Apps shortcut','User Apps shortcut']]
     def at_current(label,stage):
      def observe():
       body=settings_body();p=projection()
       if not body or not p or p['phase']!='Coherent' or body.get('publication')!=p.get('publication') or not body.get('documentFocused'):return None
       buttons=[b for b in body['buttons'] if b['accessibleName']==label and not b['disabled'] and b['id']==body.get('focus')]
       if len(buttons)!=1:return None
       b=buttons[0];value=at_observe();reader=(value.get('reader') or {}).get('focus') or {}
       nodes=[n for n in value['nodes'] if n.get('pid')==web.pid and n.get('name')==label and (n.get('attributes') or {}).get('id')==b['id'] and n.get('role') in ['button','push button','toggle button'] and {'focused','enabled','sensitive','visible','showing'}<=set(n.get('states',[]))]
       return (value,nodes[0],body) if len(nodes)==1 and reader.get('name')==label and reader.get('identity')==nodes[0].get('identity') else None
      value,node,body=wait(observe);report.setdefault('firstUseATSnapshots',[]).append({'stage':stage,'snapshot':value,'node':node,'body':body});return node
     def focus_button(label):
      body=wait(lambda:settings_body() if button(label) and not button(label)['disabled'] else None);target=button(label)
      for _ in range(len(body['buttons'])+2):
       body=settings_body()
       check('CurrentSettingsLeaseAndPublication',bool(body) and body.get('lease') and body.get('publication')==(projection() or {}).get('publication'))
       if body.get('focus')==target['id']:break
       key(15)
      check('PhysicalFocus'+label,settings_body()['focus']==target['id'])
     old_bindings=existing();check('ActualConflictingCustomBindings',len(old_bindings)==2,bindings=old_bindings)
     state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/shortcuts.json'
     def stored():return json.loads(state_file.read_text()) if state_file.exists() else None
     bar_route('Open settings');wait(lambda:button('Use Apps menu default'))
     body=wait(lambda:settings_body() if button('Use Apps menu alternative') and not button('Use Apps menu alternative')['disabled'] else None)
     check('ActualConflictVisible',button('Use Apps menu default')['disabled'] and 'Unavailable: existing binding' in body['text'],body=body)
     focus_button('Dismiss help');at_current('Dismiss help','before-dismiss');key(28);wait(lambda:button('Show help'))
     keyboard_button('Use Apps menu alternative',28);keyboard_button('Use System menu default',28);keyboard_button('Keep existing shortcut for Notification history',28)
     check('UnsavedChoiceDoesNotWrite',not stored() and not requests('shortcut-preferences-write') and existing()==old_bindings)
     focus_button('Save shortcut choices');at_current('Save shortcut choices','before-save');key(28)
     saved=wait(lambda:stored() if stored() and stored()['choices']=={'applications':'alternate','system':'default','notifications':'keep'} else None)
     wait(lambda:settings_body() if 'Shortcut choices saved and active' in settings_body()['text'] else None)
     before_bytes=state_file.read_bytes();check('OneActualPhysicalChoiceWrite',len(requests('shortcut-preferences-write'))==1 and existing()==old_bindings,stored=saved)
     focus_button('Show help');at_current('Show help','before-restart-help');key(28);wait(lambda:button('Dismiss help'));key(1);wait(closed)
     chord([125,29,56],57);wait(lambda:(body:=body_for('applications')) and body['focus']=='launcher-search');key(1);wait(closed)
     check('AlternativeWorksBeforeRestart',bool(wait(bar_focus)))
     old_binding=dict(client.bound);old_host={'pid':web.pid,'start':start_time(web.pid),'sha256':sha('/proc/'+str(web.pid)+'/exe')}
     check('DirectHostExactIdentity',old_host['sha256']==sha(binary),host=old_host)
     def find_backend():
      rows=[]
      for row in s.host.descendants():
       try:
        pid=row['pid'];args=pathlib.Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0');fields=pathlib.Path('/proc',str(pid),'stat').read_text().rpartition(') ')[2].split()
        if str(ROOT/'adapter/daemon.py').encode() in args and int(fields[1])==web.pid:rows.append({'pid':pid,'start':start_time(pid),'exe':str(pathlib.Path('/proc',str(pid),'exe').resolve()),'sha256':sha('/proc/'+str(pid)+'/exe')})
       except (FileNotFoundError,ProcessLookupError):continue
      return rows[0] if len(rows)==1 else None
     old_backend=wait(find_backend);check('BackendIsSeparateOwnedPythonChild',old_backend['pid']!=web.pid and old_backend['exe']==str(pathlib.Path('/usr/bin/python3').resolve()) and old_backend['sha256']==sha('/usr/bin/python3'),backend=old_backend)
     owned=next(row for proc,row in s.host.processes if proc is web);s.host.stop(owned,web);web.wait(timeout=5)
     check('OldDirectHostAndBackendGone',web.returncode==0 and not pathlib.Path('/proc',str(old_host['pid'])).exists() and not pathlib.Path('/proc',str(old_backend['pid'])).exists(),host=old_host,backend=old_backend,exitCode=web.returncode)
     s.guard();check('OriginalAuthorityUnloads',s.ctl('plugin','unload',pair['plugin']['path']).strip()=='ok');loaded=False
     s.guard();check('ExactAuthorityReloads',s.ctl('plugin','load',pair['plugin']['path']).strip()=='ok');loaded=True
     client=Endpoint(**config);client.hello();new_binding=dict(client.bound)
     check('FreshNativeAuthorityLifetime',new_binding['lifetime']!=old_binding['lifetime'],before=old_binding,after=new_binding)
     web=s.host.launch('warlock-restarted',[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web)
     log=OUTPUT/'warlock-restarted.log';collector=Collector();new_start=start_time(web.pid)
     check('NewDirectHostIdentity',web.pid!=old_host['pid'] and sha('/proc/'+str(web.pid)+'/exe')==sha(binary),pid=web.pid,start=new_start)
     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     backend_binding=frames('shell-shortcuts')[-1]['binding'];check('RestartedBackendUsesFreshAuthority',backend_binding['lifetime']==new_binding['lifetime'] and backend_binding['lifetime']!=old_binding['lifetime'],binding=backend_binding)
     new_backend=wait(find_backend);check('RestartedBackendIsFreshOwnedChild',new_backend['pid']!=web.pid and new_backend['pid']!=old_backend['pid'] and new_backend['exe']==str(pathlib.Path('/usr/bin/python3').resolve()) and new_backend['sha256']==sha('/usr/bin/python3'),backend=new_backend)
     check('PersistedExactRevisionAndBytes',stored()==saved and state_file.read_bytes()==before_bytes,stored=stored())
     bar_route('Open settings');wait(lambda:button('Show help') or button('Dismiss help'))
     loaded_choice=wait(lambda:next((f for f in reversed(frames('shortcut-preferences')) if f.get('snapshot')==saved),None))
     def selected_saved_body():
      body=settings_body()
      if not body:return None
      rows=[b for b in body['buttons'] if b.get('identity') in ['settings:shortcuts:applications:alternate','settings:shortcuts:system:default','settings:shortcuts:notifications:keep']]
      return body if len(rows)==3 and all(b.get('label')==b.get('accessibleName')+'Selected' for b in rows) else None
     body=wait(selected_saved_body)
     check('SavedChoicesReadBeforeAnyReapply',loaded_choice['binding']==backend_binding and not requests('shortcut-preferences-write'),body=body,receipt=loaded_choice)
     show='Show help' if button('Show help') else 'Dismiss help'
     focus_button(show);at_current(show,'after-restart-help');key(28)
     if show=='Dismiss help':wait(lambda:button('Show help'));focus_button('Show help');at_current('Show help','reopened-help');key(28)
     wait(lambda:button('Dismiss help'))
     native=client.shortcut_bindings('31001')['inventory'];report['postRestartShortcutInventoryBeforeReapply']=native
     if any(native[name]['active']!=saved['choices'][name] for name in saved['choices']):
      focus_button('Save shortcut choices');at_current('Save shortcut choices','explicit-reapply');key(28)
      wait(lambda:settings_body() if 'Shortcut choices saved and active' in settings_body()['text'] else None)
      check('ExplicitReapplyPreservesStoredBytes',stored()==saved and state_file.read_bytes()==before_bytes and len(requests('shortcut-preferences-write'))==1)
      report['explicitReapplyAfterAuthorityRestart']=True
     else:report['explicitReapplyAfterAuthorityRestart']=False
     after_native=client.shortcut_bindings('31002')['inventory'];check('FreshNativeChoiceApplied',all(after_native[name]['active']==saved['choices'][name] for name in saved['choices']),inventory=after_native)
     key(1);wait(closed);chord([125,29,56],57)
     app=wait(lambda:(body:=body_for('applications')) and body['focus']=='launcher-search' and body.get('documentFocused') and body)
     def app_at():
      value=at_observe();reader=(value.get('reader') or {}).get('focus') or {};nodes=[n for n in value['nodes'] if n.get('pid')==web.pid and n.get('name')=='Search applications' and (n.get('attributes') or {}).get('id')=='launcher-search' and {'focused','enabled','sensitive','visible','showing'}<=set(n.get('states',[]))]
      return (value,nodes[0]) if len(nodes)==1 and reader.get('identity')==nodes[0].get('identity') else None
     at_value,at_node=wait(app_at);report['firstUseActualApplicationAT']={'body':app,'snapshot':at_value,'node':at_node}
     check('SavedAlternativeInvokesActualCurrentComponent',app['focus']=='launcher-search' and at_node['pid']==web.pid)
     key(1);wait(closed);semantic=lambda rows:[{k:v for k,v in row.items() if k!='arg'} for row in rows]
     check('ForeignCustomizedBindingsRetained',semantic(existing())==semantic(old_bindings) and stored()==saved and state_file.read_bytes()==before_bytes,bindings=existing())
     report['directRestart']={'oldHost':old_host,'oldBackend':old_backend,'newHost':{'pid':web.pid,'start':new_start},'newBackend':new_backend,'oldAuthority':old_binding,'newAuthority':new_binding,'newBackendBinding':backend_binding,'saved':saved,'preReapplyInventory':native,'postReapplyInventory':after_native}
     report['nativeFirstUseDirectObserved']=True
