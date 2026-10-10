"""UI-006 actual keyboard/pointer navigation to an existing empty workspace."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text()
needle="     report['nativeTaskViewJourneyObserved']=not RETIRE_OPENER";assert source.count(needle)==1
addition=r'''     report.update(requirements=['ELM-UI-006'],scenarios=['overview-empty'],scope='Original populated Task View assertions retained, then physical keyboard and pointer navigation to a persistent existing ordinary empty workspace. Exact typed native receipts, active destination, empty app focus, durable journal, visible feedback, unchanged membership and dismissal; native ACK-loss fault, applicable AT and independent acceptance remain separate.')
     check('DeclareOwnedPersistentEmptyWorkspaceFixture',s.ctl('eval','hl.workspace_rule({workspace="3",persistent=true})').strip()=='ok')
     check('CreateOwnedEmptyWorkspaceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=3})').strip()=='ok')
     wait(lambda:s.data('monitors')[0]['activeWorkspace']['id']==3)
     check('SetFirstNavigationSourceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=1})').strip()=='ok')
     def geometry_receipt():
      rows=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
      rows=[row for row in rows if row.get('kind')=='geometry-facts']
      return rows[-1] if rows else None
     inventory=wait(lambda:(g:=geometry_receipt()) and g['facts'].get('activeWorkspace')=='1' and any(w['identity']=='3' for w in g['facts'].get('workspaces',[])) and not any(w['workspace']=='3' for w in g['facts']['windows']) and (projection() or {}).get('phase')=='Coherent' and g)
     check('DestinationIsRealInactiveNativeEmptyWorkspace',True,receipt=inventory)
     membership=sorted((w['incarnation'],w['workspace'],w['monitor'],w['minimized']) for w in inventory['facts']['windows'])
     before_windows=len(journal());before_workspace=len(requests('workspace-navigation'))
     def navigation_receipts():
      return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='workspace-navigation-outcome']
     def open_empty(navigable=True):
      opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['identity']=='bar:overview' and not b['disabled']),None))
      click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
      return wait(lambda:(body:=popup_body()) and (projection() or {}).get('mode')=='overview' and any(b['accessibleName']==('Go to empty workspace 3' if navigable else 'Browse workspace 3; active workspace') and not b['disabled'] for b in body['buttons']) and body)
     open_empty();keyboard_button('Browse workspace 3');wait(lambda:'This workspace has no windows.' in popup_body()['text'])
     popup_capture('empty-navigation-ready');capture=report['popupCaptures'][-1]
     check('EmptyDestinationGoControlHasActualNativePixels',any(row['accessibleName']=='Go to empty workspace 3' and row['brightPixels']>30 and row['paintedPixels']>.9*row['area'] for row in capture['controlRegions']),capture=capture)
     before_receipts=len(navigation_receipts());keyboard_button('Go to empty workspace 3',28)
     outcome=wait(lambda:len(navigation_receipts())==before_receipts+1 and navigation_receipts()[-1])
     check('KeyboardGoGetsMatchingNativeCommittedReceipt',outcome['status']=='Committed' and outcome['reason']=='applied' and outcome['intent']['source']['identity']=='1' and outcome['intent']['destination']==next(w for w in inventory['facts']['workspaces'] if w['identity']=='3') and requests('workspace-navigation')[-1]['binding']==outcome['binding'] and requests('workspace-navigation')[-1]['intent']==outcome['intent'],receipt=outcome)
     native=wait(lambda:(g:=geometry_receipt()) and g['facts'].get('activeWorkspace')=='3' and g['facts']['focused'] is None and (projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent' and g)
     check('KeyboardGoChangesOnlyNativeActiveWorkspace',s.data('monitors')[0]['activeWorkspace']['id']==3 and sorted((w['incarnation'],w['workspace'],w['monitor'],w['minimized']) for w in native['facts']['windows'])==membership and len(journal())==before_windows and len(requests('workspace-navigation'))==before_workspace+1,receipt=native)
     wait(lambda:'Workspace 3: now active.' in (bar_body() or {}).get('text',''))
     journal_path=pathlib.Path(config['runtime'])/'elm-window-recovery'/config['instance']/outcome['binding']['lifetime']/'workspace-navigation-v1.json'
     durable=json.loads(journal_path.read_text());check('NativeNavigationReceiptHasExactDurableSettlement',durable=={'schema':1,**{k:outcome[k] for k in ['binding','intent','status','reason']}},record=durable,path=str(journal_path))
     # This starts a separate pointer journey; the keyboard result was already
     # observed and settled. It never corrects a failed GUI navigation.
     check('SetSecondPointerNavigationSourceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=1})').strip()=='ok')
     wait(lambda:(g:=geometry_receipt()) and g['facts'].get('activeWorkspace')=='1' and (projection() or {}).get('phase')=='Coherent')
     body=open_empty()
     import re
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     helper([str(POINTER),'800','600'],f'move {box[0]+350} {box[1]+250}\nwheel 600 0\nsleep 100\n')
     body=wait(lambda:(b:=popup_body()) and b['publication']==(projection() or {}).get('publication') and any(w['accessibleName']=='Go to empty workspace 3' and w['y']>=0 and w['y']+w['height']<=box[3] for w in b['buttons']) and b)
     go=next(b for b in body['buttons'] if b['accessibleName']=='Go to empty workspace 3' and not b['disabled'])
     check('PointerGoInsideCurrentPresentedPopupViewport',go['y']>=0 and go['y']+go['height']<=box[3],body=body)
     x,y=map(round,(box[0]+go['x']+go['width']/2,box[1]+go['y']+go['height']/2));before_receipts=len(navigation_receipts())
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     pointer=wait(lambda:len(navigation_receipts())==before_receipts+1 and navigation_receipts()[-1])
     check('PointerGoCommitsNextTypedIdentityOnce',pointer['status']=='Committed' and int(pointer['intent']['request'])>int(outcome['intent']['request']) and pointer['intent']['destination']['identity']=='3' and len(requests('workspace-navigation'))==before_workspace+2,receipt=pointer)
     wait(lambda:s.data('monitors')[0]['activeWorkspace']['id']==3 and (g:=geometry_receipt()) and g['facts'].get('activeWorkspace')=='3' and g['facts']['focused'] is None and (projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     open_empty(False);keyboard_button('Browse workspace 3; active workspace');wait(lambda:'This workspace has no windows.' in popup_body()['text'])
     keyboard_button('Close Task View and return to windows');wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('NavigatedEmptyWorkspaceStillAllowsDismissalWithoutMutation',s.data('monitors')[0]['activeWorkspace']['id']==3 and geometry_receipt()['facts']['focused'] is None and len(requests('workspace-navigation'))==before_workspace+2 and len(journal())==before_windows,receipt=geometry_receipt())
     report['nativeEmptyWorkspaceNavigationObserved']=True
     report['workspaceNavigationMissing']=['Native lost-ack fault/restart campaign, applicable AT, independent original acceptance.']
'''
source=source.replace(needle,needle+'\n'+addition)
source=source.replace("button['accessibleName'].startswith('Browse workspace ')","button['accessibleName'].startswith(('Browse workspace ','Go to empty workspace '))")
sys.argv=[str(p),'--task-view'];exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
