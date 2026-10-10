"""UI-004 actual AT-SPI/Orca single-family primary names/state/action; independent acceptance separate."""
import hashlib,pathlib,sys
assert sys.argv[1:] in ([],['--at-actions']);at_actions=bool(sys.argv[1:])
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
needle="ACCESSIBILITY=sys.argv[1:]==['--accessibility']";assert source.count(needle)==1;source=source.replace(needle,'ACCESSIBILITY=True')
needle="SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY";assert source.count(needle)==1;source=source.replace(needle,"SWITCHER=sys.argv[1:]==['--switcher']")
needle="    def action(stage,operation,focus,minimized):";assert source.count(needle)==1
addition=r'''    report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-inactive','taskbar-active','taskbar-minimized'],scope='Actual private native AT-SPI and Orca observations with original primary journey, physical keyboard focus/navigation, native receipts/focus/MRU/desktop/client input/pixels. Actual AT-SPI action mode distinguished from physical Enter mode; independent original acceptance separate.')
    report['taskbarPrimaryAtInputs']=primary_at_inputs
    report['accessibilitySnapshots']=[];report['taskbarPrimaryAtActionMode']=primary_at_actions
    def primary_at_snapshot(stage):
     def observed():
      bodies=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=bar ')];body=bodies[-1] if bodies else None;p=projection()
      if not body or not p or p['phase']!='Coherent' or body['publication']!=p['publication']:return None
      value=at_observe();rows=[row for row in value['nodes'] if row.get('pid')==web.pid and any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in row['ancestors']) and row['role'] in ['button','push button','toggle button']]
      names=[b['accessibleName'] for b in body['buttons']]
      return (value,rows,body) if rows and sorted(row['name'] for row in rows)==sorted(names) else None
     value,rows,body=wait(observed);report['accessibilitySnapshots'].append({'stage':stage,**value})
     check(stage+'ActualAtNamesAndHostIdentity',all(row['pid']==web.pid for row in rows),nodes=rows,domNames=[b['accessibleName'] for b in body['buttons']])
     check(stage+'ActualAtActiveToggleState',all(bool({'pressed','checked'} & set(row['states']))==('; Active' in row['name']) for row in rows),nodes=rows)
     current=next(row for row in rows if ' ELM-ACTIVATION-PEER;' in row['name']);check(stage+'ActualAtPrimaryAvailable',{'enabled','sensitive','visible','showing'}<=set(current['states']),node=current)
     return current
    def primary_at_focus(chosen):
     def focused():
      value=at_observe();focus=(value.get('reader') or {}).get('focus') or {};rows=[row for row in value['nodes'] if row.get('pid')==web.pid and row['name']==chosen['accessibleName'] and 'focused' in row['states'] and any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in row['ancestors'])]
      return value if len(rows)==1 and focus.get('name')==chosen['accessibleName'] and focus.get('role') in ['button','push button','toggle button'] else None
     value=wait(focused);report['accessibilitySnapshots'].append({'stage':'PrimaryFocus:'+chosen['accessibleName'],**value})
     check('ActualOrcaAndNativePrimaryFocusAgree',True,reader=value['reader'],accessibleName=chosen['accessibleName'])
    def primary_at_invoke(chosen):
     node=primary_at_snapshot('BeforeAtAction');receipt=OUTPUT/('at-primary-action-'+str(len(report.get('taskbarPrimaryAtActions',[])))+'.json')
     check('ActualAtActionNamesCurrentPrimary',node['name']==chosen['accessibleName'],node=node,chosen=chosen)
     helper(['/usr/bin/python3','-B',str(ROOT/'qa/taskbar-at-action.py'),str(web.pid),node['identity'],node['name'],str(receipt)])
     value=json.loads(receipt.read_text());check('ActualAtSpiPrimaryActionInvoked',value['passed'] and value['source']=='actual-at-spi-action' and value['before']['pid']==web.pid,receipt=value);report.setdefault('taskbarPrimaryAtActions',[]).append(value)
'''
source=source.replace(needle,addition+'\n'+needle)
needle="     primary_key(28)\n";assert source.count(needle)==1
source=source.replace(needle,"     primary_at_focus(chosen)\n     if primary_at_actions:primary_at_invoke(chosen)\n     else:primary_key(28)\n")
needle="     capture(stage,minimized)\n     if focus is not None:actual_recipient(stage,focus)";assert source.count(needle)==1
# AT-SPI action acknowledgement is not a paint acknowledgement. Observe the
# required real native tree transition, within the original wait, before the
# unchanged physical frame assertion. No synthetic focus, sleep or deadline.
source=source.replace(needle,"     primary_at_snapshot(stage)\n     capture(stage,minimized)\n     if focus is not None:actual_recipient(stage,focus)")
needle="    action('InactiveActivation','activate',target,False)";assert source.count(needle)==1;source=source.replace(needle,"    primary_at_snapshot('InactiveBeforeActivation')\n"+needle)
needle="     report['nativeKeyboardPrimaryJourneyObserved']=True";assert source.count(needle)==1
source=source.replace(needle,needle+r'''
     report['nativeKeyboardPrimaryJourneyObserved']=not primary_at_actions
     report['nativeAtActionPrimaryJourneyObserved']=primary_at_actions
     utterances=OUTPUT/'orca-utterances.jsonl';report['orcaSpeechOutput']=[json.loads(line) for line in utterances.read_text().splitlines()]
     check('ActualOrcaSpeaksAllPrimaryOperations',all(any(operation+' ELM-ACTIVATION-PEER' in row.get('text','') for row in report['orcaSpeechOutput']) for operation in ['Activate','Minimize','Restore']),utterances=report['orcaSpeechOutput'])
     report['nativeTaskbarPrimaryAtObserved']=True
''')
inputs={p.name:sha(p),pathlib.Path(__file__).name:sha(pathlib.Path(__file__)),**{name:sha(p.with_name(name)) for name in ['accessibility-session.py','accessibility-inspector.py','accessibility-reader.py','taskbar-at-action.py']}}
sys.argv=[str(p),'--taskbar-primary-keyboard']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'primary_at_inputs':inputs,'primary_at_actions':at_actions})
