"""Original REN-015 two-MAX input-hole journey on the protected current tuple.

This wrapper retains the original private host, six-second waits and cleanup.
The original GTK fixture already supplies its real Wayland input-hole command.
Scene dependency revision is recorded as metadata, never certified as render/
hit committed-scene agreement. That separate original obligation remains open.
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
     p=control.with_suffix('.events.jsonl')
     return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
    def bodies():return [json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=popup ')]
    def body():
     current=projection();return next((row for row in reversed(bodies()) if current and row['publication']==current['publication']),None)
    def popup_pointer(button,secondary=False):
     matches=re.findall(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',text());assert matches
     dx,dy,_,_=map(int,matches[-1]);x,y=round(dx+button['x']+button['width']/2),round(dy+button['y']+button['height']/2)
     check('PopupPointerWithinOriginalViewport',0<=x<800 and 0<=y<600,point=[x,y])
     b=273 if secondary else 272
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton {b} 1\nsleep 50\nbutton {b} 0\nsleep 100\n')
    def select(id,secondary):
     wait(lambda:(projection() or {}).get('mode')=='closed')
     click(wait(lambda:group('Choose a window from')))
     wait(lambda:(projection() or {}).get('mode')=='picker')
     chosen=wait(lambda:next((b for b in (body() or {}).get('buttons',[]) if b['id'].endswith(':'+id) and not b['disabled']),None))
     before=len(journal());popup_pointer(chosen,secondary)
     if secondary:
      menu=wait(lambda:body() if (projection() or {}).get('mode')=='menu' and body() else None)
      check('ContextReadNeverActivates'+id,len(journal())==before)
      return menu
     wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and (projection() or {}).get('mode')=='closed')
    def action(id,label):
     menu=select(id,True)
     selected=wait(lambda:next((b for b in (body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
     before=len(journal());popup_pointer(selected)
     wait(lambda:len(journal())==before+1 and transaction_state()=='Committed' and (projection() or {}).get('mode')=='closed')
     check('ExactNative'+label+'Once'+id,len(journal())==before+1,intent=journal()[-1])
    def root(id):return next(row for row in facts()['facts']['windows'] if row['incarnation']==id)
    initial={id:root(id)['geometry'] for id in [primary,peer]}
    action(primary,'Maximize');wait(lambda:root(primary)['fullscreenMode']==1)
    first=root(primary)['geometry']
    action(peer,'Maximize');wait(lambda:root(peer)['fullscreenMode']==1 and root(primary)['fullscreenMode']==1)
    second=root(peer)['geometry']
    check('SecondMaxPreservesFirstNativePlacement',root(primary)['geometry']==first,first=root(primary),second=root(peer))
    select(peer,False);wait(lambda:facts()['facts']['focused']==peer)
    check('ActualTwoOverlappingMaxSurfaces',root(primary)['fullscreenMode']==root(peer)['fullscreenMode']==1 and first==second,first=root(primary),second=root(peer))
    fixture_control('input-hole')
    def hit(name,local,expected):
     x,y=round(second[0]+local[0]),round(second[1]+local[1])
     # Original pointer cadence also allows the unchanged GTK control poll and
     # real wl_surface input-region commit; no deadline extension or fake hit.
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\n')
     before_facts=facts();image=OUTPUT/(name+'.png');helper(['/usr/bin/grim',str(image)])
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));offset=y*pix.get_rowstride()+x*pix.get_n_channels();red,green,blue=pix.get_pixels()[offset:offset+3]
     check(name+'UpperMAXPixelsRetained',green>180 and red<80 and blue<80,point=[x,y],rgb=[red,green,blue],image=str(image),sha256=sha(image))
     before=len([e for e in events() if e['kind']=='pressed'])
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     pressed=wait(lambda:[e for e in events() if e['kind']=='pressed'] if len([e for e in events() if e['kind']=='pressed'])==before+1 else None)
     wait(lambda:facts()['facts']['focused']==labels[expected])
     check(name+'RealGTKRecipientAndFocus',pressed[-1]['window']==expected,pressed=pressed[-1],focused=facts()['facts']['focused'])
     check(name+'PreservesBothMaxGeometry',root(primary)['fullscreenMode']==root(peer)['fullscreenMode']==1 and root(primary)['geometry']==first and root(peer)['geometry']==second)
     report.setdefault('maxInputCaptures',[]).append({'path':str(image),'sha256':sha(image),'point':[x,y],'localPoint':local,'rgb':[red,green,blue],'painted':peer,'recipient':labels[expected],'beforeDependencyFacts':before_facts,'afterDependencyFacts':facts(),'committedSceneAgreementAccepted':False})
    hit('IncludedPoint',[200,180],'ELM-ACTIVATION-PEER')
    hit('ExcludedPoint',[100,90],'ELM-AUTHORITY-FIXTURE')
    action(peer,'Restore');wait(lambda:root(peer)['fullscreenMode']==0)
    check('RestorePeerRetainsOtherMAX',root(primary)['fullscreenMode']==1 and root(primary)['geometry']==first and root(peer)['geometry']==initial[peer],primary=root(primary),peer=root(peer))
    action(primary,'Restore');wait(lambda:root(primary)['fullscreenMode']==0)
    check('BothOriginalReturnPlacementsRecovered',root(primary)['geometry']==initial[primary] and root(peer)['geometry']==initial[peer],initial=initial,primary=root(primary),peer=root(peer))
    report['nativeTwoMaxInputHoleObserved']=True
    report['committedSceneAgreementAccepted']=False
'''
adapted=original[:start]+branch+original[end:]
adapted=adapted.replace("'native-taskbar-focus-' if FOCUS", "'native-max-input-region-' if FOCUS")
needle="   if DENSEPICKER:\n    fixture_control('many-documents')";assert adapted.count(needle)==1
fixture=r'''   peer_row=next(row for row in s.data('clients') if row['title']=='ELM-ACTIVATION-PEER')
   peer_selector='address:'+peer_row['address']
   if not peer_row['floating']:check('SecondRootFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
'''
adapted=adapted.replace(needle,fixture+needle)
needle='try:\n with host.PrivateHyprSession';assert adapted.count(needle)==1
packet={'originalPath':str(path),'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'change':'Float original peer; replace FOCUS branch with actual two-MAX overlap, original real GTK input region, physical included/excluded clicks and return placement. No scene-revision acceptance inferred.'}
adapted=adapted.replace(needle,"report.update(requirements=['ELM-REN-015'],scenarios=['max-input-region'],scope='Original two floating MAX surfaces, upper native pixels, real GTK lower input-hole recipient and actual focus. Committed render/hit scene agreement and independent acceptance remain open.',nativeMaxInputRunner="+repr(packet)+")\n"+needle)
sys.argv=[str(path),'--taskbar-focus'];exec(compile(adapted,str(path),'exec'),globals())
