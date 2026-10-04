"""One durable uncertain window intent; never an executable retry queue."""
import fcntl,json,os,secrets,stat
from pathlib import Path
from endpoint import Refused,binding,canonical,exact,unique

MAX_RECORD=4096

def validate(record):
 exact(record,['schema','binding','intent','status'])
 if type(record['schema']) is not int or record['schema']!=1:raise Refused('Recovery schema')
 binding(record['binding']);intent=record['intent']
 exact(intent,['request','generation','incarnation','operation','context'])
 for key in ['request','generation','incarnation']:canonical(intent[key])
 exact(intent['context'],['lifetime','epoch','output','revision'])
 for value in intent['context'].values():canonical(value)
 if intent['context']['lifetime']!=record['binding']['lifetime'] or intent['context']['epoch']!=record['binding']['frontend']:raise Refused('Recovery context')
 if intent['operation'] not in ['minimize','restore','activate'] or record['status'] not in ['Pending','Committed','Refused','Unknown']:raise Refused('Recovery outcome')
 return record

class Journal:
 def __init__(self,runtime):
  runtime=Path(runtime)
  if not runtime.is_absolute() or runtime.resolve()!=runtime:raise Refused('Recovery runtime')
  info=runtime.lstat()
  if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:raise Refused('Recovery runtime ownership')
  root=runtime/'elm-window-recovery'
  try:root.mkdir(mode=0o700)
  except FileExistsError:pass
  self.fd=os.open(root,os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  info=os.fstat(self.fd)
  if info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:os.close(self.fd);raise Refused('Recovery directory ownership')
  self.lock=None
  try:
   self.lock=os.open('writer.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
   self.verify(self.lock);fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BaseException:self.close();raise
 def verify(self,fd):
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:raise Refused('Recovery file ownership')
 def read(self):
  try:fd=os.open('intent.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
  except FileNotFoundError:return None
  try:
   self.verify(fd);raw=os.read(fd,MAX_RECORD+1)
   if len(raw)>MAX_RECORD:raise Refused('Recovery capacity')
   return validate(json.loads(raw,object_pairs_hook=unique))
  finally:os.close(fd)
 def write(self,record):
  raw=json.dumps(validate(record),separators=(',',':'),ensure_ascii=True).encode()
  if len(raw)>MAX_RECORD:raise Refused('Recovery capacity')
  name='pending-'+secrets.token_hex(12)
  fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
  try:
   offset=0
   while offset<len(raw):offset+=os.write(fd,raw[offset:])
   os.fsync(fd)
   os.replace(name,'intent.json',src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)
  finally:
   os.close(fd)
   try:os.unlink(name,dir_fd=self.fd)
   except FileNotFoundError:pass
 def begin(self,bound,intent):
  self.write({'schema':1,'binding':bound,'intent':intent,'status':'Pending'})
 def settle(self,outcome):
  record=self.read()
  if record is None or record['binding']!=outcome['binding'] or record['intent']!=outcome['intent'] or record['status']!='Pending':raise Refused('Recovery receipt correlation')
  self.write(dict(record,status=outcome['status']))
 def uncertain(self,bound):
  record=self.read()
  if record is None:return None
  if record['binding']['lifetime']!=bound['lifetime']:raise Refused('Recovery compositor lifetime')
  if record['status'] not in ['Pending','Unknown']:return None
  return {'protocolVersion':3,'kind':'host-uncertain','binding':bound,'intent':record['intent']}
 def close(self):
  if self.lock is not None:os.close(self.lock);self.lock=None
  if self.fd is not None:os.close(self.fd);self.fd=None
 def __enter__(self):return self
 def __exit__(self,*_):self.close()
