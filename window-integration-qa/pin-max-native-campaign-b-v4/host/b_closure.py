"""Separate B classification; original fixed A host evidence stays unchanged."""
from pathlib import Path
import hashlib,json,os,re,stat,sys,importlib.util
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
B=Path(__file__).resolve().parent.parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
registry=load('_b_closure_registry',B/'producer-registry/registry.py')
authority=load('_b_closure_original_authority',V2/'case_authority.py')
sys.path.insert(0,str(V2))
try:episode=load('_b_closure_original_episode',V2/'input_episode.py')
finally:sys.path.pop(0)
sys.path.insert(0,str(V2/'proposed'))
try:original=load('_b_closure_original_host_observation',V2/'proposed/host_observation.py')
finally:sys.path.pop(0)
exact=registry.exact;require=registry.require;BASE=['privateBus','weston','hyprland']

def strict(raw):
 def pairs(v):
  result={}
  for k,x in v:
   require(k not in result,'duplicate registry/raw metadata field');result[k]=x
  return result
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:require(False,'nonfinite registry/raw metadata'))
def publish(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as out:json.dump(value,out,indent=2,allow_nan=False);out.write('\n');out.flush();os.fsync(out.fileno())
 fd=os.open(Path(path).parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def identity(row):
 require(type(row)is dict and type(row.get('pid'))is int and row['pid']>0 and type(row.get('pgid'))is int and row['pgid']==row['pid']and type(row.get('start'))is str and re.fullmatch('[1-9][0-9]*',row['start'])is not None,'typed same selected PID/start/group')
 return [row['pid'],row['start'],row['pgid']]
def source(path,frozen):
 p=Path(path);s=p.lstat();key=str(p)
 require(stat.S_ISREG(s.st_mode)and type(frozen['inputModes'].get(key))is int and stat.S_IMODE(s.st_mode)==frozen['inputModes'][key]and registry.sha(p)==frozen['inputs'].get(key),'exact literal current frozen source')
 return dict(path=key,sha256=frozen['inputs'][key],mode=frozen['inputModes'][key])
def derive(selected,packet,sources,output):
 require(type(selected)is list and all(type(r)is dict for r in selected)and [r.get('name')for r in selected[:3]]==BASE,'exact original base registry')
 require(type(packet)is dict and packet.get('sealed')is True and type(packet.get('rows'))is list and 0<len(packet['rows'])<=256,'durable nonempty sealed B producer registry')
 rows=packet['rows'];require(len(selected)==3+len(rows),'no omitted/extra host registration')
 lives=[identity(r)for r in selected];require(len(set(tuple(v)for v in lives))==len(lives)and len(set(v[0]for v in lives))==len(lives),'unique selected lifetime/PGID')
 names=[];bindings=[]
 for row,registered in zip(rows,selected[3:],strict=True):
  require(type(row)is dict and row.get('kind')in {'qt','pointer','key'}and type(row.get('case'))is str and re.fullmatch(r'B(?:0[1-9]|1[0-2])',row['case'])is not None and type(row.get('ordinal'))is int and 1<=row['ordinal']<=64,'bounded known B source role')
  name='pin-'+row['case'].lower()+'-'+row['kind']+'-'+str(row['ordinal']);require(row.get('name')==name and name not in names,'unique exact reviewed role');names.append(name)
  kind=row['kind'];argv=row.get('argv')
  if kind=='qt':expected=[str(registry.FIXTURE),str(Path(output)/'actors'/row['case']/('qt-'+str(row['ordinal'])))]
  elif kind=='pointer':expected=[str(registry.POINTER),'1600','1000']
  else:
   require(type(argv)is list and len(argv)==3 and argv[2]=='super-p','only reviewed first-phase physical super-p route')
   expected=[str(registry.KEYBOARD),'--chord','super-p']
  require(exact(argv,expected)and exact(registered,row.get('registered'))and exact(registered.get('name'),name)and exact(registered.get('command'),expected),'exact full original registration/argv')
  require(exact(row.get('source'),sources.get(expected[0]))and row.get('forced')is False,'same frozen source/no forced cleanup')
  end=row.get('normalTerminal');require(type(end)is dict and type(end.get('pid'))is int and end['pid']==registered['pid']and type(end.get('returncode'))is int and end['returncode']==0 and end.get('gone')is True and exact(end.get('sourceAfter'),row['source']),'actual matching normal producer terminal')
  receipt=end.get('receipt');require(type(receipt)is dict,'typed genuine terminal receipt')
  if kind=='qt':
   require(receipt.get('kind')=='qt-quit'and type(receipt.get('pid'))is int and receipt['pid']==registered['pid']and type(receipt.get('commandEpoch'))is int and receipt['commandEpoch']>0 and receipt.get('commandHandled')is True,'same-lifetime genuine Qt quit')
   for key in ['eventLogSHA256','stateSHA256']:require(type(receipt.get(key))is str and re.fullmatch('[0-9a-f]{64}',receipt[key])is not None,'exact raw Qt artifact hash')
  elif kind=='pointer':
   require(receipt.get('kind')=='pointer-eof'and receipt.get('allButtonsReleased')is True and receipt.get('stdinClosed')is True,'normal pointer released EOF')
   authority.input_safe(receipt.get('finalNative',{}))
  else:
   require(receipt.get('kind')=='physical-chord'and receipt.get('route')=='super-p','exact physical terminal route')
   captured=authority.token(receipt.get('captured'));delivery=receipt.get('delivery');require(type(delivery)is dict and type(delivery.get('events'))is list,'complete raw physical delivery')
   require(exact(episode.episode([],delivery['events'],'super-p',captured),delivery),'original full actual core/Seat key delivery parser')
  bindings.append(dict(name=name,registered=registered,source=row['source'],normalTerminal=end))
 return bindings

def capture(host,selected):
 proof=dict(ok=False,error=None,beforeDelegatedClose=True,rawPersisted=False,bindings=[],rows=[],sources={})
 try:
  packet_path=host.output.parent/'native/producer-registry.json';s=packet_path.lstat()
  require(stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==os.getuid()and s.st_nlink==1 and 0<s.st_size<=16*1024*1024,'owned bounded literal raw registry')
  raw=packet_path.read_bytes();packet=strict(raw);copy=host.output/'b-producer-registry-before-close.json'
  fd=os.open(copy,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb')as out:out.write(raw);out.flush();os.fsync(out.fileno())
  proof.update(rawPersisted=True,registryPath=str(packet_path),registrySHA256=hashlib.sha256(raw).hexdigest(),rawArtifact=str(copy))
  frozen=host.b_frozen
  for p in [registry.FIXTURE,registry.POINTER,registry.KEYBOARD,B/'controller/minimal_controller.py',B/'producer-registry/registry.py',Path(__file__)]:proof['sources'][str(p)]=source(p,frozen)
  proof['bindings']=derive([dict(row)for _,row in selected],packet,proof['sources'],host.output.parent/'native')
  for proc,row in selected[3:]:
   item=dict(registered=dict(row),registeredExact=any(p is proc and r is row for p,r in host.processes),pid=proc.pid,returncode=proc.poll(),gone=not Path('/proc/'+str(proc.pid)).exists());proof['rows'].append(item)
   require(item['registeredExact']is True and type(item['pid'])is int and item['pid']==row['pid']and type(item['returncode'])is int and item['returncode']==0 and item['gone']is True,'before-stop already normal exact selected producer')
  for b in proof['bindings']:
   if b['name'].split('-')[2]!='qt':continue
   folder=Path(b['registered']['command'][1]);receipt=b['normalTerminal']['receipt']
   require(registry.sha(folder/'events.jsonl')==receipt['eventLogSHA256']and registry.sha(folder/'state.json')==receipt['stateSHA256'],'same final raw Qt artifacts')
   events=[strict(line)for line in (folder/'events.jsonl').read_bytes().splitlines()]
   require(any(e.get('event')=='commandHandled'and e.get('command')=='quit'and type(e.get('epoch'))is int and e['epoch']==receipt['commandEpoch']for e in events),'raw genuine same-epoch quit callback')
  require(packet_path.read_bytes()==raw,'registry stable across current before-close capture');proof['ok']=True
 except BaseException as error:proof['error']=repr(error)
 publish(host.output/'b-client-closure-before.json',proof);return proof

def classify(raw,proof):
 try:
  require(type(raw)is dict and raw.get('closeError')is None and type(raw.get('originalStopSeconds'))is int and raw['originalStopSeconds']==4 and type(raw.get('originalWaitSeconds'))is int and raw['originalWaitSeconds']==4,'exact inherited close/error/4s limits')
  require(type(proof)is dict and proof.get('ok')is True and proof.get('error')is None and proof.get('beforeDelegatedClose')is True and proof.get('rawPersisted')is True,'complete durable B before-close proof')
  rows=raw.get('rows');bindings=proof.get('bindings');pre=proof.get('rows')
  require(type(rows)is list and type(bindings)is list and type(pre)is list and all(type(v)is dict for v in rows+bindings+pre)and 0<len(bindings)<=256 and len(rows)==3+len(bindings)and len(pre)==len(bindings),'complete known host/producer rows')
  require([r.get('name')for r in rows[:3]]==BASE and all(original.normal_row(r)for r in rows[:3]),'strict unchanged core/Weston/bus normal closure')
  lives=[identity(r)for r in rows];require(len(set(tuple(v)for v in lives))==len(lives)and len(set(v[0]for v in lives))==len(lives),'no replaced or ambiguous lifetime')
  require(exact(raw.get('registeredStopOrder'),list(reversed([r['name']for r in rows]))),'exact complete reverse registration stop order')
  for row,binding,before in zip(rows[3:],bindings,pre,strict=True):
   for field in ['name','pid','start','pgid','command']:require(exact(row.get(field),binding['registered'].get(field))and exact(before['registered'].get(field),binding['registered'].get(field)),'same exact before/post registered producer')
   require(row.get('registeredExact')is True and row.get('reaped')is True and row.get('stopError')is None and type(row.get('returncode'))is int and row['returncode']==0 and exact(row.get('signals'),[]),'normal0/no-signals/no-error/reaped producer')
   require(before.get('registeredExact')is True and type(before.get('pid'))is int and before['pid']==row['pid']and type(before.get('returncode'))is int and before['returncode']==0 and before.get('gone')is True,'actual pre-close producer terminal')
  return True
 except (ValueError,KeyError,TypeError):return False

class BClosureMixin:
 def close(self):
  if not self.runtime:return super().close()
  selected=list(self.processes);proof=capture(self,selected);error=None
  try:return super().close()
  except BaseException as caught:error=repr(caught);raise
  finally:
   raw=self.evidence.get('ownedNormalClosure',{})
   outcome=dict(originalHostNormalClosure=str(self.output/'host-normal-closure.json'),originalHostNormalClosureSHA256=registry.sha(self.output/'host-normal-closure.json')if (self.output/'host-normal-closure.json').is_file()else None,before=proof,delegatedCloseError=error,normal=error is None and classify(raw,proof),scope='B producer closure classification only; original raw fixed-A classifier unchanged')
   self.evidence['campaignBNormalClosure']=outcome;publish(self.output/'b-host-normal-classification.json',outcome)
