"""Typed atomic admission authority prototype. No native effect or transport."""
import copy,hashlib,re
from archive_base import Archive,Corrupt,Refused,canonical,decode,fields,integer,ref,PAGE,EVENT,MAX64

COMPLETION_BYTES=3*(EVENT+18*PAGE+PAGE+4096)
COMPLETION_FILES=3*23

def counter(value,zero=False):
 if type(value) is not str or not re.fullmatch(r'0|[1-9][0-9]{0,19}',value) or int(value)>MAX64 or (not zero and value=='0'):raise Refused('noncanonical authority UInt64')
 return value

def binding(value):
 if type(value) is not dict or set(value)!= {'lifetime','session','frontend'}:raise Refused('binding shape')
 for v in value.values():counter(v)
 return value

def pending(raw):
 if type(raw) is not bytes or len(raw)>4096:raise Refused('exact record byte bound')
 try:r=decode(raw)
 except Corrupt as e:raise Refused('invalid record JSON') from e
 if type(r) is not dict or set(r)!= {'schema','effectProtocol','binding','intent','status'} or type(r['schema']) is not int or r['schema']!=2 or type(r['effectProtocol']) is not int or r['effectProtocol'] not in [1,2] or r['status']!='Pending':raise Refused('Pending record schema')
 binding(r['binding']);intent=r['intent']
 if type(intent) is not dict or set(intent)!= {'request','generation','incarnation','operation','context'}:raise Refused('intent shape')
 for name in ['request','generation','incarnation']:counter(intent[name])
 c=intent['context']
 if type(c) is not dict or set(c)!= {'lifetime','epoch','output','revision'}:raise Refused('context shape')
 for value in c.values():counter(value)
 if c['lifetime']!=r['binding']['lifetime'] or c['epoch']!=r['binding']['frontend']:raise Refused('record context binding')
 operations=['minimize','restore','activate'] if r['effectProtocol']==1 else ['maximize','restore-geometry']
 if intent['operation'] not in operations:raise Refused('operation/protocol')
 return r

def origin(r):return {name:copy.deepcopy(r[name]) for name in ['effectProtocol','binding','intent']}
def event_key(r):return {'namespace':'admission-authority-v665','origin':origin(r),'fact':'Admission'}

class Authority(Archive):
 def __init__(self,path,native_lifetime,**kwargs):
  self.native_lifetime=counter(native_lifetime)
  super().__init__(path,**kwargs)
  try:
   self._transition(self.root)
   # Parent's barrier preceded validation of cross-generation conservation;
   # establish another fresh barrier after all authority checks before expose.
   self._sync('authority-restart-root')
  except BaseException:self.poisoned=True;self.close();raise

 def _empty(self):return {'authoritySchema':1,'nativeLifetime':self.native_lifetime,'marks':[],'live':[]}
 def _index(self,obj,depth=None):
  if depth is None and type(obj) is dict and 'authoritySchema' in obj:return self._authority(obj)
  return super()._index(obj,depth)

 def _authority(self,obj):
  try:
   fields(obj,('authoritySchema','nativeLifetime','marks','live'))
   if type(obj['authoritySchema']) is not int or obj['authoritySchema']!=1 or counter(obj['nativeLifetime'])!=self.native_lifetime:raise Corrupt('authority schema/lifetime')
   marks=obj['marks'];live=obj['live']
   if type(marks) is not list or len(marks)>64 or type(live) is not list or len(live)>64:raise Corrupt('authority bound')
   scopes={}
   for mark in marks:
    fields(mark,('binding','request','generation'));binding(mark['binding']);counter(mark['request']);counter(mark['generation'])
    if mark['binding']['lifetime']!=self.native_lifetime:raise Corrupt('foreign scope')
    k=canonical(mark['binding'])
    if k in scopes:raise Corrupt('duplicate scope')
    scopes[k]=mark
   origins=set();targets=set();by_scope={}
   for entry in live:
    fields(entry,('event','reservedBytes','reservedFiles'));self._check_ref(entry['event'],'event')
    if type(entry['reservedBytes']) is not int or entry['reservedBytes']!=COMPLETION_BYTES or type(entry['reservedFiles']) is not int or entry['reservedFiles']!=COMPLETION_FILES:raise Corrupt('completion reservation')
    event=self._load(entry['event']);raw=self._event(event);r=pending(raw)
    if event['kind']!='Admission' or event['key']!=event_key(r) or r['binding']['lifetime']!=self.native_lifetime:raise Corrupt('exact Admission origin')
    k=canonical(origin(r));target=r['intent']['incarnation']
    if k in origins or target in targets:raise Corrupt('duplicate live origin/target')
    origins.add(k);targets.add(target);by_scope.setdefault(canonical(r['binding']),[]).append(r)
    m=scopes.get(canonical(r['binding']))
    if m is None or int(m['request'])<int(r['intent']['request']) or int(m['generation'])<int(r['intent']['generation']):raise Corrupt('Admission without replay maxima')
   if len(scopes)>len(live):raise Corrupt('scope without admission')
   # This first slice never completes/removes live records; maxima must exactly
   # equal maxima over conserved validated Admissions, independently per domain.
   for k,m in scopes.items():
    records=by_scope.get(k,[])
    if not records:raise Corrupt('scope without matching admission')
    if int(m['request'])!=max(int(r['intent']['request']) for r in records) or int(m['generation'])!=max(int(r['intent']['generation']) for r in records):raise Corrupt('nonconserved allocation maxima')
   return obj
  except Refused as e:raise Corrupt('invalid typed authority') from e

 def _root(self,r):
  self._check_ref(r,'root');x=self._load(r)
  bootstrap=type(x) is dict and 'authority' not in x
  fields(x,('schema','lifetime','generation','count','predecessor','index','newPages') if bootstrap else ('schema','lifetime','generation','count','predecessor','index','newPages','authority'))
  if type(x['schema']) is not int or x['schema']!=1 or x['lifetime']!=self.lifetime:raise Corrupt('root schema')
  if integer(x['generation'])!=integer(x['count']):raise Corrupt('publication count')
  if x['predecessor'] is not None:self._check_ref(x['predecessor'],'root')
  if x['index'] is not None:self._check_ref(x['index'],'index')
  if type(x['newPages']) is not list or len(x['newPages'])>19:raise Corrupt('authority closure bound')
  for p in x['newPages']:self._check_ref(p)
  names=[p['name'] for p in x['newPages']]
  if len(names)!=len(set(names)):raise Corrupt('duplicate closure')
  if bootstrap:
   if x['count']!=0 or x['index'] is not None or names or x['predecessor'] is not None:raise Corrupt('nonempty archive lacks typed authority')
  else:
   self._check_ref(x['authority'],'index')
   if len(names)!=19 or sum(n.startswith('event-') for n in names)!=1 or any(n.startswith('root-') for n in names) or x['index']['name'] not in names or x['authority']['name'] not in names:raise Corrupt('incomplete authority closure')
   obj=self._authority(self._load(x['authority']))
   if len(obj['live'])!=x['count']:raise Corrupt('missing admission authority')
   if self.quota['files']<5+23*x['count']+sum(e['reservedFiles'] for e in obj['live']) or self.quota['bytes']<4096+sum(e['reservedBytes'] for e in obj['live']):raise Corrupt('unreserved completion capacity')
  return x

 def _state(self,root):return self._empty() if 'authority' not in root else self._authority(self._load(root['authority']))
 def _transition(self,root):
  current=self._state(root)
  for entry in current['live']:
   raw=self._event(self._load(entry['event']));record=pending(raw);found=self._find(event_key(record),root)
   if found is None or self._event(found)!=raw:raise Corrupt('authority/history atomic closure')
  if root['predecessor'] is None:return
  previous=self._state(self._root(root['predecessor']))
  old={e['event']['name']:e for e in previous['live']};new={e['event']['name']:e for e in current['live']}
  if len(new)!=len(old)+1 or any(new.get(k)!=e for k,e in old.items()):raise Corrupt('live authority conservation')
  added=next(e for k,e in new.items() if k not in old);record=pending(self._event(self._load(added['event'])))
  prior=next((m for m in previous['marks'] if m['binding']==record['binding']),None)
  if prior is not None and (int(record['intent']['request'])<=int(prior['request']) or int(record['intent']['generation'])<=int(prior['generation'])):raise Corrupt('new admission stale independent domain')
  for m in previous['marks']:
   n=next((x for x in current['marks'] if x['binding']==m['binding']),None)
   if n is None or int(n['request'])<int(m['request']) or int(n['generation'])<int(m['generation']):raise Corrupt('replay watermark conservation')

 def readAuthority(self,bound):
  binding(bound)
  if bound['lifetime']!=self.native_lifetime:raise Refused('foreign authority query')
  try:
   self._live();state=self._state(self.root);mark=next((m for m in state['marks'] if m['binding']==bound),None)
   live=[]
   for e in state['live']:
    raw=self._event(self._load(e['event']));r=pending(raw)
    if r['binding']==bound:live.append({'exactRecord':raw,'origin':origin(r),'reservedBytes':e['reservedBytes'],'reservedFiles':e['reservedFiles']})
   return {'binding':copy.deepcopy(bound),'request':mark['request'] if mark else '0','generation':mark['generation'] if mark else '0','admissions':live,'completionReservedBytes':sum(e['reservedBytes'] for e in state['live']),'completionReservedFiles':sum(e['reservedFiles'] for e in state['live'])}
  except BaseException:self.poisoned=True;raise

 def commitAdmission(self,raw):
  r=pending(raw)
  if r['binding']['lifetime']!=self.native_lifetime:raise Refused('foreign admission lifetime')
  try:
   self._live();state=copy.deepcopy(self._state(self.root));old=self._find(event_key(r),self.root)
   if old is not None:
    if self._event(old)!=raw:raise Refused('conflicting duplicate bytes')
    return {'newAdmission':False,'completionReserved':True} # NEVER an effect retry token
   for e in state['live']:
    existing=pending(self._event(self._load(e['event'])))
    if existing['intent']['incarnation']==r['intent']['incarnation']:raise Refused('unresolved target')
   if len(state['live'])>=64:raise Refused('live bound')
   mark=next((m for m in state['marks'] if m['binding']==r['binding']),None)
   if mark is None:
    if len(state['marks'])>=64:raise Refused('scope bound')
    mark={'binding':copy.deepcopy(r['binding']),'request':'0','generation':'0'};state['marks'].append(mark)
   if int(r['intent']['request'])<=int(mark['request']) or int(r['intent']['generation'])<=int(mark['generation']):raise Refused('independent allocation replay')
   mark.update(request=r['intent']['request'],generation=r['intent']['generation'])
   if self.root['generation']==MAX64:raise Refused('publication exhausted')
   obj={'schema':1,'key':event_key(r),'kind':'Admission','payload':__import__('base64').b64encode(raw).decode()};data=canonical(obj);er=ref(data,'event');planned=[(er,data)]
   route=hashlib.sha256(canonical(event_key(r))).hexdigest()
   def cow(rr,depth):
    node=self._index(self._load(rr),depth) if rr else {'schema':1,'depth':depth,**({'children':{}} if depth<16 else {'entries':[]})}
    if depth<16:
     children=dict(node['children']);children[route[depth]]=cow(children.get(route[depth]),depth+1);new={'schema':1,'depth':depth,'children':children}
    else:
     if len(node['entries'])>=32:raise Refused('collision bucket exhausted')
     new={'schema':1,'depth':depth,'entries':sorted(node['entries']+[{'keyHash':route,'event':er}],key=lambda e:e['keyHash'])}
    encoded=canonical(new)
    if len(encoded)>PAGE:raise Refused('index page bound')
    nr=ref(encoded,'index');planned.append((nr,encoded));return nr
   history=cow(self.root['index'],0)
   state['live'].append({'event':er,'reservedBytes':COMPLETION_BYTES,'reservedFiles':COMPLETION_FILES})
   authority_bytes=canonical(state)
   if len(authority_bytes)>PAGE:raise Refused('authority page bound')
   authority_ref=ref(authority_bytes,'index');planned.append((authority_ref,authority_bytes))
   root={'schema':1,'lifetime':self.lifetime,'generation':self.root['generation']+1,'count':self.root['count']+1,'predecessor':self.root_ref,'index':history,'newPages':[p for p,_ in planned],'authority':authority_ref}
   root_bytes=canonical(root)
   if len(root_bytes)>PAGE:raise Refused('root bound')
   nr=ref(root_bytes,'root');quota=self._quota()
   if quota['bytes']<self.quota['bytes'] or quota['files']<self.quota['files']:raise Corrupt('quota rollback')
   charged={'schema':1,'lifetime':self.lifetime,'bytes':quota['bytes']+sum(len(b) for _,b in planned)+len(root_bytes)+4096+COMPLETION_BYTES,'files':quota['files']+len(planned)+4+COMPLETION_FILES}
   if charged['bytes']>self.byte_quota or charged['files']>self.inode_quota:raise Refused('completion quota exhausted before admission')
   self._atomic('QUOTA',canonical(charged),'quota');self._sync('quota-dir');self.quota=charged
   for p,b in planned:self._immutable(p,b,'page')
   self._sync('pages-dir');self._immutable(nr,root_bytes,'manifest');self._sync('manifest-dir')
   self._atomic('CURRENT',canonical({'schema':1,'lifetime':self.lifetime,'root':nr}),'current');self._sync('root')
   self.root_ref=nr;self.root=root
   return {'newAdmission':True,'completionReserved':True}
  except Refused:raise
  except BaseException:self.poisoned=True;raise

 def append(self,*args,**kwargs):raise Refused('opaque append cannot mutate authority store')
