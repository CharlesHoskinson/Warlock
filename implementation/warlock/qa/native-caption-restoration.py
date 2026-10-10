"""Actual GTK caption MAX/snap fraction and rollback, retaining lifecycle checks."""
import pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-gesture-end.py');source=p.read_text()
# Select the existing negotiated observer, keeping real native effects/admission.
old="source=p.read_text()"
extra="source=source.replace('from effect_endpoint import Endpoint;from endpoint import start_time','from geometry_endpoint import GeometryEndpoint as Endpoint;from endpoint import start_time')\nexec(compile(source,"
source=source.replace(old,"source=p.read_text().replace("+repr('exec(compile(source,')+','+repr(extra)+')')
needle='    # Retire the actual captured window while held'
assert source.count(needle)==1
addition=r'''    client.geometry_attach('475')
    geometry_number=12000
    def geometry_operation(operation,placement=None):
     global geometry_number
     geometry_number+=1;n=str(geometry_number);f=client.geometry_facts('476')
     intent={'request':n,'generation':n,'incarnation':target,'operation':operation,'context':client.geometry_context(f)}
     if placement is not None:intent['placement']=placement
     result=client.geometry_effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result})
     check('CaptionRestorationFixture'+operation,result['status']=='Committed',result=result)
     return result
    def snap():
     f=client.geometry_facts('476');w=next(w for w in f['facts']['windows'] if w['incarnation']==target);x,y,width,height=w['workArea']
     return geometry_operation('snap',{'region':'left-half','geometry':[x,y,width/2,height],'monitor':w['monitor'],'outputOwnershipGeneration':w['outputOwnershipGeneration'],'workAreaRevision':w['workAreaRevision'],'workspaceGeneration':w['workspaceGeneration']})
    def capture_placement(label,w):
     image=OUTPUT/(label+'.png');helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
     def red(x,y):
      i=round(y)*stride+round(x)*channels;r,g,b=data[i:i+3];return r>220 and g<50 and b<50
     x,y=w['at'];width,height=w['size'];inside=red(x+30,y+80);outside=not red(x-5,y+80) if x>=5 else True
     check(label+'ActualPixelsMatchRestoredOwner',inside and outside,window=w,insideRed=inside,outsideNotRed=outside)
     report.setdefault('restorationPixels',[]).append({'label':label,'path':str(image),'sha256':sha(image),'geometry':box(w)})
    report['captionRestorations']=[]
    for placement in ['maximize','snap']:
     ordinary=root_window()
     geometry_operation('maximize') if placement=='maximize' else snap()
     placed=wait(lambda:root_window() if box(root_window())!=box(ordinary) else None)
     mode('move');before=ownership();x=round(placed['at'][0]+placed['size'][0]*0.25);y=round(placed['at'][1]+24)
     pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n);active=wait(lambda:owned('move'))
     pointer('button 272 0\nsleep 100');ended=wait(lambda:owned('idle'))
     check(placement+'CaptionClickWithoutMovementKeepsPlacement',box(root_window())==box(placed) and root_window()['fullscreen']==placed['fullscreen'] and int(ended['serial'])==int(active['serial'])+1 and draft()==saved and peer_unchanged(),before=placed,after=root_window())
     for fraction in [0.25,0.75]:
      mode('move');before=ownership();x=round(placed['at'][0]+placed['size'][0]*fraction);y=round(placed['at'][1]+24)
      pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n)
      active=wait(lambda:owned('move'));check(placement+'CaptionPressWithoutMotionKeepsPlacement',box(root_window())==box(placed) and root_window()['fullscreen']==placed['fullscreen'],before=placed,after=root_window())
      pointer('move 400 300\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':400,'y':300})
      moved=wait(lambda:root_window() if box(root_window())!=box(placed) else None)
      horizontal=(x-placed['at'][0])/placed['size'][0];expected=[400-horizontal*ordinary['size'][0],300-(y-placed['at'][1]),*ordinary['size']]
      check(placement+'CaptionPreservesFraction'+str(fraction),all(abs(a-b)<=1 for a,b in zip(box(moved),expected)) and moved['fullscreen']==0,before=placed,ordinary=ordinary,press=[x,y],after=moved,expected=expected)
      if fraction==0.25:capture_placement(placement+'-fraction-quarter',moved)
      physical('key 1 1\nsleep 50');ended=wait(lambda:owned('idle'));physical('key 1 0\nsleep 50')
      after=root_window();check(placement+'EscapeRestoresOriginalPlacement'+str(fraction),box(after)==box(placed) and after['fullscreen']==placed['fullscreen'] and after['fullscreenClient']==placed['fullscreenClient'] and after['workspace']==placed['workspace'] and after['monitor']==placed['monitor'],before=placed,after=after)
      if fraction==0.25:capture_placement(placement+'-cancel-quarter',after)
      check(placement+'CancellationKeepsOwnerDraftAndPeer'+str(fraction),int(active['serial'])==int(before['serial'])+1 and int(ended['serial'])==int(active['serial'])+1 and draft()==saved and peer_unchanged())
      pointer('button 272 0\nsleep 100');check(placement+'CancelledReleaseDoesNotEndAgain'+str(fraction),ownership()==ended)
      report['captionRestorations'].append({'placement':placement,'fraction':fraction,'ordinary':ordinary,'before':placed,'press':[x,y],'moved':moved,'after':after,'active':active,'end':ended})
     if placement=='maximize':
      geometry_operation('restore-geometry')
      check('CancelledMaxCanRestoreExactOriginalOrdinaryBox',box(root_window())==box(ordinary) and root_window()['fullscreen']==0 and draft()==saved and peer_unchanged(),before=ordinary,after=root_window())
      geometry_operation('maximize');max_release=root_window();mode('move');x=round(max_release['at'][0]+max_release['size'][0]*0.25);y=round(max_release['at'][1]+24)
      pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n);active=wait(lambda:owned('move'))
      pointer('move 400 300\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':400,'y':300});restored=wait(lambda:root_window() if root_window()['fullscreen']==0 else None)
      pointer('button 272 0\nsleep 100');ended=wait(lambda:owned('idle'))
      check('MaxRestoredCaptionReleaseCommitsOnce',box(root_window())==box(restored) and int(ended['serial'])==int(active['serial'])+1 and draft()==saved and peer_unchanged())
      geometry_operation('maximize');geometry_operation('restore-geometry')
      check('ReleasedMaxRecapturesNewOrdinaryPlacement',box(root_window())==box(restored) and root_window()['fullscreen']==0 and draft()==saved and peer_unchanged(),before=restored,after=root_window())

     else:
      # Commit actual restored caption motion; do not arrange the resulting box.
      mode('move');x=round(placed['at'][0]+placed['size'][0]*0.25);y=round(placed['at'][1]+24)
      pointer(f'move {x} {y}\nsleep 100');n=len(events());pointer('button 272 1\nsleep 50');wait_event('native-request',n);active=wait(lambda:owned('move'))
      pointer('move 400 300\nsleep 100');wait(lambda:s.data('cursorpos')=={'x':400,'y':300});moved=wait(lambda:root_window() if box(root_window())!=box(placed) else None)
      pointer('button 272 0\nsleep 100');ended=wait(lambda:owned('idle'))
      check('SnapRestoredCaptionReleaseCommitsOnce',box(root_window())==box(moved) and root_window()['fullscreen']==0 and int(ended['serial'])==int(active['serial'])+1 and draft()==saved and peer_unchanged())
    report['nativeCaptionRestorationObserved']=True
'''
source=source.replace(needle,addition+needle).replace("'native-gesture-end-' if DRAG","'native-caption-restoration-' if DRAG")
exec(compile(source,str(p),'exec'),globals())
