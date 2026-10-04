import copy,hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sys.path.insert(0,str(ROOT/'adapter'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import daemon
from reconciliation import Reconciliation
from recovery_store import RecoveryStore
from retirement_ledger import ObservationJoin
from grant_endpoint import RetirementProof,NativeBinding
from durable_ledger import encoded
from admission_ledger import storage_key
from endpoint import Refused
OUT=ROOT/'qa'/('integration-'+str(time.time_ns()));OUT.mkdir();checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def command(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);check(name,p.returncode==0);return p.stdout
try:
 frontend=REPO/'implementation/elm-reconciliation-accepted-read-v619'
 inputs=OUT/'inputs';shutil.copytree(frontend/'src',inputs/'src');shutil.copy2(frontend/'elm.json',inputs/'elm.json');shutil.copy2(frontend/'qa/Probe.elm',inputs/'src/Probe.elm')
 command('compile-actual619-public-controller',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--optimize','--output='+str(OUT/'worker.js')],inputs)
 captured=REPO/'implementation/elm-recovery-context-feedback-v592/qa/replay-1791146043447506188/captured-frames.json'
 shutil.copy2(captured,OUT/'captured573.json');templates={item['frame']['kind']:item['frame'] for item in json.loads(captured.read_text())}
 OLD=copy.deepcopy(templates['attached']['binding']);NOW={**OLD,'frontend':'2'};NEW={**OLD,'frontend':'3'}
 record={'schema':2,'effectProtocol':1,'binding':OLD,'intent':copy.deepcopy(templates['host-uncertain']['intent']),'status':'Unknown'}
 native=lambda f:{'kind':'native','frame':copy.deepcopy(f)}
 def read(kind,number,bound):
  f=copy.deepcopy(templates[kind]);f['binding']=copy.deepcopy(bound);f['requestId']=str(number)
  if kind=='action-projection':f['context'].update(lifetime=bound['lifetime'],epoch=bound['frontend'])
  if kind=='geometry-facts':f['sequence']=str(int(f['sequence'])+int(number))
  return f
 def attached(bound):return {**copy.deepcopy(templates['attached']),'binding':copy.deepcopy(bound)}
 events=[native(attached(NOW)),native(read('action-projection',1,NOW)),native(templates['host-geometry-negotiate']),native(read('geometry-attached',2,NOW)),native(read('geometry-facts',3,NOW))]
 probes=[0]
 def probe(label):
  probes[0]+=1;name=str(probes[0])+'-'+label;path=OUT/(name+'-events.json');path.write_text(json.dumps(events,indent=2));target=OUT/(name+'-rows.json')
  command(name,['node',str(frontend/'qa/probe.cjs'),str(OUT/'worker.js'),str(path),str(target)])
  return json.loads(target.read_text())[-1]
 flags=shlex.split(command('flags',['pkg-config','--cflags','--libs','json-glib-1.0']))
 command('actual-C-admissions-build',['cc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function',str(ROOT/'native/admission-test.c'),'-o',str(OUT/'admission-test'),*flags])
 runtime=OUT/'runtime';runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
 def host(records):
  requests=[{'protocolVersion':3,'kind':'window-effect','effectProtocol':r['effectProtocol'],'binding':r['binding'],'intent':r['intent']} for r in records]
  command('C-admit-'+str(len(checks)),[str(OUT/'admission-test'),str(config),json.dumps(requests),json.dumps(records[0]['binding'])])
 class Client(daemon.Endpoint):
  def __init__(self,bound,sequence):self.bound=copy.deepcopy(bound);self._grant_watermarks={};self.sequence=sequence;self.requests=[]
  def request(self,r):
   self.sequence+=1;self.requests.append(copy.deepcopy(r))
   return {'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'retire','binding':copy.deepcopy(self.bound),'queriedBinding':copy.deepcopy(r['queriedBinding']),'requestId':r['requestId'],'sequence':str(self.sequence),'grantState':'Retired'}
 host([record]);store=RecoveryStore(str(runtime),'Test',OLD['lifetime']);client=Client(NOW,100);lost=[];wire=[]
 def fail_release(frame):
  if frame['kind']=='host-reservation-released':lost.append(copy.deepcopy(frame));raise daemon.OutputFailure('synthetic lost release delivery')
  wire.append(copy.deepcopy(frame));events.append(native(frame))
 c=Reconciliation(client,store.ledger,fail_release);c.announce();row=probe('initial-proof')
 check('compiled619 requests ready before fresh independent reads',[r['kind'] for r in row['wires']]==['reconciliation-ready','projection-request','geometry-facts-request'])
 def complete(c,row,bound,label,fail=False):
  requests=row['wires'];c.proof_ready(requests[0])
  for domain,request in [('action',requests[1]),('geometry',requests[2])]:
   c.requested_read(domain,request['requestId']);frame=read('action-projection' if domain=='action' else 'geometry-facts',request['requestId'],bound)
   events.append(native(frame));accepted=probe(label+'-'+domain)
   context=frame['context'] if domain=='action' else {'lifetime':bound['lifetime'],'epoch':bound['frontend'],'output':frame['outputGeneration'],'revision':frame['revision']}
   try:c.delivered_read(domain,request['requestId'],context)
   except daemon.OutputFailure:
    if not fail:raise
    check('lost wire propagates after accepted read',domain=='geometry');return accepted
  return accepted
 before=complete(c,row,NOW,'lost',True);state=store.ledger.snapshot();original=copy.deepcopy(state['releases'][0]);first=store.ledger.delivery_snapshot()['certificates'][0]
 check('original release and first certificate durable despite lost wire',len(lost)==1 and original['phase']=='Released' and first['anchorId']==original['id'] and lost[0]['release']['id']==first['id'])
 check('same Elm view retains Unknown reservation after lost release',before['blocked'] and before['unresolved']==1 and before['history'][0]['status']=='Unknown')
 check('original durable live reservation already released',state['entries']==[] and not store.ledger.blocked(OLD['lifetime'],'2'))
 bytes_before=(store.path/'ledger-v6.json').read_bytes();store.close()
 # Continue the SAME public controller trajectory across disconnect/reconnect;
 # no reinitialization event or fabricated old release is introduced.
 events.extend([native({'protocolVersion':3,'kind':'host-disconnected'}),{'kind':'reconnect'},native(attached(NEW))]);row=probe('same-view-reconnect')
 action_request=next(r for r in row['wires'] if r['kind']=='projection-request')['requestId']
 events.extend([native(read('action-projection',action_request,NEW)),native(templates['host-geometry-negotiate'])]);row=probe('fresh-geometry-negotiate')
 attach_request=next(r for r in row['wires'] if r['kind']=='geometry-attach')['requestId'];events.append(native(read('geometry-attached',attach_request,NEW)));row=probe('fresh-geometry-attach')
 geometry_request=next(r for r in row['wires'] if r['kind']=='geometry-facts-request')['requestId'];events.append(native(read('geometry-facts',geometry_request,NEW)))
 probe('fresh-initial-geometry')
 store=RecoveryStore(str(runtime),'Test',OLD['lifetime']);client=Client(NEW,200);wire=[]
 def send(frame):
  if frame['kind']=='host-reservation-released':
   cert=store.ledger.delivery_snapshot()['certificates'][0]
   check('fresh release wire follows durable certificate',frame['release']['id']==cert['id'] and cert['anchorId']==original['id'])
  wire.append(copy.deepcopy(frame));events.append(native(frame))
 c=Reconciliation(client,store.ledger,send);c.announce();row=probe('historical-reannounce')
 check('reopened broker reannounces exact historical Unknown',wire[0]['record']==record and wire[1]['kind']=='binding-retirement' and store.ledger.snapshot()['entries']==[])
 check('historical record is not inferred Committed',row['blocked'] and row['history'][0]['status']=='Unknown')
 complete(c,row,NEW,'fresh',False);after=probe('fresh-delivery-received');latest=store.ledger.delivery_snapshot()['certificates'][0]
 check('compiled619 fresh delivery settles same-view UI reservation',not after['blocked'] and after['unresolved']==0 and after['history']==[{'binding':OLD,'status':'Unknown','released':True}])
 check('fresh delivery clears no outcome truth or counters',after['transaction']['transaction']['status']=='Unknown' and after['effectRequest']==before['effectRequest'] and after['effectGeneration']==before['effectGeneration'] and after['wires']==[])
 check('new certificate retains original anchor without rebinding oldproof',latest['anchorId']==original['id'] and latest['proof']['binding']==NEW and latest['id']!=first['id'] and store.ledger.snapshot()['releases']==[original] and (store.path/'ledger-v6.json').read_bytes()==bytes_before)
 check('no automatic effects across either broker',all(r['kind']=='binding-retire-request' for r in client.requests))
 # A foreign fresh release proof/read must remain refused by the strict public
 # decoder; the certificate anchor is intentionally not an extra wire field.
 actual_release=wire[-1];events.pop();mutant=copy.deepcopy(actual_release);mutant['release']['anchorId']=original['id'];events.append(native(mutant));bad=probe('extra-anchor-refused')
 check('wire extra anchor forbidden and UI reservation remains',bad['blocked'] and bad['unresolved']==1);events.pop();events.append(native(actual_release));probe('strict-trio-restored')
 # New unrelated live same-target record survives historical redelivery.
 live=copy.deepcopy(record);live['binding']=NEW;live['intent'].update(request='13',generation='13');live['intent']['context']['epoch']=NEW['frontend'];host([live]);store.ledger.synchronization_snapshot();live_state=store.ledger.snapshot()
 proof=RetirementProof(NativeBinding.parse(NEW),NativeBinding.parse(OLD),'9','300','observe','Retired');j=ObservationJoin(record,proof)
 for domain,request,revision in [('action','90','22'),('geometry','91','29')]:j.expect(domain,request);j.accept(domain,request,NEW,{'lifetime':NEW['lifetime'],'epoch':NEW['frontend'],'output':'7','revision':revision})
 store.ledger.attest(j)
 check('historical reattestation leaves new same-target live Unknown',store.ledger.snapshot()==live_state and store.ledger.blocked(OLD['lifetime'],'2') and (store.path/'admissions-v1'/(storage_key(live)+'.json')).exists())
 store.close()
 # Fault the REAL sidecar file barrier in the actual coordinator path. Parent
 # release is already immutable; storage failure cannot acknowledge UI release.
 fault_runtime=OUT/'runtime-fault';shutil.copytree(runtime,fault_runtime)
 store=RecoveryStore(str(fault_runtime),'Test',OLD['lifetime']);client=Client(NEW,400);notices=[];c=Reconciliation(client,store.ledger,notices.append);c.announce();p=c.active
 ready={'protocolVersion':3,'kind':'reconciliation-ready','binding':NEW,'queriedBinding':p.queried_binding.as_dict(),'proofRequestId':p.request_id};c.proof_ready(ready)
 for domain,request in [('action','92'),('geometry','93')]:c.requested_read(domain,request)
 c.delivered_read('action','92',{'lifetime':NEW['lifetime'],'epoch':NEW['frontend'],'output':'7','revision':'22'})
 fsync=os.fsync;faulted=[]
 def failed_file_barrier(fd):
  if '/delivery-pending-' in os.readlink('/proc/self/fd/'+str(fd)):faulted.append(True);raise OSError('synthetic certificate fsync EIO')
  return fsync(fd)
 with patch.object(os,'fsync',failed_file_barrier):
  try:c.delivered_read('geometry','93',{'lifetime':NEW['lifetime'],'epoch':NEW['frontend'],'output':'7','revision':'29'})
  except OSError:check('real certificate fsync failure propagates',faulted==[True])
  else:check('real certificate fsync failure propagates',False)
 check('failed attestation cannot publish release and poisons writer',store.ledger.poisoned and not any(f['kind']=='host-reservation-released' for f in notices))
 store.close();store=RecoveryStore(str(fault_runtime),'Test',OLD['lifetime'])
 check('fault reopen preserves original archive and unrelated live reservation',store.ledger.snapshot()['releases']==[original] and store.ledger.snapshot()['entries']==live_state['entries'] and store.ledger.blocked(OLD['lifetime'],'2'))
 store.close()
 # Capacity is checked before even the first partial announcement or proof.
 class Oversized:
  def synchronization_snapshot(self):
   entries=[]
   for n in range(1,65):
    r=copy.deepcopy(live);r['intent'].update(request=str(n),generation=str(n),incarnation=str(n));entries.append(r)
   return {'entries':entries,'releases':[copy.deepcopy(original)]}
 notices=[];client=Client(NEW,400);oversized=Reconciliation(client,Oversized(),notices.append)
 try:oversized.announce()
 except Refused:check('combined65 capacity refuses before any announcement/proof',not notices and not client.requests)
 else:check('combined65 capacity refuses before any announcement/proof',False)
 (OUT/'lost-wire.json').write_text(json.dumps(lost,indent=2));(OUT/'original-release.json').write_text(json.dumps(original,indent=2));(OUT/'fresh-certificate.json').write_text(json.dumps(latest,indent=2))
 report={'passed':True,'assertions':len(checks),'checks':checks,'nativeAcceptance':False,'nativeAuthentication':False,'frontendNativeDelivery':False,'powerLossSimulation':False,'claim':'Actual C admissions, Python coordinator/624filesystem; actual compiled619 public controller same-view lost-output/reconnect trajectory with synthetic proof/read transports; oversized combined capacity control synthetic',
  'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()},'compiled619SourceSHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (frontend/'src').glob('*.elm')}}
except BaseException as error:report={'passed':False,'checks':checks,'error':repr(error)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
