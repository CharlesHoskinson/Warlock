"""Original UI-005 unavailable catalog and keyboard/AT observation-only retry.

Owned desktop metadata exceeds the unchanged name bound. The real authority
returns null. Duplicate only its exact genuine failed receipt, via its writer.
"""
import hashlib,pathlib,sys
assert sys.argv[1:] in ([],['--at-actions'])
at_actions=bool(sys.argv[1:]);base=pathlib.Path(__file__).with_name('native-window-feedback.py');source=base.read_text();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for old,new in [("ACCESSIBILITY=sys.argv[1:]==['--accessibility']",'ACCESSIBILITY=True'),("SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY","SWITCHER=sys.argv[1:]==['--switcher']")]:
 assert source.count(old)==1;source=source.replace(old,new)
# Retain original raw bytes of the specifically observed Mesa diagnostic
# interleaving; never filter requests/receipts or widen the original deadline.
needle="    return raw[:raw.rfind('\\n')+1]";assert source.count(needle)==1
source=source.replace(needle,r'''    complete=raw[:raw.rfind('\n')+1];lines=[]
    for line in complete.splitlines():
     if line.startswith(('surface-report: origin=bar ','surface-report: origin=popup ','surface-inspection: ')):
      try:json.loads(line.split(': ',1)[1] if line.startswith('surface-inspection: ') else line.split(' ',2)[2])
      except json.JSONDecodeError:
       if '{mesa ' not in line:raise
       digest=hashlib.sha256(line.encode()).hexdigest();rows=report.setdefault('interleavedReadOnlyDiagnostics',[])
       if not any(r['sha256']==digest for r in rows):rows.append({'sha256':digest,'bytes':len(line.encode()),'scope':'Mesa-interleaved readonly diagnostic only. Raw bytes retained; no protocol frames filtered.'})
       continue
     lines.append(line)
    return '\n'.join(lines)+'\n' ''')
needle='   if JUMP or KEYBOARD:';assert source.count(needle)==1
fixture=r'''   if SEARCH:
    unavailable_editor=catalog_root/'warlock-editor.desktop';valid_editor=unavailable_editor.read_text()
    broken_editor='[Desktop Entry]\nType=Application\nName='+('X'*513)+'\nGenericName=Text editor\nExec=/usr/bin/true\n'
    backend_code='import importlib.util,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nspec=importlib.util.spec_from_file_location("real_warlock_backend",'+repr(str(ROOT/'adapter/daemon.py'))+')\ndaemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)\nsys.argv=[str(spec.origin),'+repr(str(broker_config))+']\noriginal_send=daemon.send\ndef send(frame):\n original_send(frame)\n if frame.get("kind")=="application-catalog" and frame.get("snapshot") is None:original_send(frame)\ndaemon.send=send\nraise SystemExit(daemon.run())\n'
    backend_fixture.write_text(backend_code);report['catalogFixture']['backendSHA256']=sha(backend_fixture)
    report['unavailableFixture']={'desktop':str(unavailable_editor),'validDesktopSHA256':sha(unavailable_editor),'failedMetadataNameUnits':513,'unchangedBoundUnits':512,'realDaemonSHA256':sha(ROOT/'adapter/daemon.py'),'scope':'Actual owned metadata exceeds unchanged CatalogAuthority text bound, yielding genuine null snapshot. Exact genuine failure receipt delivered twice through unchanged bounded writer; no failure frame or accessible node invented.'}
'''
source=source.replace(needle,fixture+needle)
needle="      if KEYBOARD:selected=button['id']==body['focus']";assert source.count(needle)==1
source=source.replace(needle,"      if SEARCH:selected=button['accessibleName'] in ['Refresh applications','Open Files']\n"+needle)
start=source.index("    else:\n     click(wait(lambda:(projection() or {}).get('openApplications')));wait(lambda:field_value()==''");end=source.index('   elif DENSEPICKER:',start)
journey=r'''    else:
     report.update(requirements=['ELM-UI-005','ELM-UI-010'],scenarios=['search-unavailable','announce-adapter unavailable'],scope='Genuine failed catalog snapshot, retained query, one current correlated polite failure per explicit read despite duplicated real receipts, actual keyboard/AT focused retry, native control pixels, successful read-only recovery with zero launch/window effects. Independent acceptance and audible/braille output remain separate.',popupPresentationAccepted=False)
     report['unavailableInputs']=unavailable_inputs;report['unavailableAtActionMode']=unavailable_at_actions
     def frames():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')=='application-catalog']
     def cues():return [row for row in [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('announcement-delivery: ')] if (corr:=json.loads(row['message']['correlation'])).get('outcome')=='adapter-unavailable' and corr.get('identity',{}).get('adapter')=='applications']
     def current_body():
      body=popup_body();p=projection()
      return body if body and p and p['phase']=='Coherent' and p['mode']=='applications' and body['publication']==p['publication'] else None
     def failed_body():
      body=current_body()
      return body if body and field_value()=='files' and 'Application list unavailable' in body['text'] and any(b['accessibleName']=='Refresh applications' and not b['disabled'] for b in body['buttons']) else None
     def focus_refresh():
      body=wait(current_body);button=next(b for b in body['buttons'] if b['accessibleName']=='Refresh applications' and not b['disabled'])
      for _ in range(len(body['buttons'])+2):
       body=wait(current_body)
       if body['focusIdentity']=='control:refresh':break
       key(15)
      body=wait(current_body);check('PhysicalKeyboardReachesCurrentRefresh',body['focusIdentity']=='control:refresh' and body['documentFocused'],body=body);return button
     def at_refresh(stage,require_status=False):
      def observed():
       value=at_observe();reader=(value.get('reader') or {}).get('focus') or {};nodes=[n for n in value['nodes'] if n.get('pid')==web.pid and n['name']=='Refresh applications' and n['role'] in ['button','push button','toggle button'] and not any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in n['ancestors'])]
       statuses=[n for n in value['nodes'] if n.get('pid')==web.pid and ('Application list unavailable' in n['name'] or 'Applications unavailable.' in n['name'])]
       return (value,nodes[0],statuses) if len(nodes)==1 and {'focused','enabled','sensitive','visible','showing'}<=set(nodes[0]['states']) and reader.get('name')=='Refresh applications' and (statuses or not require_status) else None
      value,node,statuses=wait(observed);report.setdefault('unavailableAtSnapshots',[]).append({'stage':stage,**value});check(stage+'ActualAtRetryAndOrcaFocusAgree',bool(node) and (bool(statuses) or not require_status),node=node,statuses=statuses,reader=value['reader']);return node
     def retry(stage,at=False):
      focus_refresh();node=at_refresh(stage,True)
      if at:
       receipt=OUTPUT/('retry-'+stage+'.json');helper(['/usr/bin/python3','-B',str(ROOT/'qa/launcher-retry-at-action.py'),str(web.pid),node['identity'],node['name'],str(receipt)]);report.setdefault('unavailableAtActions',[]).append(json.loads(receipt.read_text()))
      else:key(28)
     helper([str(keyboard)],'key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100\nsync\n')
     wait(lambda:field_value()=='' and any(b['accessibleName']=='Open Files' and not b['disabled'] for b in (current_body() or {}).get('buttons',[])))
     query([33,23,38,18,31],'files');wait(lambda:'Choose a matching application.' in current_body()['text']);initial=current_body();initial_reads=len(requests('catalog-request'))
     unavailable_editor.write_text(broken_editor);report['unavailableFixture']['failedDesktopSHA256']=sha(unavailable_editor)
     focus_refresh();before=wait(current_body);key(28);body=wait(failed_body);failed=frames()[-1]
     check('GenuineNullCatalogPreservesQueryAndReachableRetry',failed['snapshot'] is None and field_value()=='files' and len(requests('catalog-request'))==initial_reads+1 and not launches() and not journal(),receipt=failed,body=body)
     check('CatalogFailurePublishesOneCorrelatedPoliteNotice',len(cues())==1 and not cues()[0]['message']['interrupt'] and cues()[0]['recipient']==cues()[0]['announcer'] and cues()[0]['recipient']['surface']=='popup' and len(body['announcements'])==1 and body['announcements'][0]['live']=='polite',cues=cues(),body=body)
     correlation=json.loads(cues()[0]['message']['correlation']);check('FailureNoticeHasExactRequestIdentity',correlation['binding']==failed['binding'] and correlation['identity']=={'adapter':'applications','request':failed['requestId'],'service':None,'revision':None},receipt=failed,correlation=correlation)
     check('FailureReceiptDoesNotRelocateKeyboardFocus',body['focusNode']==before['focusNode'] and body['focusIdentity']==before['focusIdentity'] and body['documentFocused'],before=before,after=body)
     check('DuplicatedGenuineFailureAnnouncesOnce',sum(f['requestId']==failed['requestId'] for f in frames())==2 and len(cues())==1,receipts=frames(),cues=cues())
     at_refresh('Unavailable',True);popup_capture('unavailable');capture=report['popupCaptures'][-1];check('UnavailableRefreshActuallyPaints',len(capture['controlRegions'])==1 and capture['controlRegions'][0]['accessibleName']=='Refresh applications' and capture['controlRegions'][0]['brightPixels']>30 and capture['controlRegions'][0]['paintedPixels']>.9*capture['controlRegions'][0]['area'],capture=capture)
     key(28);wait(lambda:len(cues())==2 and failed_body());second=frames()[-1];check('ExplicitFailedRetryHasFreshIdentityAndNoReplay',second['requestId']!=failed['requestId'] and second['snapshot'] is None and sum(f['requestId']==second['requestId'] for f in frames())==2 and not launches() and not journal() and len(requests('catalog-request'))==initial_reads+2,receipt=second,cues=cues())
     # Unavailable field Enter is explicitly observation-only. Use real keys to
     # reach the input; no helper Focus, script injection or corrected timeout.
     helper([str(keyboard)],'key 42 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 42 0\nsleep 100\nsync\n');helper([str(keyboard)],'key 42 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 42 0\nsleep 100\nsync\n');wait(lambda:current_body()['focus']=='launcher-search');key(28)
     check('UnavailableFieldEnterCannotLaunchOrReadAgain',not launches() and not journal() and len(requests('catalog-request'))==initial_reads+2 and field_value()=='files')
     unavailable_editor.write_text(valid_editor);retry('Recovery',unavailable_at_actions)
     recovered_body=wait(lambda:(body:=current_body()) and field_value()=='files' and any(b['accessibleName']=='Open Files' and not b['disabled'] for b in body['buttons']) and body);recovered=frames()[-1]
     check('ExplicitRetryRecoversCurrentCatalogWithoutAutomaticLaunch',recovered['snapshot'] is not None and recovered['requestId']!=second['requestId'] and len(requests('catalog-request'))==initial_reads+3 and len(cues())==2 and not launches() and not journal() and not any(b['accessibleName']=='Open Editor' for b in recovered_body['buttons']),receipt=recovered,body=recovered_body)
     focus_refresh();at_refresh('Recovered');popup_capture('recovered');capture=report['popupCaptures'][-1];check('RecoveredResultAndRetryActuallyPaint',len(capture['controlRegions'])==2 and all(r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     report['unavailableSchedule']={'initial':initial,'firstFailure':failed,'secondFailure':second,'recovered':recovered,'failureBody':body,'recoveredBody':recovered_body,'receipts':frames(),'requests':requests('catalog-request'),'cues':cues()}
     report['unavailableOrcaSpeech']=[json.loads(l) for l in (OUTPUT/'orca-utterances.jsonl').read_text().splitlines()]
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');check('RecoveryAndEscapeNeverMutateWindowOrLaunch',not launches() and not journal())
     report['nativeLauncherUnavailableKeyboardObserved']=True;report['nativeLauncherUnavailableAtActionObserved']=unavailable_at_actions;report['popupControlsPhysicallyObserved']=True
'''
source=source[:start]+journey+source[end:]
inputs={base.name:sha(base),pathlib.Path(__file__).name:sha(pathlib.Path(__file__)),**{n:sha(base.with_name(n)) for n in ['accessibility-session.py','accessibility-inspector.py','accessibility-reader.py','launcher-retry-at-action.py']}}
sys.argv=[str(base),'--launcher-search']
exec(compile(source,str(base),'exec'),{'__name__':'__main__','__file__':str(base),'unavailable_inputs':inputs,'unavailable_at_actions':at_actions})
