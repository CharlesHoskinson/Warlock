"""QA-only actual activation process supervisor; no native acceptance."""
import ctypes, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope, verify_runtime

def identity(pid):
 p=Path('/proc')/str(pid);st=p.stat();raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
 if st.st_uid!=os.getuid():raise RuntimeError('foreign process UID')
 return {'pid':pid,'start':fields[19],'pgid':int(fields[2]),'ppid':int(fields[1]),'uid':st.st_uid}

def live(row):
 try:return all(identity(row['pid'])[k]==row[k] for k in ('pid','start','pgid','uid'))
 except (OSError,ValueError):return False

def main():
 require_qa_scope();runtime=verify_runtime(Path(os.environ['XDG_RUNTIME_DIR']))
 if len(sys.argv)!=3:raise RuntimeError('descriptor and journal required')
 descriptor=Path(sys.argv[1]);journal=Path(sys.argv[2])
 if descriptor.is_symlink() or not descriptor.resolve().is_relative_to(runtime) or descriptor.stat().st_uid!=os.getuid():raise RuntimeError('private descriptor ownership')
 data=json.loads(descriptor.read_text());argv=data['argv'];binary=Path(argv[0])
 if set(data)!={'argv','binarySHA256'} or not isinstance(argv,list) or not argv or any(type(x)!=str or '\0' in x for x in argv):raise RuntimeError('closed activation descriptor')
 if not binary.is_absolute() or hashlib.sha256(binary.read_bytes()).hexdigest()!=data['binarySHA256']:raise RuntimeError('actual Exec binary pin')
 if os.getpgrp()!=os.getpid():os.setsid()
 libc=ctypes.CDLL(None,use_errno=True)
 if libc.prctl(36,1,0,0,0)!=0:raise OSError(ctypes.get_errno(),'PR_SET_CHILD_SUBREAPER')
 stop=[False];signal.signal(signal.SIGTERM,lambda *_:stop.__setitem__(0,True));signal.signal(signal.SIGINT,lambda *_:stop.__setitem__(0,True))
 if journal.is_dir():journal=journal/(str(os.getpid())+'-'+str(time.time_ns())+'.jsonl')
 seq=0
 with journal.open('x',encoding='utf-8') as log:
  def emit(kind,**fields):
   nonlocal seq
   seq+=1;log.write(json.dumps({'sequence':seq,'kind':kind,'monotonic':time.monotonic(),**fields})+'\n');log.flush()
  own=identity(os.getpid());emit('supervisor-start',identity=own,argv=argv)
  child=subprocess.Popen(argv,stdin=subprocess.DEVNULL);known={};statuses={};shutdown=None;kill=False
  def discover():
   # Group membership alone is insufficient: authenticate parent chain first.
   allrows={}
   for p in Path('/proc').glob('[0-9]*'):
    try:
     row=identity(int(p.name))
     if row['pgid']==own['pid']:allrows[row['pid']]=row
    except (OSError,ValueError,RuntimeError):continue
   parents={own['pid'],*known}
   for _ in range(len(allrows)+1):
    found=[r for p,r in allrows.items() if p!=own['pid'] and p not in known and r['ppid'] in parents]
    if not found:break
    for r in found:known[r['pid']]=r;parents.add(r['pid']);emit('owned-child',identity=r)
  def reap():
   while True:
    try:pid,status=os.waitpid(-1,os.WNOHANG)
    except ChildProcessError:return
    if pid==0:return
    if pid not in known:emit('unobserved-child-exit',pid=pid,status=status);raise RuntimeError('child exited before identity observation')
    code=os.waitstatus_to_exitcode(status);statuses[pid]=code;emit('child-exit',identity=known[pid],waitStatus=status,exitCode=code)
    if pid==child.pid:child.returncode=code
  discover()
  while True:
   discover();reap()
   active=[r for p,r in known.items() if p not in statuses and live(r)]
   if child.pid in statuses and not active:break
   if stop[0] and shutdown is None:
    shutdown=time.monotonic();emit('shutdown-request')
    for r in active:
     if live(r):os.kill(r['pid'],signal.SIGTERM);emit('signal',identity=r,signal=signal.SIGTERM)
   if shutdown is not None:
    # Newly discovered activation descendants must also terminate; never signal foreign groups.
    if time.monotonic()-shutdown>.5 and not kill:
     kill=True
     for r in active:
      if live(r):os.kill(r['pid'],signal.SIGKILL);emit('signal',identity=r,signal=signal.SIGKILL)
    if time.monotonic()-shutdown>2.5:raise RuntimeError('original bounded activation drain expired')
   time.sleep(.01)
  emit('terminal',childExitCode=statuses[child.pid],cancelled=shutdown is not None,fallback=kill,allWaitStatuses=statuses,liveDescendants=[])
  return 0 if statuses[child.pid]==0 and shutdown is None else 2
if __name__=='__main__':sys.exit(main())
