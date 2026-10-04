"""Qt scene lifetime joins. No compositor presentation/Qt-global authority."""
import re
from pathlib import Path
from journal import Refused,integer
from protocol import Trace,NotReady
from geometry import identity,marker,point,extent,action_region
from observer import roles,selected

ADDRESS=re.compile(r'0x[1-9a-f][0-9a-f]{0,15}')

def current_role(rows,name):
 if name not in ('A','B','C','D','P') or type(rows) is not list or len(rows)>16384:raise Refused('bounded Qt role history')
 candidates=[r for r in rows if r.get('role')==name]
 if not candidates:return None
 for r in candidates:integer(r.get('instance'),1,2**32-1)
 newest=max(r['instance'] for r in candidates)
 current=[r for r in candidates if r['instance']==newest]
 # Late local destruction of an old QObject is legitimate, never a current binding.
 if any(r['instance']!=newest and r['event']!='local-destroy' for r in candidates[candidates.index(current[0])+1:]):raise Refused('stale Qt role callback after replacement')
 latest=current[-1]
 if latest['event'] in ('destroy-request','local-destroy','unmap') or latest.get('visible') is False:return None
 if type(latest.get('visible')) is not bool:raise Refused('canonical Qt visibility')
 if latest.get('surfaceId')==0 or latest.get('mapGeneration')==0:return None
 identity(latest)
 if any(r.get('mapGeneration',0)>latest['mapGeneration'] for r in current):raise Refused('Qt map generation regressed')
 return latest

def actor_identity(role,*,pid,started):
 integer(pid,2,2**31-1);integer(started,1,2**63-1)
 if integer(role.get('pid'),2,2**31-1)!=pid or integer(role.get('processStarted'),1,2**63-1)!=started:raise Refused('Qt role process lifetime differs')
 return {**identity(role),'pid':pid,'processStarted':started}

def native_client(clients,*,name,pid):
 if type(clients) is not list or len(clients)>256:raise Refused('complete native client inventory bound')
 seen=set()
 for c in clients:
  if type(c) is not dict or type(c.get('address')) is not str or not ADDRESS.fullmatch(c['address']) or c['address'] in seen:raise Refused('native client unique address')
  seen.add(c['address']);integer(c.get('pid'),2,2**31-1)
  if type(c.get('title')) is not str or type(c.get('xwayland')) is not bool:raise Refused('native client title/type')
  try:title_bytes=c['title'].encode('utf-8',errors='strict')
  except UnicodeError as error:raise Refused('native title UTF8') from error
  if len(title_bytes)>4096:raise Refused('native title bound')
  point(c.get('at'));extent(c.get('size'))
 matches=[c for c in clients if c['pid']==pid and c['title']==f'ELM-QT6-{name}-{pid}']
 if not matches:raise NotReady('native Qt role not mapped yet')
 if len(matches)!=1:raise Refused('ambiguous exact Qt native title/PID')
 c=matches[0]
 if c['xwayland']:raise Refused('Wayland Qt role required')
 point(c.get('at'));extent(c.get('size'))
 return c

def join_window(rows,raw,clients,role_state,*,name,pid,started,compositor_pid,require_landmark=True):
 if name=='P':raise Refused('popup requires raw/native popup ownership join')
 q=current_role(rows,name)
 if q is None:return None
 life=actor_identity(q,pid=pid,started=started)
 try:c=native_client(clients,name=name,pid=pid);wire=Trace(raw).role(role=name,pid=pid,surface_id=q['surfaceId'])
 except NotReady:return None
 observed=roles(role_state,compositor_pid=compositor_pid)
 eligibility=selected(observed,address=c['address'],pid=pid)
 if c['size']!=wire['windowGeometry'][2:]:return None
 if [integer(q.get('windowWidth'),1,2**23),integer(q.get('windowHeight'),1,2**23)]!=wire['windowGeometry'][2:]:return None
 result={'qt':q,'native':c,'wire':wire,'identity':life,'nativeRole':eligibility,'presentationProved':False}
 if require_landmark:result['marker']=marker(q,identity=identity(q),native_real=[*c['at'],*c['size']],window_geometry=wire['windowGeometry'])
 return result

def resource(row,*,pid,uid):
 if type(row) is not dict or set(row)!={'id','pid','uid'}:raise Refused('native popup resource schema')
 integer(row['id'],1,2**32-1)
 if integer(row['pid'],2,2**31-1)!=pid or integer(row['uid'],0,2**32-1)!=uid:raise Refused('native resource PID/UID owner')
 return row['id']

def join_popup(rows,raw,state,*,parent,pid,started,uid,compositor_pid):
 q=current_role(rows,'P')
 if q is None:return None
 life=actor_identity(q,pid=pid,started=started)
 if parent['identity']['pid']!=pid or parent['identity']['processStarted']!=started:raise Refused('popup parent process lifetime')
 if integer(q.get('transientSurfaceId'),1,2**32-1)!=parent['identity']['surfaceId']:raise Refused('Qt popup transient surface differs')
 fields={'schema','pid','grabPresent','grabKeyboard','grabPointer','keyboardFocus','pointerFocus','popups'}
 if type(state) is not dict or set(state)!=fields or integer(state['schema'],1,1)!=1 or integer(state['pid'],2,2**31-1)!=compositor_pid:raise Refused('owning popup observer envelope')
 for k in ('keyboardFocus','pointerFocus'):
  focus=state[k]
  if focus is not None:
   if type(focus) is not dict or set(focus)!={'id','pid','uid'}:raise Refused('native focus resource schema')
   integer(focus['id'],1,2**32-1);integer(focus['pid'],2,2**31-1);integer(focus['uid'],0,2**32-1)
 for k in ('grabPresent','grabKeyboard','grabPointer'):
  if type(state[k]) is not bool:raise Refused('canonical native grab')
 if type(state['popups']) is not list or len(state['popups'])>512:raise Refused('native popup list bound')
 matches=[];seen=set()
 fields={'viewAddress','surface','t1Root','position','size','visible','grabMember','rootGrabMember'}
 for row in state['popups']:
  if type(row) is not dict or set(row)!=fields or type(row['viewAddress']) is not str or not ADDRESS.fullmatch(row['viewAddress']) or row['viewAddress'] in seen:raise Refused('native popup exact unique view')
  seen.add(row['viewAddress']);point(row['position']);extent(row['size'])
  for k in ('visible','grabMember','rootGrabMember'):
   if type(row[k]) is not bool:raise Refused('native popup flags')
  # Validate every resource shape even when owned by an unrelated client.
  for k in ('surface','t1Root'):
   value=row[k]
   if type(value) is not dict or set(value)!={'id','pid','uid'}:raise Refused('complete popup resource inventory')
   integer(value['id'],1,2**32-1);integer(value['pid'],2,2**31-1);integer(value['uid'],0,2**32-1)
  if row['surface']['pid']==pid and row['surface']['id']==q['surfaceId']:matches.append(row)
 if not matches:return None
 if len(matches)!=1:raise Refused('ambiguous current popup resource')
 n=matches[0];resource(n['surface'],pid=pid,uid=uid)
 if resource(n['t1Root'],pid=pid,uid=uid)!=parent['identity']['surfaceId']:raise Refused('native popup T1 root differs')
 if not n['visible']:return None
 try:
  trace=Trace(raw)
  live_parent=trace.role(role=parent['identity']['role'],pid=pid,surface_id=parent['identity']['surfaceId'])
  for k in ('toplevelId','xdgSurfaceId','wlSurfaceId','surfaceEpoch'):
   if live_parent[k]!=parent['wire'][k]:raise Refused('popup parent raw resource lifetime retired/replaced')
  wire=trace.popup(surface_id=q['surfaceId'],parent_xdg=parent['wire']['xdgSurfaceId'])
 except NotReady:return None
 if n['size']!=wire['windowGeometry'][2:]:return None
 result={'qt':q,'native':{'address':n['viewAddress'],'at':n['position'],'size':n['size'],'pid':pid},'wire':wire,'identity':life,'nativePopup':n,'grab':{k:state[k] for k in ('grabPresent','grabKeyboard','grabPointer')},'nativeFocus':{k:state[k] for k in ('keyboardFocus','pointerFocus')},'presentationProved':False}
 result['marker']=marker(q,identity=identity(q),native_real=[*n['position'],*n['size']],window_geometry=wire['windowGeometry'],popup=True,local=(4,4))
 result['action']=action_region(q,native_real=[*n['position'],*n['size']],window_geometry=wire['windowGeometry'])
 return result

def bind(actor,session,name,*,require_landmark=True):
 session.guard()
 if actor.process.poll() is not None:raise Refused('Qt actor no longer live')
 try:stat=Path('/proc',str(actor.pid),'stat').read_text().rsplit(')',1)[1].split()
 except (OSError,IndexError,UnicodeError) as error:raise Refused('Qt actor process lifetime unavailable') from error
 if len(stat)<20 or stat[19]!=actor.started:raise Refused('Qt actor process replaced')
 compositor=next((r for _,r in session.host.processes if r.get('name')=='hyprland'),None)
 if compositor is None:raise Refused('owned compositor missing')
 with actor.stderr.open('rb') as f:raw=f.read(8*1024*1024+1)
 return join_window(actor.read(),raw,session.data('clients'),session.data('elm_role_state'),name=name,pid=actor.pid,started=int(actor.started),compositor_pid=compositor['pid'],require_landmark=require_landmark)

def same(before,after):
 if type(before) is not dict or type(after) is not dict:return False
 return all(before.get(k)==after.get(k) for k in ('identity','native','wire','marker','nativeRole','nativePopup','grab','nativeFocus','action'))
