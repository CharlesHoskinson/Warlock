"""Original pin/MAX regression followed by REN-017 fullscreen/pin/menu matrix."""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-pin-max.py');source=p.read_text()
needle="    report['nativePinMaxObserved']=True"
assert source.count(needle)==1
addition=r'''
    def target_menu(identity):
     wait(lambda:(projection() or {}).get('mode')=='closed')
     click(wait(lambda:group('Choose a window from')))
     wait(lambda:(projection() or {}).get('mode')=='picker')
     choice=wait(lambda:next((b for b in (body() or {}).get('buttons',[]) if b['id'].endswith(':'+identity) and not b['disabled']),None))
     before=len(journal());popup_pointer(choice,True)
     menu=wait(lambda:body() if (projection() or {}).get('mode')=='menu' and body() else None)
     check('FullscreenContextReadHasNoWindowEffect'+identity,len(journal())==before)
     return menu
    def window(identity):return next(row for row in facts()['facts']['windows'] if row['incarnation']==identity)
    def pixel_hit(name,point,expected):
     x,y=point;image=OUTPUT/(name+'.png');helper(['/usr/bin/grim',str(image)])
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));offset=y*pix.get_rowstride()+x*pix.get_n_channels();rgb=list(pix.get_pixels()[offset:offset+3])
     color=rgb[0]>180 and rgb[1]<80 and rgb[2]<80 if expected==primary else rgb[1]>180 and rgb[0]<80 and rgb[2]<80
     check(name+'NativePixels',color,rgb=rgb,point=point,image=str(image),sha256=sha(image))
     before=len([e for e in events() if e['kind']=='pressed']);released_before=len([e for e in events() if e['kind']=='released'])
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     pressed=wait(lambda:[e for e in events() if e['kind']=='pressed'] if len([e for e in events() if e['kind']=='pressed'])==before+1 else None)
     released=wait(lambda:[e for e in events() if e['kind']=='released'] if len([e for e in events() if e['kind']=='released'])==released_before+1 else None)
     wait(lambda:facts()['facts']['focused']==expected)
     check(name+'ActualGTKPressReleaseAndFocus',pressed[-1]['window']==released[-1]['window']==next(k for k,v in labels.items() if v==expected),pressed=pressed[-1],released=released[-1],native=facts())
     report.setdefault('fullscreenPixelHits',[]).append({'name':name,'point':point,'image':str(image),'sha256':sha(image),'rgb':rgb,'pressed':pressed[-1],'released':released[-1],'native':facts()})
    open_menu();action('Restore');wait(lambda:root()['fullscreenMode']==0)
    original_geometry=root()['geometry'];peer_geometry=window(peer)['geometry']
    target_menu(peer);action('Always on top');wait(lambda:window(peer)['pinned'])
    primary_row=next(row for row in s.data('clients') if row['title']=='ELM-AUTHORITY-FIXTURE');selector='address:'+primary_row['address']
    command="hl.dsp.window.fullscreen({mode='fullscreen',action='set',layout_aware=false,window='"+selector+"'})"
    check('PrivateFixtureEntersTrueFullscreen',s.ctl('dispatch',command).strip()=='ok')
    wait(lambda:root()['fullscreenMode']==2)
    fullscreen_geometry=root()['geometry']
    check('TrueFullscreenIsNotFloatingMAX',root()['fullscreenMode']==2 and root()['geometry']!=maximum and window(peer)['pinned'] and window(peer)['fullscreenMode']==0,owner=root(),pinned=window(peer))
    pixel_hit('PinnedAboveTrueFullscreen',[250,260],peer)
    check('PinnedFocusRetainsTrueFullscreen',root()['fullscreenMode']==2 and root()['geometry']==fullscreen_geometry and window(peer)['geometry']==peer_geometry,native=facts())
    pixel_hit('TrueFullscreenOutsidePinned',[650,350],primary)
    menu=target_menu(primary)
    check('TrueFullscreenMenuPreservesNativePlacement',root()['fullscreenMode']==2 and root()['geometry']==fullscreen_geometry and window(peer)['pinned'],native=facts())
    check('TrueFullscreenCannotUseMAXOrPinMenu',all(b['disabled'] for b in menu['buttons'] if b['accessibleName'] in ['Maximize','Always on top']),menu=menu)
    exit_item=next((b for b in menu['buttons'] if b['accessibleName']=='Exit fullscreen'),None)
    check('NegotiatedTrueFullscreenExitEnabled',exit_item is not None and not exit_item['disabled'],menu=menu)
    before=len(journal());popup_pointer(exit_item)
    wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and (projection() or {}).get('mode')=='closed' and root()['fullscreenMode']==0)
    check('ExitFullscreenExactlyOneTypedNativeEffect',journal()[-1]['intent']['operation']=='exit-fullscreen' and len(journal())==before+1,receipt=journal()[-1])
    check('FullscreenExitKeepsPinAndRestoresOrdinaryGeometry',root()['geometry']==original_geometry and window(peer)['pinned'] and window(peer)['geometry']==peer_geometry,owner=root(),pinned=window(peer))
    pixel_hit('PinnedAfterFullscreenExit',[250,260],peer)
    menu=target_menu(peer)
    check('OrdinaryPinnedTargetHasNoFullscreenExit',not any(b['accessibleName']=='Exit fullscreen' for b in menu['buttons']),menu=menu)
    action('Always on top');wait(lambda:not window(peer)['pinned'])
    check('FullscreenExitLeavesOriginalPinMAXRegressionIntact',root()['fullscreenMode']==0 and root()['geometry']==original_geometry and window(peer)['geometry']==peer_geometry)
    report['nativeFullscreenPinMenuObserved']=True
'''
source=source.replace(needle,needle+addition)
source=source.replace("'native-pin-max-' if FOCUS","'native-fullscreen-pin-' if FOCUS")
source=source.replace("requirements=['ELM-UX-016'],scenarios=['ux-016']","requirements=['ELM-REN-017'],scenarios=['ren-017']")
source=source.replace("scope='Original native pin/unpin of maximized family overlapping float; correlated UI/native states, stable MAX geometry and actual visible pixel/GTK pointer hit; independent acceptance separate'","scope='Original pin/MAX journey retained, then actual true-fullscreen and pinned pixels/hit/focus, read-only context menu and one negotiated fullscreen-exit effect; independent acceptance separate'")
exec(compile(source,str(p),'exec'),globals())
