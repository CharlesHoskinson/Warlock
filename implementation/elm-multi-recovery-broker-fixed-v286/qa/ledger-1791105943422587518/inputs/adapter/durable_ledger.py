"""Bounded durable unresolved intents. An observation store, never a retry queue."""
import copy,fcntl,hashlib,json,os,secrets
from endpoint import Refused,binding,canonical,exact,unique
from recovery_journal import Journal,validate,effect_protocol

MAX_UNRESOLVED=64
MAX_SCOPES=128
MAX_BYTES=524288
NAME='ledger-v4.json'

def encoded(value):return json.dumps(value,separators=(',',':'),ensure_ascii=True).encode()
def normalize(record):
 validate(record)
 return {'schema':2,'effectProtocol':effect_protocol(record),'binding':copy.deepcopy(record['binding']),
         'intent':copy.deepcopy(record['intent']),'status':record['status']}
def key(record):
 record=normalize(record)
 return encoded({k:record[k] for k in ['effectProtocol','binding','intent']})
def scope(bound):return encoded(binding(bound))
def watermark(bound,request,generation):return {'binding':copy.deepcopy(bound),'request':request,'generation':generation}

class Ledger(Journal):
 def __init__(self,runtime,instance,lifetime):
  self.poisoned=False
  super().__init__(runtime,instance,lifetime)
  try:
   host_lock=os.open('host-writer.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
   try:
    self.verify(host_lock);fcntl.flock(host_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    raw=self.raw(self.fd,NAME,MAX_BYTES)
    if raw is None:self._bootstrap()
    else:self._validate(json.loads(raw,object_pairs_hook=unique))
   finally:os.close(host_lock)
  except BaseException:self.close();raise
 def _source_hashes(self):
  hashes={}
  for name in ['host-intent.json','intent.json']:
   raw=self.raw(self.fd,name,4096)
   hashes[name]=hashlib.sha256(raw).hexdigest() if raw is not None else None
  return hashes
 def _bootstrap(self):
  prior=self.raw(self.fd,'ledger-v3.json',MAX_BYTES)
  if prior is not None:
   state=self._validate_prior(json.loads(prior,object_pairs_hook=unique))
   self._save(dict(state,schema=4,latest=None,predecessorSHA256=hashlib.sha256(prior).hexdigest()));return
  host=self.read('host-intent.json');broker=self.read()
  records=[]
  if host is not None:records.append(normalize(host))
  if broker is not None:
   broker=normalize(broker)
   records=[r for r in records if key(r)!=key(broker)];records.append(broker)
  entries=[r for r in records if r['status'] in ['Pending','Unknown']]
  marks={}
  for r in records:
   s=scope(r['binding']);old=marks.get(s,watermark(r['binding'],'0','0'))
   marks[s]=watermark(r['binding'],str(max(int(old['request']),int(r['intent']['request']))),str(max(int(old['generation']),int(r['intent']['generation']))))
  state={'schema':4,'predecessorSHA256':None,'latest':normalize(broker or host) if broker or host else None,'lifetime':self.target['lifetime'],'entries':entries,'watermarks':list(marks.values()),'bootstrapHashes':self._source_hashes()}
  self._validate(state);self._save(state)
 def _validate_prior(self,state):
  exact(state,['schema','lifetime','entries','watermarks','bootstrapHashes'])
  if type(state['schema']) is not int or state['schema']!=3 or state['lifetime']!=self.target['lifetime']:raise Refused('Ledger lifetime/schema')
  exact(state['bootstrapHashes'],['host-intent.json','intent.json'])
  if state['bootstrapHashes']!=self._source_hashes():raise Refused('Legacy producer changed after ledger migration')
  entries,marks=state['entries'],state['watermarks']
  if not isinstance(entries,list) or len(entries)>MAX_UNRESOLVED or not isinstance(marks,list) or len(marks)>MAX_SCOPES:raise Refused('Ledger capacity')
  scopes=set()
  for m in marks:
   exact(m,['binding','request','generation']);binding(m['binding']);canonical(m['request'],True);canonical(m['generation'],True)
   if m['binding']['lifetime']!=self.target['lifetime'] or scope(m['binding']) in scopes:raise Refused('Ledger watermark scope')
   scopes.add(scope(m['binding']))
  keys=set();targets=set()
  for r in entries:
   validate(r)
   if r['schema']!=2 or r['binding']['lifetime']!=self.target['lifetime'] or r['status'] not in ['Pending','Unknown'] or len(encoded(r))>4096:raise Refused('Ledger unresolved entry')
   target=r['intent']['incarnation']
   if key(r) in keys or target in targets:raise Refused('Ledger duplicate unresolved target/key')
   keys.add(key(r));targets.add(target)
   mark=next((m for m in marks if m['binding']==r['binding']),None)
   if mark is None or int(mark['request'])<int(r['intent']['request']) or int(mark['generation'])<int(r['intent']['generation']):raise Refused('Ledger missing allocation watermark')
  if len(encoded(state))>MAX_BYTES:raise Refused('Ledger byte capacity')
  return state
 def _validate(self,state):
  exact(state,['schema','lifetime','entries','watermarks','bootstrapHashes','latest','predecessorSHA256'])
  if type(state['schema']) is not int or state['schema']!=4:raise Refused('Ledger schema')
  prior=self.raw(self.fd,'ledger-v3.json',MAX_BYTES)
  digest=hashlib.sha256(prior).hexdigest() if prior is not None else None
  if state['predecessorSHA256']!=digest:raise Refused('Prior ledger producer changed after migration')
  previous={k:v for k,v in state.items() if k not in ['latest','predecessorSHA256']};previous['schema']=3
  self._validate_prior(previous)
  latest=state['latest']
  if latest is not None:
   validate(latest)
   if latest['schema']!=2 or latest['binding']['lifetime']!=self.target['lifetime'] or len(encoded(latest))>4096:raise Refused('Ledger latest scope')
   mark=next((m for m in state['watermarks'] if m['binding']==latest['binding']),None)
   if mark is None or int(mark['request'])<int(latest['intent']['request']) or int(mark['generation'])<int(latest['intent']['generation']):raise Refused('Ledger latest allocation watermark')
   matching=[r for r in state['entries'] if key(r)==key(latest)]
   if latest['status'] in ['Pending','Unknown'] and (len(matching)!=1 or matching[0]!=latest):raise Refused('Ledger latest unresolved correlation')
   if latest['status'] in ['Committed','Refused'] and matching:raise Refused('Ledger latest terminal correlation')
  if len(encoded(state))>MAX_BYTES:raise Refused('Ledger byte capacity')
  return state
 def _load(self):
  if self.poisoned:raise Refused('Ledger storage failure requires explicit close and correction')
  raw=self.raw(self.fd,NAME,MAX_BYTES)
  if raw is None:raise Refused('Ledger missing after initialization')
  return self._validate(json.loads(raw,object_pairs_hook=unique))
 def _save(self,state):
  if self.poisoned:raise Refused('Ledger storage failure requires explicit close and correction')
  self._validate(state);raw=encoded(state)
  temporary='ledger-pending-'+secrets.token_hex(12);fd=None
  try:
   # Validate an existing destination before replacing it; never normalize an
   # unsafe public/symlink/hardlink file into an apparently valid record.
   self.raw(self.fd,NAME,MAX_BYTES)
   fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
   offset=0
   while offset<len(raw):
    try:count=os.write(fd,raw[offset:])
    except InterruptedError:continue
    if count<=0:raise OSError('Ledger write made no progress')
    offset+=count
   os.fsync(fd);closing=fd;fd=None;os.close(closing)
   os.replace(temporary,NAME,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)
  except BaseException:
   self.poisoned=True;raise
  finally:
   if fd is not None:
    try:os.close(fd)
    except BaseException:self.poisoned=True;raise
   try:os.unlink(temporary,dir_fd=self.fd)
   except FileNotFoundError:pass
 def snapshot(self):return copy.deepcopy(self._load())
 def blocked(self,lifetime,incarnation):
  canonical(lifetime);canonical(incarnation)
  if lifetime!=self.target['lifetime']:raise Refused('Ledger foreign lifetime')
  return any(r['intent']['incarnation']==incarnation for r in self._load()['entries'])
 def begin(self,bound,intent,effectProtocol=1):
  """True means newly durably admitted. False is duplicate, NEVER resubmit."""
  r=normalize({'schema':2,'binding':bound,'intent':intent,'effectProtocol':effectProtocol,'status':'Pending'})
  if bound['lifetime']!=self.target['lifetime']:raise Refused('Ledger foreign binding')
  state=self._load()
  if any(key(old)==key(r) for old in state['entries']):return False
  if any(old['intent']['incarnation']==intent['incarnation'] for old in state['entries']):raise Refused('Ledger unresolved native target')
  if len(state['entries'])>=MAX_UNRESOLVED:raise Refused('Ledger unresolved capacity')
  m=next((m for m in state['watermarks'] if m['binding']==bound),None)
  if m is None:
   if len(state['watermarks'])>=MAX_SCOPES:raise Refused('Ledger allocation scope capacity')
   m=watermark(bound,'0','0');state['watermarks'].append(m)
  if int(intent['request'])<=int(m['request']) or int(intent['generation'])<=int(m['generation']):raise Refused('Ledger allocation replay/order')
  m.update(request=intent['request'],generation=intent['generation']);state['entries'].append(r);state['latest']=copy.deepcopy(r)
  self._save(state);return True
 def settle(self,outcome):
  """Only full original native receipt settles its key; definitive frees one."""
  exact(outcome,['protocolVersion','kind','effectProtocol','binding','intent','status','reason','revision','outputGeneration'])
  if type(outcome['protocolVersion']) is not int or outcome['protocolVersion']!=3 or outcome['kind']!='effect-outcome':raise Refused('Ledger receipt envelope')
  r=normalize({'schema':2,'binding':outcome['binding'],'intent':outcome['intent'],'effectProtocol':outcome['effectProtocol'],'status':outcome['status']})
  if r['status'] not in ['Committed','Refused','Unknown']:raise Refused('Ledger receipt status')
  canonical(outcome['revision']);canonical(outcome['outputGeneration'])
  reason=outcome['reason']
  try:valid=isinstance(reason,str) and len(reason.encode('utf-16-le'))//2<=256 and not any(ord(c)<32 or 127<=ord(c)<=159 for c in reason)
  except UnicodeEncodeError:valid=False
  if not valid:raise Refused('Ledger receipt reason')
  self._settle_record(r)
 def _settle_record(self,r):
  r=normalize(r)
  if r['status'] not in ['Committed','Refused','Unknown']:raise Refused('Ledger receipt status')
  state=self._load();matching=[e for e in state['entries'] if key(e)==key(r)]
  if len(matching)!=1:raise Refused('Ledger uncorrelated receipt')
  if r['status']=='Unknown':matching[0]['status']='Unknown'
  else:state['entries']=[e for e in state['entries'] if key(e)!=key(r)]
  if state['latest'] is not None and key(state['latest'])==key(r):state['latest']=copy.deepcopy(r)
  self._save(state)
 def recover(self,current_binding):
  """Internal informational DTO. No native command or observation is emitted."""
  binding(current_binding)
  if current_binding['lifetime']!=self.target['lifetime']:raise Refused('Ledger foreign recovery lifetime')
  state=self._load()
  return {'binding':copy.deepcopy(current_binding),'entries':[dict(copy.deepcopy(r),status='Unknown') for r in state['entries']], 'watermarks':copy.deepcopy(state['watermarks'])}
