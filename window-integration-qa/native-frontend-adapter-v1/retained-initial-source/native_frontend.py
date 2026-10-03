#!/usr/bin/python3
"""Opt-in candidate product CLI: one identity-bound V12 request, no fallback.

The unmodified taskbar invokes this copied private hypr-windowctl candidate.
CLI success means a verified durable accepted receipt; it never means rendering
or completion. Native outcome is independently observed by the service/desktop.
Imports create no socket, process, actor or desktop input.
"""
from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,re,socket,stat,struct,sys,time,types

class Refused(RuntimeError):pass
class UnknownAcceptance(RuntimeError):pass

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def process(pid):
 p=Path('/proc')/str(pid)
 if p.stat().st_uid!=os.getuid():raise Refused('Selected process UID differs')
 s=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start':s[19],'parent':int(s[1]),'pgid':int(s[2])}
def live(identity):
 current=process(identity['pid'])
 if any(current[k]!=identity[k] for k in ('pid','start')):raise Refused('Selected process lifetime changed')
 return current

def regular(path,mode):
 p=Path(path);s=p.lstat()
 if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=mode:raise Refused('Owned exact-mode regular source required:'+str(p))
 return s

def private_directory(path):
 p=Path(path);s=p.lstat()
 if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o700 or p.resolve()!=p.absolute():raise Refused('Selected owned nonsymlink0700 directory required')
 return p

def read_config(path):
 regular(path,0o600);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 with os.fdopen(fd) as f:r=json.load(f)
 if not isinstance(r,dict) or r.get('version')!=1:raise Refused('Explicit candidate frontend configuration required')
 return r

def parse_cli(args):
 if len(args)!=4 or args[0] not in ('minimize','restore'):raise Refused('Explicit operation/address/stableID/PID required; no inferred active window')
 op,address,stable,pid=args
 if not re.fullmatch(r'0x[0-9a-f]+',address) or not re.fullmatch(r'[0-9a-f]+',stable) or not re.fullmatch(r'[1-9][0-9]*',pid):raise Refused('Canonical exact native identity required')
 return {'command':'request','operation':op,'address':address,'stableId':stable,'pid':int(pid)}

def read_compositor(config,command):
 peer=config['compositor'];live(peer);path=Path(config['compositorSocket']);before=path.lstat()
 if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid() or [before.st_dev,before.st_ino]!=config['compositorSocketIdentity']:raise Refused('Selected compositor socket changed')
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
  c.settimeout(2);c.connect(str(path));pid,uid,_=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  if pid!=peer['pid'] or uid!=os.getuid():raise Refused('Selected compositor actual peer differs')
  live(peer);c.sendall(command);reply=bytearray()
  while part:=c.recv(65536):
   reply.extend(part)
   if len(reply)>4*1024*1024:raise Refused('Compositor observation exceeds bound')
 after=path.lstat();live(peer)
 if [after.st_dev,after.st_ino]!=config['compositorSocketIdentity']:raise Refused('Selected compositor socket replaced during observation')
 return json.loads(reply)

def validate(config,request,entry):
 runtime=private_directory(config['runtime']);home=private_directory(config['selectors']['HOME'])
 if not home.is_relative_to(runtime) or any(os.environ.get(k)!=v for k,v in config['selectors'].items()):raise Refused('Selected frontend profile/environment differs')
 if any(os.environ.get(k) for k in ('AT_SPI_BUS_ADDRESS','WAYLAND_SOCKET','SESSION_MANAGER')):raise Refused('Foreign desktop handle refused')
 if Path(entry).resolve()!=Path(config['entry']).resolve() or digest(entry)!=config['entrySHA256']:raise Refused('Candidate actual entry source differs')
 regular(entry,0o700);identity=process(os.getpid());parent=process(identity['parent'])
 roots=[r for r in config['requestRoots'] if r['identity']['pid']==parent['pid']]
 if len(roots)!=1:raise Refused('Frontend invocation has no captured exact requester')
 root=roots[0];live(root['identity']);proc=Path('/proc')/str(parent['pid'])
 argv=[v.decode() for v in (proc/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
 if argv!=root['argv'] or str((proc/'exe').resolve())!=root['executable'] or digest(proc/'exe')!=root['executableSHA256']:raise Refused('Captured requester source/argv differs')
 if (proc/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise Refused('Requester scope differs')
 for path,row in config['delegateInputs'].items():
  if digest(path)!=row['sha256'] or stat.S_IMODE(Path(path).stat().st_mode)!=row['mode']:raise Refused('Exact V12 delegate input differs')
 windows=read_compositor(config,b'j/clients');matching=[r for r in windows if r.get('address')==request['address']]
 if len(matching)!=1 or any(matching[0].get(k)!=request[k] for k in ('address','stableId','pid')):raise Refused('Current mapped native identity differs')
 if not matching[0].get('mapped',True):raise Refused('Current native target unmapped')
 return {'frontend':identity,'requester':parent,'root':root['role'],'currentWindow':matching[0]}

class EofSocket:
 """Transport wrapper for unchanged V12 request_runtime: EOF precedes reply."""
 def __init__(self,*args,**kwargs):self.socket=socket.socket(*args,**kwargs);self.proof={};self.consumed=False;self.expected=None
 def __enter__(self):return self
 def __exit__(self,*args):self.socket.close()
 def settimeout(self,t):return self.socket.settimeout(t)
 def connect(self,p):
  result=self.socket.connect(p)
  if self.expected is not None:
   pid,uid,_=struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if pid!=self.expected['pid'] or uid!=os.getuid():raise Refused('Captured exact native service actual peer differs')
   live(self.expected);self.proof['actualPeer']={'pid':pid,'uid':uid,'start':self.expected['start']}
  return result
 def getsockopt(self,*a):return self.socket.getsockopt(*a)
 def sendall(self,data):self.proof['sendStarted']=True;return self.socket.sendall(data)
 def recv(self,size):
  if self.consumed:return b''
  data=bytearray()
  while True:
   part=self.socket.recv(min(8193-len(data),8193))
   if not part:break
   data.extend(part)
   if len(data)>8192:raise ValueError('Unbounded API reply')
  self.consumed=True
  if not data.endswith(b'\n') or data.count(b'\n')!=1:raise ValueError('Exactly one complete API frame and actual EOF required')
  self.proof.update(completeServerEOF=True,replySHA256=hashlib.sha256(data).hexdigest(),replyBytes=len(data))
  return bytes(data)

def delegate(config,request):
 peer=config['service'];live(peer);api=Path(config['serviceRoot'])/'api.sock';before=api.lstat()
 if [before.st_dev,before.st_ino]!=config['serviceSocketIdentity']:raise Refused('Captured exact native service socket changed')
 directory=Path(config['delegateDirectory']);sys.path.insert(0,str(directory))
 spec=importlib.util.spec_from_file_location('_candidate_native_runtime_delegate',directory/'native_runtime.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 sockets=[]
 def factory(*a,**k):value=EofSocket(*a,**k);value.expected=peer;sockets.append(value);return value
 # Only this isolated client module's socket reference changes. Real V12 request,
 # owner/process/peer/send logic remains delegated exactly once.
 module.socket=types.SimpleNamespace(**{k:getattr(socket,k) for k in ('AF_UNIX','SOCK_STREAM','SOL_SOCKET','SO_PEERCRED')},socket=factory)
 try:answer=module.request_runtime(config['serviceRoot'],config['session'],request,timeout=2)
 except module.UncertainAcceptance as e:raise UnknownAcceptance(str(e)) from e
 if len(sockets)!=1 or not sockets[0].proof.get('completeServerEOF'):raise UnknownAcceptance('Actual V12 response EOF proof absent')
 after=api.lstat();live(peer)
 if [after.st_dev,after.st_ino]!=config['serviceSocketIdentity']:raise UnknownAcceptance('Native service socket replaced after submission')
 if answer.get('ok') is False and answer.get('accepted') is False:raise Refused('Native service explicitly refused request')
 if answer.get('ok') is not True or answer.get('accepted') is not True or answer.get('completed') is not False or type(answer.get('receipt')) is not int or answer['receipt']<1:raise UnknownAcceptance('Submitted native service response has ambiguous acceptance')
 return answer,sockets[0].proof

def append(config,row):
 p=Path(config['log']);regular(p,0o600);fd=os.open(p,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC)
 with os.fdopen(fd,'a') as f:
  fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

def main(args=None):
 args=sys.argv[1:] if args is None else args;config=None;record={'timeNs':time.monotonic_ns(),'result':'refused','nativeCompletionClaimed':False}
 try:
  request=parse_cli(args);config=read_config(os.environ.get('WINDOW_MOTION_NATIVE_CONFIG',''));record['request']=request
  proof=validate(config,request,sys.argv[0]);record['authority']=proof
  answer,transport=delegate(config,request);record.update(result='accepted',answer=answer,transport=transport);append(config,record);print(json.dumps(answer));return 0
 except UnknownAcceptance as e:
  record.update(result='unknown-acceptance',error=str(e));code=75
 except Exception as e:record.update(error=str(e));code=125
 if config:
  try:append(config,record)
  except Exception as e:record['logError']=str(e)
 print(json.dumps(record),file=sys.stderr);return code
if __name__=='__main__':raise SystemExit(main())
