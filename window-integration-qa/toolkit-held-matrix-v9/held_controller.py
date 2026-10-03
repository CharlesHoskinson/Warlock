"""Serial actual held cases; all feature decisions use queried native/public state.

The route owns isolation, real clients and exact product frontend integration.
This module neither launches clients nor fabricates native outcomes.
"""
import copy
import math
import json
import os
import time
from observations import captured,exact,group_snapshot,positive_group_drop,released,retired
from public_toolkit import callback_count,paired_button,rectangle

FIELDS=('address','stableId','pid','at','size','pinned')

def geometry(row):return {name:copy.deepcopy(row[name]) for name in FIELDS}

def allocated_point(native,target,name):
    matches=[row for row in native['decorationAllocations'] if exact(row['window'],target)
             and (row['name']=='Hyprbar' if name=='caption' else row['type']==0) and row['flags']&1]
    if len(matches)!=1:raise ValueError('One exact allocated input decoration required')
    box=rectangle(matches[0]['box'])
    return [box[0]+box[2]/2,box[1]+box[3]/2]

def retain_retirement(route,before,before_public,after,peer,target,ack):
    observation=dict(before=before,publicBefore=before_public,after=after,peer=peer,target=target,interruptionACK=ack,timeNs=time.monotonic_ns(),pointerKnownDown=sorted(route.pointer.down),keyboardKnownDown=sorted(route.keyboard.down),errors=[])
    try:
        route.guard();observation['publicAfter']=route.fixture.state();observation['nativeClientsAfter']=route.session.data('clients');route.guard()
    except Exception as error:observation['errors'].append(repr(error))
    path=route.folder/'retirement-observation.json';fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(observation,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    route.record('after actual nonrelease interruption',dict(native=after,public=observation.get('publicAfter'),nativeClients=observation.get('nativeClientsAfter'),timeNs=observation['timeNs'],interruptionACK=ack,observationPath=str(path),observationErrors=observation['errors']))
    if observation['errors']:raise RuntimeError('Guarded retirement evidence incomplete: '+str(observation['errors']))
    return observation

class HeldController:
    def __init__(self,route):self.route=route
    def sample(self,label):
        value=self.route.native();self.route.record(label,dict(native=value,public=self.route.fixture.state(),timeNs=time.monotonic_ns()));return value
    def point(self,point,label):
        self.route.pointer.absolute(point,self.route.extents)
        def arrived():
            native=self.route.native()
            return native if all(abs(a-b)<=.5 for a,b in zip(native['cursor'],point)) else None
        value=self.route.wait(arrived,'Actual float cursor before '+label,seconds=3)
        self.route.record(label,dict(requested=point,native=value,tolerance=.5));return value
    def callback(self,role):
        target=self.route.window(role);prior=None
        def paired():
            nonlocal prior
            native=self.route.native();rows=[w for w in native['windows'] if exact(w,target)]
            if len(rows)!=1:raise ValueError('Exact callback native lifetime disappeared')
            public=self.route.fixture.state();point=paired_button(public,role,rows[0],self.route.toolkit)
            key=(tuple(rows[0]['surfaceBox']),tuple(public['windows'][role]['buttonClient']))
            stable=prior==key;prior=key
            return (point,public,native) if stable else None
        point,public,native=self.route.wait(paired,'Two consecutive actual public/native callback allocations')
        before=callback_count(public,role,self.route.toolkit);arrival=self.point(point,'callback '+role)
        if not exact(arrival['pointerOwner'],target) or not exact(arrival['hitOwner'],target):raise ValueError('Actual callback cursor hit/input owner mismatch')
        self.route.pointer.button(272,True);self.route.pointer.button(272,False)
        result=self.route.wait(lambda:self.route.fixture.state() if callback_count(self.route.fixture.state(),role,self.route.toolkit)==before+1 else None,'Actual public callback increment after real release')
        self.route.gate('Actual public callback after release '+role,callback_count(result,role,self.route.toolkit)==before+1,before=before,after=callback_count(result,role,self.route.toolkit),point=point,nativeBefore=arrival,nativeAfter=self.route.native())
    def run(self,case):
        route=self.route;target=route.window('source');peer=route.window('peer');initial=self.sample('case baseline');released(initial)
        initial_geometry=geometry(target);peer_geometry=geometry(peer);baseline_counts={role:callback_count(route.fixture.state(),role,route.toolkit) for role in ('source','peer')}
        route.press_geometry=copy.deepcopy(initial_geometry)
        point=allocated_point(initial,target,'caption') if case['kind'] in ('move','pending') else route.resize_point(target,initial)
        arrival=self.point(point,'actual native press allocation')
        if not exact(arrival['hitOwner'],target):raise ValueError('Actual native allocated press hit wrong lifetime')
        if case['kind']=='resize':route.keyboard.key(125,True)
        route.pointer.button(case['button'],True)
        pressed=route.wait(lambda:route.native() if route.native()['signalDownButtonIds']==[case['button']] else None,'Actual raw press signal')
        route.record('actual press',dict(native=pressed,target=target,point=point))
        if case['kind']=='pending':
            if pressed['coreDragTarget'] is not None:raise ValueError('Pending caption unexpectedly established core target')
        else:
            self.point([point[0]+35,point[1]+25],'first real held motion')
            def established():
                value=route.native()
                if not exact(value['coreDragTarget'],target):return None
                captured(value,target,case['nativeMode'],case['button'])
                if value['coreDragTargetType']!=0:raise ValueError('Actual window controller target type required')
                return value
            held=route.wait(established,'Exact actual window gesture established')
            route.gate('Held real gesture captured exact lifetime mode type and raw signal',True,native=held)
            changed=geometry(route.window('source'))
            route.gate('Actual held gesture changed source geometry only',changed!=initial_geometry and geometry(route.window('peer'))==peer_geometry,press=initial_geometry,current=changed,peer=peer_geometry)
        ack=route.focus_peer(peer)
        focused=route.wait(lambda:route.native() if exact(route.native()['nativeFocus'],peer) else None,'Actual independent peer focus intervention')
        if case['kind']!='pending':captured(focused,target,case['nativeMode'],case['button'])
        elif focused['coreDragTarget'] is not None:raise ValueError('Pending target appeared during focus intervention')
        route.record('separate WM focus intervention',dict(commandACK=ack,native=focused,featureEvidence=exact(focused['nativeFocus'],peer)))
        if case['name']=='genuine-group-release-positive':
            self.point(allocated_point(route.native(),peer,'group'),'actual positive group drop region')
            captured(route.native(),target,case['nativeMode'],case['button'])
            route.pointer.button(case['button'],False)
            if case['kind']=='resize':route.keyboard.key(125,False)
            state=route.wait(lambda:route.native() if route.native()['coreDragTarget'] is None and not route.native()['signalDownButtonIds'] and not route.native()['heldButtons'] else None,'Actual positive release completion')
            released(state);positive_group_drop(state,target,peer)
            route.gate('Only genuine actual release inserts exact source into peer group',True,native=state)
            self.callback('source');return
        if case['kind']!='pending':
            # The same queried public peer drop region is used for all negative
            # cases. The held source can cover it until genuine cancellation.
            self.point(allocated_point(route.native(),peer,'group'),'actual negative group drop region')
            captured(route.native(),target,case['nativeMode'],case['button'])
        before=self.sample('before actual nonrelease interruption');before_public=copy.deepcopy(route.report['trace'][-1]['public']);current_geometry=geometry(route.window('source'))
        end=case.get('end') or ('escape' if case['name'].endswith('escape') else 'reload')
        if end=='escape':
            route.keyboard.key(1,True);route.keyboard.key(1,False)
            ack=dict(actualNativeEscape=True,commandACK=False)
        else:ack=route.interrupt(end,target,current_geometry)
        after=route.wait(lambda:route.native() if route.native()['coreDragTarget'] is None else None,'Actual nonrelease retirement')
        retain_retirement(route,before,before_public,after,peer,target,ack)
        retired(before,after,peer)
        if case['kind']=='resize':route.keyboard.key(125,False)
        if end=='close-reopen':
            replacement=route.reopen_source(target)
            if exact(replacement,target):raise ValueError('Public reopen reused exact old native lifetime')
            # A public dialog open is an explicit new focus/lifetime operation.
            # Its ACK is not a gesture retirement feature observation.
            baseline_counts['source']=callback_count(route.fixture.state(),'source',route.toolkit)
        else:
            required=current_geometry if end=='minimize-preview' else initial_geometry
            actual=geometry(route.window('source'))
            if actual!=required:raise ValueError('Actual interruption geometry/pin authority mismatch')
        route.gate('Actual nonrelease retirement preserves groups raw hold and independent focus',True,before=before,after=after,interruptionACK=ack)
        route.pointer.button(case['button'],False)
        released_after=route.wait(lambda:route.native() if not route.native()['signalDownButtonIds'] and route.native()['coreDragTarget'] is None and not route.native()['heldButtons'] else None,'Actual genuine swallowed release completion')
        released(released_after)
        route.gate('Genuine release creates no group insertion or public callback leak',group_snapshot(before)==group_snapshot(released_after) and all(callback_count(route.fixture.state(),role,route.toolkit)==count for role,count in baseline_counts.items()),native=released_after,counts=baseline_counts,public=route.fixture.state())
        if end=='minimize-preview':route.restore_frontend(target,current_geometry)
        self.callback('source');self.callback('peer')
        route.gate('Independent peer geometry remains exact after complete case',geometry(route.window('peer'))==peer_geometry,expected=peer_geometry,actual=geometry(route.window('peer')))
