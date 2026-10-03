"""Authenticated keeper's durable actor history; no operation on import.

The keeper embeds this exact source in its sealed executable. It calls
observe_registration at the still-closed gate and retains original source rows.
This primitive grants no desktop authority and never signals a group.
"""
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MAX_JOBS=512
MAX_LEDGER_BYTES=8*1024*1024
ENV_NAMES=('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')
# Exact inherited, reviewed gate and confinement sources. The Keeper embeds
# this verifier in its own sealed source; arbitrary confined code is refused.
HANDOFF_SHA256='1163ab4a469fae45d51a8d1f2b58d5198de77c22721f0dd45ac1b751b7ea4be6'
POLICY_SHA256='6605947351bc1f986737dafefbd9faaceed7229a8f4152b5fcdf00a0cb0437c3'

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def positive(value):
 if type(value) is not int or value<1:raise ValueError('positive typed identity required')
 return value

def nonce(value):
 if type(value) is not str or re.fullmatch('[0-9a-f]{32}',value) is None:raise ValueError('exact bounded nonce required')
 return value

def sha256(value):
 if type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None:raise ValueError('exact digest required')
 return value

def process_record(pid):
 raw=Path(f'/proc/{positive(pid)}/stat').read_text();head,tail=raw.rsplit(') ',1);f=tail.split()
 if head.split(' ',1)[0]!=str(pid) or len(f)<20:raise ValueError('complete single process record required')
 return {'start':positive(int(f[19])),'state':f[0],'group':int(f[2]),'session':int(f[3])}

def material(path,*,sealed):
 fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_mode&0o022 or a.st_size>128*1024*1024:raise ValueError('regular immutable bounded job material required')
  h=hashlib.sha256();offset=0
  while data:=os.pread(fd,1048576,offset):h.update(data);offset+=len(data)
  b=os.fstat(fd)
  if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns) or offset!=a.st_size:raise ValueError('job material changed during observation')
  seals=fcntl.fcntl(fd,fcntl.F_GET_SEALS) if sealed else None
  required=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
  if sealed and seals&required!=required:raise ValueError('complete job material seals required')
  return {'device':a.st_dev,'inode':a.st_ino,'size':a.st_size,'sha256':h.hexdigest(),'seals':seals}
 finally:os.close(fd)

def checked_intent(value):
 if not isinstance(value,dict) or set(value)!={'actor','receipt','token','captured','scope','lease'}:raise ValueError('complete exact cancellation intent required')
 positive(value['actor']);positive(value['receipt'])
 if type(value['token']) is not str or re.fullmatch('[0-9a-f]{12}-[1-9][0-9]{0,14}',value['token']) is None:raise ValueError('exact current producer token required')
 def identity(v):
  if not isinstance(v,list) or len(v)!=3 or type(v[0]) is not str or re.fullmatch('0x[0-9a-f]{1,16}',v[0]) is None or type(v[1]) is not str or re.fullmatch('[0-9a-f]{1,16}',v[1]) is None:raise ValueError('exact captured member identity required')
  positive(v[2]);return tuple(v)
 captured=identity(value['captured']);scope=value['scope']
 if not isinstance(scope,list) or not 1<=len(scope)<=256:raise ValueError('complete bounded member scope required')
 ids=[identity(v) for v in scope]
 if len(set(ids))!=len(ids) or captured not in ids or ids!=sorted(ids):raise ValueError('canonical distinct exact captured scope required')
 lease=value['lease']
 if not isinstance(lease,dict) or set(lease)!={'pid','start','nonce','rootIdentity','lockIdentity','session'}:raise ValueError('exact current lease required')
 positive(lease['pid']);positive(lease['start']);nonce(lease['nonce'])
 for k in ('rootIdentity','lockIdentity'):
  a=lease[k]
  if not isinstance(a,list) or len(a)!=2 or any(type(v) is not int or v<0 for v in a) or a[1]<1:raise ValueError('exact typed lease inode required')
 if type(lease['session']) is not str or not lease['session'] or len(lease['session'])>256:raise ValueError('exact selected lease session required')
 return deepcopy(value)

def observe_registration(ownership,kind,actor,environment):
 if kind not in ('helper','renderer','native-effect','native-export','cpu-test') or actor is not None and (type(actor) is not int or actor<1):raise ValueError('exact job role/actor required')
 if not isinstance(ownership,dict):raise ValueError('complete source ownership required')
 pid=positive(ownership.get('pid'));start=positive(ownership.get('start'))
 if ownership.get('uid')!=os.getuid() or type(ownership.get('uid')) is not int or ownership.get('environment')!=environment:raise ValueError('exact job UID/selected session required')
 before=process_record(pid)
 if before['start']!=start or before['group']!=pid or before['session']!=pid:raise ValueError('exact job lifetime/group/session differs')
 for k in ('scriptFD','producerFD'):
  if type(ownership.get(k)) is not int or ownership[k]<0:raise ValueError('typed selected source descriptors required')
 for k,where,sealed in [('launcher',f'/proc/{pid}/exe',False),('script',f"/proc/{pid}/fd/{ownership['scriptFD']}",True),('producer',f"/proc/{pid}/fd/{ownership['producerFD']}",True)]:
  if digest(material(where,sealed=sealed))!=digest(ownership.get(k)):raise ValueError('actual job '+k+' source differs')
 argv=ownership.get('argv')
 if not isinstance(argv,list) or any(type(v) is not str for v in argv) or Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]!=[v.encode() for v in argv]:raise ValueError('actual gated job argv differs')
 if ownership['script']['sha256']!=HANDOFF_SHA256 or ownership.get('policySHA256')!=POLICY_SHA256 or ownership.get('policy')!='linux-x86_64-group-confinement-v1':raise ValueError('exact reviewed handoff and confinement source required')
 target=ownership.get('targetArgv');mode=ownership.get('mode')
 if not isinstance(target,list) or not target or any(type(v) is not str for v in target) or len(argv)!=8 or argv[1]!=f"/proc/self/fd/{ownership['scriptFD']}" or argv[4]!=str(ownership['producerFD']) or digest(json.loads(argv[5]))!=digest(target) or argv[6]!=mode or mode not in ('elf','python','bash'):raise ValueError('actual reviewed handoff target argument/descriptor binding differs')
 required_role=None
 if len(target)>2 and target[1]=='repl' and any(value in target[2] for value in ('window_atlas(', 'window_snapshot(')):required_role='native-export'
 elif len(target)>1 and (target[1] in ('minimize','restore','dispatch') or target[1]=='repl' and 'retire_gesture_current' in target[2]):required_role='native-effect'
 if required_role is not None and kind!=required_role:raise ValueError('actual effect/export argument cannot borrow a nonnative job role')
 raw=Path(f'/proc/{pid}/environ').read_bytes();env=dict(p.split(b'=',1) for p in raw.split(b'\0') if b'=' in p)
 if any(env.get(k.encode())!=v.encode() for k,v in environment.items()):raise ValueError('actual job environment differs')
 status=dict(line.split(':',1) for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line)
 if status.get('NoNewPrivs','').strip()!='1' or status.get('Seccomp','').strip()!='2' or any(int(v)!=os.getuid() for v in status['Uid'].split()):raise ValueError('actual job confinement/UID differs')
 after=process_record(pid)
 if any(after[k]!=before[k] for k in ('start','group','session')):raise ValueError('job lifetime/group/session changed at registration')
 return digest(ownership)

class ActorLedger:
 def __init__(self,issuer,persist):
  self.issuer=deepcopy(issuer);self.persist=persist;self.jobs={};self.freezes={};self.revisions={};self.fault=False
 def snapshot(self):return {'version':1,'issuer':deepcopy(self.issuer),'jobs':deepcopy(self.jobs),'freezes':deepcopy(self.freezes),'revisions':deepcopy(self.revisions),'fault':self.fault}
 def ready(self):
  if self.fault:raise ValueError('actor ledger durability failed; quarantined')
 def commit(self,job=None,actor=None):
  if actor is not None:self.revisions[str(actor)]=self.revisions.get(str(actor),0)+1
  try:self.persist(self.snapshot())
  except BaseException:self.fault=True;raise
 def register(self,job,kind,actor,ownership):
  self.ready();nonce(job)
  if job in self.jobs or len(self.jobs)>=MAX_JOBS:raise ValueError('complete nontruncated bounded ledger cannot register job')
  if actor is not None and str(actor) in self.freezes:raise ValueError('frozen actor cannot register a new job')
  self.jobs[job]={'job':job,'kind':kind,'actor':actor,'pid':ownership['pid'],'start':ownership['start'],'sourceSHA256':digest(ownership),'ownership':deepcopy(ownership),'phase':'gated','returned':None,'uncertain':False}
  self.commit(job,actor);return self.projection(job)
 def projection(self,job):return {k:deepcopy(v) for k,v in self.jobs[job].items() if k!='ownership'}
 def rows(self,actor):return [self.projection(k) for k in sorted(self.jobs) if self.jobs[k]['actor']==actor]
 def released(self,job):
  self.ready();row=self.jobs[job]
  if row['phase']!='gated' or row['actor'] is not None and str(row['actor']) in self.freezes:raise ValueError('exact unfrozen gated job required for release')
  row['phase']='released';self.commit(job,row['actor'])
 def complete(self,job):
  self.ready();row=self.jobs[job]
  if row['phase'] not in ('gated','released'):raise ValueError('exact physical job completion required')
  row['phase']='closed';self.commit(job,row['actor'])
 def uncertain(self,job):
  self.ready();self.jobs[job]['uncertain']=True;self.commit(job,self.jobs[job]['actor'])
 def returned(self,job,proof):
  self.ready();row=self.jobs[job]
  if row['kind'] not in ('native-effect','native-export') or row['uncertain'] or row['returned'] is not None:raise ValueError('exact unambiguous native result required')
  if not isinstance(proof,dict) or set(proof)!={'job','pid','start','sourceSHA256','journalSHA256','resultSHA256'}:raise ValueError('complete native semantic journal proof required')
  if any(type(proof[k]) is not type(row[k]) or proof[k]!=row[k] for k in ('job','pid','start','sourceSHA256')):raise ValueError('native result belongs to another source/lifetime/job')
  sha256(proof['journalSHA256']);sha256(proof['resultSHA256']);row['returned']=deepcopy(proof);self.commit(job,row['actor'])
 def freeze(self,intent):
  self.ready();intent=checked_intent(intent);actor=intent['actor'];old=self.freezes.get(str(actor))
  if old is not None and old!=intent:raise ValueError('another current receipt already froze actor')
  if old is None:self.freezes[str(actor)]=intent;self.commit(actor=actor)
  return self.witness(actor)
 def witness(self,actor):
  self.ready();positive(actor)
  if str(actor) not in self.freezes:raise ValueError('exact durable actor freeze missing')
  rows=self.rows(actor)
  return {'issuer':deepcopy(self.issuer),'intent':deepcopy(self.freezes[str(actor)]),'revision':self.revisions.get(str(actor),0),'jobCount':len(rows),'ledgerSHA256':digest(rows)}
 def attest(self,actor,expected):
  self.ready();witness=self.witness(actor)
  if digest(witness)!=digest(expected):raise ValueError('actor ledger witness changed')
  rows=self.rows(actor)
  if not rows or any(row['phase']!='closed' or row['uncertain'] or row['kind'] in ('native-effect','native-export') and row['returned'] is None for row in rows):raise ValueError('actual actor history has unfinished/uncertain work')
  return witness

def read_anchored(root,identity,name,limit=1048576):
 root=Path(root)
 if root.resolve()!=root.absolute() or '/' in name or name in ('','.', '..'):raise ValueError('canonical anchored keeper material required')
 directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  before=os.fstat(directory);named=root.lstat()
  if [before.st_dev,before.st_ino]!=identity or (named.st_dev,named.st_ino)!=(before.st_dev,before.st_ino) or before.st_uid!=os.getuid() or stat.S_IMODE(before.st_mode)!=0o700:raise ValueError('live anchored root differs')
  fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.getuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_size>limit:raise ValueError('exact bounded private actor material required')
   data=os.read(fd,limit+1);b=os.fstat(fd);target=os.stat(name,dir_fd=directory,follow_symlinks=False)
   if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns) or (target.st_dev,target.st_ino)!=(a.st_dev,a.st_ino) or len(data)!=a.st_size:raise ValueError('actor material replaced/changed while reading')
  finally:os.close(fd)
  named=root.lstat();after=os.fstat(directory)
  if (named.st_dev,named.st_ino)!=(before.st_dev,before.st_ino) or (after.st_dev,after.st_ino)!=(before.st_dev,before.st_ino):raise ValueError('actor root replaced while reading')
  return json.loads(data)
 finally:os.close(directory)

def journal_body(root,identity):
 document=read_anchored(root,identity,'journal.json');body=document.get('body')
 if not isinstance(body,dict) or document.get('sha256')!=digest(body) or body.get('version')!=1:raise ValueError('exact current durable journal checksum required')
 positive(body.get('snapshot'));return body,document['sha256']

def verify_freeze(intent,issuer):
 intent=checked_intent(intent);lease=intent['lease'];root=issuer['root'];identity=issuer['rootIdentity']
 if (lease['pid'],lease['start'],lease['rootIdentity'],lease['session'])!=(issuer['servicePID'],issuer['serviceStart'],identity,issuer['environment']['HYPRLAND_INSTANCE_SIGNATURE']):raise ValueError('freeze belongs to another selected service/root/session')
 owner=read_anchored(root,identity,'owner.json')
 if any(type(owner.get(k)) is not type(lease[k]) or owner.get(k)!=lease[k] for k in ('pid','start','nonce','session')):raise ValueError('freeze lease differs from actual current owner')
 if process_record(lease['pid'])['start']!=lease['start']:raise ValueError('freeze owner lifetime changed')
 fd=os.open(Path(root)/'runtime.lock',os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  info=os.fstat(fd)
  if [info.st_dev,info.st_ino]!=lease['lockIdentity'] or not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600:raise ValueError('freeze exact runtime lease lock differs')
  try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:pass
  else:fcntl.flock(fd,fcntl.LOCK_UN);raise ValueError('freeze lease is not held')
 finally:os.close(fd)
 body,_=journal_body(root,identity)
 if body.get('session')!=lease['session']:raise ValueError('freeze journal belongs to another session')
 records=body.get('scenes');receipts=body.get('receipts')
 if not isinstance(records,list) or not isinstance(receipts,list):raise ValueError('complete current scene/receipt journal required')
 selected=[r for r in records if isinstance(r,dict) and type(r.get('actor')) is int and r.get('actor')==intent['actor']]
 if len(selected)!=1:raise ValueError('exact single current actor required')
 row=selected[0];profile=row.get('profile',{})
 if row.get('token')!=intent['token'] or digest(row.get('requested'))!=digest(intent['captured']) or digest(sorted(row.get('members',[])))!=digest(intent['scope']) or type(profile.get('managerReceipt')) is not int or profile.get('managerReceipt')!=intent['receipt'] or digest(profile.get('liveCancelIntent'))!=digest(intent) or profile.get('liveCancelReserved') is not True:raise ValueError('freeze is not the exact durable explicit current intent')
 mapping={tuple(k):v for k,v in receipts}
 if any(type(mapping.get(tuple(k))) is not int or mapping.get(tuple(k))!=intent['receipt'] for k in intent['scope']):raise ValueError('freeze receipt was superseded')
 if read_anchored(root,identity,'owner.json')!=owner:raise ValueError('owner changed during freeze proof')
 return intent

def verify_native_return(job,proof,ledger):
 row=ledger.jobs[job];body,journal_sha=journal_body(ledger.issuer['root'],ledger.issuer['rootIdentity'])
 if proof.get('journalSHA256')!=journal_sha:raise ValueError('native return not in exact current durable journal')
 records=body.get('actorNativeResults')
 if not isinstance(records,list):raise ValueError('durable semantic native results missing')
 matches=[r for r in records if isinstance(r,dict) and r.get('job')==job]
 if len(matches)!=1:raise ValueError('exact unique native result journal required')
 result=matches[0]
 if any(type(result.get(k)) is not type(row[k]) or result.get(k)!=row[k] for k in ('job','pid','start','sourceSHA256','actor','kind')) or proof.get('resultSHA256')!=digest(result):raise ValueError('durable native result source/lifetime/role differs')
 if result.get('returned') is not True or result.get('uncertain') is not False or not isinstance(result.get('semanticResult'),dict) or not result['semanticResult']:raise ValueError('exact decoded native result missing/uncertain')
 # SemanticResult is emitted by the guarded native caller after validating its
 # actual returned result. This primitive cannot invent such a caller record.
 positive(result.get('receipt'))
 if type(result.get('token')) is not str or re.fullmatch('[0-9a-f]{12}-[1-9][0-9]{0,14}',result['token']) is None:raise ValueError('native result exact producer token missing')
 sha256(result.get('scopeSHA256'))
 if body.get('session')!=ledger.issuer['environment']['HYPRLAND_INSTANCE_SIGNATURE']:raise ValueError('native result journal selected session differs')
 return deepcopy(proof)
