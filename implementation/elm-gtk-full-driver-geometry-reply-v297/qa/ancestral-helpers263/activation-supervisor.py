"""QA-only real activation supervisor. All exits are actual waitpid statuses."""
import ctypes,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime

def identity(pid):
 p=Path('/proc')/str(pid);st=p.stat();raw=(p/'stat').read_text();f=raw[raw.rfind(')')+2:].split()
 if st.st_uid!=os.getuid():raise RuntimeError('foreign UID')
 return {'pid':pid,'start':f[19],'pgid':int(f[2]),'ppid':int(f[1]),'uid':st.st_uid}

def live(row):
 try:
  actual=identity(row['pid']);return all(actual[k]==row[k] for k in ('pid','start','uid'))
 except (OSError,ValueError):return False

def main():
 require_qa_scope();runtime=verify_runtime(Path(os.environ['XDG_RUNTIME_DIR']))
 if len(sys.argv)!=3:raise RuntimeError('descriptor/journal required')
 descriptor=Path(sys.argv[1]);journal=Path(sys.argv[2])
 if descriptor!=descriptor.resolve() or descriptor.is_symlink() or not descriptor.resolve().is_relative_to(runtime) or descriptor.stat().st_uid!=os.getuid():raise RuntimeError('private descriptor ownership')
 data=json.loads(descriptor.read_text())
 if type(data)!=dict or set(data)!={'argv','binarySHA256'}:raise RuntimeError('closed descriptor')
 argv=data['argv']
 if type(argv)!=list or not argv or any(type(x)!=str or '\0' in x for x in argv):raise RuntimeError('closed argv')
 binary=Path(argv[0])
 if not binary.is_absolute() or hashlib.sha256(binary.read_bytes()).hexdigest()!=data['binarySHA256']:raise RuntimeError('actual Exec binary pin')
 # Journal directory must be explicitly created owned0700; never follow a symlink.
 if journal.is_dir():
  if journal.is_symlink() or journal.stat().st_uid!=os.getuid() or journal.stat().st_mode&0o777!=0o700:raise RuntimeError('journal directory ownership')
  journal=journal/(str(os.getpid())+'-'+str(time.time_ns())+'.jsonl')
 if journal.parent!=journal.parent.resolve() or journal.exists() or journal.is_symlink() or journal.parent.is_symlink() or journal.parent.stat().st_uid!=os.getuid():raise RuntimeError('exclusive owned journal path')
 if os.getpgrp()!=os.getpid():os.setsid()
 if ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)!=0:raise RuntimeError('subreaper required')
 stop=[False];signal.signal(signal.SIGTERM,lambda *_:stop.__setitem__(0,True));signal.signal(signal.SIGINT,lambda *_:stop.__setitem__(0,True));seq=0
 fd=os.open(journal,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w',encoding='utf-8') as log:
  def emit(kind,**fields):
   nonlocal seq
   seq+=1;log.write(json.dumps({'sequence':seq,'kind':kind,'monotonic':time.monotonic(),**fields})+'\n');log.flush()
  own=identity(os.getpid());emit('supervisor-start',identity=own,argv=argv,descriptor=str(descriptor),descriptorSHA256=hashlib.sha256(descriptor.read_bytes()).hexdigest())
  child=None;known={};statuses={};sent={};shutdown=None;failure=None
  def key(row):return (row['pid'],row['start'])
  def discover():
   allrows={}
   for p in Path('/proc').glob('[0-9]*'):
    try:r=identity(int(p.name));allrows[r['pid']]=r
    except (OSError,ValueError,RuntimeError):continue
   parents={own['pid']}|{r['pid'] for k,r in known.items() if k not in statuses and live(r)}
   for _ in range(len(allrows)+1):
    added=[]
    for r in allrows.values():
     if r['pid']!=own['pid'] and key(r) not in known and r['ppid'] in parents:added.append(r)
    if not added:break
    for r in added:
     known[key(r)]=r;parents.add(r['pid']);emit('owned-child',identity=r)
  def reap():
   while True:
    try:pid,status=os.waitpid(-1,os.WNOHANG)
    except ChildProcessError:return
    if pid==0:return
    matches=[k for k in known if k[0]==pid and k not in statuses]
    if len(matches)!=1:emit('unobserved-child-exit',pid=pid,status=status);raise RuntimeError('missing unique PID/start before reap')
    k=matches[0];code=os.waitstatus_to_exitcode(status);statuses[k]=code;emit('child-exit',identity=known[k],waitStatus=status,exitCode=code)
    if child is not None and pid==child.pid:child.returncode=code
  def signal_active(now):
   for k,r in known.items():
    if k in statuses or not live(r):continue
    previous=sent.get(k,0);desired=signal.SIGKILL if now-shutdown>.5 else signal.SIGTERM
    if previous==desired or previous==signal.SIGKILL:continue
    try:os.kill(r['pid'],desired)
    except ProcessLookupError:continue
    sent[k]=desired;emit('signal',identity=r,signal=desired)
  try:
   child=subprocess.Popen(argv,stdin=subprocess.DEVNULL);r=identity(child.pid);known[key(r)]=r;emit('owned-child',identity=r);childkey=key(r)
   while True:
    discover();reap();active=[k for k,r in known.items() if k not in statuses and live(r)]
    if childkey in statuses and not active:break
    if stop[0] and shutdown is None:shutdown=time.monotonic();emit('shutdown-request')
    if shutdown is not None:
     signal_active(time.monotonic())
     if time.monotonic()-shutdown>2.5:raise RuntimeError('bounded activation drain expired')
    time.sleep(.01)
  except BaseException as error:
   failure=repr(error);emit('supervisor-failure',error=failure);shutdown=time.monotonic() if shutdown is None else shutdown
   # Preserve failure, still reclaim the actually owned tree inside the same drain cap.
   while time.monotonic()-shutdown<2.5:
    discover();signal_active(time.monotonic())
    try:reap()
    except RuntimeError:pass
    if all(k in statuses or not live(r) for k,r in known.items()):break
    time.sleep(.01)
  remaining=[r for k,r in known.items() if k not in statuses and live(r)]
  emit('terminal',childExitCode=None if child is None else child.returncode,cancelled=shutdown is not None,fallback=signal.SIGKILL in sent.values(),allWaitStatuses=[{'identity':known[k],'exitCode':v} for k,v in statuses.items()],liveDescendants=remaining,error=failure)
  return 0 if failure is None and child is not None and child.returncode==0 and shutdown is None and not remaining else 2
if __name__=='__main__':sys.exit(main())
