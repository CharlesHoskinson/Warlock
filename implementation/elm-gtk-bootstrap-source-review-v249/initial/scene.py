"""Bind current GTK role journal, raw protocol and native client identity."""
from journal import Refused,integer
from protocol import Trace
from geometry import marker

def current_role(rows,name):
 # Latest lifetime event must still identify a mapped live instance.
 selected=[r for r in rows if r.get('role')==name]
 if not selected:return None
 latest=selected[-1]
 if latest['event'] in ('close','unmap','destroy-request','local-destroy') or latest.get('mapped') is not True:return None
 for key in ('instance','mapGeneration','surfaceId'):integer(latest.get(key),1,2**32-1)
 return latest

def bind(actor,session,name,*,require_landmark=True):
 rows=actor.read();role=current_role(rows,name)
 if role is None:return None
 matches=[c for c in session.data('clients') if c.get('pid')==actor.pid and c.get('title')==f'ELM-GTK4-{name}-{actor.pid}']
 if len(matches)!=1:return None
 native=matches[0]
 if type(native.get('address')) is not str or native.get('xwayland') is not False:raise Refused('actual owning Wayland native window')
 with actor.stderr.open('rb') as source:raw=source.read(8*1024*1024+1)
 try:wire=Trace(raw).role(role=name,pid=actor.pid,surface_id=role['surfaceId'])
 except Refused:return None # Readiness only; enclosing absolute deadline never renewed.
 identity={k:role[k] for k in ('role','instance','mapGeneration','surfaceId')}
 result={'gtk':role,'native':native,'wire':wire,'identity':identity}
 if require_landmark:
  result['marker']=marker(role,identity=identity,native_real=[*native['at'],*native['size']],window_geometry=wire['windowGeometry'])
 return result

def same(before,after):
 if before['identity']!=after['identity'] or before['native']['address']!=after['native']['address'] or before['wire']['surfaceEpoch']!=after['wire']['surfaceEpoch'] or before['wire']['wlSurfaceId']!=after['wire']['wlSurfaceId']:raise Refused('owning GTK/native identity changed during interval')
 return True
