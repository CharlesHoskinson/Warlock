"""ELM-UI-006: original cross-workspace restore and cancel through real AT.

Retains the existing native keyboard/pixel/recipient/receipt assertions and
original deadlines. Accessible objects and reader output are never fabricated.
"""
import hashlib, pathlib, sys

assert not sys.argv[1:]
p = pathlib.Path(__file__).with_name('native-window-feedback.py')
source = p.read_text()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def replace(old, new):
    global source
    assert source.count(old) == 1, (old, source.count(old))
    source = source.replace(old, new)

replace("ACCESSIBILITY=sys.argv[1:]==['--accessibility']", 'ACCESSIBILITY=True')
replace("SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY", "SWITCHER=sys.argv[1:]==['--switcher']")
begin = source.index('    def keyboard_button(label,code=57):')
end = source.index('    if KEYBOARD:', begin)
helper = source[begin:end]
old = "popup_body()['focus']==button['id']"
assert helper.count(old) == 2
helper = helper.replace(old, "any(b['accessibleName']==label and not b['disabled'] and popup_body()['focus']==b['id'] for b in popup_body()['buttons'])")
helper = helper.replace('     key(code)', '     taskview_at_focus(label)\n     key(code)')
source = source[:begin] + helper + source[end:]
needle = '     def peer_window():return next(w for w in facts()[\'facts\'][\'windows\'] if w[\'incarnation\']==peer_identity)'
addition = r'''     report.update(requirements=['ELM-UI-006'],scenarios=['overview-select','overview-cancel'],scope='Original minimized cross-workspace Task View selection/native restore receipt/workspace/focus/client keyboard/pixels retained, with real private AT-SPI names/states and Orca focus/speech. Cancellation has zero effect and eligible opener return. Independent original acceptance remains separate.')
     report['taskViewAtInputs']=taskview_at_inputs;report['accessibilitySnapshots']=[]
     for name in taskview_at_inputs:(OUTPUT/name).write_bytes((ROOT/'qa'/name).read_bytes())
     def taskview_at_snapshot(stage):
      def observed():
       body=popup_body();p=projection()
       if not body or not p or p['phase']!='Coherent' or body['publication']!=p['publication']:return None
       names=[b['accessibleName'] for b in body['buttons']]
       value=at_observe();rows=[row for row in value['nodes'] if row.get('pid')==web.pid and row['role'] in ['button','push button','toggle button'] and row['name'] in names]
       return (value,rows,body) if sorted(row['name'] for row in rows)==sorted(names) else None
      value,rows,body=wait(observed);report['accessibilitySnapshots'].append({'stage':stage,**value})
      check(stage+'ActualNativeAtNamesRolesAndHostIdentity',all(row['pid']==web.pid for row in rows),nodes=rows,body=body)
      return value,rows,body
     def taskview_at_focus(label):
      def observed():
       value=at_observe();focus=(value.get('reader') or {}).get('focus') or {}
       rows=[row for row in value['nodes'] if row.get('pid')==web.pid and row['name']==label and 'focused' in row['states'] and row['role'] in ['button','push button','toggle button']]
       return (value,rows[0]) if len(rows)==1 and focus.get('name')==label and focus.get('role') in ['button','push button','toggle button'] else None
      value,row=wait(observed);report['accessibilitySnapshots'].append({'stage':'Focus:'+label,**value})
      check('ActualTaskViewOrcaAndNativeFocusAgree',{'enabled','sensitive','visible','showing','focused'}<=set(row['states']),node=row,reader=value['reader'])
'''
replace(needle, addition + needle)
needle = "     keyboard_button(button['accessibleName']);restored('TaskViewRestore',before)"
addition = r'''     taskview_at_snapshot('TaskViewBeforeFilter')
     keyboard_button('Browse workspace 2')
     value,rows,body=taskview_at_snapshot('TaskViewWorkspaceTwoFilter')
     filters=[row for row in rows if row['name'].startswith('Browse ')]
     check('ActualAtWorkspaceFilterHasOneCurrentPressedState',sum(bool({'pressed','checked'} & set(row['states'])) for row in filters)==1 and any(row['name']=='Browse workspace 2' and {'pressed','checked'} & set(row['states']) for row in filters),nodes=filters)
     check('AtBrowseDoesNotRestoreOrNavigate',len(journal())==before and peer_window()['minimized'] and s.data('monitors')[0]['activeWorkspace']['id']==1)
     keyboard_button('Close Task View and return to windows',28)
     wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('AtTaskViewCancelHasNoNativeMutation',len(journal())==before and peer_window()['minimized'] and s.data('monitors')[0]['activeWorkspace']['id']==1 and native_membership()==original_membership)
     def opener_return():
      body=bar_body();p=projection()
      if not body or not p or body['publication']!=p['publication']:return None
      opener=next((b for b in body['buttons'] if b['accessibleName']=='Open Task View' and not b['disabled']),None)
      return body if opener and body['focus']==opener['id'] else None
     returned=wait(opener_return);value=at_observe();report['accessibilitySnapshots'].append({'stage':'TaskViewCancelled',**value})
     check('AtCancellationReturnsCurrentEligibleOpener',any(row.get('pid')==web.pid and row['name']=='Open Task View' and 'focused' in row['states'] for row in value['nodes']) and (value.get('reader') or {}).get('focus',{}).get('name')=='Open Task View',body=returned,reader=value.get('reader'))
     opener=next(b for b in returned['buttons'] if b['accessibleName']=='Open Task View' and not b['disabled'])
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if 'ELM-ACTIVATION-PEER on workspace 2' in b['accessibleName'] and not b['disabled']),None))
     taskview_at_snapshot('TaskViewReopenedBeforeRestore')
'''
replace(needle, addition + needle)
needle = "     report['nativeNavigationJourneyObserved']=True"
addition = r'''     utterances=OUTPUT/'orca-utterances.jsonl';report['orcaSpeechOutput']=[json.loads(line) for line in utterances.read_text().splitlines()]
     check('ActualOrcaSpeaksTaskViewFilterRestoreAndDismissal',all(any(name in row.get('text','') for row in report['orcaSpeechOutput']) for name in ['Browse workspace 2','Restore ELM-ACTIVATION-PEER','Close Task View']),utterances=report['orcaSpeechOutput'])
     report['nativeTaskViewAtObserved']=True;report['accessibilityFixture']['nativeATObserved']=True
'''
replace(needle, addition + needle)
inputs = {p.name: sha(p), pathlib.Path(__file__).name: sha(pathlib.Path(__file__)), **{name: sha(p.with_name(name)) for name in ['accessibility-session.py', 'accessibility-inspector.py', 'accessibility-reader.py']}}
sys.argv = [str(p), '--workspace-navigation']
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__, 'taskview_at_inputs': inputs})
