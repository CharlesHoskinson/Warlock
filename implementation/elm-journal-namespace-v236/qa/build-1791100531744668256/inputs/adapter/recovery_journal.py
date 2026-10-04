"""One durable uncertain window intent; never an executable retry queue."""
import fcntl,json,os,secrets,stat,re,hashlib
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
 @staticmethod
 def namespace_path(runtime,instance,lifetime):
  if not isinstance(instance,str) or not re.fullmatch(r'[A-Za-z0-9_]{1,255}',instance):raise Refused('Recovery instance')
  canonical(lifetime)
  return Path(runtime)/'elm-window-recovery'/instance/lifetime
 def __init__(self,runtime,instance,lifetime):
  runtime=Path(runtime);self.path=self.namespace_path(runtime,instance,lifetime);self.target={'instance':instance,'lifetime':lifetime}
  self.fd=None;self.lock=None;self.legacy=None
  if not runtime.is_absolute() or runtime.resolve()!=runtime:raise Refused('Recovery runtime')
  info=runtime.lstat()
  if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:raise Refused('Recovery runtime ownership')
  def child(parent,name):
   try:os.mkdir(name,mode=0o700,dir_fd=parent)
   except FileExistsError:pass
   fd=os.open(name,os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);info=os.fstat(fd)
   if info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:os.close(fd);raise Refused('Recovery directory ownership')
   return fd
  root=os.open(runtime,os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   self.legacy=child(root,'elm-window-recovery');scope=child(self.legacy,instance)
   try:self.fd=child(scope,lifetime)
   finally:os.close(scope)
   self.lock=os.open('writer.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
   self.verify(self.lock);fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   self.migrate()
  except BaseException:self.close();raise
  finally:os.close(root)
 def raw(self,directory,name,limit):
  try:fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
  except FileNotFoundError:return None
  try:
   self.verify(fd);raw=os.read(fd,limit+1)
   if len(raw)>limit:raise Refused('Recovery capacity')
   return raw
  finally:os.close(fd)
 def atomic(self,name,raw):
  if len(raw)>16384:raise Refused('Recovery metadata capacity')
  temporary='pending-'+secrets.token_hex(12)
  fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
  try:
   offset=0
   while offset<len(raw):offset+=os.write(fd,raw[offset:])
   os.fsync(fd);os.replace(temporary,name,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)
  finally:
   os.close(fd)
   try:os.unlink(temporary,dir_fd=self.fd)
   except FileNotFoundError:pass
 def plan_valid(self,plan):
  exact(plan,['schema','target','records','sourceHashes'])
  if type(plan['schema']) is not int or plan['schema']!=1 or plan['target']!=self.target:raise Refused('Recovery migration target')
  exact(plan['records'],['host-intent.json','intent.json']);exact(plan['sourceHashes'],['host-intent.json','intent.json'])
  for name,record in plan['records'].items():
   digest=plan['sourceHashes'][name]
   if digest is not None and (not isinstance(digest,str) or not re.fullmatch(r'[0-9a-f]{64}',digest)):raise Refused('Recovery migration hash')
   if record is not None:
    validate(record)
    if record['binding']['lifetime']!=self.target['lifetime'] or (name=='host-intent.json' and record['status']!='Pending'):raise Refused('Recovery migration scope')
  return plan
 def migrate(self):
  encode=lambda value:json.dumps(value,separators=(',',':'),ensure_ascii=True).encode()
  plan_raw=self.raw(self.fd,'migration-plan.json',16384)
  if plan_raw is None:
   locks=[]
   try:
    # Both old writers must quiesce before a stable legacy snapshot is taken.
    for name in ['writer.lock','host-writer.lock']:
     fd=os.open(name,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.legacy);locks.append(fd);self.verify(fd);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    records={};hashes={}
    for name in ['host-intent.json','intent.json']:
     raw=self.raw(self.legacy,name,4096);hashes[name]=hashlib.sha256(raw).hexdigest() if raw is not None else None
     record=validate(json.loads(raw,object_pairs_hook=unique)) if raw is not None else None
     if record is not None and name=='host-intent.json' and record['status']!='Pending':raise Refused('Legacy host admission status')
     records[name]=record if record is not None and record['binding']['lifetime']==self.target['lifetime'] else None
    plan={'schema':1,'target':self.target,'records':records,'sourceHashes':hashes}
    self.plan_valid(plan);plan_raw=encode(plan);self.atomic('migration-plan.json',plan_raw)
   finally:
    for fd in locks:os.close(fd)
  plan=self.plan_valid(json.loads(plan_raw,object_pairs_hook=unique))
  marker_raw=self.raw(self.fd,'migration.json',4096);digest=hashlib.sha256(plan_raw).hexdigest()
  expected={'schema':1,'target':self.target,'planSHA256':digest,'complete':True}
  if marker_raw is not None:
   marker=json.loads(marker_raw,object_pairs_hook=unique)
   if marker!=expected:raise Refused('Recovery migration marker')
   return
  # No attached frame/effects precede completion. Interrupted copies are restored
  # from the durable plan rather than taking a second mutable legacy snapshot.
  for name,record in plan['records'].items():
   if record is not None:self.atomic(name,encode(record))
  self.atomic('migration.json',encode(expected))
 def verify(self,fd):
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:raise Refused('Recovery file ownership')
 def read(self,name='intent.json'):
  if name not in ['intent.json','host-intent.json']:raise Refused('Recovery filename')
  raw=self.raw(self.fd,name,4096)
  if raw is None:return None
  record=validate(json.loads(raw,object_pairs_hook=unique))
  if record['binding']['lifetime']!=self.target['lifetime']:raise Refused('Recovery namespace lifetime')
  if name=='host-intent.json' and record['status']!='Pending':raise Refused('Host admission status')
  return record
 def write(self,record):
  raw=json.dumps(validate(record),separators=(',',':'),ensure_ascii=True).encode()
  if record['binding']['lifetime']!=self.target['lifetime'] or len(raw)>4096:raise Refused('Recovery write scope')
  self.atomic('intent.json',raw)
 def begin(self,bound,intent):
  self.write({'schema':1,'binding':bound,'intent':intent,'status':'Pending'})
 def settle(self,outcome):
  record=self.read()
  if record is None or record['binding']!=outcome['binding'] or record['intent']!=outcome['intent'] or record['status']!='Pending':raise Refused('Recovery receipt correlation')
  self.write(dict(record,status=outcome['status']))
 def uncertain(self,bound):
  admitted=self.read('host-intent.json');settled=self.read()
  # The host's latest admitted intent precedes broker submission. Only its exact
  # correlated durable settlement can supersede Pending; never borrow an older
  # receipt or replay the admission record as a command.
  record=admitted or settled
  if admitted is not None and settled is not None and admitted['binding']==settled['binding'] and admitted['intent']==settled['intent']:
   record=settled
  if record is None:return None
  if record['binding']['lifetime']!=bound['lifetime']:raise Refused('Recovery compositor lifetime')
  if record['status'] not in ['Pending','Unknown']:return None
  return {'protocolVersion':3,'kind':'host-uncertain','binding':bound,'intent':record['intent']}
 def close(self):
  if self.lock is not None:os.close(self.lock);self.lock=None
  if self.fd is not None:os.close(self.fd);self.fd=None
  if self.legacy is not None:os.close(self.legacy);self.legacy=None
 def __enter__(self):return self
 def __exit__(self,*_):self.close()
