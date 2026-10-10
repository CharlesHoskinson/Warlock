"""ELM-UI-006: actual workspace refusal and lost-receipt recovery.

Retains the prior real keyboard/pointer empty-navigation journey, original
physical input, deadlines, pinned ABI, main preservation and normal cleanup.
"""
import ast, pathlib, sys

assert not sys.argv[1:]
p = pathlib.Path(__file__).with_name('native-window-feedback.py')
navigation = p.with_name('native-taskview-navigation.py')
tree = ast.parse(navigation.read_text())
addition = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'addition' for t in n.targets))
pointer_target = "     go=next(b for b in body['buttons'] if b['accessibleName']=='Go to empty workspace 3' and not b['disabled'])"
assert addition.count(pointer_target) == 1
addition = addition.replace(pointer_target, r'''     # Physical wheel scrolling is smooth. Observe settled current bounds
     # inside the original wait rather than clicking an in-flight old position.
     pointer_bounds=None;pointer_changed=0
     def settled_pointer_target():
      global pointer_bounds,pointer_changed
      current=popup_body();p=projection()
      if not current or not p or current['publication']!=p['publication']:return None
      candidate=next((b for b in current['buttons'] if b['accessibleName']=='Go to empty workspace 3' and not b['disabled']),None)
      if candidate is None:return None
      bounds=tuple(candidate[k] for k in ['x','y','width','height'])
      if bounds!=pointer_bounds:pointer_bounds=bounds;pointer_changed=time.monotonic();return None
      return current if time.monotonic()-pointer_changed>=.15 and candidate['y']>=0 and candidate['y']+candidate['height']<=box[3] else None
     body=wait(settled_pointer_target)
''' + pointer_target)
source = p.read_text()
old_focus = "popup_body()['focus']==button['id']"
begin = source.index('    def keyboard_button(label,code=57):')
end = source.index('    if KEYBOARD:', begin)
keyboard_helper = source[begin:end]
assert keyboard_helper.count(old_focus) == 2
# Publication stamps can change during ordinary native observation. Follow the
# same named current control, retaining physical Tab and the original bound.
source = source[:begin] + keyboard_helper.replace(old_focus, "any(b['accessibleName']==label and not b['disabled'] and popup_body()['focus']==b['id'] for b in popup_body()['buttons'])") + source[end:]
launch = "str(backend_fixture if CATALOG or CHORD else ROOT/'adapter/daemon.py')"
assert source.count(launch) == 1
source = source.replace(launch, "str(backend_fixture if CATALOG or CHORD else ROOT/'qa/workspace-navigation-transport.py')")
needle = "     report['nativeTaskViewJourneyObserved']=not RETIRE_OPENER"
assert source.count(needle) == 1
extra = r'''
     # The preceding keyboard and pointer successes have settled. Start a
     # separate genuine native refusal with an actual pinned source window.
     check('SetWorkspaceRefusalSourceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=1})').strip()=='ok')
     pin_target=next(w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE')
     selector='address:'+pin_target['address']
     check('PinActualWorkspaceRefusalSource',s.ctl('dispatch',"hl.dsp.window.pin({window='"+selector+"'})").strip()=='ok')
     refused_before=wait(lambda:(g:=geometry_receipt()) and g['facts']['activeWorkspace']=='1' and any(w['pin']['pinned'] for w in g['facts']['windows']) and (projection() or {}).get('phase')=='Coherent' and g)
     source_focus=s.data('activewindow').get('address')
     open_empty();keyboard_button('Browse workspace 3')
     before_receipts=len(navigation_receipts());before_requests=len(requests('workspace-navigation'))
     keyboard_button('Go to empty workspace 3',28)
     refused=wait(lambda:len(navigation_receipts())==before_receipts+1 and navigation_receipts()[-1])
     check('ActualWorkspaceGoGetsExactNativeRefusal',refused['status']=='Refused' and refused['reason']=='destination-not-empty' and refused['binding']==requests('workspace-navigation')[-1]['binding'] and refused['intent']==requests('workspace-navigation')[-1]['intent'] and len(requests('workspace-navigation'))==before_requests+1,receipt=refused)
     restored=wait(lambda:(b:=popup_body()) and (projection() or {}).get('mode')=='overview' and b['publication']==projection()['publication'] and 'switch refused (destination-not-empty)' in b['text'] and 'This workspace has no windows.' in b['text'] and any(w['accessibleName']=='Browse workspace 3' and w['id']==b['focus'] for w in b['buttons']) and b)
     after=geometry_receipt()
     check('NativeWorkspaceRefusalPreservesDesktopAndMembership',s.data('monitors')[0]['activeWorkspace']['id']==1 and all(after['facts'][k]==refused_before['facts'][k] for k in ['activeWorkspace','windows']) and len(journal())==before_windows,receipt=after)
     check('WorkspaceRefusalRestoresCurrentSelectionAndKeyboardFocus',any(w['accessibleName']=='Browse workspace 3' and w['id']==restored['focus'] and not w['disabled'] for w in restored['buttons']),body=restored)
     popup_capture('workspace-refused')
     keyboard_button('Refresh window status; read observations without retrying actions')
     wait(lambda:(projection() or {}).get('phase')=='Coherent' and popup_body() and 'switch refused' in popup_body()['text'])
     check('RefusalRefreshReadsWithoutWorkspaceReplay',len(requests('workspace-navigation'))==before_requests+1)
     keyboard_button('Close Task View and return to windows');wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('WorkspaceRefusalDismissalDoesNotMutate',s.data('monitors')[0]['activeWorkspace']['id']==1 and len(requests('workspace-navigation'))==before_requests+1 and len(journal())==before_windows and s.data('activewindow').get('address')==source_focus)
     # Reset only the explicitly pinned fixture after its refusal is verified.
     check('UnpinOwnedWorkspaceRefusalFixture',s.ctl('dispatch',"hl.dsp.window.pin({window='"+selector+"'})").strip()=='ok')
     wait(lambda:(g:=geometry_receipt()) and not any(w['pin']['pinned'] for w in g['facts']['windows']) and (projection() or {}).get('phase')=='Coherent')
     arm=OUTPUT/'workspace-navigation-loss.arm';arm.write_text('after-native-before-settlement\n');arm.chmod(0o600)
     marker=OUTPUT/'workspace-navigation-loss.json';release=OUTPUT/'workspace-navigation-loss.release'
     open_empty();keyboard_button('Browse workspace 3');before_requests=len(requests('workspace-navigation'));before_receipts=len(navigation_receipts())
     keyboard_button('Go to empty workspace 3',28)
     interrupted=wait(lambda:marker.exists() and json.loads(marker.read_text()))
     record=interrupted['nativeRecord'];journal_path=pathlib.Path(config['runtime'])/'elm-window-recovery'/config['instance']/record['binding']['lifetime']/'workspace-navigation-v1.json'
     check('RealNativeCommittedButFrontendReceiptLost',record['status']=='Committed' and record['intent']==requests('workspace-navigation')[-1]['intent'] and json.loads(journal_path.read_text())==interrupted['durableRecord'] and interrupted['durableRecord']['status']=='Unknown' and len(navigation_receipts())==before_receipts and s.data('monitors')[0]['activeWorkspace']['id']==3,proof=interrupted)
     unknown=wait(lambda:'switch could not be confirmed' in (bar_body() or {}).get('text','') and bar_body())
     check('LostReceiptPaintsUnknownWithoutReplay',len(requests('workspace-navigation'))==before_requests+1 and len(journal())==before_windows,body=unknown)
     image=OUTPUT/'workspace-unknown.png';helper(['/usr/bin/grim',str(image)]);report['workspaceUnknownCapture']={'path':str(image),'sha256':sha(image)}
     release.write_text('lose-receipt\n');release.chmod(0o600)
     wait(lambda:(projection() or {}).get('phase')=='Detached' and 'switch could not be confirmed' in (bar_body() or {}).get('text',''))
     reconnect=next(b for b in bar_body()['buttons'] if b['accessibleName']=='Reconnect to the window system' and not b['disabled'])
     click({'visible':0<=reconnect['x']<800 and 0<=reconnect['y']<48,'point':[reconnect['x']+reconnect['width']/2,reconnect['y']+reconnect['height']/2]})
     def recoveries():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='workspace-navigation-recovery']
     recovered=wait(lambda:(projection() or {}).get('phase')=='Coherent' and recoveries()[-1].get('record',{}).get('status')=='Committed' and recoveries()[-1])
     check('ReconnectReadsExactHistoricalWorkspaceOutcome',recovered['record']==record and recovered['binding']!=record['binding'] and len(requests('workspace-navigation'))==before_requests+1 and len(navigation_receipts())==before_receipts and json.loads(journal_path.read_text())==record,receipt=recovered)
     wait(lambda:'Workspace 3: now active.' in (bar_body() or {}).get('text',''))
     check('LostReceiptRecoveryPreservesActualDestinationAndWindowMembership',s.data('monitors')[0]['activeWorkspace']['id']==3 and geometry_receipt()['facts']['focused'] is None and sorted((w['incarnation'],w['workspace'],w['monitor'],w['minimized']) for w in geometry_receipt()['facts']['windows'])==membership and len(journal())==before_windows)
     open_empty(False);keyboard_button('Browse workspace 3; active workspace');keyboard_button('Close Task View and return to windows')
     wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('RecoveredEmptyWorkspaceStillDismissesWithoutReplay',len(requests('workspace-navigation'))==before_requests+1 and len(journal())==before_windows)
     # The broker remains live in this separate loss case. Suppress exactly
     # its real settled receipt; the taskbar must offer the existing read path.
     check('SetTaskbarReadRecoverySourceFixture',s.ctl('dispatch','hl.dsp.focus({workspace=1})').strip()=='ok')
     wait(lambda:(g:=geometry_receipt()) and g['facts']['activeWorkspace']=='1' and (projection() or {}).get('phase')=='Coherent')
     arm.write_text('after-settlement-before-frontend\n');arm.chmod(0o600)
     frontend_marker=OUTPUT/'workspace-navigation-frontend-loss.json'
     open_empty();keyboard_button('Browse workspace 3');before_requests=len(requests('workspace-navigation'));before_receipts=len(navigation_receipts());before_recoveries=len(recoveries())
     keyboard_button('Go to empty workspace 3',28)
     dropped=wait(lambda:frontend_marker.exists() and json.loads(frontend_marker.read_text()))
     unknown=wait(lambda:(projection() or {}).get('phase')=='Coherent' and 'switch could not be confirmed' in (bar_body() or {}).get('text','') and any(b['identity']=='bar:workspace-refresh' and not b['disabled'] for b in bar_body()['buttons']) and bar_body())
     check('LostFrontendReceiptOffersDirectTaskbarRead',dropped['nativeRecord']['status']=='Committed' and dropped['nativeRecord']['intent']==requests('workspace-navigation')[-1]['intent'] and len(navigation_receipts())==before_receipts and len(requests('workspace-navigation'))==before_requests+1 and s.data('monitors')[0]['activeWorkspace']['id']==3 and not any(not b['disabled'] for b in unknown['buttons'] if b['identity'].startswith('bar:group:')),body=unknown,proof=dropped)
     refresh=next(b for b in unknown['buttons'] if b['identity']=='bar:workspace-refresh')
     image=OUTPUT/'workspace-taskbar-read.png';helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
     left=max(0,round(refresh['x']+4));top=max(0,round(refresh['y']+4));right=min(pix.get_width(),round(refresh['x']+refresh['width']-4));bottom=min(pix.get_height(),round(refresh['y']+refresh['height']-4))
     bright=sum(1 for y in range(top,bottom) for x in range(left,right) if min(pixels[y*stride+x*channels:y*stride+x*channels+3])>100)
     check('DirectTaskbarReadControlHasActualNativePixels',bright>30 and right>left and bottom>top,path=str(image),sha256=sha(image),brightPixels=bright,region=[left,top,right,bottom])
     reads_before=len(requests('workspace-navigation-recover'))
     click({'visible':0<=refresh['x']<800 and 0<=refresh['y']<48,'point':[refresh['x']+refresh['width']/2,refresh['y']+refresh['height']/2]})
     read=wait(lambda:len(recoveries())>before_recoveries and recoveries()[-1]['record']['status']=='Committed' and 'Workspace 3: now active.' in (bar_body() or {}).get('text','') and recoveries()[-1])
     check('PhysicalTaskbarReadSettlesExactOutcomeWithoutReplay',read['record']==dropped['nativeRecord'] and len(requests('workspace-navigation-recover'))==reads_before+1 and len(requests('workspace-navigation'))==before_requests+1 and len(navigation_receipts())==before_receipts and len(journal())==before_windows and not any(b['identity']=='bar:workspace-refresh' for b in bar_body()['buttons']),receipt=read)
     check('TaskbarReadPreservesEmptyDestinationAndMembership',s.data('monitors')[0]['activeWorkspace']['id']==3 and geometry_receipt()['facts']['focused'] is None and sorted((w['incarnation'],w['workspace'],w['monitor'],w['minimized']) for w in geometry_receipt()['facts']['windows'])==membership)
     report['nativeWorkspaceRefusalObserved']=True;report['nativeWorkspaceReceiptLossRecoveryObserved']=True
     report['nativeTaskbarWorkspaceReadObserved']=True
     report['scope']='Original populated Task View and real keyboard/pointer empty navigation retained, actual pinned-source workspace Refused and restored context/dismissal; real native receipt interrupted before durable settlement and frontend delivery, exact historical recovery after authenticated reconnect, then a separate settled receipt loss with painted direct taskbar read recovery and no replay. Applicable AT and independent original acceptance remain separate.'
     report['workspaceNavigationMissing']=['Applicable AT and independent original acceptance; no physical hardware claim.']
     report['workspaceTransportFixture']={'path':str(ROOT/'qa/workspace-navigation-transport.py'),'sha256':sha(ROOT/'qa/workspace-navigation-transport.py'),'scope':'One real native Committed result interrupted before durable settlement/frontend delivery; original timer, new authenticated broker, exact read-only historical recovery and no replay.'}
'''
inputs = "\n     report['workspaceRecoveryInputs']={name:sha(ROOT/'qa'/name) for name in ['native-workspace-recovery.py','workspace-navigation-transport.py','native-taskview-navigation.py','native-window-feedback.py']}\n     for name in report['workspaceRecoveryInputs']:(OUTPUT/name).write_bytes((ROOT/'qa'/name).read_bytes())\n"
source = source.replace(needle, needle + inputs + addition + extra)
source = source.replace("button['accessibleName'].startswith('Browse workspace ')", "button['accessibleName'].startswith(('Browse workspace ','Go to empty workspace '))")
sys.argv = [str(p), '--task-view']
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__})
