"""Strict315 diagnostic DTO; deliberately no authenticated grant constructor."""
import json
from dataclasses import dataclass

class Refused(ValueError): pass
def integer(v,lo,hi):
    if type(v) is not int or not lo<=v<=hi: raise Refused('integer bound')
    return v
def boolean(v):
    if type(v) is not bool: raise Refused('boolean')
    return v
def fields(v,names):
    if type(v) is not dict or set(v)!=set(names): raise Refused('closed object fields')
    return v
def pairs(rows):
    result={}
    for k,v in rows:
        if k in result: raise Refused('duplicate key')
        result[k]=v
    return result
def constant(_): raise Refused('nonfinite JSON')
@dataclass(frozen=True)
class Surface:
    id:int; pid:int; uid:int; connection:int
@dataclass(frozen=True)
class Member:
    surface:Surface; mapped:bool
@dataclass(frozen=True)
class Popup:
    surface:Surface; parent:Surface|None; root:Surface
    layer:bool; owner:bool; mapped:bool; root_accepted:bool
@dataclass(frozen=True)
class Snapshot:
    pid:int; sequence:int; surfaces:int; clients:int
    grab:bool; keyboard:bool; pointer:bool; xdg:bool
    locked:bool; exclusive:bool; drag:bool; held:bool
    members:tuple[Member,...]; popups:tuple[Popup,...]

def parse(raw,*,core_pid,previous_sequence=0):
    integer(core_pid,2,2**31-1);integer(previous_sequence,0,2**64-1)
    if type(raw) is not bytes or len(raw)>65536: raise Refused('payload bound')
    try: o=json.loads(raw.decode('utf-8',errors='strict'),object_pairs_hook=pairs,parse_constant=constant)
    except (UnicodeError,ValueError,RecursionError) as e: raise Refused('strict JSON') from e
    fields(o,('schema','pid','sequence','complete','surfaceCount','surfaceClientCount','grabPresent','grabKeyboard','grabPointer','xdgGrab','sessionLocked','exclusiveLayerPresent','layoutDragPresent','heldButtons','members','popups'))
    if integer(o['schema'],1,1)!=1 or integer(o['pid'],2,2**31-1)!=core_pid or boolean(o['complete']) is not True: raise Refused('complete owning snapshot')
    q=o['sequence']
    if type(q) is not str or not q or len(q)>20 or q[0]=='0' or any(c<'0' or c>'9' for c in q): raise Refused('canonical sequence')
    seq=integer(int(q),1,2**64-1)
    if seq<=previous_sequence: raise Refused('stale sequence')
    count=integer(o['surfaceCount'],0,4096);clients=integer(o['surfaceClientCount'],0,count)
    if bool(count)!=bool(clients): raise Refused('surface/client census consistency')
    connections={};resources={}
    def surface(v):
        fields(v,('id','pid','uid','connection'))
        s=Surface(integer(v['id'],1,2**32-1),integer(v['pid'],1,2**31-1),integer(v['uid'],0,2**32-1),integer(v['connection'],1,clients))
        peer=(s.pid,s.uid)
        if connections.setdefault(s.connection,peer)!=peer: raise Refused('connection credentials changed')
        if resources.setdefault((s.connection,s.id),s)!=s: raise Refused('resource identity changed')
        return s
    if type(o['members']) is not list or len(o['members'])>min(256,count): raise Refused('member bound')
    members=[];seen=set()
    for row in o['members']:
        fields(row,('surface','mapped'));s=surface(row['surface'])
        if s in seen: raise Refused('duplicate member')
        seen.add(s);members.append(Member(s,boolean(row['mapped'])))
    if type(o['popups']) is not list or len(o['popups'])>64: raise Refused('popup bound')
    popups=[];seen_popups=set()
    for row in o['popups']:
        fields(row,('surface','parent','root','layerRoot','owner','mapped','rootAccepted'))
        s=surface(row['surface']);p=None if row['parent'] is None else surface(row['parent']);r=surface(row['root'])
        popup=Popup(s,p,r,boolean(row['layerRoot']),boolean(row['owner']),boolean(row['mapped']),boolean(row['rootAccepted']))
        if s in seen_popups or s not in seen or not popup.mapped or s==r or popup.root_accepted!=(r in seen): raise Refused('popup/member/root consistency')
        seen_popups.add(s);popups.append(popup)
    if len(resources)>count: raise Refused('resource census exceeds native total')
    grab=boolean(o['grabPresent']);xdg=boolean(o['xdgGrab'])
    keyboard=boolean(o['grabKeyboard']);pointer=boolean(o['grabPointer'])
    if (not grab and (members or keyboard or pointer or xdg)) or (not xdg and popups) or (xdg and (not grab or not popups or sum(p.owner for p in popups)!=1)): raise Refused('grab/protocol consistency')
    return Snapshot(core_pid,seq,count,clients,grab,keyboard,pointer,xdg,
        boolean(o['sessionLocked']),boolean(o['exclusiveLayerPresent']),boolean(o['layoutDragPresent']),boolean(o['heldButtons']),tuple(members),tuple(popups))

def match_layer_popup(snapshot,*,host_pid,host_uid,popup_id,root_id):
    """A diagnostic correspondence only. Same-PID host connection is unauthenticated."""
    integer(host_pid,2,2**31-1);integer(host_uid,0,2**32-1)
    integer(popup_id,1,2**32-1);integer(root_id,1,2**32-1)
    if not isinstance(snapshot,Snapshot) or not snapshot.grab or not snapshot.xdg or not snapshot.keyboard or not snapshot.pointer or snapshot.exclusive or snapshot.drag or snapshot.held: raise Refused('blocking/unknown native state')
    candidates=[p for p in snapshot.popups if p.owner and p.surface.id==popup_id and p.root.id==root_id and p.surface.pid==host_pid and p.surface.uid==host_uid]
    if len(candidates)!=1: raise Refused('exact diagnostic owner')
    owner=candidates[0];connection=owner.surface.connection
    if any(not p.layer or p.root!=owner.root or any(s and (s.pid!=host_pid or s.uid!=host_uid or s.connection!=connection) for s in (p.surface,p.parent,p.root)) for p in snapshot.popups): raise Refused('foreign/mixed popup roots')
    popup_surfaces={p.surface for p in snapshot.popups};allowed=set(popup_surfaces)
    for p in snapshot.popups:
        if p.parent is not None and p.parent not in popup_surfaces and p.parent!=owner.root: raise Refused('unjoined immediate parent')
        if p.root_accepted: allowed.add(p.root)
    if {m.surface for m in snapshot.members}!=allowed or any(not m.mapped for m in snapshot.members): raise Refused('extra/unmapped accepted member')
    return {'scope':'diagnostic correspondence only','connection':connection,'popup':popup_id,'root':root_id,
        'authenticated':False,'ownBlockerGrantQualified':False}
