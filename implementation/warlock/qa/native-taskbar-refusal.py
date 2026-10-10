"""UI-004 real taskbar activation refused by native pinned-output guard; AT/independent acceptance separate."""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
needle='retirement_fixture=None';assert source.count(needle)==1
fixture=r'''refusal_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');refusal_inputs.mkdir(mode=0o700,exist_ok=True)
original_refusal_fixture=FIXTURE;fixture_source=FIXTURE.read_text();entry_needle='    content.put(entry,8,8)';assert fixture_source.count(entry_needle)==1
fixture_source=fixture_source.replace(entry_needle,entry_needle+"\n    entry.connect('changed',lambda entry:log(name,'draft',text=entry.get_text()))\n    entry.set_text('UNSAVED-WARLOCK-REFUSAL-DRAFT')")
FIXTURE=refusal_inputs/'refusal-fixture.py';FIXTURE.write_text(fixture_source)
'''
source=source.replace(needle,fixture+'\n'+needle)
needle="    report['nativeDragOwnershipObserved']=True";assert source.count(needle)==1
addition=r'''    report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-refusal'],scope='Actual current taskbar pointer Activate from another output, real native pinned implicit-transfer refusal, authoritative target/peer/focus/draft, visible current feedback and no replay. Original two-output drag/custody fixture retained; AT/independent original acceptance separate.')
    report['taskbarRefusalInputs']=refusal_source_inputs
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('phase')=='Coherent' and (projection() or {}).get('mode')=='closed')
    refusal_before_pin=root_window();refusal_owner=next(m for m in s.data('monitors') if m['id']==refusal_before_pin['monitor']);refusal_other=next(m for m in s.data('monitors') if m['id']!=refusal_owner['id'])
    check('PinActualTargetOnLiveOutput',s.ctl('dispatch',"hl.dsp.window.pin({window='address:"+refusal_before_pin['address']+"'})").strip()=='ok')
    wait(lambda:root_window()['pinned'] and (projection() or {}).get('phase')=='Coherent')
    check('PinnedRefusalFixtureRetainsPlacement',all(root_window()[k]==refusal_before_pin[k] for k in ['workspace','monitor','at','size']))
    # Independent original GTK green root creates a second application family.
    peer_source=FIXTURE.read_text();initial="create('ELM-AUTHORITY-FIXTURE', 'red')\ncreate('ELM-ACTIVATION-PEER', 'green')";assert peer_source.count(initial)==1 and peer_source.count('control = Path(sys.argv[1])')==1
    peer_source=peer_source.replace('control = Path(sys.argv[1])',"GLib.set_prgname('warlock-refusal-peer')\ncontrol = Path(sys.argv[1])").replace(initial,"create('ELM-ACTIVATION-PEER', 'green')")
    refusal_peer_fixture=refusal_inputs/'refusal-peer-fixture.py';refusal_peer_fixture.write_text(peer_source)
    check('SelectOtherOutputForPeerFixture',s.ctl('dispatch','hl.dsp.focus({monitor="'+refusal_other['name']+'"})').strip()=='ok')
    refusal_peer_control=OUTPUT/'refusal-peer-control.json';refusal_peer=s.host.launch('refusal-peer-fixture',['/usr/bin/python3','-B',str(refusal_peer_fixture),str(refusal_peer_control)],env=env);apps.append(refusal_peer)
    wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')))
    peer_setup=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER');report['taskbarRefusalPeerSetup']={'initial':peer_setup,'target':root_window(),'monitors':s.data('monitors')}
    # Declare the initial inactive-pin/other-output-active-peer scene using
    # existing supported native fixture commands before the GUI action.
    if peer_setup['monitor']!=refusal_other['id']:
     check('InitializePeerOnDeclaredOtherWorkspace',s.ctl('dispatch',"hl.dsp.window.move({workspace="+str(refusal_other['activeWorkspace']['id'])+",follow=false,window='address:"+peer_setup['address']+"'})").strip()=='ok')
    check('InitializeActiveOtherOutputPeer',s.ctl('dispatch',"hl.dsp.focus({window='address:"+peer_setup['address']+"'})").strip()=='ok')
    wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' and w['monitor']==refusal_other['id'] for w in s.data('clients')))
    peer_identity=next(w['incarnation'] for w in client.snapshot('442')['windows'] if w['label']=='ELM-ACTIVATION-PEER');wait(lambda:facts()['facts']['focused']==peer_identity and (projection() or {}).get('phase')=='Coherent' and group('Activate'))
    target_before=root_window();peer_before=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER');effect_before=len(journal());before_facts=facts()
    activation=group('Activate');x,y=activation['point'];x+=refusal_other['x'];y+=refusal_other['y']
    report['taskbarRefusalAttempt']={'target':target_before,'peer':peer_before,'facts':before_facts,'button':activation,'owner':refusal_owner,'sourceOutput':refusal_other}
    helper([str(POINTER),'1600','600'],input_text=f'move {round(x)} {round(y)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    wait(lambda:transaction_state()=='Refused' and (projection() or {}).get('phase')=='Coherent' and len(journal())==effect_before+1)
    submitted=journal()[-1]
    def refusal_receipts():return [f for f in [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ')] if f.get('kind')=='effect-outcome' and f.get('binding')==submitted['binding'] and f.get('intent')==submitted['intent']]
    receipts=wait(refusal_receipts);check('ActualTaskbarGetsPinnedNativeRefusalOnce',submitted['intent']['operation']=='activate' and submitted['intent']['incarnation']==target and len(receipts)==1 and receipts[0]['status']=='Refused' and receipts[0]['reason']=='implicit-transfer-required',request=submitted,receipts=receipts)
    check('RefusalPreservesAuthoritativeNativeWindowsAndFocus',facts()['facts']['focused']==peer_identity and root_window()['pinned'] and all(root_window()[k]==target_before[k] for k in ['workspace','monitor','at','size']) and all(next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')[k]==peer_before[k] for k in ['workspace','monitor','at','size']),target=root_window(),peer=peer_before,facts=facts())
    def refusal_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')];body=rows[-1] if rows else None;p=projection()
     return body if body and p and p['publication']==body['publication'] and body.get('feedback') and 'refused' in body['feedback']['text'] else None
    body=wait(refusal_body);feedback=body['feedback'];check('CurrentTaskbarRefusalFeedbackVisible',feedback['width']>0 and feedback['height']>0 and feedback['y']>=0 and feedback['y']+feedback['height']<=48 and feedback['clip']=='none' and feedback['display']!='none',body=body)
    recovery=next(b for b in body['buttons'] if b['identity']=='bar:recovery-refresh');actions=body['actions']
    check('RefusedReadOnlyRecoveryVisibleWithoutScrolling',not recovery['disabled'] and recovery['x']>=actions['x'] and recovery['x']+recovery['width']<=actions['x']+actions['width'],recovery=recovery,actions=actions)
    check('RefusedTargetRemainsInactiveActivate',group('Activate') is not None and group('Minimize') is None,projection=projection())
    events=control.with_suffix('.events.jsonl');draft=lambda:[json.loads(l) for l in events.read_text().splitlines() if l.strip() and json.loads(l).get('kind')=='draft' and json.loads(l).get('window')=='ELM-AUTHORITY-FIXTURE']
    check('PinnedRefusalKeepsUnsavedDraft',draft()[-1]['text']=='UNSAVED-WARLOCK-REFUSAL-DRAFT',draft=draft()[-1])
    peer_events=refusal_peer_control.with_suffix('.events.jsonl');root_lines=len(events.read_text().splitlines());peer_lines=len(peer_events.read_text().splitlines());physical('key 30 1\nsleep 50\nkey 30 0\nsleep 100')
    report['taskbarRefusalKeyboardObservation']={'targetEvents':[json.loads(l) for l in events.read_text().splitlines()[root_lines:] if l.strip()],'peerEvents':[json.loads(l) for l in peer_events.read_text().splitlines()[peer_lines:] if l.strip()],'bar':refusal_body()}
    check('RefusalCannotSendKeysToPinnedInactiveTarget',not any(e.get('kind')=='key' for e in report['taskbarRefusalKeyboardObservation']['targetEvents']),observation=report['taskbarRefusalKeyboardObservation'])
    check('RefusalPreservesActualPeerKeyboardRecipient',any(e.get('kind')=='key' and e.get('keyval')==97 for e in report['taskbarRefusalKeyboardObservation']['peerEvents']),observation=report['taskbarRefusalKeyboardObservation'])
    def refusal_reads():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind'] in ['projection-request','geometry-facts-request']]
    read_before=len(refusal_reads());rx=recovery['x']+recovery['width']/2+refusal_other['x'];ry=recovery['y']+recovery['height']/2+refusal_other['y']
    helper([str(POINTER),'1600','600'],input_text=f'move {round(rx)} {round(ry)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    wait(lambda:len(refusal_reads())>read_before and (projection() or {}).get('phase')=='Coherent' and refusal_body())
    check('ActualRecoveryReadsWithoutRetryingRefusedAction',len(journal())==effect_before+1 and transaction_state()=='Refused' and root_window()['pinned'] and all(root_window()[k]==target_before[k] for k in ['workspace','monitor','at','size']) and facts()['facts']['focused']==peer_identity and draft()[-1]['text']=='UNSAVED-WARLOCK-REFUSAL-DRAFT',reads=refusal_reads()[read_before:],facts=facts(),target=root_window())
    body=refusal_body();feedback=body['feedback'];report['taskbarRefusalRecoveredBody']=body
    image=OUTPUT/'taskbar-native-refused.png';helper(['/usr/bin/grim',str(image)]);report['taskbarRefusalPixels']={'path':str(image),'sha256':sha(image),'feedback':feedback,'sourceOutput':refusal_other}
    check('RefusalDoesNotReplayOrLaunch',len(journal())==effect_before+1 and not any(json.loads(l.split(': ',1)[1])['kind']=='application-launch' for l in text().splitlines() if l.startswith('frontend-request: ')))
    report['taskbarRefusalFixture']={'original':str(original_refusal_fixture),'originalSHA256':sha(original_refusal_fixture),'rootFixture':str(FIXTURE),'rootFixtureSHA256':sha(FIXTURE),'peerFixture':str(refusal_peer_fixture),'peerFixtureSHA256':sha(refusal_peer_fixture),'scope':'Only original GTK draft observer and independent green peer process/program identity; no replacement GUI/native effect policy.'}
    report['nativeTaskbarRefusalObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition);sys.argv=[str(p),'--drag-ownership']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'refusal_source_inputs':{p.name:sha(p),pathlib.Path(__file__).name:sha(pathlib.Path(__file__))}})
