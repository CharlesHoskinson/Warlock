"""UI-006 real Task View refusal; reuse the pinned cross-output native fixture."""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-taskbar-refusal.py');source=p.read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def replace(old,new):
 global source
 assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
replace("requirements=['ELM-UI-004'],scenarios=['taskbar-refusal']","requirements=['ELM-UI-006'],scenarios=['overview-refusal']")
replace('Actual current taskbar pointer Activate from another output, real native pinned implicit-transfer refusal, authoritative target/peer/focus/draft, visible current feedback and no replay.','Actual Task View filtered physical keyboard choice, real native pinned cross-output refusal, restored context/current focused control/pixels and read-only recovery without replay.')
start=source.index("    activation=group('Activate');");end=source.index("    submitted=journal()[-1]",start)
source=source[:start]+r'''    def overview_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     body=rows[-1] if rows else None;p=projection()
     return body if body and p and p.get('mode')=='overview' and p['publication']==body['publication'] else None
    def overview_key(code):physical(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100')
    def overview_button(identity):
     body=overview_body()
     return next((b for b in (body or {}).get('buttons',[]) if b['identity']==identity and not b['disabled']),None)
    def overview_choose(identity):
     button=wait(lambda:overview_button(identity))
     for _ in range(len(overview_body()['buttons'])+2):
      if overview_body()['focusIdentity']==identity:break
      overview_key(15)
     body=overview_body();check('PhysicalKeyboardReaches'+identity,body['focusIdentity']==identity and body['documentFocused'],body=body)
     overview_key(28)
    bar_rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
    opener=next(b for b in bar_rows[-1]['buttons'] if b['identity']=='bar:overview' and not b['disabled'])
    x=refusal_other['x']+opener['x']+opener['width']/2;y=refusal_other['y']+opener['y']+opener['height']/2
    helper([str(POINTER),'1600','600'],input_text=f'move {round(x)} {round(y)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
    wait(overview_body)
    selected_workspace='overview:workspace:'+str(target_before['workspace']['id'])
    overview_choose(selected_workspace)
    selected_identity='overview:family:'+target
    wait(lambda:overview_button(selected_identity) and overview_body()['focusIdentity']==selected_workspace)
    check('OverviewFilterIsRealAndObservationOnly',len(journal())==effect_before and any(b['identity']==selected_workspace and 'Selected' in b['label'] for b in overview_body()['buttons']),body=overview_body())
    report['taskViewBeforeRefusal']={'body':overview_body(),'target':target_before,'peer':peer_before,'workspace':selected_workspace,'owner':refusal_owner,'sourceOutput':refusal_other}
    overview_choose(selected_identity)
    wait(lambda:transaction_state()=='Refused' and (projection() or {}).get('phase')=='Coherent' and len(journal())==effect_before+1 and overview_body() and overview_body()['focusIdentity']==selected_identity)
''' +source[end:]
replace('ActualTaskbarGetsPinnedNativeRefusalOnce','ActualTaskViewGetsPinnedNativeRefusalOnce')
start=source.index("    peer_events=refusal_peer_control.with_suffix");end=source.index("    def refusal_reads()",start)
source=source[:start]+r'''    overview=overview_body();selected_button=overview_button(selected_identity)
    check('RefusedTaskViewRestoresExactFilterAndFamilyFocus',overview['documentFocused'] and overview['focusIdentity']==selected_identity and any(b['identity']==selected_workspace and 'Selected' in b['label'] for b in overview['buttons']) and 'refused' in overview['text'] and selected_button['width']>0 and selected_button['height']>0,body=overview)
    report['taskViewRefusalRestoredBody']=overview
''' +source[end:]
start=source.index("    read_before=len(refusal_reads());");end=source.index("    check('ActualRecoveryReadsWithoutRetryingRefusedAction'",start)
source=source[:start]+r'''    read_before=len(refusal_reads());overview_choose('overview:refresh')
    wait(lambda:len(refusal_reads())>read_before and (projection() or {}).get('phase')=='Coherent' and overview_body())
''' +source[end:]
start=source.index("    body=refusal_body();feedback=body['feedback'];report['taskbarRefusalRecoveredBody']=body");end=source.index("    check('RefusalDoesNotReplayOrLaunch'",start)
source=source[:start]+r'''    body=overview_body();report['taskViewRefusalRecoveredBody']=body
    check('ReadOnlyRefreshRetainsOverviewContext',body['documentFocused'] and body['focusIdentity']=='overview:refresh' and any(b['identity']==selected_workspace and 'Selected' in b['label'] for b in body['buttons']),body=body)
    import re
    boxes=[line for line in text().splitlines() if 'xdg_popup' in line and '.configure(' in line]
    box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',boxes[-1]).groups()))
    image=OUTPUT/'task-view-native-refused.png';helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
    for identity in [selected_workspace,selected_identity,'overview:refresh']:
     button=overview_button(identity);left=max(0,round(refusal_other['x']+box[0]+button['x']+4));top=max(0,round(refusal_other['y']+box[1]+button['y']+4));right=min(pix.get_width(),round(refusal_other['x']+box[0]+button['x']+button['width']-4));bottom=min(pix.get_height(),round(refusal_other['y']+box[1]+button['y']+button['height']-4))
     bright=sum(1 for py in range(top,bottom) for px in range(left,right) if min(pixels[py*stride+px*channels:py*stride+px*channels+3])>100)
     regions.append({'identity':identity,'region':[left,top,right,bottom],'brightPixels':bright})
    report['taskViewRefusalPixels']={'path':str(image),'sha256':sha(image),'box':box,'sourceOutput':refusal_other,'controlRegions':regions}
    check('RestoredTaskViewHasActualNativeControlPixels',all(row['brightPixels']>15 for row in regions),capture=report['taskViewRefusalPixels'])
    overview_key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
    peer_events=refusal_peer_control.with_suffix('.events.jsonl');root_lines=len(events.read_text().splitlines());peer_lines=len(peer_events.read_text().splitlines());overview_key(30)
    target_events=[json.loads(l) for l in events.read_text().splitlines()[root_lines:] if l.strip()];peer_keys=[json.loads(l) for l in peer_events.read_text().splitlines()[peer_lines:] if l.strip()]
    check('RefusalDismissalPreservesActualPeerKeyboardRecipient',not any(e.get('kind')=='key' for e in target_events) and any(e.get('kind')=='key' and e.get('keyval')==97 for e in peer_keys),targetEvents=target_events,peerEvents=peer_keys)
''' +source[end:]
replace("report['nativeTaskbarRefusalObserved']=True","report['nativeTaskViewRefusalObserved']=True")
# Execute the reviewed wrapper, retaining both original fixture sources by hash.
replace("{p.name:sha(p),pathlib.Path(__file__).name:sha(pathlib.Path(__file__))}","{p.name:sha(p),'native-taskbar-refusal.py':taskbar_refusal_sha,pathlib.Path(__file__).name:sha(pathlib.Path(__file__))}")
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(pathlib.Path(__file__)),'taskbar_refusal_sha':sha(p)})
