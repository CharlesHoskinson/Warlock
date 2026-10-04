"""Owning WAYLAND_DEBUG client transcript joins, not server presentation receipts."""
import re
from journal import Refused,integer
OBJ=r'([a-z_][a-z_0-9]*)[@#]([1-9][0-9]*)'
CALL=re.compile(r'^\s*\[\s*[0-9]+\.[0-9]+\]\s*(?P<direction>->\s*)?(?P<iface>[a-z_][a-z_0-9]*)[@#](?P<id>[1-9][0-9]*)\.(?P<method>[a-z_][a-z_0-9]*)\((?P<args>.*)\)\s*$')
class Trace:
 def __init__(self,raw):
  if type(raw) is not bytes or len(raw)>8*1024*1024:raise Refused('owning Wayland transcript bound')
  try:text=raw.decode('utf-8',errors='strict')
  except UnicodeError as error:raise Refused('Wayland transcript Unicode') from error
  self.surfaces={};self.toplevels={};self.popups={};self.calls=[];self.surface_epochs={};self.live_surfaces={};self.attachments={}
  for index,line in enumerate(text.split('\n')[:-1]):
   m=CALL.fullmatch(line)
   if not m:continue
   row=m.groupdict();row.update(index=index,id=integer(int(row['id']),1,2**32-1),direction='request' if row['direction'] else 'event');self.calls.append(row)
   iface,oid,method,args=row['iface'],row['id'],row['method'],row['args']
   if row['direction']=='request':
    if iface=='wl_compositor' and method=='create_surface':
     sid=self.new_id(args,'wl_surface');self.surface_epochs[sid]=self.surface_epochs.get(sid,0)+1;self.live_surfaces[sid]=self.surface_epochs[sid]
    elif iface=='xdg_wm_base' and method=='get_xdg_surface':
     match=re.fullmatch(r'new id xdg_surface[@#]([1-9][0-9]*), wl_surface[@#]([1-9][0-9]*)',args)
     if not match:raise Refused('actual xdg/wl surface join syntax')
     xid,sid=map(int,match.groups());self.surfaces[xid]={'surface':sid,'epoch':self.live_surfaces.get(sid),'geometry':None,'configure':[],'ack':[],'commits':[]}
     if self.surfaces[xid]['epoch'] is None:raise Refused('xdg surface without current created wl surface')
    elif iface=='xdg_surface' and method=='get_toplevel':
     tid=self.new_id(args,'xdg_toplevel');self.toplevels[tid]={'xdgSurface':oid,'title':None,'parent':None,'proposals':[]}
    elif iface=='xdg_surface' and method=='get_popup':
     match=re.fullmatch(r'new id xdg_popup[@#]([1-9][0-9]*), xdg_surface[@#]([1-9][0-9]*), xdg_positioner[@#]([1-9][0-9]*)',args)
     if not match:raise Refused('popup requires actual immediate xdg parent')
     pid,parent,positioner=map(int,match.groups());self.popups[pid]={'xdgSurface':oid,'parent':parent,'positioner':positioner,'grab':None}
    elif iface=='xdg_toplevel' and method=='set_title' and oid in self.toplevels:
     import json
     try:title=json.loads(args)
     except ValueError as error:raise Refused('title transcript quoting') from error
     if type(title) is not str:raise Refused('title string')
     self.toplevels[oid]['title']=title
    elif iface=='xdg_toplevel' and method=='set_parent' and oid in self.toplevels:
     parent=None if args=='nil' else self.object_id(args,'xdg_toplevel');self.toplevels[oid]['parent']=parent
    elif iface=='xdg_surface' and method=='set_window_geometry' and oid in self.surfaces:
     values=self.numbers(args,4);integer(values[2],1,2**23);integer(values[3],1,2**23);self.surfaces[oid]['geometry']={'index':index,'rectangle':values}
    elif iface=='xdg_surface' and method=='ack_configure' and oid in self.surfaces:
     serial=integer(int(args),0,2**32-1);self.surfaces[oid]['ack'].append({'index':index,'serial':serial})
    elif iface=='wl_surface' and method=='attach':
     match=re.fullmatch(r'(?:wl_buffer[@#]([1-9][0-9]*)|nil), -?(?:0|[1-9][0-9]*), -?(?:0|[1-9][0-9]*)',args)
     if not match:raise Refused('actual buffer attachment syntax')
     self.attachments[oid]={'index':index,'bufferId':int(match.group(1)) if match.group(1) else None,'epoch':self.live_surfaces.get(oid)}
    elif iface=='wl_surface' and method=='commit':
     for surface in self.surfaces.values():
      if surface['surface']==oid and surface['epoch']==self.live_surfaces.get(oid):surface['commits'].append({'index':index,'attachment':self.attachments.get(oid)})
    elif iface=='xdg_popup' and method=='grab' and oid in self.popups:
     match=re.fullmatch(r'wl_seat[@#]([1-9][0-9]*), ([0-9]+)',args)
     if not match:raise Refused('raw popup seat/grab serial')
     seat,serial=map(int,match.groups());self.popups[oid]['grab']={'index':index,'seat':seat,'serial':integer(serial,0,2**32-1)}
    elif method=='destroy':
     if iface=='wl_surface':self.live_surfaces.pop(oid,None)
     elif iface=='xdg_toplevel':self.toplevels.pop(oid,None)
     elif iface=='xdg_popup':self.popups.pop(oid,None)
     elif iface=='xdg_surface':self.surfaces.pop(oid,None)
   elif iface=='xdg_surface' and method=='configure' and oid in self.surfaces:
    self.surfaces[oid]['configure'].append({'index':index,'serial':integer(int(args),0,2**32-1)})
   elif iface=='xdg_toplevel' and method=='configure' and oid in self.toplevels:
    self.toplevels[oid]['proposals'].append({'index':index,'args':args})
 @staticmethod
 def new_id(args,iface):
  m=re.fullmatch(r'new id '+iface+r'[@#]([1-9][0-9]*)',args)
  if not m:raise Refused('actual new resource syntax')
  return integer(int(m.group(1)),1,2**32-1)
 @staticmethod
 def object_id(args,iface):
  m=re.fullmatch(iface+r'[@#]([1-9][0-9]*)',args)
  if not m:raise Refused('resource reference syntax')
  return integer(int(m.group(1)),1,2**32-1)
 @staticmethod
 def numbers(args,count):
  if not re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:, -?(?:0|[1-9][0-9]*)){'+str(count-1)+'}',args):raise Refused('canonical geometry transcript')
  return [integer(int(v),-(2**23),2**23) for v in args.split(', ')]
 def role(self,*,role,pid,surface_id):
  title=f'ELM-GTK4-{role}-{pid}';matches=[]
  for tid,toplevel in self.toplevels.items():
   surface=self.surfaces.get(toplevel['xdgSurface'])
   if toplevel['title']==title and surface and surface['surface']==surface_id and surface['epoch']==self.live_surfaces.get(surface_id):matches.append((tid,toplevel,surface))
  if len(matches)!=1:raise Refused('unique current owning title/protocol/resource join')
  tid,toplevel,surface=matches[0]
  if surface['geometry'] is None or not surface['ack']:raise Refused('actual window geometry/ACK absent')
  ack=surface['ack'][-1];config=[c for c in surface['configure'] if c['serial']==ack['serial'] and c['index']<ack['index']]
  commits=[c for c in surface['commits'] if c['index']>ack['index'] and c['index']>surface['geometry']['index'] and c['attachment'] and c['attachment']['epoch']==surface['epoch'] and c['attachment']['bufferId'] is not None]
  if not config or not commits:raise Refused('configure→ACK→geometry/buffer commit chronology absent')
  return {'toplevelId':tid,'xdgSurfaceId':toplevel['xdgSurface'],'wlSurfaceId':surface_id,'surfaceEpoch':surface['epoch'],'parentToplevel':toplevel['parent'],'windowGeometry':surface['geometry']['rectangle'],'configure':config[-1],'ack':ack,'lastCommitIndex':commits[-1]['index'],'bufferId':commits[-1]['attachment']['bufferId'],'presentationProved':False}
