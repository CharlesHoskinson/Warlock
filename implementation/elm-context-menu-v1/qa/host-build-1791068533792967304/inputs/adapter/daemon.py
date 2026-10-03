"""One owned authenticated effect authority connection, event-driven refresh, bounded stdio."""
import json,os,selectors,signal,socket,stat,struct,sys,time,traceback
from pathlib import Path
from endpoint import Refused,exact,canonical,binding
from effect_endpoint import Endpoint

MAX_INPUT=4096
MAX_EVENT=65536
MAX_OUTPUT=1048576

def send(frame):
 raw=json.dumps(frame,separators=(',',':'),ensure_ascii=True).encode()
 if len(raw)>MAX_OUTPUT:raise Refused('Output bound')
 sys.stdout.buffer.write(raw+b'\n');sys.stdout.buffer.flush()

def event_socket(client):
 client.verify_process();client.verify_paths()
 path=client.path.with_name('.socket2.sock');before=path.lstat()
 if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid():raise Refused('Unsafe event socket')
 connection=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);connection.settimeout(2)
 try:
  connection.connect(str(path));pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  if pid!=client.pid or uid!=os.getuid():raise Refused('Event peer mismatch')
  after=path.lstat()
  if (before.st_dev,before.st_ino,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_ctime_ns):raise Refused('Event socket replaced')
  client.verify_process();connection.setblocking(False);return connection
 except BaseException:connection.close();raise

def main():
 config=json.loads(Path(sys.argv[1]).read_text());client=Endpoint(**config)
 # Subscribe before initial projection; notifications may coalesce before a new
 # authoritative snapshot is requested, never after numbered publication.
 with event_socket(client) as events,selectors.DefaultSelector() as selector:
  hello=client.hello();send(hello)
  selector.register(0,selectors.EVENT_READ,'stdin');selector.register(events,selectors.EVENT_READ,'events')
  incoming=bytearray();notifications=bytearray();dirty=False;have_snapshot=False;last_notice=0.0
  relevant={b'openwindow',b'closewindow',b'windowtitle',b'windowtitlev2',b'activewindow',b'movewindow',b'movewindowv2',b'changefloatingmode'}
  while True:
   timeout=max(0.0,.04-(time.monotonic()-last_notice)) if dirty and have_snapshot else None
   ready=selector.select(timeout)
   for key,_ in ready:
    if key.data=='stdin':
     data=os.read(0,4096)
     if not data:return 0
     incoming.extend(data)
     if len(incoming)>MAX_INPUT:raise Refused('Frontend input bound')
     while b'\n' in incoming:
      line,_,rest=incoming.partition(b'\n');incoming=bytearray(rest)
      request=json.loads(line)
      if request.get('kind')=='window-effect':
       exact(request,['protocolVersion','kind','effectProtocol','binding','intent'])
       if type(request['effectProtocol']) is not int or request['effectProtocol']!=1:raise Refused('Effect protocol')
      else:exact(request,['protocolVersion','kind','binding','requestId'])
      if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or binding(request['binding'])!=client.bound:raise Refused('Frontend scope mismatch')
      if request['kind']=='window-effect':
       outcome=client.effect(request['intent'])
       send(outcome)
      elif request['kind']=='projection-request':
       canonical(request['requestId'])
       before=client.scene_facts(request['requestId']);snapshot=client.snapshot(request['requestId']);after=client.scene_facts(request['requestId'])
       facts={w['incarnation']:w for w in after['facts']['windows']}
       if before['revision']!=after['revision'] or before['outputGeneration']!=after['outputGeneration'] or set(facts)!={w['incarnation'] for w in snapshot['windows']} or any(w['minimized']!=facts[w['incarnation']]['minimized'] for w in snapshot['windows']):
        send({'kind':'host-refresh'})
       else:
        send({'protocolVersion':3,'kind':'action-projection','binding':client.bound,'requestId':request['requestId'],'context':client.context(after),'scene':{'revision':after['revision'],'windows':snapshot['windows']}})
       have_snapshot=True;dirty=False
      else:raise Refused('Unsupported frontend request')
    else:
     data=events.recv(4096)
     if not data:raise Refused('Event connection closed')
     notifications.extend(data)
     if len(notifications)>MAX_EVENT:raise Refused('Event capacity exceeded')
     while b'\n' in notifications:
      line,_,rest=notifications.partition(b'\n');notifications=bytearray(rest)
      if bytes(line.split(b'>>',1)[0]) in relevant:dirty=True
   if dirty and have_snapshot and time.monotonic()-last_notice>=.04:
    client.verify_process();send({'protocolVersion':3,'kind':'host-refresh'});last_notice=time.monotonic();dirty=False

if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as error:
  send({'protocolVersion':3,'kind':'host-disconnected'})
  print('Backend failure locations: '+','.join(Path(frame.filename).name+':'+str(frame.lineno)+':'+frame.name for frame in traceback.extract_tb(error.__traceback__)),file=sys.stderr)
  print('Authority backend stopped: '+(str(error) if isinstance(error,Refused) else type(error).__name__),file=sys.stderr);raise SystemExit(1)
