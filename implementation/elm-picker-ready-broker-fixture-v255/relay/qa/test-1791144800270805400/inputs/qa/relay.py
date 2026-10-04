"""Private QA broker EOF relay; no synthesized protocol frames or effect replay."""
import array,errno,fcntl,hashlib,json,os,selectors,stat,subprocess,sys,time
from pathlib import Path
MAX=4096
class RelayFailure(RuntimeError):pass
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def start(pid):
 try:
  p=Path('/proc')/str(pid)
  if p.stat().st_uid!=os.getuid():return None
  return (p/'stat').read_text().rsplit(')',1)[1].split()[19]
 except (OSError,IndexError):return None
def unique(items):
 d={}
 for k,v in items:
  if k in d:raise RelayFailure('Duplicate control field')
  d[k]=v
 return d
def decode(b):
 if len(b)>MAX:raise RelayFailure('Control capacity')
 return json.loads(b,object_pairs_hook=unique)
def exact(d,keys):
 if type(d) is not dict or set(d)!=set(keys):raise RelayFailure('Exact control schema')
def directory(path):
 p=Path(path);s=p.lstat()
 if not p.is_absolute() or p.resolve(strict=True)!=p or not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o700:raise RelayFailure('Private canonical control directory')
 return p
def read_private(path):
 p=Path(path)
 if not p.is_absolute() or p.resolve(strict=True)!=p:raise RelayFailure('Canonical private file')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600:raise RelayFailure('Private single-link file')
  return decode(os.read(fd,MAX+1))
 finally:os.close(fd)
def write_all(fd,data):
 while data:
  try:n=os.write(fd,data)
  except InterruptedError:continue
  if n<=0:raise RelayFailure('Zero write')
  data=data[n:]
def actor_status(control_directory):
 p=directory(control_directory);marker=read_private(p/'actor.json');exact(marker,['relay','child']);return marker
def exit_status(control_directory):
 p=directory(control_directory);d=read_private(p/'exit.json');exact(d,['relay','child','childExit','stdinClosed']);return d
def close_stdin(control_directory):
 p=directory(control_directory);marker=read_private(p/'actor.json');exact(marker,['relay','child'])
 for actor in marker.values():
  exact(actor,['pid','start'])
  if type(actor['pid']) is not int or actor['pid']<=0 or type(actor['start']) is not str or start(actor['pid'])!=actor['start']:raise RelayFailure('Control actor not live')
 fd=os.open(p/'gate.json',os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600:raise RelayFailure('Private gate')
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);d=decode(os.read(fd,MAX+1))
  if d!={'action':'forward'}:raise RelayFailure('Gate already used')
  raw=json.dumps({'action':'close',**marker}).encode();os.lseek(fd,0,0);os.ftruncate(fd,0);write_all(fd,raw);os.fsync(fd)
 finally:os.close(fd)
 return marker

def pump(command,control_directory):
 p=directory(control_directory)
 gate=os.open(p/'gate.json',os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 write_all(gate,b'{"action":"forward"}');os.fsync(gate);gate_id=os.fstat(gate)
 child=None;closing=False;deadline=None;buffer=bytearray();outgoing=bytearray();output_eof=False;closed=False;remaining=None
 try:
  child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=None,close_fds=True)
  marker={'relay':{'pid':os.getpid(),'start':start(os.getpid())},'child':{'pid':child.pid,'start':start(child.pid)}}
  assert all(r['start'] for r in marker.values())
  fd=os.open(p/'actor.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
  try:write_all(fd,json.dumps(marker).encode());os.fsync(fd)
  finally:os.close(fd)
  os.set_blocking(child.stdin.fileno(),False);os.set_blocking(0,False);os.set_blocking(1,False)
  if not stat.S_ISFIFO(os.fstat(0).st_mode) or not stat.S_ISFIFO(os.fstat(1).st_mode):raise RelayFailure('Relay requires owned pipe transport')
  with selectors.DefaultSelector() as selector:
   selector.register(0,selectors.EVENT_READ,'input');selector.register(child.stdout,selectors.EVENT_READ,'output')
   while True:
    try:fcntl.flock(gate,fcntl.LOCK_SH|fcntl.LOCK_NB);locked=True
    except BlockingIOError:locked=False
    d=None
    try:
     current=(p/'gate.json').lstat()
     if (current.st_dev,current.st_ino)!=(gate_id.st_dev,gate_id.st_ino) or current.st_nlink!=1 or stat.S_IMODE(current.st_mode)!=0o600:raise RelayFailure('Gate replaced')
     if locked:os.lseek(gate,0,0);d=decode(os.read(gate,MAX+1))
    finally:
     if locked:fcntl.flock(gate,fcntl.LOCK_UN)
    if d is not None and d!={'action':'forward'}:
     if d!={'action':'close',**marker} or (not closed and start(child.pid)!=marker['child']['start']):raise RelayFailure('Control scope mismatch')
     if not closing:
      closing=True;deadline=time.monotonic()+3
      # Snapshot the bytes already accepted by the parent pipe at this cut.
      pending=array.array('i',[0]);fcntl.ioctl(0,0x541B,pending,True);remaining=pending[0]
      if not 0<=remaining<=fcntl.fcntl(0,fcntl.F_GETPIPE_SZ):raise RelayFailure('Pipe backlog bound')
    if deadline is not None and time.monotonic()>=deadline:raise RelayFailure('Broker EOF deadline')
    if buffer and not closed:
     try:n=os.write(child.stdin.fileno(),buffer)
     except (BlockingIOError,InterruptedError):n=0
     if n:del buffer[:n]
    if outgoing:
     try:n=os.write(1,outgoing)
     except (BlockingIOError,InterruptedError):n=0
     if n:del outgoing[:n]
    if closing and remaining==0 and not buffer and not closed:child.stdin.close();closed=True
    if child.poll() is not None and output_eof and not outgoing:
     if deadline is not None and time.monotonic()>=deadline:raise RelayFailure('Broker EOF deadline')
     if child.returncode!=0:raise RelayFailure('Broker did not exit normally')
     exit_record={'relay':marker['relay'],'child':marker['child'],'childExit':0,'stdinClosed':closed}
     fd=os.open(p/'exit.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
     try:write_all(fd,json.dumps(exit_record).encode());os.fsync(fd)
     finally:os.close(fd)
     return marker
    if deadline is not None and time.monotonic()>=deadline:raise RelayFailure('Broker EOF deadline')
    # Pause full queues instead of spinning on ready-but-unread pipes.
    for fd,tag,wanted in [(0,'input',not closed and len(buffer)<=MAX and (not closing or remaining!=0)),(child.stdout,'output',not output_eof and len(outgoing)<=MAX)]:
     try:selector.get_key(fd);registered=True
     except KeyError:registered=False
     if wanted and not registered:selector.register(fd,selectors.EVENT_READ,tag)
     elif not wanted and registered:selector.unregister(fd)
    for key,_ in selector.select(.02):
     if key.data=='output':
      data=os.read(child.stdout.fileno(),MAX)
      if data:outgoing.extend(data);assert len(outgoing)<=MAX*2
      else:output_eof=True;selector.unregister(child.stdout)
     elif len(buffer)<=MAX and (not closing or remaining!=0):
      try:data=os.read(0,min(MAX,remaining) if closing else MAX)
      except BlockingIOError:continue
      if data:
       buffer.extend(data);assert len(buffer)<=MAX*2
       if closing:remaining-=len(data)
      else:
       if closing and remaining:raise RelayFailure('Parent backlog disappeared')
       closing=True;remaining=0;deadline=time.monotonic()+3;selector.unregister(0)
 finally:
  os.close(gate)
  if child is not None:
   if sys.exc_info()[0] is not None and child.poll() is None:child.terminate()
   if child.stdin and not child.stdin.closed:child.stdin.close()
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:
    child.terminate()
    try:child.wait(timeout=3)
    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
   child.stdout.close()

BROKER_MANIFEST='9678ba49758ba4fd7688d1c0faed2a1fafef4b91e62be3d7dad23e830fb25b5a'
RECEIPT_MANIFEST='dd1edd57bff4fd2102ce59cf12294bafb6f7b54e334341a93514134a9d1d3063'
def verify_receipt(root):
 manifest=root/'qa/held-source-manifest.json'
 if sha(manifest)!=RECEIPT_MANIFEST:raise RelayFailure('Receipt inventory changed')
 packet=json.loads(manifest.read_text())
 if packet.get('sourceHeld') is not True or packet.get('evidenceIntegrityPassed') is not True:raise RelayFailure('Receipt source not held')
 for rel,e in packet['files'].items():
  path=root/rel
  if Path(rel).is_absolute() or '..' in Path(rel).parts:raise RelayFailure('Receipt inventory path')
  if 'symlink' in e:
   if not path.is_symlink() or os.readlink(path)!=e['symlink']:raise RelayFailure('Receipt symlink changed')
  else:
   if path.is_symlink() or not path.is_file():raise RelayFailure('Receipt regular source changed')
   st=path.stat()
   if st.st_size!=e['size'] or stat.S_IMODE(st.st_mode)!=e['mode'] or sha(path)!=e['sha256']:raise RelayFailure('Receipt captured source changed')
 return root/'qa/broker-entrypoint.py'
def command_for(cfg,repo):
 if type(cfg) is not dict or cfg.get('profile') not in ('broker','receipt'):raise RelayFailure('Closed relay profile')
 profile=cfg['profile'];field='authorityConfig' if profile=='broker' else 'receiptConfig'
 exact(cfg,['profile',field,'controlDirectory','runtime','instance'])
 if type(cfg[field]) is not str or type(cfg['controlDirectory']) is not str:raise RelayFailure('Config path types')
 directory(cfg['controlDirectory']);source=Path(cfg[field]);payload=read_private(source)
 authority=payload if profile=='broker' else read_private(payload['authorityConfig'])
 if type(cfg['runtime']) is not str or type(cfg['instance']) is not str or authority.get('runtime')!=cfg['runtime'] or authority.get('instance')!=cfg['instance']:raise RelayFailure('Host/broker authority identity mismatch')
 directory(cfg['runtime'])
 import re
 if re.fullmatch(r'[A-Za-z0-9_]{1,255}',cfg['instance']) is None:raise RelayFailure('Authority instance syntax')
 if profile=='receipt':
  entry=verify_receipt(repo/'implementation/elm-picker-ready-broker-fixture-v255/receipt')
  # A fresh fixed interpreter parses the private receipt config through the
  # held entrypoint itself; there is no import into this relay process.
  return ['/usr/bin/python3','-B',str(entry),str(source)]
 root=repo/'implementation/elm-picker-ready-broker-fixture-v255/receipt'
 verify_receipt(root)
 sys.path.insert(0,str(root/'qa'))
 from wrapper import verified_backend_root
 backend=verified_backend_root()/'daemon.py'
 return ['/usr/bin/python3','-B',str(backend),str(source)]

def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa')
 from qa_launch import require_qa_scope
 require_qa_scope()
 if len(sys.argv)!=2:raise RelayFailure('One private relay config required')
 cfg=read_private(sys.argv[1]);repo=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
 command=command_for(cfg,repo);pump(command,cfg['controlDirectory'])
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as error:print('QA relay stopped: '+str(error),file=sys.stderr);raise SystemExit(1)
