"""One owned authenticated effect authority connection, event-driven refresh, bounded stdio."""
from contextlib import ExitStack
import json,os,selectors,signal,socket,stat,struct,sys,time,traceback,threading
from pathlib import Path
from endpoint import Refused,exact,canonical,binding,unique
from geometry_endpoint import GeometryEndpoint
from grant_endpoint import GrantEndpoint
from reconciliation import Reconciliation
from taskbar_projection import coherent_scene
from catalog_transport import CatalogTransport
from recovery_journal import RecoveryFailure,guarded
from recovery_store import RecoveryStore as Journal
from recovery_fault import after_submit

MAX_INPUT=4096
MAX_EVENT=65536
MAX_OUTPUT=1048576
OUTPUT_SECONDS=3

class Endpoint(GrantEndpoint,GeometryEndpoint):
 """One authenticated transport, geometry state and native proof history."""
 pass

class OutputFailure(Refused):
 """Delivery failed; durable operation status is never inferred from this."""
 pass

class OutputWriter:
 """One bounded, serialized frame; partial failure permanently closes the lane."""
 def __init__(self):self.lock=threading.Lock();self.poisoned=False
 def write(self,raw):
  deadline=time.monotonic()+OUTPUT_SECONDS
  def remaining():
   left=deadline-time.monotonic()
   if left<=0:raise OutputFailure('Output delivery deadline')
   return left
  if not self.lock.acquire(timeout=remaining()):
   self.poisoned=True;raise OutputFailure('Output serialization deadline')
  try:
   if self.poisoned:raise OutputFailure('Output delivery already failed')
   fd=sys.stdout.fileno();os.set_blocking(fd,False)
   # select supports pipes and regular-file stdout alike; fd is the owned stdio
   # endpoint, never a descriptor supplied by frontend data.
   with selectors.SelectSelector() as selector:
    selector.register(fd,selectors.EVENT_WRITE);offset=0
    while offset<len(raw):
     if self.poisoned:raise OutputFailure('Concurrent output delivery failed')
     remaining()
     try:n=os.write(fd,raw[offset:])
     except (BlockingIOError,InterruptedError):
      selector.select(remaining());remaining();continue
     if n<=0:raise OutputFailure('Output delivery made no progress')
     offset+=n;remaining()
    if self.poisoned:raise OutputFailure('Concurrent output delivery failed')
  except BaseException:
   self.poisoned=True;raise
  finally:self.lock.release()

output_writer=OutputWriter()

def send(frame):
 raw=json.dumps(frame,separators=(',',':'),ensure_ascii=True).encode()
 if len(raw)>MAX_OUTPUT:raise Refused('Output bound')
 output_writer.write(raw+b'\n')

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


def handle_request(client,catalog,request,recovery,reconciliation):
 if not isinstance(request,dict):raise Refused('Frontend request object')
 kind=request.get('kind')
 if kind=='reconciliation-ready':
  reconciliation.proof_ready(request);return
 if kind in {'catalog-request','application-launch'}:
  send(catalog.handle(request));return
 if kind=='window-effect':
  exact(request,['protocolVersion','kind','effectProtocol','binding','intent'])
  if type(request['effectProtocol']) is not int or request['effectProtocol'] not in (1,2):raise Refused('Effect protocol')
 elif kind=='geometry-attach':
  exact(request,['protocolVersion','kind','geometryProtocol','binding','requestId'])
 elif kind=='geometry-facts-request':
  if request['geometryProtocol']!=client.geometry_protocol:raise Refused('Geometry negotiated version mismatch')
  exact(request,['protocolVersion','kind','geometryProtocol','binding','requestId','minimumWatermark'])
 elif kind=='projection-request':
  exact(request,['protocolVersion','kind','binding','requestId'])
 else:raise Refused('Unsupported frontend request')
 if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or binding(request['binding'])!=client.bound:raise Refused('Frontend scope mismatch')
 if kind.startswith('geometry-'):
  if type(request['geometryProtocol']) is not int or request['geometryProtocol'] not in (1,2):raise Refused('Geometry protocol')
 if kind=='window-effect':
  admitted=guarded(lambda:recovery.begin(client.bound,request['intent'],request['effectProtocol']))
  if not admitted:raise Refused('Duplicate durable intent; not resubmitted')
  outcome=client.geometry_effect(request['intent']) if request['effectProtocol']==2 else client.effect(request['intent'])
  after_submit(client,recovery,outcome)
  guarded(lambda:recovery.settle(outcome))
  for frame in guarded(lambda:recovery.settlement_frames(client.bound)):send(frame)
  send(outcome)
 elif kind=='geometry-attach':
  canonical(request['requestId']);send(client.geometry_attach(request['requestId'],request['geometryProtocol']))
 elif kind=='geometry-facts-request':
  if request['geometryProtocol']!=client.geometry_protocol:raise Refused('Geometry negotiated version mismatch')
  canonical(request['requestId']);canonical(request['minimumWatermark'],True)
  reconciliation.requested_read('geometry',request['requestId'])
  facts=client.geometry_facts(request['requestId'],request['minimumWatermark'])
  read_context=client.geometry_context(facts)
  send(facts)
  reconciliation.delivered_read('geometry',request['requestId'],read_context)
 else:
  canonical(request['requestId'])
  reconciliation.requested_read('action',request['requestId'])
  before=client.scene_facts(request['requestId']);snapshot=client.snapshot(request['requestId']);after=client.scene_facts(request['requestId'])
  scene=coherent_scene(before,snapshot,after)
  if scene is None:send({'protocolVersion':3,'kind':'projection-unavailable','binding':client.bound,'requestId':request['requestId'],'reason':'scene-changed'})
  else:
   read_context=client.context(after)
   send({'protocolVersion':3,'kind':'action-projection','binding':client.bound,'requestId':request['requestId'],'context':read_context,'scene':scene})
   reconciliation.delivered_read('action',request['requestId'],read_context)

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

def publish_startup(client,hello,recovery):
 # Complete every short-lock startup read before attached can trigger the C
 # host's nonblocking admission bind. Stage announcements without changing their
 # frontend order, then restore the live callback before any read can arrive.
 settlements=guarded(lambda:recovery.settlement_frames(client.bound))
 recovered=guarded(lambda:recovery.recovery_frames(client.bound))
 staged=[]
 reconciliation=Reconciliation(client,recovery.ledger,lambda frame:staged.append(frame))
 guarded(reconciliation.announce)
 reconciliation.send=send
 send(hello)
 for frame in settlements:send(frame)
 for frame in recovered[:1]:send(frame)
 for frame in staged:send(frame)
 send({'protocolVersion':3,'kind':'host-geometry-negotiate'})
 return reconciliation

def main():
 config=json.loads(Path(sys.argv[1]).read_text());roots=config.pop('catalogRoots',None);client=Endpoint(**config);catalog=CatalogTransport(client,roots)
 # Subscribe before initial projection; notifications may coalesce before a new
 # authoritative snapshot is requested, never after numbered publication.
 with event_socket(client) as events,selectors.DefaultSelector() as selector,ExitStack() as lifetime:
  hello=client.hello()
  recovery=lifetime.enter_context(guarded(lambda:Journal(config['runtime'],config['instance'],client.bound['lifetime'])))
  reconciliation=publish_startup(client,hello,recovery)
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
      handle_request(client,catalog,request,recovery,reconciliation)
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
  # A failed/partial output frame cannot carry a further safe diagnostic frame.
  # Durable settlement/Unknown recovery is independent of frontend delivery.
  if not output_writer.poisoned:
   try:
    if isinstance(error,RecoveryFailure):send({'protocolVersion':3,'kind':'host-recovery-failed','reason':error.reason})
    send({'protocolVersion':3,'kind':'host-disconnected'})
   except Exception:pass
  print('Backend failure locations: '+','.join(Path(frame.filename).name+':'+str(frame.lineno)+':'+frame.name for frame in traceback.extract_tb(error.__traceback__)),file=sys.stderr)
  print('Authority backend stopped: '+(str(error) if isinstance(error,Refused) else type(error).__name__),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(run())
