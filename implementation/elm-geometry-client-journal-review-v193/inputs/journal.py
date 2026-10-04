import json, re
class InvalidJournal(ValueError): pass
KNOWN={'configure','ack-configure','buffercommit','ready','buffer-release','server-close','pointer-enter','pointer-leave','pointer-motion','pointer-button','server-barrier','request','inspect','normalexit'}
def parse(data,pid,profile,terminal=False):
 def require(ok,why):
  if not ok:raise InvalidJournal(why)
 def integer(v,lo,hi):return type(v) is int and lo<=v<=hi
 def pairs(values):
  out={}
  for k,v in values:
   if k in out:raise InvalidJournal('duplicate key')
   out[k]=v
  return out
 require(type(data) is bytes and len(data)<=2*1024*1024,'journal bound')
 require(not data or data.endswith(b'\n'),'truncated journal')
 lines=data.splitlines();require(len(lines)<=8192,'event bound')
 rows=[];phase=None;serial=None;dimensions=None;last_time=0;ready=False;exited=False;commits=0
 for i,line in enumerate(lines,1):
  require(len(line)<=8192,'line bound')
  try:r=json.loads(line,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(InvalidJournal('nonfinite JSON')))
  except (UnicodeError,ValueError,RecursionError) as exc:raise InvalidJournal('invalid JSON') from exc
  require(type(r) is dict and r.get('pid')==pid and type(r.get('pid')) is int,'PID')
  require(r.get('sequence')==i and type(r.get('sequence')) is int,'sequence')
  require(integer(r.get('monotonicNs'),1,2**64-1) and r['monotonicNs']>=last_time,'time');last_time=r['monotonicNs']
  require(not exited,'event after exit')
  for key in ('serial','ackedSerial'):require(integer(r.get(key),0,2**32-1),'serial')
  for key in ('width','height'):require(integer(r.get(key),32,4096),'dimensions')
  for key in ('maximized','fullscreen'):require(type(r.get(key)) is bool,'mode')
  kind=r.get('event');require(type(kind) is str and kind in KNOWN,'event')
  if phase is not None:require(kind==phase,'configure/ACK/commit order')
  if kind=='configure':serial=r['serial'];dimensions=[r['width'],r['height']];phase='ack-configure'
  elif kind=='ack-configure':
   require(phase=='ack-configure' and r['serial']==serial and r['ackedSerial']==serial and [r['width'],r['height']]==dimensions,'ACK mismatch');phase='buffercommit'
  elif kind=='buffercommit':
   require(phase=='buffercommit' and r['serial']==serial and r['ackedSerial']==serial and r.get('bufferSerial')==serial and [r['width'],r['height']]==dimensions,'commit mismatch')
   x,y,right,bottom,scale=profile;w,h=dimensions
   for key,length in [('geometry',4),('surfaceSize',2),('bufferSize',2)]:require(type(r.get(key)) is list and len(r[key])==length and all(type(v) is int for v in r[key]),'extent type')
   require(type(r.get('scale')) is int and type(r.get('bufferSerial')) is int,'commit integer type')
   require(r.get('geometry')==[x,y,w,h] and r.get('surfaceSize')==[x+w+right,y+h+bottom] and r.get('bufferSize')==[(x+w+right)*scale,(y+h+bottom)*scale] and r.get('scale')==scale,'profile mismatch')
   require(integer(r.get('inflight'),1,8) and integer(r.get('allocatedBytes'),r['bufferSize'][0]*r['bufferSize'][1]*4,128*1024*1024),'resource bound')
   require(type(r.get('argb')) is str and re.fullmatch(r'ff[0-9a-f]{6}',r['argb']) is not None,'color')
   phase=None;commits+=1
  elif kind=='ready':
   require(commits>0 and not ready and r.get('title')==f'ELM-XDG-ORIGIN-PROBE-{pid}' and r.get('appId')=='elm-xdg-origin-probe','ready identity');ready=True
  elif kind=='normalexit':exited=True
  rows.append(r)
 require(phase is None,'incomplete configure generation')
 if terminal:require(exited and ready and commits>0,'terminal lifecycle')
 return {'events':rows,'commits':commits,'ready':ready,'normalExit':exited}
