"""Original ux-016 on the existing protected native host and physical input.

Keep the owning ABI/private bus/normal helper cleanup/six-second observations.
Only fixture overlap placement and the original FOCUS observation branch change.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
path=pathlib.Path(__file__).with_name('native-window-feedback.py');original=path.read_text()
start=original.index('   elif FOCUS:\n');end=original.index('   else:\n    # Current real taskbar primary action',start)
branch=r'''   elif FOCUS:
    import re,gi
    gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    labels={row['label']:row['incarnation'] for row in client.snapshot('510')['windows']}
    primary=labels['ELM-AUTHORITY-FIXTURE'];peer=labels['ELM-ACTIVATION-PEER']
    def events():
     path=control.with_suffix('.events.jsonl')
     return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    def bodies():return [json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=popup ')]
    def body():
     current=projection();return next((row for row in reversed(bodies()) if current and row['publication']==current['publication']),None)
    def popup_pointer(button,secondary=False):
     matches=re.findall(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',text());assert matches
     dx,dy,_,_=map(int,matches[-1]);x,y=round(dx+button['x']+button['width']/2),round(dy+button['y']+button['height']/2)
     check('PopupPointerWithinOriginalViewport',0<=x<800 and 0<=y<600,button=button,point=[x,y])
     b=273 if secondary else 272
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton {b} 1\nsleep 50\nbutton {b} 0\nsleep 100\n')
    def open_menu():
     wait(lambda:(projection() or {}).get('mode')=='closed')
     click(wait(lambda:group('Choose a window from')))
     wait(lambda:(projection() or {}).get('mode')=='picker')
     selection=wait(lambda:next((b for b in (body() or {}).get('buttons',[]) if b['id'].endswith(':'+primary) and 'ELM-AUTHORITY-FIXTURE' in b['accessibleName'] and not b['disabled']),None))
     popup_pointer(selection,True)
     return wait(lambda:body() if (projection() or {}).get('mode')=='menu' and body() else None)
    def action(label):
     selected=wait(lambda:next((b for b in (body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
     before=len(journal());popup_pointer(selected)
     wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and (projection() or {}).get('mode')=='closed')
     check('ExactNative'+label+'Once',len(journal())==before+1,intent=journal()[-1])
    def root():return next(row for row in facts()['facts']['windows'] if row['incarnation']==primary)
    def physical_hit(name):
     image=OUTPUT/(name+'.png');helper(['/usr/bin/grim',str(image)])
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();x,y=250,260;offset=y*pix.get_rowstride()+x*pix.get_n_channels();red,green,blue=pixels[offset:offset+3]
     visible='ELM-AUTHORITY-FIXTURE' if red>180 and green<80 and blue<80 else 'ELM-ACTIVATION-PEER' if green>180 and red<80 and blue<80 else None
     check(name+'VisibleNativeFamilyPixel',visible is not None,point=[x,y],rgb=[red,green,blue],image=str(image),sha256=sha(image))
     before=len([e for e in events() if e['kind']=='pressed'])
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     seen=wait(lambda: [e for e in events() if e['kind']=='pressed'] if len([e for e in events() if e['kind']=='pressed'])==before+1 else None)
     check(name+'VisiblePixelMatchesRealGTKHit',seen[-1]['window']==visible and facts()['facts']['focused']==labels[visible],pressed=seen[-1],visible=visible)
     report.setdefault('pinMaxCaptures',[]).append({'path':str(image),'sha256':sha(image),'point':[x,y],'rgb':[red,green,blue],'visible':visible})
    before=len(journal());menu=open_menu();check('ContextOpenNeverActivatesFamily',len(journal())==before)
    action('Maximize');wait(lambda:root()['fullscreenMode']==1)
    maximum=root()['geometry'];check('OriginalFixtureMaximizedOverFloat',any(row['incarnation']==peer and row['workspace']=='1' for row in facts()['facts']['windows']),maximum=maximum)
    physical_hit('UnpinnedMax')
    menu=open_menu();check('DisplayedUnpinnedMaxIsObserved',any('Maximized' in b['label'] for b in menu['buttons']) and any(b['accessibleName']=='Always on top' and not b['disabled'] for b in menu['buttons']) and not root()['pinned'],body=menu,native=root())
    action('Always on top');wait(lambda:root()['pinned'])
    check('PinPreservesNativeMaxAndGeometry',root()['fullscreenMode']==1 and root()['geometry']==maximum,native=root())
    physical_hit('PinnedMax')
    menu=open_menu();check('DisplayedPinAndMaxAgreeWithNative',any('Always on top' in b['label'] and 'Maximized' in b['label'] for b in menu['buttons']) and any(b['accessibleName']=='Unpin window' and not b['disabled'] for b in menu['buttons']),body=menu,native=root())
    action('Unpin window');wait(lambda:not root()['pinned'])
    check('UnpinPreservesNativeMaxAndGeometry',root()['fullscreenMode']==1 and root()['geometry']==maximum,native=root())
    physical_hit('UnpinnedAgain')
    menu=open_menu();check('DisplayedUnpinKeepsMax',any('Maximized' in b['label'] for b in menu['buttons']) and any(b['accessibleName']=='Always on top' and not b['disabled'] for b in menu['buttons']) and not any(b['accessibleName']=='Unpin window' for b in menu['buttons']),body=menu,native=root())
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
    helper([str(keyboard)],'key 1 1\nsleep 50\nkey 1 0\nsleep 100\nsync\n');wait(lambda:(projection() or {}).get('mode')=='closed')
    check('PinUnpinUsesExactlyThreeSharedWindowIntents',[entry['intent']['operation'] for entry in journal()[before:]]==['maximize','pin','unpin'],journal=journal())
    report['nativePinMaxObserved']=True
'''
adapted=original[:start]+branch+original[end:]
adapted=adapted.replace("'native-taskbar-focus-' if FOCUS", "'native-pin-max-' if FOCUS")
needle="   if DENSEPICKER:\n    fixture_control('many-documents')"
assert adapted.count(needle)==1
fixture=r'''   peer_row=next(row for row in s.data('clients') if row['title']=='ELM-ACTIVATION-PEER')
   peer_selector='address:'+peer_row['address']
   if not peer_row['floating']:check('OverlapPeerFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
   check('OverlapPeerSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+peer_selector+"'})").strip()=='ok')
   check('OverlapPeerPosition',s.ctl('dispatch',"hl.dsp.window.move({x=100,y=140,window='"+peer_selector+"'})").strip()=='ok')
'''
adapted=adapted.replace(needle,fixture+needle)
needle='try:\n with host.PrivateHyprSession';assert adapted.count(needle)==1
packet={'originalPath':str(path),'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'change':'Actual overlapping float fixture plus original FOCUS branch replaced with physical maximize/pin/unpin and pixel-to-GTK-hit oracle. Owning tuple, native authority, original timing, private sessions and cleanup unchanged.'}
adapted=adapted.replace(needle,"report.update(requirements=['ELM-UX-016'],scenarios=['ux-016'],scope='Original native pin/unpin of maximized family overlapping float; correlated UI/native states, stable MAX geometry and actual visible pixel/GTK pointer hit; independent acceptance separate',nativePinMaxRunner="+repr(packet)+")\n"+needle)
sys.argv=[str(path),'--taskbar-focus'];exec(compile(adapted,str(path),'exec'),globals())
