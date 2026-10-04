"""Current popup protocol/GTK/native joins; no theme or queued-display inference."""
from pathlib import Path
import json
from geometry import marker,number
from journal import Refused,integer
from protocol import Trace

def binding(actor,session,root):
 rows=actor.read();selected=[r for r in rows if r.get('role')=='P']
 if not selected:return None
 role=selected[-1]
 if role.get('mapped') is not True or role.get('landmarkBoundsAvailable') is not True or role.get('buttonBoundsAvailable') is not True:return None
 sid=integer(role.get('surfaceId'),1,2**32-1);trace=Trace(actor.stderr.read_bytes());matches=[]
 for oid,p in trace.popups.items():
  s=trace.surfaces.get(p['xdgSurface'])
  if s and s['surface']==sid and s['epoch']==trace.live_surfaces.get(sid):matches.append((oid,p,s))
 if len(matches)!=1:raise Refused('one current popup role/protocol/surface lifetime')
 oid,p,s=matches[0]
 if p['parent']!=root['wire']['xdgSurfaceId'] or not p['grab']:raise Refused('actual immediate parent and popup grab request')
 if not s['geometry'] or not s['ack']:return None
 ack=s['ack'][-1];configured=[c for c in s['configure'] if c['serial']==ack['serial'] and c['index']<ack['index']]
 commits=[c for c in s['commits'] if c['index']>ack['index'] and c['index']>s['geometry']['index'] and c['attachment'] and c['attachment']['epoch']==s['epoch'] and c['attachment']['bufferId'] is not None]
 if not configured or not commits:return None
 native=json.loads(session.ctl('elm_popup_state'));actual=[q for q in native['popups'] if q.get('surface',{}).get('id')==sid and q['surface'].get('pid')==actor.pid]
 if len(actual)!=1:return None
 q=actual[0]
 if q.get('t1Root',{}).get('id')!=root['identity']['surfaceId'] or q['t1Root'].get('pid')!=actor.pid or q.get('visible') is not True or q.get('grabMember') is not True:raise Refused('live native popup ownership/visibility/grab')
 ident={k:role[k] for k in ('role','instance','mapGeneration','surfaceId')};geometry=s['geometry']['rectangle']
 landmark=marker(role,identity=ident,native_real=[*q['position'],*q['size']],window_geometry=geometry)
 local=[number(role['buttonNativeX'])+number(role['buttonWidth'])/2-number(role['buttonSurfaceTransformX']),number(role['buttonNativeY'])+number(role['buttonHeight'])/2-number(role['buttonSurfaceTransformY'])]
 if role['buttonWidth']<=0 or role['buttonHeight']<=0 or any(not 0<=v<limit for v,limit in zip(local,(role['surfaceWidth'],role['surfaceHeight']))):raise Refused('actual positive popup button bounds within its surface')
 point=[q['position'][i]+local[i]-geometry[i] for i in (0,1)]
 if any(type(v) not in (int,float) or int(v)!=v or not 0<=v<limit for v,limit in zip(point,(800,600))):raise Refused('integer measured popup button point')
 return {'gtk':role,'identity':ident,'native':q,'nativeInventory':native,'wire':{'popupId':oid,'xdgSurfaceId':p['xdgSurface'],'surfaceEpoch':s['epoch'],'parent':p['parent'],'grab':p['grab'],'geometry':geometry,'ack':ack,'lastCommitIndex':commits[-1]['index']},'marker':landmark,'button':{'surface':local,'global':point}}

def samples(data,point,color):
 if type(data) is not bytes or len(data)!=800*600*3 or type(color) is not list or len(color)!=3:raise Refused('qualified RGB/output extent')
 if type(point) is not list or len(point)!=2 or any(type(v) is not int for v in point):raise Refused('integer sample point')
 x,y=point
 if not 1<=x<799 or not 1<=y<599:raise Refused('complete3x3 sample bound')
 result=[{'point':[px,py],'rgb':list(data[(py*800+px)*3:(py*800+px)*3+3])} for py in range(y-1,y+2) for px in range(x-1,x+2)]
 return {'samples':result,'expected':color,'passed':all(r['rgb']==color for r in result)}
