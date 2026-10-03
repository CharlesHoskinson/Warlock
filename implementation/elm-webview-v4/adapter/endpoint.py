"""Read-only authority endpoint bound to a supervisor-selected native process."""
import hashlib,json,os,re,socket,stat,struct,time
from pathlib import Path

class Refused(RuntimeError):pass

def start_time(pid):
 raw=Path('/proc',str(pid),'stat').read_text()
 return raw[raw.rfind(')')+2:].split()[19]

def canonical(value,zero=False):
 if not isinstance(value,str) or not re.fullmatch(r'0|[1-9][0-9]{0,19}',value) or int(value)>18446744073709551615 or (not zero and value=='0'):raise Refused('Noncanonical authority counter')
 return value

def exact(obj,fields):
 if not isinstance(obj,dict) or set(obj)!=set(fields):raise Refused('Unexpected protocol fields')

def binding(obj):
 exact(obj,['lifetime','session','frontend'])
 for value in obj.values():canonical(value)
 return obj

def unique(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise Refused('Duplicate JSON key')
  result[key]=value
 return result

class Endpoint:
 def __init__(self,runtime,instance,pid,expected_start,binary_sha256):
  self.runtime=Path(runtime);self.instance=instance;self.pid=pid;self.start=expected_start;self.binary_sha256=binary_sha256;self.bound=None
  if not re.fullmatch(r'[A-Za-z0-9_]+',instance) or not isinstance(pid,int) or pid<=0:raise Refused('Invalid supervisor target')
  if not self.runtime.is_absolute() or self.runtime.resolve()!=self.runtime:raise Refused('Runtime path is not canonical')
  self.path=self.runtime/'hypr'/instance/'.socket.sock'
  self.verify_paths();self.verify_process()
  # Hash through a held descriptor of the actual running executable, not PATH.
  with open('/proc/'+str(pid)+'/exe','rb') as stream:
   self.executable=os.fstat(stream.fileno());digest=hashlib.file_digest(stream,'sha256').hexdigest()
  if digest!=binary_sha256:raise Refused('Native executable hash mismatch')
  self.verify_process()
 def verify_process(self):
  try:
   info=os.stat('/proc/'+str(self.pid));current=start_time(self.pid)
   if info.st_uid!=os.getuid() or current!=self.start:raise Refused('Native process identity changed')
   if hasattr(self,'executable'):
    info=os.stat('/proc/'+str(self.pid)+'/exe')
    if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)!=(self.executable.st_dev,self.executable.st_ino,self.executable.st_size,self.executable.st_mtime_ns):raise Refused('Native executable identity changed')
  except OSError as error:raise Refused('Native process unavailable') from error
 def verify_paths(self):
  if self.runtime.resolve()!=self.runtime:raise Refused('Runtime ancestry changed')
  for path in [self.runtime,self.runtime/'hypr',self.path.parent]:
   info=path.lstat()
   if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o022:raise Refused('Unsafe endpoint directory')
  if stat.S_IMODE(self.runtime.stat().st_mode)!=0o700:raise Refused('Runtime must be private')
  info=self.path.lstat()
  if not stat.S_ISSOCK(info.st_mode) or info.st_uid!=os.getuid():raise Refused('Unsafe endpoint socket')
  return info.st_dev,info.st_ino,info.st_ctime_ns
 def request(self,payload):
  self.verify_process();before=self.verify_paths();deadline=time.monotonic()+3
  raw=('j/elm_observe '+json.dumps(payload,separators=(',',':'),ensure_ascii=True)).encode()
  if len(raw)>4096:raise Refused('Request bound')
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
   connection.settimeout(2);connection.connect(str(self.path))
   peer_pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if peer_pid!=self.pid or uid!=os.getuid():raise Refused('Endpoint peer mismatch')
   self.verify_process()
   if self.verify_paths()!=before:raise Refused('Socket replaced during connect')
   connection.sendall(raw);connection.shutdown(socket.SHUT_WR);reply=bytearray()
   while True:
    connection.settimeout(max(.001,min(2,deadline-time.monotonic())))
    chunk=connection.recv(65536)
    if not chunk:break
    reply.extend(chunk)
    if len(reply)>1048576 or time.monotonic()>deadline:raise Refused('Reply bound')
  self.verify_process()
  if self.verify_paths()!=before:raise Refused('Socket replaced during reply')
  response=json.loads(reply.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Refused('Nonfinite JSON')))
  if not isinstance(response,dict) or response.get('protocolVersion')!=3 or type(response.get('protocolVersion')) is not int:raise Refused('Protocol version')
  if response.get('kind')=='refused':raise Refused(response.get('reason','Native refusal'))
  return response
 def hello(self):
  response=self.request({'protocolVersion':3,'kind':'hello'})
  exact(response,['protocolVersion','kind','binding','compositor','capabilities'])
  if response['kind']!='attached':raise Refused('Handshake kind')
  compositor=response['compositor'];exact(compositor,['pid','instance','coreHash'])
  if compositor['pid']!=self.pid or compositor['instance']!=self.instance or not isinstance(compositor['coreHash'],str):raise Refused('Wrong native session')
  caps=response['capabilities'];exact(caps,['observe','effects','minimizedState'])
  if any(type(value) is not bool for value in caps.values()) or caps!={'observe':True,'effects':False,'minimizedState':False}:raise Refused('Unsupported capabilities')
  attached=binding(response['binding'])
  if self.bound and attached['lifetime']==self.bound['lifetime'] and attached['session']==self.bound['session'] and int(attached['frontend'])<=int(self.bound['frontend']):raise Refused('Frontend epoch did not advance')
  self.bound=attached;return response
 def snapshot(self,request_id,minimum_watermark='0'):
  if not self.bound:raise Refused('Handshake required')
  canonical(request_id);canonical(minimum_watermark,True)
  response=self.request({'protocolVersion':3,'kind':'snapshot-request','binding':self.bound,'requestId':request_id,'minimumWatermark':minimum_watermark})
  exact(response,['protocolVersion','kind','binding','requestId','sequence','revision','windows'])
  if response['kind']!='snapshot' or binding(response['binding'])!=self.bound or response['requestId']!=request_id:raise Refused('Uncorrelated snapshot')
  canonical(response['sequence'],True);canonical(response['revision'],True)
  if int(response['sequence'])<int(minimum_watermark):raise Refused('Obsolete snapshot')
  windows=response['windows']
  if not isinstance(windows,list) or len(windows)>256:raise Refused('Window bound')
  seen=set()
  for window in windows:
   exact(window,['incarnation','label','minimized']);identity=canonical(window['incarnation'])
   if identity in seen:raise Refused('Duplicate incarnation')
   seen.add(identity)
   label=window['label']
   if not isinstance(label,str) or len(label.encode('utf-16-le'))//2>256 or any(ord(c)<32 for c in label):raise Refused('Label bound')
   if window['minimized'] is not None:raise Refused('Unavailable minimize state was fabricated')
  return response
