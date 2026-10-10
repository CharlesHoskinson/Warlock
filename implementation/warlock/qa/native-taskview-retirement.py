"""UI-006 overview-retire: actual chosen transfer member disappears."""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text()
start=source.index('    elif NAV:\n');end=source.index('    elif TRANSFER:\n',start)
source=source[:start]+r'''    elif NAV:
     report.update(requirements=['ELM-UI-006'],scenarios=['overview-retire'],scope='Actual selected transfer member disappears; current browse fallback/focus, painted controls, zero native mutation or replacement and original Escape/real client recipient. AT and independent original acceptance separate.',nativeTaskViewRetirementObserved=False)
     check('OwnedWorkspaceTwoPersistsAfterMemberRetirement',s.ctl('eval','hl.workspace_rule({workspace="2",persistent=true})').strip()=='ok')
     before=len(journal());original=facts();membership=sorted(w['incarnation'] for w in original['facts']['windows'])
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     keyboard_button('Browse workspace 2')
     wait(lambda:any(b['identity']=='overview:workspace:2' and 'Selected' in b['label'] for b in (popup_body() or {}).get('buttons',[])))
     keyboard_button('Move ELM-ACTIVATION-PEER to another workspace')
     chooser=wait(lambda:(body:=popup_body()) and any(b['accessibleName']=='Cancel window transfer' for b in body['buttons']) and body)
     check('ExactSelectedTransferHasDestinationsWithoutMutation',any(b['identity'].startswith('overview:destination:') and not b['disabled'] for b in chooser['buttons']) and len(journal())==before,body=chooser)
     control.write_text(json.dumps({'op':'retire-peer'}))
     wait(lambda:all(w['incarnation']!=peer_identity for w in facts()['facts']['windows']))
     def returned():
      body=popup_body();current=projection()
      if not body or not current or current['phase']!='Coherent' or current['mode']!='overview' or body['publication']!=current['publication']:return None
      if not any(b['accessibleName']=='Close Task View and return to windows' for b in body['buttons']):return None
      target_identity='overview:workspace:2' if any(b['identity']=='overview:workspace:2' for b in body['buttons']) else 'overview:all'
      return body if body['documentFocused'] and body['focusIdentity']==target_identity else None
     body=wait(returned);current=facts();report['retiredTransferReturn']={'before':chooser,'after':body,'nativeBefore':original,'nativeAfter':current}
     check('RetiredTransferReturnsEligibleCurrentBrowseFocus',not any(b['identity'].startswith(('overview:destination:','overview:family:'+peer_identity,'overview:transfer:'+peer_identity)) for b in body['buttons']) and len(journal())==before,body=body,journal=journal()[before:])
     check('MemberRemovalNeverActivatesReplacement',sorted(w['incarnation'] for w in current['facts']['windows'])==[identity for identity in membership if identity!=peer_identity] and current['facts']['focused']==target and s.data('monitors')[0]['activeWorkspace']['id']==1,before=original,after=current)
     popup_capture('retired-transfer-browse');capture=report['popupCaptures'][-1]
     check('RetiredTransferFallbackControlsActuallyPainted',bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('RetirementDismissalNeverMutates',len(journal())==before)
     events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
     key(30);delivered=[json.loads(line) for line in events.read_text().splitlines()[before_events:]] if events.exists() else []
     check('RetirementDismissalReturnsActualKeyboardRecipient',facts()['facts']['focused']==target and any(event['kind']=='key' and event['keyval']==97 and event['window']=='ELM-AUTHORITY-FIXTURE' for event in delivered),events=delivered)
     report['nativeTaskViewRetirementObserved']=True
'''+source[end:]
sys.argv=[str(p),'--workspace-navigation']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':__file__})
