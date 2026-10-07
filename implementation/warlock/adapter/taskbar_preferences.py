"""Identity-only pin order; native-selected private storage, CAS and atomic save."""
import fcntl,json,os,secrets,stat
from pathlib import Path
from endpoint import Refused,exact,canonical,unique

MAX_REVISION=(1<<64)-1

def identities(values):
 if not isinstance(values,list) or len(values)>32 or any(not isinstance(s,str) or not s or len(s)>256 or any(ord(c)<32 or ord(c)==127 for c in s) for s in values) or len(set(values))!=len(values):raise Refused('Pin identities')
 if len(json.dumps(values,ensure_ascii=False,separators=(',',':')).encode())>3000:raise Refused('Pin byte bound')
 return values

def snapshot(value):
 exact(value,['revision','identities']);canonical(value['revision']);identities(value['identities']);return value

class Store:
 def __init__(self,state_home=None):
  base=Path(state_home or os.environ.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))
  if not base.is_absolute():raise Refused('State root must be absolute')
  self.path=base/'warlock'
 def _private(self,fd,directory=False):
  s=os.fstat(fd)
  if s.st_uid!=os.getuid() or s.st_mode&0o077 or (not stat.S_ISDIR(s.st_mode) if directory else not stat.S_ISREG(s.st_mode)) or (not directory and s.st_nlink!=1):raise Refused('Unsafe pin storage')
 def _open(self):
  self.path.mkdir(mode=0o700,parents=True,exist_ok=True)
  directory=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   self._private(directory,True)
   lock=os.open('taskbar.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600,dir_fd=directory)
   try:self._private(lock);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BaseException:os.close(lock);raise
   return directory,lock
  except BaseException:os.close(directory);raise
 def _read(self,directory):
  try:fd=os.open('taskbar.json',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
  except FileNotFoundError:return {'revision':'1','identities':[]}
  try:
   self._private(fd);body=os.read(fd,16385)
   if len(body)>16384:raise Refused('Pin storage bound')
   value=json.loads(body,object_pairs_hook=unique);exact(value,['schema','revision','identities'])
   if type(value['schema']) is not int or value['schema']!=1:raise Refused('Pin schema')
   return snapshot({k:value[k] for k in ['revision','identities']})
  finally:os.close(fd)
 def read(self):
  directory,lock=self._open()
  try:return self._read(directory)
  finally:os.close(lock);os.close(directory)
 def save(self,proposal):
  snapshot(proposal);directory,lock=self._open();temporary=None;renamed=False
  try:
   old=self._read(directory)
   if old['revision']!=proposal['revision']:return 'Refused',old
   if old['identities']==proposal['identities']:return 'Refused',old
   if int(old['revision'])==MAX_REVISION:return 'Refused',old
   value={'schema':1,'revision':str(int(old['revision'])+1),'identities':proposal['identities']}
   body=json.dumps(value,separators=(',',':'),ensure_ascii=False).encode()
   temporary='taskbar.'+secrets.token_hex(12)+'.tmp'
   fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
   try:
    with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
   except BaseException:raise
   os.rename(temporary,'taskbar.json',src_dir_fd=directory,dst_dir_fd=directory);renamed=True;temporary=None;os.fsync(directory)
   return 'Saved',{k:value[k] for k in ['revision','identities']}
  except (OSError,ValueError):
   if renamed:return 'Unknown',None
   raise
  finally:
   if temporary:
    try:os.unlink(temporary,dir_fd=directory)
    except FileNotFoundError:pass
   os.close(lock);os.close(directory)
