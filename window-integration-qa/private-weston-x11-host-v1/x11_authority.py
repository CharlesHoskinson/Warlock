"""Strict private Xwayland authentication; importing this module starts nothing."""
from pathlib import Path
import hashlib,json,os,re,resource,socket,stat,struct,sys,time
QA=Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope,verify_runtime
NAME=b'MIT-MAGIC-COOKIE-1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def private_file(path,mode=0o600):
 p=Path(path);s=p.lstat()
 if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=mode:raise RuntimeError('private file owner/type/mode mismatch')
 return {'path':str(p),'uid':s.st_uid,'device':s.st_dev,'inode':s.st_ino,'mode':stat.S_IMODE(s.st_mode)}
def process(pid):
 p=Path('/proc')/str(pid);s=p.stat()
 if s.st_uid!=os.getuid():raise RuntimeError('process UID mismatch')
 raw=(p/'stat').read_text();parts=raw[raw.rfind(')')+2:].split()
 return {'pid':pid,'start':parts[19],'ppid':int(parts[1]),'pgid':int(parts[2])}
def argv(pid):return [p.decode() for p in (Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0') if p]
def environment(pid):return dict(item.decode().split('=',1) for item in (Path('/proc')/str(pid)/'environ').read_bytes().split(b'\0') if b'=' in item)
def parse_args(args):
 if len(args)!=11 or not re.fullmatch(r':(?:[0-9]|[12][0-9]|3[0-2])',args[0]) or args[1:3]!=['-rootless','-core'] or args[3::2]!=['-listenfd','-listenfd','-displayfd','-wm']:raise RuntimeError('unexpected upstream Xwayland argv')
 fds=[int(v) for v in args[4::2] if re.fullmatch(r'[0-9]+',v)]
 if len(fds)!=4 or min(fds)<3 or len(set(fds))!=4:raise RuntimeError('invalid or reused inherited descriptors')
 return args[0],fds

def authority_bytes(display,cookie):
 if not re.fullmatch(r':[0-9]+',display) or len(cookie)!=16:raise ValueError('invalid authority data')
 # FamilyWild is limited to this private file and this exact display number.
 fields=(b'',display[1:].encode(),NAME,cookie)
 return struct.pack('>H',65535)+b''.join(struct.pack('>H',len(v))+v for v in fields)
def decode_authority(raw):
 family,=struct.unpack('>H',raw[:2]);offset=2;fields=[]
 for _ in range(4):
  n,=struct.unpack('>H',raw[offset:offset+2]);offset+=2;fields.append(raw[offset:offset+n]);offset+=n
  if len(fields[-1])!=n:raise ValueError('truncated authority')
 if offset!=len(raw) or family!=65535 or fields[0] or fields[2]!=NAME or len(fields[3])!=16:raise ValueError('invalid authority record')
 return ':'+fields[1].decode(),fields[3]
def setup_request(cookie=None):
 name=NAME if cookie is not None else b'';data=cookie if cookie is not None else b''
 if cookie is not None and len(cookie)!=16:raise ValueError('invalid cookie')
 return b'l\0'+struct.pack('<HHHHH',11,0,len(name),len(data),0)+name+b'\0'*((-len(name))%4)+data+b'\0'*((-len(data))%4)
def setup_reply(connection):
 def exact(n):
  data=bytearray()
  while len(data)<n:
   part=connection.recv(n-len(data))
   if not part:raise RuntimeError('truncated X11 setup reply')
   data.extend(part)
  return bytes(data)
 header=exact(8);status=header[0];major,minor,units=struct.unpack('<HHH',header[2:])
 if units>16384:raise RuntimeError('oversize X11 setup reply')
 body=exact(units*4)
 if status not in (0,1,2):raise RuntimeError('unknown setup status')
 return {'status':status,'major':major,'minor':minor,'bytes':8+len(body),'sha256':hashlib.sha256(header+body).hexdigest()}
def socket_identity(path):
 p=Path(path);parent=p.parent.lstat()
 if p.parent!=Path('/tmp/.X11-unix') or not stat.S_ISDIR(parent.st_mode) or parent.st_uid not in (0,os.getuid()):raise RuntimeError('X listener directory authority mismatch')
 s=p.lstat()
 if not stat.S_ISSOCK(s.st_mode) or s.st_uid!=os.getuid():raise RuntimeError('X listener owner/type mismatch')
 return {'path':str(p),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid}
def socket_kernel_inode(path):
 matches=[]
 for line in Path('/proc/net/unix').read_text().splitlines()[1:]:
  fields=line.split()
  if len(fields)==8 and fields[-1]==str(path) and fields[3]=='00010000':matches.append(fields[6])
 if len(matches)!=1:raise RuntimeError('ambiguous or nonlistening X socket')
 return matches[0]
def has_fd(pid,inode):
 for p in (Path('/proc')/str(pid)/'fd').iterdir():
  try:
   if os.readlink(p)=='socket:['+inode+']':return True
  except OSError:pass
 return False

def launcher():
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Xwayland must inherit core1')
 runtime=verify_runtime(Path(os.environ['XDG_RUNTIME_DIR']));control=runtime/'x11-control.json';private_file(control)
 row=json.loads(control.read_text());config=runtime/'hyprland.lua';private_file(config)
 if sha(config)!=row['configSHA256']:raise RuntimeError('private compositor config changed')
 private_file(runtime/'bin/Xwayland',0o700)
 if sha(runtime/'bin/Xwayland')!=row['launcherSHA256']:raise RuntimeError('private PATH launcher changed')
 display,fds=parse_args(sys.argv[1:]);parent=process(os.getppid());pargs=argv(parent['pid'])
 if Path('/proc/'+str(parent['pid'])+'/exe').resolve()!=Path('/usr/bin/Hyprland') or pargs!=['/usr/bin/Hyprland','--config',str(config)]:raise RuntimeError('Xwayland requires exact private Hyprland parent')
 if parent['pid']!=parent['pgid']:raise RuntimeError('private compositor must lead own group')
 penv=environment(parent['pid'])
 if penv.get('XDG_RUNTIME_DIR')!=str(runtime) or penv.get('WQA_X11_CONFIG')!=str(config) or penv.get('PATH')!=str(runtime/'bin')+':/usr/bin:/bin':raise RuntimeError('private compositor environment mismatch')
 if os.environ.get('DISPLAY')!=display or display==row.get('mainDisplay') or os.environ.get('XAUTHORITY'):raise RuntimeError('display/authority routing mismatch')
 if os.environ.get('WQA_X11_CONFIG')!=str(config):raise RuntimeError('wrong private launch contract')
 for fd in fds[:2]:
  if os.readlink('/proc/self/fd/'+str(fd))!=os.readlink('/proc/'+str(parent['pid'])+'/fd/'+str(fd)):raise RuntimeError('descriptor not inherited from captured parent')
 for fd in (fds[0],fds[1],fds[3],int(os.environ['WAYLAND_SOCKET'])):
  if not stat.S_ISSOCK(os.fstat(fd).st_mode):raise RuntimeError('required inherited Unix socket missing')
 for fd in (fds[3],int(os.environ['WAYLAND_SOCKET'])):
  with socket.socket(fileno=os.dup(fd)) as endpoint:
   pid,uid,gid=struct.unpack('3i',endpoint.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if pid!=parent['pid'] or uid!=os.getuid():raise RuntimeError('socketpair creator is not captured parent')
 if not stat.S_ISFIFO(os.fstat(fds[2]).st_mode):raise RuntimeError('display readiness pipe missing')
 secret=runtime/'x11-cookie';private_file(secret);cookie=secret.read_bytes()
 auth=runtime/'x11-authority';descriptor=os.open(auth,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(descriptor,'wb') as stream:stream.write(authority_bytes(display,cookie))
 record={'server':process(os.getpid()),'parent':parent,'display':display,'upstreamArgs':sys.argv[1:],'actualExecutable':'/usr/bin/Xwayland','authority':private_file(auth),'authorityFlag':True,'coreLimit':[1,1]}
 destination=runtime/'x11-launch.json';fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(record,stream)
 env=dict(os.environ);env['XAUTHORITY']=str(auth);env.pop('WQA_X11_CONFIG',None)
 os.execve('/usr/bin/Xwayland',['/usr/bin/Xwayland',*sys.argv[1:],'-auth',str(auth)],env)

if __name__=='__main__':launcher()
