"""QA observation-only remaining-budget derivative; no effect path or retries."""
import json,os,socket,struct,time
from endpoint import Refused,ValidatedNativeRefusal,exact,unique
from geometry_endpoint import GeometryEndpoint
class ObserverEndpoint(GeometryEndpoint):
 parentDeadline=float('inf')
 def request(self,payload):
  deadline=min(time.monotonic()+3,self.parentDeadline)
  def remaining():
   left=deadline-time.monotonic()
   if left<=0:raise Refused('Absolute transport deadline')
   return min(2,left)
  self.verify_process();before=self.verify_paths()
  raw=('j/elm_observe '+json.dumps(payload,separators=(',',':'),ensure_ascii=True)).encode()
  if len(raw)>4096:raise Refused('Request bound')
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
   connection.settimeout(remaining());connection.connect(str(self.path));remaining()
   peer_pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if peer_pid!=self.pid or uid!=os.getuid():raise Refused('Endpoint peer mismatch')
   self.verify_process()
   if self.verify_paths()!=before:raise Refused('Socket replaced during connect')
   connection.settimeout(remaining());connection.sendall(raw);remaining()
   connection.settimeout(remaining());connection.shutdown(socket.SHUT_WR);remaining();reply=bytearray()
   while True:
    connection.settimeout(remaining());chunk=connection.recv(65536);remaining()
    if not chunk:break
    reply.extend(chunk)
    if len(reply)>1048576:raise Refused('Reply bound')
  self.verify_process()
  if self.verify_paths()!=before:raise Refused('Socket replaced during reply')
  remaining()
  response=json.loads(reply.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Refused('Nonfinite JSON')))
  remaining()
  if not isinstance(response,dict) or response.get('protocolVersion')!=3 or type(response.get('protocolVersion')) is not int:raise Refused('Protocol version')
  if response.get('kind')=='refused':
   exact(response,['protocolVersion','kind','reason'])
   reason=response['reason']
   if not isinstance(reason,str):raise Refused('Native refusal reason type')
   try:units=len(reason.encode('utf-16-le'))//2
   except UnicodeEncodeError:raise Refused('Native refusal reason Unicode')
   if not reason or units>256 or any(ord(c)<32 or 127<=ord(c)<=159 for c in reason):raise Refused('Native refusal reason bound')
   raise ValidatedNativeRefusal(reason)
  return response
