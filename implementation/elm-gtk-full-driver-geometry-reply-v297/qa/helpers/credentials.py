"""Bounded actual proc credentials; real UID is ownership, effective UID is metadata."""
import os,signal
from pathlib import Path
FIELDS={'pid','start','pgid','ppid','uid','realUid','effectiveUid','savedUid','filesystemUid','procOwnerUid','privilegedCredentials'}
def bounded_text(path):
 with open(path,'rb') as stream:raw=stream.read(8193)
 if len(raw)>8192:raise RuntimeError('bounded proc identity')
 return raw.decode('ascii','strict')
def metadata(pid):
 row={'pid':pid,'procOwnerUid':None,'stat':None,'status':None,'error':None,'exe':None,'exeError':None}
 try:
  p=Path('/proc')/str(pid);row['procOwnerUid']=p.stat().st_uid;row['stat']=bounded_text(p/'stat');row['status']=bounded_text(p/'status')
 except (OSError,ValueError,RuntimeError) as error:row['error']=repr(error)
 try:
  row['exe']=os.readlink(Path('/proc')/str(pid)/'exe')
  if len(row['exe'])>4096:row['exe']=None;row['exeError']='bounded executable link'
 except OSError as error:row['exeError']=repr(error)
 return row
def identity(pid):
 if type(pid)!=int or not 0<pid<=2147483647:raise RuntimeError('canonical proc PID')
 m=metadata(pid)
 if m['error'] is not None:raise RuntimeError('proc identity unavailable: '+m['error'])
 raw=m['stat'];fields=raw[raw.rfind(')')+2:].split()
 if int(raw.split(' ',1)[0])!=pid or len(fields)<20:raise RuntimeError('exact proc stat PID')
 uidlines=[line for line in m['status'].splitlines() if line.startswith('Uid:')]
 if len(uidlines)!=1:raise RuntimeError('one proc credential tuple')
 values=uidlines[0].split()[1:]
 if len(values)!=4 or any(not x.isascii() or not x.isdecimal() or len(x)>10 for x in values):raise RuntimeError('canonical proc credential tuple')
 uids=list(map(int,values))
 if any(x>4294967295 for x in uids) or uids[0]!=os.getuid():raise RuntimeError('foreign real UID')
 start=fields[19]
 if not start.isascii() or not start.isdecimal() or start.startswith('0') or len(start)>20:raise RuntimeError('canonical proc start')
 return {'pid':pid,'start':start,'pgid':int(fields[2]),'ppid':int(fields[1]),'uid':uids[0],'realUid':uids[0],'effectiveUid':uids[1],'savedUid':uids[2],'filesystemUid':uids[3],'procOwnerUid':m['procOwnerUid'],'privilegedCredentials':any(x!=os.getuid() for x in uids[1:])}
def signalable(original,current):
 return all(current[k]==original[k] for k in ('pid','start','uid')) and all(current[k]==os.getuid() and original.get(k)==os.getuid() for k in ('realUid','effectiveUid','savedUid','filesystemUid'))

class PrivilegedSignalRefused(RuntimeError):
 def __init__(self,current):super().__init__("privileged credentials cannot be signalled");self.current=current

def signal_exact(original,signum):
 if signum not in (signal.SIGTERM,signal.SIGKILL):raise RuntimeError('closed owned signal')
 fd=os.pidfd_open(original['pid'],0)
 try:
  current=identity(original['pid'])
  if any(current[k]!=original[k] for k in ('pid','start','uid')):raise RuntimeError('replaced child cannot be signalled')
  if not signalable(original,current):raise PrivilegedSignalRefused(current)
  signal.pidfd_send_signal(fd,signum,None,0)
  return current
 finally:os.close(fd)
