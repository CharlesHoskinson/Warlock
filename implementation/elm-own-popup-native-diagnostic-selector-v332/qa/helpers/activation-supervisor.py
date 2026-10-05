"""QA-only real activation supervisor. All exits are actual waitpid statuses."""
import ctypes,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime

from credentials import identity,metadata,signalable,signal_exact,PrivilegedSignalRefused

def live(row):
 try:
  actual=identity(row['pid']);return all(actual[k]==row[k] for k in ('pid','start','uid'))
 except (OSError,ValueError,RuntimeError):return False

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
  child=None;known={};statuses={};sent={};refused_signals=set();signal_errors=set();shutdown=None;failure=None
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
    try:pending=os.waitid(os.P_ALL,0,os.WEXITED|os.WNOHANG|os.WNOWAIT)
    except ChildProcessError:return
    if pending is None:return
    # WNOWAIT retains the zombie and its exact /proc start before destructive reap.
    try:row=identity(pending.si_pid)
    except (OSError,ValueError,RuntimeError) as error:
     emit('pending-identity-failure',pendingPid=pending.si_pid,pendingUid=pending.si_uid,waitidCode=pending.si_code,waitidStatus=pending.si_status,metadata=metadata(pending.si_pid),error=repr(error));raise
    if row['pid']!=pending.si_pid:raise RuntimeError('pending exact PID identity')
    if pending.si_uid!=row['uid']:raise RuntimeError('pending waitid UID correlation')
    if row['ppid']!=own['pid']:raise RuntimeError('pending exit is not direct owned kernel child')
    k=key(row)
    prior=[old for old in known if old[0]==pending.si_pid and old not in statuses]
    if prior and prior!=[k]:raise RuntimeError('pending child PID/start changed')
    if k not in known:
     known[k]=row;emit('owned-child',identity=row)
     emit('kernel-child-acquired',identity=row,waitidCode=pending.si_code,waitidStatus=pending.si_status)
    if k in statuses:raise RuntimeError('duplicate exact pending child exit')
    pid,status=os.waitpid(pending.si_pid,os.WNOHANG)
    if pid!=pending.si_pid:raise RuntimeError('exact pending waitpid correlation')
    code=os.waitstatus_to_exitcode(status)
    expected=pending.si_status if pending.si_code==os.CLD_EXITED else -pending.si_status if pending.si_code in (os.CLD_KILLED,os.CLD_DUMPED) else None
    statuses[k]=code;emit('child-exit',identity=known[k],observedIdentity=row,waitStatus=status,exitCode=code)
    if child is not None and pid==child.pid:child.returncode=code
    if code!=expected:raise RuntimeError('waitid versus waitpid actual status correlation')
  def signal_active(now):
   errors=[]
   for k,r in known.items():
    if k in statuses or not live(r):continue
    previous=sent.get(k,0);desired=signal.SIGKILL if now-shutdown>.5 else signal.SIGTERM
    if previous==desired or previous==signal.SIGKILL:continue
    try:current=signal_exact(r,desired)
    except ProcessLookupError:continue
    except PrivilegedSignalRefused as error:
     stamp=(k,desired,tuple(error.current[x] for x in ('realUid','effectiveUid','savedUid','filesystemUid')))
     if stamp not in refused_signals:
      refused_signals.add(stamp);emit('signal-identity-refused',identity=r,observedIdentity=error.current,signal=desired,metadata=metadata(r['pid']))
     continue
    except (OSError,ValueError,RuntimeError) as error:
     detail=repr(error);stamp=(k,desired,detail)
     if stamp not in signal_errors:
      signal_errors.add(stamp);emit('signal-identity-error',identity=r,signal=desired,metadata=metadata(r['pid']),error=detail[:4096])
     errors.append(detail);continue
    sent[k]=desired;emit('signal',identity=r,observedIdentity=current,signal=desired)
   if errors:raise RuntimeError('owned signal errors: '+ '; '.join(errors)[:4096])
  try:
   child=subprocess.Popen(argv,stdin=subprocess.DEVNULL);r=identity(child.pid);known[key(r)]=r;emit('owned-child',identity=r);childkey=key(r)
   while True:
    discover();reap();discover()
    # Reaping a parent may adopt a still-live descendant after the first scan.
    children=Path('/proc/self/task/'+str(os.getpid())+'/children').read_text().split()
    for text in children:
     row=identity(int(text));k=key(row)
     if row['ppid']!=own['pid']:raise RuntimeError('kernel child ownership changed')
     if k not in known:known[k]=row;emit('owned-child',identity=row)
    active=[k for k,r in known.items() if k not in statuses and live(r)]
    if childkey in statuses and not active and not children:break
    if stop[0] and shutdown is None:shutdown=time.monotonic();emit('shutdown-request')
    if shutdown is not None:
     signal_active(time.monotonic())
     if time.monotonic()-shutdown>2.5:raise RuntimeError('bounded activation drain expired')
    time.sleep(.01)
  except BaseException as error:
   failure=repr(error);emit('supervisor-failure',error=failure);shutdown=time.monotonic() if shutdown is None else shutdown
   # Preserve failure, still reclaim the actually owned tree inside the same drain cap.
   while time.monotonic()-shutdown<2.5:
    for phase,fn in [('discover',discover),('signal',lambda:signal_active(time.monotonic())),('reap',reap)]:
     try:fn()
     except BaseException as drain_error:
      detail=phase+': '+repr(drain_error)
      if detail!=failure:
       emit('supervisor-failure',error=detail[:4096]);failure=detail[:4096]
    if all(k in statuses or not live(r) for k,r in known.items()):break
    time.sleep(.01)
  remaining=[r for k,r in known.items() if k not in statuses and live(r)]
  emit('terminal',childExitCode=None if child is None else child.returncode,cancelled=shutdown is not None,fallback=signal.SIGKILL in sent.values(),allWaitStatuses=[{'identity':known[k],'exitCode':v} for k,v in statuses.items()],liveDescendants=remaining,error=failure)
  return 0 if failure is None and child is not None and child.returncode==0 and shutdown is None and not remaining else 2
if __name__=='__main__':sys.exit(main())
