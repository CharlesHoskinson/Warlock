"""UI-006 actual native empty-workspace inventory/browse; navigation acceptance open."""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
needle="     report['nativeTaskViewJourneyObserved']=not RETIRE_OPENER";assert source.count(needle)==1
addition=r'''     report.update(requirements=['ELM-UI-006'],scenarios=['overview-empty'],scope='Current native empty workspace inventory and active marker with no focused application, physical keyboard browsing/current empty view/dismissal and native pixels; actual GUI workspace activation, applicable AT and independent acceptance remain open.')
     # Native fixture creates an ordinary empty workspace through the core's
     # existing dispatcher, before any user GUI selection. It is not a GUI
     # navigation effect or a focus workaround after selection.
     check('CreateActualEmptyWorkspaceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=3})').strip()=='ok')
     wait(lambda:s.data('monitors')[0]['activeWorkspace']['id']==3 and facts()['facts']['focused'] is None and (projection() or {}).get('phase')=='Coherent')
     def current_empty_inventory():
      rows=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
      frames=[row for row in rows if row.get('kind')=='geometry-facts']
      return frames[-1] if frames and frames[-1]['facts'].get('activeWorkspace')=='3' else None
     empty_native=wait(current_empty_inventory)
     check('NativeInventoryIncludesRealEmptyWorkspace',empty_native['facts']['activeWorkspace']=='3' and any(w['identity']=='3' for w in empty_native['facts']['workspaces']) and not any(w['workspace']=='3' for w in empty_native['facts']['windows']),receipt=empty_native)
     report['emptyWorkspaceNativeFixture']=empty_native
     before_empty=len(journal());opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['identity']=='bar:overview' and not b['disabled']),None))
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     def empty_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='overview' and body['publication']==p['publication'] else None
     def active_empty():
      body=empty_body()
      return body if body and body['focusIdentity']=='overview:workspace:3' and body['documentFocused'] and any(b['identity']=='overview:workspace:3' and 'Active workspace' in b['label'] for b in body['buttons']) else None
     body=wait(active_empty);check('EmptyNativeActiveMarkerReceivesKeyboardFocus',True,body=body)
     keyboard_button('Browse workspace 3; active workspace')
     body=wait(lambda:(b:=empty_body()) and 'This workspace has no windows.' in b['text'] and any(w['identity']=='overview:workspace:3' and 'Selected' in w['label'] for w in b['buttons']) and b)
     check('CurrentEmptyViewKeepsBrowseAndDismissalAvailable',body['focusIdentity']=='overview:workspace:3' and not any(b['identity'].startswith('overview:family:') for b in body['buttons']) and any(b['accessibleName']=='Close Task View and return to windows' and not b['disabled'] for b in body['buttons']) and len(journal())==before_empty,body=body)
     popup_capture('empty-workspace');capture=report['popupCaptures'][-1]
     check('EmptyWorkspaceMarkersHaveActualNativePixels',any(row['accessibleName']=='Browse workspace 3; active workspace' and row['brightPixels']>30 and row['paintedPixels']>.9*row['area'] for row in capture['controlRegions']),capture=capture)
     keyboard_button('Browse workspace 1');wait(lambda:'ELM-AUTHORITY-FIXTURE' in empty_body()['text']);check('KeyboardCanLeaveEmptyViewWithoutNativeEffects',len(journal())==before_empty and s.data('monitors')[0]['activeWorkspace']['id']==3 and facts()['facts']['focused'] is None,body=empty_body())
     keyboard_button('Browse workspace 3; active workspace');wait(lambda:'This workspace has no windows.' in empty_body()['text'])
     keyboard_button('Close Task View and return to windows');wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('EmptyWorkspaceDismissalPreservesNativeDesktopFocusAndMembership',facts()['facts']['focused'] is None and s.data('monitors')[0]['activeWorkspace']['id']==3 and len(journal())==before_empty and all(row['workspace'] in ['1','2'] for row in facts()['facts']['windows']),facts=facts())
     report['nativeEmptyWorkspaceInventoryObserved']=True
     report['emptyWorkspaceScopeMissing']=['Actual GUI workspace navigation to an empty destination, applicable AT and independent original acceptance.']
'''
source=source.replace(needle,needle+'\n'+addition);sys.argv=[str(p),'--task-view']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
