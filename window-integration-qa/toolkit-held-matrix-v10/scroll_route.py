"""Reveal the same source card through genuine bounded wheel input only."""
import copy
import math
import helper_observer
from observations import exact,released,valid_identity

MAX_DETENTS=32

def rectangle(row):
    values=[row[k] for k in ('x','y','width','height')]
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in values) or values[2]<=0 or values[3]<=0:
        raise ValueError('Actual finite positive popup rectangle required')
    return values

def intersection(*rectangles):
    left=max(r[0] for r in rectangles);top=max(r[1] for r in rectangles)
    right=min(r[0]+r[2] for r in rectangles);bottom=min(r[1]+r[3] for r in rectangles)
    if right<=left or bottom<=top:raise ValueError('Actual positive visible popup intersection required')
    return [left,top,right-left,bottom-top]

def selection(widget,native_layer,target):
    if widget['popupOpen'] is not True or widget['menuMode'] is not False or widget['keyboardMode'] is not False:
        raise ValueError('Exact genuine hover preview remains open required')
    geometry=widget['popupGeometry'];viewport=widget['popupViewportBounds']
    if geometry['coordinateSpace']!='layer-window' or viewport['coordinateSpace']!='layer-window' or geometry['maskMode']!='card' or geometry['open'] is not True or geometry['visible'] is not True or viewport['clip'] is not True:
        raise ValueError('Actual hover mask and clipped viewport coordinate space required')
    layer_box=native_layer['box']
    if len(layer_box)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in layer_box) or layer_box[2]<=0 or layer_box[3]<=0:
        raise ValueError('Actual exact positive native layer box required')
    allocated=rectangle(geometry['layer'])
    if allocated!=[0,0,layer_box[2],layer_box[3]]:raise ValueError('Actual QML/native layer allocation differs')
    visible=intersection(allocated,rectangle(geometry['card']),rectangle(geometry['content']),rectangle(viewport))
    items=[row for row in widget['previewItems'] if exact(row,target)]
    if len(items)!=1:raise ValueError('One actual preview of exact source address/stableId/PID required')
    item=rectangle(items[0]);x,y,w,h=visible
    fully=item[0]>=x and item[1]>=y and item[0]+item[2]<=x+w and item[1]+item[3]<=y+h
    if item[2]>w or item[3]>h:raise ValueError('Exact source card cannot fit actual clipped viewport')
    direction=-1 if item[1]<y else 1
    point=[layer_box[0]+item[0]+item[2]/2,layer_box[1]+item[1]+item[3]/2]
    viewport_point=[layer_box[0]+x+w/2,layer_box[1]+y+h/2]
    scroll=viewport['contentY'];height=viewport['contentHeight'];count=widget['wheelEvents']
    if type(count) is not int or count<0 or type(scroll) not in (int,float) or not math.isfinite(scroll) or type(height) not in (int,float) or not math.isfinite(height) or not 0<=scroll<=max(0,height-viewport['height']):
        raise ValueError('Exact bounded actual wheel counter and scroll state required')
    return dict(item=copy.deepcopy(items[0]),visible=visible,fullyVisible=fully,direction=direction,point=point,viewportPoint=viewport_point,scroll=scroll,maxScroll=max(0,height-viewport['height']),wheelEvents=count)

def binding(widget,native_layer,target,shell_identity,native):
    if not helper_observer.still_live(shell_identity):raise RuntimeError('Exact taskbar shell lifetime changed')
    released(native)
    identities=[{k:row[k] for k in ('address','stableId','pid')} for row in widget['previewItems']]
    if not identities or any(not valid_identity(row) for row in identities) or len({row['address'] for row in identities})!=len(identities) or not any(exact(row,target) for row in identities):
        raise ValueError('Complete ordered exact taskbar source identity list required')
    for identity in identities:
        windows=[row for row in native['windows'] if exact(row,identity) and row['mapped'] is True]
        if len(windows)!=1:raise ValueError('Exact popup member actual native lifetime changed')
    if native_layer['pid']!=shell_identity['pid'] or native_layer['namespace']!='hoskinson-taskbar-popup' or native_layer['mapped'] is not True or native_layer['visible'] is not True:
        raise ValueError('Exact mapped current taskbar popup lifetime required')
    epoch=widget['diagnosticPopupEpoch']
    if type(epoch) is not int or epoch<1 or type(widget['popupIndex']) is not int or widget['popupIndex']<0 or not isinstance(widget['popupKey'],str) or not widget['popupKey']:
        raise ValueError('Exact actual popup key/index/epoch required')
    return dict(shell=copy.deepcopy(shell_identity),layer=dict(address=native_layer['address'],pid=native_layer['pid'],namespace=native_layer['namespace']),key=widget['popupKey'],index=widget['popupIndex'],epoch=epoch,identities=identities)

def source_binding(route,target):
    if route.pointer.down or route.keyboard.down or not exact(route.window('source'),target):raise RuntimeError('Exact released source lifetime required before taskbar input')

def observe(frontend,route,target,shell_identity,expected,evidence):
    import json
    from frontend_route import layer
    source_binding(route,target)
    widget=json.loads(frontend.ipc('hoskinson.windows','state'));native=route.native()
    native_layer=layer(native,frontend.shell.pid,'hoskinson-taskbar-popup')
    actual=binding(widget,native_layer,target,shell_identity,native)
    evidence.emit('scroll-state',dict(widgetState=widget,native=native,binding=actual))
    if actual!=expected:raise RuntimeError('Actual popup/source/layer/key/index/epoch changed or reset')
    return widget,native,native_layer,selection(widget,native_layer,target)

def strict_owner(native,point,pid):
    owner=native['pointerLayerOwner']
    return all(abs(a-b)<=.5 for a,b in zip(native['cursor'],point)) and owner is not None and owner['pid']==pid and owner['namespace']=='hoskinson-taskbar-popup' and owner['mapped']

def stable_key(state):
    widget,native,layer_row,plan=state
    return dict(item=plan['item'],layer=layer_row,card=widget['popupGeometry']['card'],content=widget['popupGeometry']['content'],viewport=widget['popupViewportBounds'],wheelEvents=plan['wheelEvents'])

def reveal(frontend,route,target,shell_identity,widget,native,native_layer,evidence):
    source_binding(route,target)
    expected=binding(widget,native_layer,target,shell_identity,native);current=(widget,native,native_layer,selection(widget,native_layer,target));detents=0
    while True:
        prior=None;baseline=current[3]
        def stable():
            nonlocal prior
            value=observe(frontend,route,target,shell_identity,expected,evidence);key=stable_key(value)
            if value[3]['wheelEvents']!=baseline['wheelEvents'] or value[3]['scroll']!=baseline['scroll']:raise RuntimeError('Uncommanded actual popup wheel/scroll before stable selection')
            settled=prior==key;prior=key
            return value if settled else None
        current=route.wait(stable,'Two consecutive exact actual preview allocations')
        plan=current[3]
        if plan['fullyVisible']:return current,expected,detents
        if detents>=MAX_DETENTS:raise RuntimeError('Bounded genuine wheel detents did not reveal exact source')
        point=plan['viewportPoint']
        evidence.emit('scroll-viewport-proposed',dict(point=point,selection=plan,binding=expected,detents=detents,inputTraceIndex=len(route.pointer.trace)))
        route.pointer.absolute(point,route.extents)
        def arrived():
            value=observe(frontend,route,target,shell_identity,expected,evidence)
            if value[3]['wheelEvents']!=plan['wheelEvents'] or value[3]['scroll']!=plan['scroll']:raise RuntimeError('Uncommanded actual popup scroll/counter changed')
            accepted=strict_owner(value[1],point,frontend.shell.pid)
            evidence.emit('scroll-viewport-arrival',dict(point=point,native=value[1],widgetState=value[0],originalOwnerPredicate=accepted))
            return value if accepted else None
        current=route.wait(arrived,'Actual pointer owns exact clipped popup viewport before wheel')
        before=current[3];direction=before['direction']
        if (direction>0 and before['scroll']>=before['maxScroll']) or (direction<0 and before['scroll']<=0):raise RuntimeError('Exact hidden source at actual scroll boundary')
        source_binding(route,target)
        evidence.emit('wheel-proposed',dict(direction=direction,detent=detents+1,selection=before,binding=expected,native=current[1],widgetState=current[0],inputTraceIndex=len(route.pointer.trace)))
        route.pointer.wheel(direction);detents+=1
        def receipt():
            value=observe(frontend,route,target,shell_identity,expected,evidence);after=value[3]
            if not strict_owner(value[1],point,frontend.shell.pid):raise RuntimeError('Actual popup pointer input owner changed during wheel')
            if after['wheelEvents']==before['wheelEvents'] and after['scroll']==before['scroll']:return None
            if after['wheelEvents']!=before['wheelEvents']+1 or (after['scroll']-before['scroll'])*direction<=0:
                raise RuntimeError('Exact actual wheel receipt lacks single counter and directional progress')
            evidence.emit('wheel-receipt',dict(direction=direction,detent=detents,before=before,after=after,binding=expected,native=value[1],widgetState=value[0],inputTrace=route.pointer.trace[-2:]))
            return value
        current=route.wait(receipt,'Actual widget wheel counter and directional contentY receipt')

def validate_card(frontend,route,target,shell_identity,expected,evidence,point,allocation):
    value=observe(frontend,route,target,shell_identity,expected,evidence)
    if not value[3]['fullyVisible'] or value[3]['point']!=point or stable_key(value)!=allocation:raise RuntimeError('Actual same-source visible preview allocation/counter changed before input')
    return value
