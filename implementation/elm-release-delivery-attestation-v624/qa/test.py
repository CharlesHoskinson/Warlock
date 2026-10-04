import copy,hashlib,json,os,pathlib,resource,stat,subprocess,sys,time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from delivery_ledger import DeliveryLedger,NAME,MARKER
from retirement_ledger import ObservationJoin
from grant_endpoint import RetirementProof,NativeBinding
from admission_ledger import storage_key
from durable_ledger import encoded
from endpoint import Refused

OLD={'lifetime':'19','session':'1','frontend':'1'}
NOW={'lifetime':'19','session':'2','frontend':'1'}
NEW={'lifetime':'19','session':'3','frontend':'2'}
def record(bound=OLD,number='12',target='2'):
 return {'schema':2,'effectProtocol':1,'binding':copy.deepcopy(bound),'status':'Unknown','intent':{'request':number,'generation':number,'incarnation':target,'operation':'minimize','context':{'lifetime':'19','epoch':bound['frontend'],'output':'7','revision':'21'}}}
def join(r=None,bound=NOW,sequence='19',number='3'):
 r=r or record();proof=RetirementProof(NativeBinding.parse(bound),NativeBinding.parse(r['binding']),number,sequence,'observe','Retired')
 value=ObservationJoin(r,proof)
 for domain,request,revision in [('action','91','22'),('geometry','37','29')]:
  value.expect(domain,request);value.accept(domain,request,bound,{'lifetime':'19','epoch':bound['frontend'],'output':'7','revision':revision})
 return value
def child(runtime,stop,mode):
 ledger=DeliveryLedger(runtime,'Test','19');events=[];saved={n:getattr(os,n) for n in ['fsync','replace']}
 def wrap(name):
  def call(*args,**kwargs):
   if mode=='before' and len(events)+1==int(stop):events.append(name);raise OSError('precall '+name)
   result=saved[name](*args,**kwargs);events.append(name)
   if len(events)==int(stop):
    if mode=='crash':os._exit(73)
    raise OSError('aftercall '+name)
   return result
  return call
 try:
  with patch.multiple(os,**{n:wrap(n) for n in saved}):ledger.attest(join(bound=NEW,sequence='20'))
 except OSError:
  assert ledger.poisoned
  for fn in [ledger.snapshot,ledger.delivery_snapshot,lambda:ledger.attest(join(bound=NEW,sequence='21'))]:
   try:fn()
   except Refused:pass
   else:raise AssertionError('Failed storage acknowledged state')
  ledger.close();return 74
 ledger.close();return 0
if len(sys.argv)>1 and sys.argv[1]=='child':raise SystemExit(child(*sys.argv[2:]))

OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir();checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
def denied(name,fn):
 try:fn()
 except (Refused,OSError,ValueError):check(name,True)
 else:check(name,False)
def command(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=120)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 check(name,p.returncode==0);return p
try:
 inherited=command('unchanged608-driver',[sys.executable,'-B',str(ROOT/'qa/inherited608.py')])
 inherited_path=pathlib.Path(inherited.stdout.strip().splitlines()[-1]);inherited_report=json.loads(inherited_path.read_text())
 check('inherited608 driver passed',inherited_report['passed'])
 flags=command('pkg-config',['pkg-config','--cflags','--libs','json-glib-1.0']).stdout.split()
 command('actual608-C-producer-compiles',['cc','-std=gnu11','-O2',str(ROOT/'native/admission-test.c'),'-o',str(OUT/'admission-test'),*flags])
 def host(runtime,r):
  config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
  request={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':r['binding'],'intent':r['intent']}
  p=subprocess.run([str(OUT/'admission-test'),str(config),json.dumps([request]),json.dumps(r['binding'])],capture_output=True,text=True)
  check('actual C admission '+runtime.name+' '+r['intent']['request'],p.returncode==0)
 def setup(name):
  runtime=OUT/name;runtime.mkdir(mode=0o700);host(runtime,record());ledger=DeliveryLedger(str(runtime),'Test','19')
  anchor=ledger.release(join());return runtime,ledger,anchor
 runtime,ledger,anchor=setup('reconnect')
 before=(ledger.path/'ledger-v6.json').read_bytes();original=ledger.snapshot()
 cert=ledger.attest(join()) # Deliberately lose this output; no sender exists here.
 check('delivery certificate anchors exact original release',cert['anchorId']==anchor['id'] and cert['record']==record() and cert['proof']==anchor['proof'])
 check('certificate hash binds anchor and fresh payload',cert['id']==hashlib.sha256(encoded({k:v for k,v in cert.items() if k!='id'})).hexdigest())
 check('delivery sidecar private single link',stat.S_IMODE((ledger.path/NAME).stat().st_mode)==0o600 and (ledger.path/NAME).stat().st_nlink==1)
 check('initial attestation preserves parent V6 exact bytes',(ledger.path/'ledger-v6.json').read_bytes()==before and ledger.snapshot()==original)
 check('exact payload attestation idempotent',ledger.attest(join())==cert)
 ledger.close();ledger=DeliveryLedger(str(runtime),'Test','19')
 fresh=join(bound=NEW,sequence='20',number='4');fresh.requested['action']='92';fresh.requested['geometry']='38'
 updated=ledger.attest(fresh)
 check('new current binding produces fresh anchored delivery',updated['anchorId']==anchor['id'] and updated['proof']['binding']==NEW and updated['observation']['actionRequestId']=='92' and updated['id']!=cert['id'])
 check('bounded latest delivery replaces old hotcache only',ledger.delivery_snapshot()['certificates']==[updated] and ledger.snapshot()==original and (ledger.path/'ledger-v6.json').read_bytes()==before)
 denied('stale sequence cannot replace latest certificate',lambda:ledger.attest(join(bound=NEW,sequence='19')))
 changed=join(bound=NEW,sequence='20');changed.requested['action']='93'
 denied('same sequence different payload cannot replace certificate',lambda:ledger.attest(changed))
 wrong=record();wrong['intent']['context']['revision']='20'
 denied('wrong exact Unknown cannot attest',lambda:ledger.attest(join(wrong,bound=NEW,sequence='21')))
 for state in ['Registered','Future']:
  proof=RetirementProof(NativeBinding.parse(NEW),NativeBinding.parse(OLD),'5','21','observe',state)
  denied(state+' proof cannot create join',lambda proof=proof:ObservationJoin(record(),proof))
 rejected=join(bound=NEW,sequence='21');rejected.proof['kind']='error'
 denied('refused malformed native proof cannot attest',lambda:ledger.attest(rejected))
 partial=join(bound=NEW,sequence='21');partial.accepted.pop('geometry')
 denied('one accepted domain cannot attest',lambda:ledger.attest(partial))
 # A new explicit effect reservation can use the same target after the old
 # retirement. Delivery attestation must neither remove nor settle that record.
 live=record(NEW,'13');host(runtime,live);check('new same-target request admitted',ledger.begin(NEW,live['intent']))
 state=ledger.snapshot();live_before=(ledger.path/'ledger-v6.json').read_bytes()
 ledger.attest(join(bound=NEW,sequence='21',number='6'))
 check('unrelated same-target live reservation untouched',ledger.snapshot()==state and (ledger.path/'ledger-v6.json').read_bytes()==live_before and ledger.blocked('19','2') and (ledger.path/'admissions-v1'/(storage_key(live)+'.json')).exists())
 denied('live unreleased Unknown has no delivery anchor',lambda:ledger.attest(join(live,bound=NOW,sequence='22')))
 cache=ledger.delivery_snapshot()
 for field,value in [('sequence','0'),('sequence',True),('requestId','01'),('grantState','Future')]:
  malformed=join(bound=NEW,sequence='22');malformed.proof[field]=value
  denied('delivery input rejects '+field+' '+str(value),lambda malformed=malformed:ledger.attest(malformed))
 check('invalid input preserves latest cache and live state',ledger.delivery_snapshot()==cache and ledger.snapshot()==state and not ledger.poisoned)
 mutated=copy.deepcopy(cache);mutated['certificates']=[copy.deepcopy(cache['certificates'][0]) for _ in range(65)]
 denied('sidecar count65 refuses before certificate traversal',lambda:ledger._delivery_validate(mutated,state))
 committed=record();committed['status']='Committed'
 denied('definitive record cannot be reclassified as delivery Unknown',lambda:join(committed,bound=NEW,sequence='22'))
 ledger.close()

 runtime=OUT/'per-record';runtime.mkdir(mode=0o700);other=record(OLD,'13','3')
 host(runtime,record());host(runtime,other);ledger=DeliveryLedger(str(runtime),'Test','19')
 first_anchor=ledger.release(join());second_anchor=ledger.release(join(other))
 first=ledger.attest(join(bound=NEW,sequence='20'));second=ledger.attest(join(other,bound=NEW,sequence='21'))
 before_parent=(ledger.path/'ledger-v6.json').read_bytes();replacement=ledger.attest(join(bound=NEW,sequence='22'))
 check('latest certificate is independent per historical record',ledger.delivery_snapshot()['certificates']==[replacement,second] and second['anchorId']==second_anchor['id'] and replacement['anchorId']==first_anchor['id'])
 check('cache replacement does not rewrite either immutable anchor',(ledger.path/'ledger-v6.json').read_bytes()==before_parent and ledger.snapshot()['releases']==[first_anchor,second_anchor]);ledger.close()

 # Unsafe/missing/corrupt sidecars and markers fail closed on reopening.
 for case in ['symlink','hardlink','public','duplicateJSON','missing','marker-missing','marker-bool','marker-extra','foreign-anchor','duplicate-certificate','schema-bool']:
  runtime,ledger,anchor=setup('unsafe-'+case);ledger.attest(join());path=ledger.path/NAME;mark=ledger.path/MARKER;ledger.close()
  if case=='symlink':saved=path.with_name('held.json');path.rename(saved);path.symlink_to(saved.name)
  elif case=='hardlink':os.link(path,path.with_name('held.json'))
  elif case=='public':path.chmod(0o644)
  elif case=='missing':path.unlink()
  elif case=='marker-missing':mark.unlink()
  elif case=='duplicateJSON':path.write_bytes(b'{"schema":1,"schema":1,"lifetime":"19","certificates":[]}')
  elif case.startswith('marker'):
   value=json.loads(mark.read_text());value['schema']=True if case=='marker-bool' else 1
   if case=='marker-extra':value['extra']=1
   mark.write_bytes(encoded(value))
  else:
   value=json.loads(path.read_text())
   if case=='foreign-anchor':value['certificates'][0]['anchorId']='0'*64
   elif case=='duplicate-certificate':value['certificates'].append(copy.deepcopy(value['certificates'][0]))
   elif case=='schema-bool':value['schema']=True
   path.write_bytes(encoded(value))
  denied('unsafe sidecar refused '+case,lambda runtime=runtime:DeliveryLedger(str(runtime),'Test','19'))

 # Real partial writes succeed; interrupted/zero writes and cleanup failures
 # never produce a positive return and poison every inherited/read entry point.
 runtime,ledger,anchor=setup('partial-writes');saved=os.write;calls=[]
 def partial_write(fd,raw):calls.append(len(raw));return saved(fd,raw[:7])
 with patch.object(os,'write',partial_write):cert=ledger.attest(join(bound=NEW,sequence='20'))
 check('partial writes loop to exact certificate',len(calls)>2 and ledger.delivery_snapshot()['certificates']==[cert]);ledger.close()
 for case in ['zero-write','write-error','cleanup-error','close-error']:
  runtime,ledger,anchor=setup(case);saved_write=os.write;saved_unlink=os.unlink;saved_close=os.close
  def bad_write(fd,raw):
   if case=='zero-write':return 0
   if case=='write-error':raise OSError('write EIO')
   return saved_write(fd,raw)
  def bad_unlink(name,*a,**kw):
   if case=='cleanup-error' and str(name).startswith('delivery-pending-'):raise OSError('cleanup EIO')
   return saved_unlink(name,*a,**kw)
  def bad_close(fd):
   # Fail only the temporary certificate close, not inherited host locks.
   destination=os.readlink('/proc/self/fd/'+str(fd))
   if case=='close-error' and '/delivery-pending-' in destination:saved_close(fd);raise OSError('close EIO')
   return saved_close(fd)
  with patch.multiple(os,write=bad_write,unlink=bad_unlink,close=bad_close):denied('storage failure has no attestation '+case,lambda:ledger.attest(join(bound=NEW,sequence='20')))
  check('storage failure poisons '+case,ledger.poisoned)
  denied('poison refuses inherited snapshot '+case,ledger.snapshot)
  denied('poison refuses delivery snapshot '+case,ledger.delivery_snapshot)
  denied('poison refuses attestation '+case,lambda:ledger.attest(join(bound=NEW,sequence='21')))
  ledger.close();ledger=DeliveryLedger(str(runtime),'Test','19')
  check('reopen storage failure keeps original archive '+case,ledger.snapshot()['releases']==[anchor]);ledger.close()

 for mode in ['crash','after','before']:
  for stop in range(1,7):
   runtime,ledger,anchor=setup(mode+'-'+str(stop));parent_bytes=(ledger.path/'ledger-v6.json').read_bytes();path=ledger.path;ledger.close()
   p=subprocess.run([sys.executable,'-B',str(__file__),'child',str(runtime),str(stop),mode],capture_output=True,text=True,timeout=30)
   (OUT/(mode+'-'+str(stop)+'.stderr')).write_text(p.stderr)
   check('interruption has no ack '+mode+str(stop),p.returncode==(73 if mode=='crash' else 74))
   saved_fsync=os.fsync;restart=[]
   def logged(fd):restart.append(stat.S_ISDIR(os.fstat(fd).st_mode));return saved_fsync(fd)
   with patch.object(os,'fsync',logged):ledger=DeliveryLedger(str(runtime),'Test','19');recovered=ledger.delivery_snapshot()
   check('restart barrier before positive exposure '+mode+str(stop),restart and restart[0] is True)
   visible=stop>=5 if mode!='before' else stop>=6
   check('restart sidecar exact visibility '+mode+str(stop),len(recovered['certificates'])==(1 if visible else 0))
   check('crash never rewrites original parent archive '+mode+str(stop),(path/'ledger-v6.json').read_bytes()==parent_bytes and ledger.snapshot()['releases']==[anchor] and ledger.snapshot()['entries']==[])
   cert=ledger.attest(join(bound=NEW,sequence='20'))
   check('explicit retry persists same fresh certificate '+mode+str(stop),ledger.delivery_snapshot()['certificates']==[cert]);ledger.close()

 report={'passed':True,'assertions':len(checks),'checks':checks,'inherited608Report':str(inherited_path.relative_to(ROOT)),'inherited608Assertions':inherited_report['assertions'],'nativeAcceptance':False,'nativeAuthentication':False,'powerLossSimulation':False,'productionWired':False,'claim':'Real isolated filesystem and unchanged608 compiled C admissions; synthetic constructable typed proofs/accepted contexts; crash-visible restart and pre/post-call storage faults',
  'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()}}
except BaseException as error:report={'passed':False,'checks':checks,'error':repr(error)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
