"""Exclusive durable fixture publication and literal source verification."""
from pathlib import Path
import hashlib,json,os,stat

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(exact(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b
def strict(raw):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('Duplicate JSON field')
   out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def directory(path):
 p=Path(path);s=p.lstat()
 if not p.is_absolute()or p.resolve()!=p or not stat.S_ISDIR(s.st_mode)or s.st_uid!=os.getuid()or stat.S_IMODE(s.st_mode)!=0o700:raise ValueError('Canonical owned0700 directory required')
 return p
def publish(path,raw,mode=0o600):
 p=Path(path);directory(p.parent)
 if type(raw)is not bytes or mode not in (0o600,0o700):raise ValueError('Exact bytes/private mode required')
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
 try:
  view=memoryview(raw)
  while view:
   n=os.write(fd,view)
   if n<=0:raise OSError('Full publication failed')
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)
 return sha(p)
def publish_json(path,value):return publish(path,(json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def verify(packet):
 if type(packet)is not dict or type(packet.get('inputs'))is not dict or type(packet.get('inputModes'))is not dict or type(packet.get('symlinks'))is not dict:raise ValueError('Exact source inventory required')
 for name,h in packet['inputs'].items():
  p=Path(name);s=p.stat()
  # Named aliases are admitted only with their separately frozen literal links.
  if type(h)is not str or type(packet['inputModes'].get(name))is not int or not stat.S_ISREG(s.st_mode)or sha(p)!=h or stat.S_IMODE(s.st_mode)!=packet['inputModes'][name]:raise ValueError('Frozen bytes/mode changed: '+name)
 for name,target in packet['symlinks'].items():
  if type(target)is not str or not Path(name).is_symlink()or os.readlink(name)!=target:raise ValueError('Frozen literal link changed: '+name)
 for name,mode in packet.get('directoryModes',{}).items():
  p=Path(name)
  if type(mode)is not int or p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise ValueError('Frozen directory mode changed: '+name)
 return packet
