"""Deterministic owned CPU process/stat FD disappearance; no synthetic errno."""
from pathlib import Path
import os,select,subprocess
from unittest.mock import patch

def observe(module,function='still_live'):
 child=subprocess.Popen(['/usr/bin/python3','-IS','-c','import os;os.read(0,1);os._exit(0)'],stdin=subprocess.PIPE)
 fd=None;result=None;failure=None;observations={}
 try:
  identity=module.process(child.pid);fd=os.pidfd_open(child.pid);stat_path=Path('/proc')/str(child.pid)/'stat';real=Path.open
  observations.update(identity=identity,ownedUID=stat_path.stat().st_uid)
  def opened(path,*args,**kwargs):
   stream=real(path,*args,**kwargs)
   if path==stat_path:
    # The actual descriptor exists while the captured process is alive. Its
    # next read happens after actual normal exit and exact pidfd exit proof.
    before=os.fstat(stream.fileno());observations['openFDIdentity']=[before.st_dev,before.st_ino,before.st_uid,before.st_mode]
    child.stdin.write(b'G');child.stdin.flush();child.wait(timeout=3)
    poll=select.poll();poll.register(fd,select.POLLIN);events=poll.poll(0)
    observations.update(actualChildExit=child.returncode,pidfdExitObserved=bool(events),procPathGone=not stat_path.exists())
   return stream
  with patch.object(Path,'open',opened):
   try:result=getattr(module,function)(identity if function=='still_live' else child.pid)
   except Exception as error:failure=dict(type=type(error).__name__,errno=getattr(error,'errno',None),message=str(error))
  return dict(result=result,error=failure,**observations)
 finally:
  if child.poll() is None:
   try:child.stdin.write(b'G');child.stdin.flush()
   except BrokenPipeError:pass
  child.wait(timeout=3);child.stdin.close()
  if fd is not None:os.close(fd)
