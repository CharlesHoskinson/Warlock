"""UI-006 overview-cancel: actual nested transfer dismissal and eligible focus."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text()
needle="button['accessibleName'].startswith('Browse workspace ') or (NAV and button['accessibleName'].startswith('Restore ELM-ACTIVATION-PEER'))"
assert source.count(needle)==1
source=source.replace(needle,needle+" or (NAV and button.get('identity')=='overview:transfer:'+peer_identity)")
start=source.index('    elif NAV:\n');end=source.index('    elif TRANSFER:\n',start)
source=source[:start]+r'''    elif NAV:
     report.update(requirements=['ELM-UI-006'],scenarios=['overview-cancel'],scope='Actual Escape and Cancel dismiss the transfer chooser, focus the exact eligible Move origin and paint it; full Task View dismissal makes no mutation and returns physical keyboard input to the original native opener. Applicable AT and independent acceptance remain separate.',nativeTaskViewTransferCancelObserved=False)
     before=len(journal());original=facts();membership={w['incarnation']:(w['workspace'],w['monitor']) for w in original['facts']['windows']}
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     keyboard_button('Browse workspace 2')
     wait(lambda:any(b['identity']=='overview:workspace:2' and 'Selected' in b['label'] for b in (popup_body() or {}).get('buttons',[])))
     keyboard_button('Move ELM-ACTIVATION-PEER to another workspace')
     chooser=wait(lambda:(body:=popup_body()) and any(b['accessibleName']=='Cancel window transfer' for b in body['buttons']) and body)
     check('ExactTransferChooserHasNoNativeAction',any(b['identity'].startswith('overview:destination:') for b in chooser['buttons']) and len(journal())==before,body=chooser)
     def returned():
      body=popup_body();current=projection()
      if not body or not current or current['phase']!='Coherent' or current['mode']!='overview' or body['publication']!=current['publication']:return None
      if any(b['accessibleName']=='Cancel window transfer' for b in body['buttons']):return None
      return body if body['documentFocused'] and body['focusIdentity']=='overview:transfer:'+peer_identity and any(b['identity']==body['focusIdentity'] and not b['disabled'] and b['id']==body['focus'] for b in body['buttons']) else None
     key(1);body=wait(returned)
     check('EscapeReturnsExactEligibleCurrentTransferOpener',len(journal())==before and any(b['identity']=='overview:workspace:2' and 'Selected' in b['label'] for b in body['buttons']),body=body)
     report['escapeTransferReturn']=body
     # Enter now acts on the physically focused Move origin, without traversing.
     key(28);wait(lambda:any(b['accessibleName']=='Cancel window transfer' for b in (popup_body() or {}).get('buttons',[])))
     check('ReturnedKeyboardOriginReopensExactChooser',len(journal())==before,body=popup_body())
     keyboard_button('Cancel window transfer');body=wait(returned);report['cancelTransferReturn']=body
     popup_capture('cancelled-transfer-origin');capture=report['popupCaptures'][-1]
     check('ReturnedTransferOriginActuallyPainted',any(r['accessibleName']=='Move ELM-ACTIVATION-PEER to another workspace' and r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     current=facts()
     check('BothCancellationsPreserveNativeWindowAndWorkspaceMembership',len(journal())==before and {w['incarnation']:(w['workspace'],w['monitor']) for w in current['facts']['windows']}==membership and current['facts']['focused']==target and s.data('monitors')[0]['activeWorkspace']['id']==1,before=original,after=current)
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
     key(30);delivered=[json.loads(line) for line in events.read_text().splitlines()[before_events:]] if events.exists() else []
     check('OverviewCancellationReturnsActualEligibleKeyboardRecipient',len(journal())==before and facts()['facts']['focused']==target and any(event['kind']=='key' and event['keyval']==97 and event['window']=='ELM-AUTHORITY-FIXTURE' for event in delivered),events=delivered)
     report['nativeTaskViewTransferCancelObserved']=True
'''+source[end:]
sys.argv=[str(p),'--workspace-navigation']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':__file__})
