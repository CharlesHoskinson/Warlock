"""Original two-output drag journey plus current-output launcher pixels and real keyboard no-match."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-window-feedback.py');source=p.read_text()
needle="    report['nativeDragOwnershipObserved']=True"
assert source.count(needle)==1
addition=r'''    import re
    report.update(requirements=['ELM-UX-023','ELM-UI-005'],scenarios=['ux-023','search-no-match'],scope='Current focused-output Apps chord and native configured popup, actual control pixels and keyboard no-match/query retention. Original two-output move/resize/cancel/refusal/capture retained; AT/hardware/independent acceptance remain open.')
    def shortcut_popup_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     b=rows[-1] if rows else None;q=projection()
     return b if b and q and b.get('publication')==q.get('publication') and q.get('mode')=='applications' else None
    body=wait(lambda:(b:=shortcut_popup_body()) and b.get('focus')=='launcher-search' and b.get('documentFocused') and b.get('fields') and any(x['accessibleName']=='Refresh applications' and not x['disabled'] for x in b['buttons']) and b)
    # Native event retains the press-time focus monitor, while the host exposes
    # current issued view identities/geometry. Inspect both without moving focus.
    events=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')=='shell-shortcuts']
    event=events[-1]['events'][-1];box=event['output'];native=root_window()
    monitor=next(m for m in s.data('monitors') if m['id']==native['monitor'])
    check('ShortcutCapturesActualFocusedNativeOutput',box==[monitor['x'],monitor['y'],monitor['width']/monitor['scale'],monitor['height']/monitor['scale']],event=event,monitor=monitor)
    commits=[l for l in text().splitlines() if l.startswith('view-commit: popup=')]
    owner=int(re.search(r'popup=(\d+)',commits[-1]).group(1))
    rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('view-topology: ')]
    topology=rows[-1];location=next(row for row in topology['locations'] if int(row['scope']['id'])==owner)
    check('ShortcutUsesCurrentMatchingHostView',location['box']==box and owner==2,topology=topology,owner=owner,event=event)
    before_journal=len(journal());before_geometry=root_window()
    # Preserve the original real keyboard 50ms/100ms cadence; text is never a command.
    for code in [44,44,44,44,16,47]:physical(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100')
    query='zzzzqv'
    body=wait(lambda:(b:=shortcut_popup_body()) and any(f['value']==query for f in b.get('fields',[])) and 'No matching applications' in b.get('text','') and b)
    check('CurrentOutputKeyboardNoMatchRetainsQueryAndFocus',body['focus']=='launcher-search' and body['documentFocused'] and not any(b['accessibleName'].startswith('Launch ') for b in body['buttons']),body=body)
    check('NoMatchNeverLaunchesOrMutatesWindow',len(journal())==before_journal and root_window()['at']==before_geometry['at'] and root_window()['size']==before_geometry['size'] and not any(json.loads(l.split(': ',1)[1])['kind']=='application-launch' for l in text().splitlines() if l.startswith('frontend-request: ')))
    configured=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l]
    local=list(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',configured[-1]).groups()))
    global_box=[box[0]+local[0],box[1]+local[1],local[2],local[3]]
    check('ActualPopupRemainsInsideShortcutOutput',global_box[0]>=box[0] and global_box[1]>=box[1]+48 and global_box[0]+global_box[2]<=box[0]+box[2] and global_box[1]+global_box[3]<=box[1]+box[3],local=local,globalBox=global_box,output=box)
    image=OUTPUT/'shortcut-current-output.png';helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
    for button in body['buttons']:
     if button['accessibleName'] not in ['Refresh applications','Close applications and return to windows']:continue
     x,y,w,h=global_box;l=max(0,int(x+button['x'])+12);t=max(0,int(y+button['y'])+6);rr=min(pix.get_width(),int(x+button['x']+button['width'])-12);bb=min(pix.get_height(),int(y+button['y']+button['height'])-6)
     area=max(0,rr-l)*max(0,bb-t);bright=sum(1 for py in range(t,bb) for px in range(l,rr) if all(pixels[py*stride+px*channels+c]>170 for c in range(3)));painted=sum(1 for py in range(t,bb) for px in range(l,rr) if all(pixels[py*stride+px*channels+c]>15 for c in range(3)))
     regions.append({'accessibleName':button['accessibleName'],'brightPixels':bright,'paintedPixels':painted,'area':area,'region':[l,t,rr,bb]})
     check('CurrentOutputPaintedControl'+button['accessibleName'],area>0 and bright>15 and painted>.9*area,region=regions[-1])
    check('BothCurrentOutputLauncherControlsObserved',len(regions)==2)
    report['shortcutOutputCapture']={'path':str(image),'sha256':sha(image),'nativeBox':global_box,'owner':location['scope'],'event':event,'controlRegions':regions,'body':body}
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');wait(lambda:(projection() or {}).get('mode')=='closed')
    check('CurrentOutputEscapeClosesWithoutWindowMutation',len(journal())==before_journal and current_window()['geometry']==[float(before_geometry['at'][0]),float(before_geometry['at'][1]),float(before_geometry['size'][0]),float(before_geometry['size'][1])])
    report['nativeShortcutCurrentOutputObserved']=True
'''
source=source.replace(needle,needle+'\n'+addition)
sys.argv=[str(p),'--shortcut-output']
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
