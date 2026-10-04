"""One owned authenticated effect authority connection, event-driven refresh, bounded stdio."""
from contextlib import ExitStack
import json,os,selectors,signal,socket,stat,struct,sys,time,traceback
from pathlib import Path
from endpoint import Refused,exact,canonical,binding,unique
from geometry_endpoint import GeometryEndpoint as Endpoint
from taskbar_projection import coherent_scene
from catalog_transport import CatalogTransport
from recovery_journal import Journal,RecoveryFailure,guarded
from recovery_fault import after_submit

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


def handle_request(client,catalog,request,recovery):
 if not isinstance(request,dict):raise Refused('Frontend request object')
 kind=request.get('kind')
 if kind in {'catalog-request','application-launch'}:
  send(catalog.handle(request));return
 if kind=='window-effect':
  exact(request,['protocolVersion','kind','effectProtocol','binding','intent'])
  if type(request['effectProtocol']) is not int or request['effectProtocol'] not in (1,2):raise Refused('Effect protocol')
 elif kind=='geometry-attach':
  exact(request,['protocolVersion','kind','geometryProtocol','binding','requestId'])
 elif kind=='geometry-facts-request':
  exact(request,['protocolVersion','kind','geometryProtocol','binding','requestId','minimumWatermark'])
 elif kind=='projection-request':
  exact(request,['protocolVersion','kind','binding','requestId'])
 else:raise Refused('Unsupported frontend request')
 if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or binding(request['binding'])!=client.bound:raise Refused('Frontend scope mismatch')
 if kind.startswith('geometry-'):
  if type(request['geometryProtocol']) is not int or request['geometryProtocol']!=1:raise Refused('Geometry protocol')
 if kind=='window-effect':
  guarded(lambda:recovery.begin(client.bound,request['intent'],request['effectProtocol']))
  outcome=client.geometry_effect(request['intent']) if request['effectProtocol']==2 else client.effect(request['intent'])
  after_submit(client,recovery,outcome)
  guarded(lambda:recovery.settle(outcome))
  send(outcome)
 elif kind=='geometry-attach':
  canonical(request['requestId']);send(client.geometry_attach(request['requestId']))
 elif kind=='geometry-facts-request':
  canonical(request['requestId']);canonical(request['minimumWatermark'],True)
  send(client.geometry_facts(request['requestId'],request['minimumWatermark']))
 else:
  canonical(request['requestId'])
  before=client.scene_facts(request['requestId']);snapshot=client.snapshot(request['requestId']);after=client.scene_facts(request['requestId'])
  scene=coherent_scene(before,snapshot,after)
  if scene is None:send({'protocolVersion':3,'kind':'host-refresh'})
  else:send({'protocolVersion':3,'kind':'action-projection','binding':client.bound,'requestId':request['requestId'],'context':client.context(after),'scene':scene})

class FrontendFrames:
 """Bound each wire frame including newline; bounded tail, never aggregate quota."""
 def __init__(self):self.tail=bytearray()
 def feed(self,data):
  if len(data)>4096:raise Refused('Frontend read bound')
  self.tail.extend(data)
  while b'\n' in self.tail:
   line,_,rest=self.tail.partition(b'\n');self.tail=bytearray(rest)
   if len(line)+1>MAX_INPUT:raise Refused('Frontend input bound')
   yield bytes(line)
  if len(self.tail)>=MAX_INPUT:raise Refused('Frontend input bound')
 def finish(self):
  if self.tail:raise Refused('Frontend truncated frame')

def main():
 config=json.loads(Path(sys.argv[1]).read_text());roots=config.pop('catalogRoots',None);client=Endpoint(**config);catalog=CatalogTransport(client,roots)
 # Subscribe before initial projection; notifications may coalesce before a new
 # authoritative snapshot is requested, never after numbered publication.
 with event_socket(client) as events,selectors.DefaultSelector() as selector,ExitStack() as lifetime:
  hello=client.hello()
  recovery=lifetime.enter_context(guarded(lambda:Journal(config['runtime'],config['instance'],client.bound['lifetime'])))
  send(hello)
  uncertain=guarded(lambda:recovery.uncertain(client.bound))
  if uncertain is not None:send(uncertain)
  send({"protocolVersion":3,"kind":"host-geometry-negotiate"})
  selector.register(0,selectors.EVENT_READ,'stdin');selector.register(events,selectors.EVENT_READ,'events')
  incoming=FrontendFrames();notifications=bytearray();dirty=False;have_snapshot=False;last_notice=0.0
  relevant={b'elmwindowstate',b'workspace',b'workspacev2',b'focusedmon',b'focusedmonv2',b'monitoradded',b'monitoraddedv2',b'monitorremoved',b'fullscreen',b'pin',b'openwindow',b'closewindow',b'windowtitle',b'windowtitlev2',b'activewindow',b'movewindow',b'movewindowv2',b'changefloatingmode'}
  while True:
   timeout=max(0.0,.04-(time.monotonic()-last_notice)) if dirty and have_snapshot else None
   ready=selector.select(timeout)
   for key,_ in ready:
    if key.data=='stdin':
     data=os.read(0,4096)
     if not data:incoming.finish();return 0
     for line in incoming.feed(data):
      request=json.loads(line,object_pairs_hook=unique)
      handle_request(client,catalog,request,recovery)
      if request.get('kind')=='projection-request':have_snapshot=True;dirty=False
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

def run():
 try:return main()
 except Exception as error:
  if isinstance(error,RecoveryFailure):send({'protocolVersion':3,'kind':'host-recovery-failed','reason':error.reason})
  send({'protocolVersion':3,'kind':'host-disconnected'})
  print('Backend failure locations: '+','.join(Path(frame.filename).name+':'+str(frame.lineno)+':'+frame.name for frame in traceback.extract_tb(error.__traceback__)),file=sys.stderr)
  print('Authority backend stopped: '+(str(error) if isinstance(error,Refused) else type(error).__name__),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(run())
