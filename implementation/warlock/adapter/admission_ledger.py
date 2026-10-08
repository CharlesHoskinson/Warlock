"""Shared host admissions plus bounded durable settlement retirement.

Admissions are observation evidence; neither import nor recovery replays effects.
"""
import copy,fcntl,hashlib,json,os,re,secrets,stat,struct
from contextlib import contextmanager
from durable_ledger import Ledger,normalize,key,watermark,scope,encoded
from recovery_journal import Journal,validate
from endpoint import Refused,exact,unique
NAME='ledger-v5.json'
MARKER='ledger-v5.initialized'
MAX_BYTES=1048576

def storage_key(record):
 r=normalize(record);b,i=r['binding'],r['intent'];c=i['context']
 fields=[b['lifetime'],b['session'],b['frontend'],r['effectProtocol'],i['request'],i['generation'],i['incarnation'],i['operation'],c['lifetime'],c['epoch'],c['output'],c['revision']]
 if i['operation']=='snap':
  p=i['placement'];fields.extend(p[name] for name in ['region','monitor','outputOwnershipGeneration','workAreaRevision','workspaceGeneration'])
  fields.extend(struct.pack('>d',0.0 if value==0 else float(value)).hex() for value in p['geometry'])
 return hashlib.sha256(json.dumps(fields,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

class AdmissionLedger(Ledger):
 def __init__(self,runtime,instance,lifetime):
  self.poisoned=False
  Journal.__init__(self,runtime,instance,lifetime)
  try:
   with self.host_guard() as directory:
    raw=self.raw(self.fd,NAME,MAX_BYTES)
    if raw is None:
     if self.raw(self.fd,MARKER,4096) is not None:raise Refused('Admission ledger missing after initialization')
     self._bootstrap()
    else:self._validate(json.loads(raw,object_pairs_hook=unique))
    self._ensure_marker();self._sync(directory)
  except BaseException:self.close();raise
 @contextmanager
 def host_guard(self):
  fd=os.open('host-writer.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
  directory=None
  try:
   self.verify(fd);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   try:os.mkdir('admissions-v1',0o700,dir_fd=self.fd);os.fsync(self.fd)
   except FileExistsError:pass
   directory=os.open('admissions-v1',os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd);st=os.fstat(directory)
   if st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o700:raise Refused('Admission directory ownership')
   yield directory
  finally:
   if directory is not None:os.close(directory)
   os.close(fd)
 def admissions(self,directory):
  result=[];targets=set();temporary=0
  for name in os.listdir(directory):
   if re.fullmatch(r'host-pending-[0-9a-f-]{36}',name):
    temporary+=1
    if temporary>64:raise Refused('Admission temporary capacity')
    self.raw(directory,name,4096);continue
   if not re.fullmatch(r'[0-9a-f]{64}\.json',name):raise Refused('Admission filename')
   raw=self.raw(directory,name,4096)
   if raw is None:raise Refused('Admission changed under storage lock')
   r=validate(json.loads(raw,object_pairs_hook=unique))
   if r['schema']!=2 or r['status']!='Pending' or r['binding']['lifetime']!=self.target['lifetime'] or storage_key(r)+'.json'!=name:raise Refused('Admission key/scope')
   if r['intent']['incarnation'] in targets:raise Refused('Admission duplicate target')
   targets.add(r['intent']['incarnation']);result.append(normalize(r))
   if len(result)>64:raise Refused('Admission capacity')
  return result
 def _bootstrap(self):
  prior_name=None;prior=None
  for name in ['ledger-v4.json','ledger-v3.json']:
   raw=self.raw(self.fd,name,524288)
   if raw is None:continue
   prior_name=name;prior=raw;state=json.loads(raw,object_pairs_hook=unique)
   if name=='ledger-v4.json':Ledger._validate(self,state)
   else:self._validate_prior(state);state=dict(state,latest=None)
   break
  if prior is None:
   host=self.read('host-intent.json');broker=self.read();records=[]
   if host is not None:records.append(normalize(host))
   if broker is not None:
    broker=normalize(broker);records=[r for r in records if key(r)!=key(broker)];records.append(broker)
   marks={}
   for r in records:
    old=marks.get(scope(r['binding']),watermark(r['binding'],'0','0'))
    marks[scope(r['binding'])]=watermark(r['binding'],str(max(int(old['request']),int(r['intent']['request']))),str(max(int(old['generation']),int(r['intent']['generation']))))
   state={'lifetime':self.target['lifetime'],'entries':[r for r in records if r['status'] in ['Pending','Unknown']],'watermarks':list(marks.values()),'bootstrapHashes':self._source_hashes(),'latest':normalize(broker or host) if broker or host else None}
  latest=state['latest'];settled=[copy.deepcopy(latest)] if latest is not None and latest['status'] in ['Committed','Refused'] else []
  state={k:state[k] for k in ['lifetime','entries','watermarks','bootstrapHashes','latest']}
  state.update(schema=5,predecessorName=prior_name,predecessorSHA256=hashlib.sha256(prior).hexdigest() if prior is not None else None,settled=settled)
  self._save(state)
 def _validate(self,state):
  exact(state,['schema','lifetime','entries','watermarks','bootstrapHashes','latest','predecessorName','predecessorSHA256','settled'])
  if type(state['schema']) is not int or state['schema']!=5:raise Refused('Admission ledger schema')
  name=state['predecessorName']
  if name not in [None,'ledger-v3.json','ledger-v4.json']:raise Refused('Admission predecessor name')
  prior=self.raw(self.fd,name,524288) if name is not None else None
  if state['predecessorSHA256']!=(hashlib.sha256(prior).hexdigest() if prior is not None else None) or (name is not None and prior is None):raise Refused('Admission predecessor changed')
  if name!='ledger-v4.json' and self.raw(self.fd,'ledger-v4.json',524288) is not None:raise Refused('Older producer appeared after admission migration')
  if name is None and self.raw(self.fd,'ledger-v3.json',524288) is not None:raise Refused('Older producer appeared after admission migration')
  if name=='ledger-v4.json':Ledger._validate(self,json.loads(prior,object_pairs_hook=unique))
  raw3=self.raw(self.fd,'ledger-v3.json',524288)
  view={k:state[k] for k in ['lifetime','entries','watermarks','bootstrapHashes','latest']};view.update(schema=4,predecessorSHA256=hashlib.sha256(raw3).hexdigest() if raw3 is not None else None)
  Ledger._validate(self,view)
  settled=state['settled']
  if not isinstance(settled,list) or len(settled)>64:raise Refused('Admission settlement capacity')
  seen={key(r) for r in state['entries']}
  for r in settled:
   validate(r)
   if r['schema']!=2 or r['status'] not in ['Committed','Refused'] or r['binding']['lifetime']!=self.target['lifetime'] or key(r) in seen:raise Refused('Admission settlement key/scope')
   seen.add(key(r));m=next((m for m in state['watermarks'] if m['binding']==r['binding']),None)
   if m is None or int(m['request'])<int(r['intent']['request']) or int(m['generation'])<int(r['intent']['generation']):raise Refused('Admission settlement allocation')
  if len(encoded(state))>MAX_BYTES:raise Refused('Admission ledger byte capacity')
  return state
 def _load(self):
  if self.poisoned:raise Refused('Admission ledger requires explicit correction')
  raw=self.raw(self.fd,NAME,MAX_BYTES)
  if raw is None:raise Refused('Admission ledger missing after initialization')
  return self._validate(json.loads(raw,object_pairs_hook=unique))
 def _ensure_marker(self):
  expected={'schema':1,'lifetime':self.target['lifetime'],'kind':'admission-ledger-initialized'}
  raw=self.raw(self.fd,MARKER,4096)
  if raw is not None:
   actual=json.loads(raw,object_pairs_hook=unique)
   if actual!=expected or type(actual.get('schema')) is not int:raise Refused('Admission ledger marker')
  else:self.atomic(MARKER,encoded(expected))
 def _save(self,state):
  if self.poisoned:raise Refused('Admission ledger requires explicit correction')
  self._validate(state);raw=encoded(state);temporary='admission-ledger-pending-'+secrets.token_hex(12);fd=None
  try:
   self.raw(self.fd,NAME,MAX_BYTES)
   fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd);offset=0
   while offset<len(raw):
    try:n=os.write(fd,raw[offset:])
    except InterruptedError:continue
    if n<=0:raise OSError('Admission ledger write made no progress')
    offset+=n
   os.fsync(fd);closing=fd;fd=None;os.close(closing);os.replace(temporary,NAME,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)
  except BaseException:self.poisoned=True;raise
  finally:
   if fd is not None:
    try:os.close(fd)
    except BaseException:self.poisoned=True;raise
   try:os.unlink(temporary,dir_fd=self.fd)
   except FileNotFoundError:pass
 def _mark(self,state,r):
  m=next((m for m in state['watermarks'] if m['binding']==r['binding']),None)
  if m is None:
   if len(state['watermarks'])>=128:raise Refused('Admission allocation scope capacity')
   m=watermark(r['binding'],'0','0');state['watermarks'].append(m)
  m['request']=str(max(int(m['request']),int(r['intent']['request'])));m['generation']=str(max(int(m['generation']),int(r['intent']['generation'])))
 def _sync(self,directory,exclude=None):
  state=self._load();original=encoded(state);admitted=self.admissions(directory);present={key(r) for r in admitted}
  # Even if a host unlink was visible after a failed fsync, persist absence before
  # forgetting its definitive settlement. No power-loss resurrection is assumed.
  if any(key(r) not in present for r in state['settled']):os.fsync(directory)
  state['settled']=[r for r in state['settled'] if key(r) in present]
  for r in admitted:
   if exclude is not None and key(r)==key(exclude):continue
   if any(key(old)==key(r) for old in state['entries']+state['settled']):continue
   latest=state['latest']
   if latest is not None and key(latest)==key(r) and latest['status'] in ['Committed','Refused']:
    state['settled'].append(copy.deepcopy(latest));continue
   if any(old['intent']['incarnation']==r['intent']['incarnation'] for old in state['entries']):raise Refused('Admission conflicts with unresolved target')
   state['entries'].append(dict(r,status='Unknown'));self._mark(state,r)
  if encoded(state)!=original:self._save(state)
  return state
 def begin(self,bound,intent,effectProtocol=1):
  wanted=normalize({'schema':2,'binding':bound,'intent':intent,'effectProtocol':effectProtocol,'status':'Pending'})
  with self.host_guard() as directory:
   state=self._sync(directory,exclude=wanted)
   if not any(key(r)==key(wanted) for r in self.admissions(directory)):raise Refused('No matching durable host admission')
   # Original base implementation enforces full-key duplication, target guards,
   # both allocation maxima, budgets and fsync-before-submission.
   return Ledger.begin(self,bound,intent,effectProtocol)
 def _settle_record(self,r):
  r=normalize(r)
  if r['status'] not in ['Committed','Refused','Unknown']:raise Refused('Admission receipt status')
  with self.host_guard() as directory:
   state=self._sync(directory);matching=[old for old in state['entries'] if key(old)==key(r)]
   if len(matching)!=1:raise Refused('Admission uncorrelated receipt')
   if r['status']=='Unknown':matching[0]['status']='Unknown'
   else:
    state['entries']=[old for old in state['entries'] if key(old)!=key(r)]
    if len(state['settled'])>=64:raise Refused('Admission settlement capacity')
    state['settled'].append(copy.deepcopy(r))
   if state['latest'] is not None and key(state['latest'])==key(r):state['latest']=copy.deepcopy(r)
   self._save(state)
 def synchronization_snapshot(self):
  with self.host_guard() as directory:return copy.deepcopy(self._sync(directory))
