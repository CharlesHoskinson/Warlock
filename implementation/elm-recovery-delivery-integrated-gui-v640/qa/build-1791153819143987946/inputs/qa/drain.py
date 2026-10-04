import copy,hashlib,json,pathlib,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-recovery-delivery-integration-v630';PACK=SOURCE/'qa/integration-1791152781571263529';OUT=ROOT/'qa'/('drain-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(SOURCE/'adapter'))
from reconciliation import Reconciliation
from recovery_store import RecoveryStore
from grant_endpoint import RetirementProof,NativeBinding
from retirement_ledger import ObservationJoin
checks=[];commands=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
PRIMARY=max((ROOT/'qa').glob('tests-*/report.json')).parent;worker=PRIMARY/'worker.js';inputs=PRIMARY/'inputs/src'
for p in (ROOT/'src').glob('*.elm'):assert sha(p)==sha(inputs/p.name)
events=json.loads((PACK/'13-strict-trio-restored-events.json').read_text());templates={r['frame']['kind']:r['frame'] for r in json.loads((PACK/'captured573.json').read_text())};native=lambda f:{'kind':'native','frame':copy.deepcopy(f)}
def probe(name):
 inp=OUT/(name+'-events.json');out=OUT/(name+'-rows.json');inp.write_text(json.dumps(events,indent=2)+'\n');cmd=['node',str(ROOT/'qa/probe.cjs'),str(worker),str(inp),str(out)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=15);(OUT/(name+'.log')).write_text(p.stdout+p.stderr);commands.append({'name':name,'command':cmd,'exit':p.returncode});assert p.returncode==0;return json.loads(out.read_text())[-1]
try:
 check('held-corrected-compiled-inputs-match-all-production-source',all(sha(p)==sha(inputs/p.name) for p in (ROOT/'src').glob('*.elm')))
 initial=probe('initial-local-A-released');check('A-already-released-before-reconnect',initial['unresolved']==0 and initial['history'][0]['released'])
 runtime=OUT/'runtime';shutil.copytree(PACK/'runtime',runtime);original=json.loads((PACK/'original-release.json').read_text());OLD=original['record']['binding'];current=events[-1]['frame']['binding'];nextbound={**current,'frontend':'4'};store=RecoveryStore(str(runtime),'Test',OLD['lifetime'])
 live=copy.deepcopy(store.ledger.snapshot()['entries'][0]);check('historical-C-produced-live-same-target-fixture',live['intent']['incarnation']==original['record']['intent']['incarnation'] and live!=original['record'])
 j=ObservationJoin(live,RetirementProof(NativeBinding.parse(nextbound),NativeBinding.parse(live['binding']),'80','800','retire','Retired'))
 for d,r in [('action','81'),('geometry','82')]:j.expect(d,r);j.accept(d,r,nextbound,{'lifetime':nextbound['lifetime'],'epoch':nextbound['frontend'],'output':'1','revision':'21'})
 store.ledger.release(j);anchors=copy.deepcopy(store.ledger.snapshot()['releases']);check('second-live-origin-durably-released-without-UI-delivery',len(anchors)==2 and store.ledger.snapshot()['entries']==[])
 events.append(native({'protocolVersion':3,'kind':'host-reservation-unknown','binding':current,'record':live}));row=probe('mixed-A-released-B-retained-Unknown');check('mixed-UI-one-released-one-still-reserved',len(row['history'])==2 and sum(r['released'] for r in row['history'])==1 and row['unresolved']==1)
 counter_before=(row['effectRequest'],row['effectGeneration']);serial=[]
 class Client:
  def __init__(self,bound,seq):self.bound=copy.deepcopy(bound);self.seq=seq;self.requests=[]
  def retire(self,r,b):self.seq+=1;self.requests.append((r,copy.deepcopy(b)));return RetirementProof(NativeBinding.parse(self.bound),NativeBinding.parse(b),r,str(self.seq),'retire','Retired')
 def read(kind,id,bound):
  f=copy.deepcopy(templates[kind]);f.update(binding=copy.deepcopy(bound),requestId=id)
  if kind=='action-projection':f['context'].update(lifetime=bound['lifetime'],epoch=bound['frontend'])
  if kind=='geometry-facts':f['sequence']=str(int(f['sequence'])+int(id))
  return f
 def reconnect(bound,label):
  events.extend([native({'protocolVersion':3,'kind':'host-disconnected'}),{'kind':'reconnect'},native({**templates['attached'],'binding':bound})]);row=probe(label+'-attached');a=next(w for w in row['wires'] if w['kind']=='projection-request')['requestId'];events.extend([native(read('action-projection',a,bound)),native(templates['host-geometry-negotiate'])]);row=probe(label+'-negotiate');g=next(w for w in row['wires'] if w['kind']=='geometry-attach')['requestId'];events.append(native(read('geometry-attached',g,bound)));row=probe(label+'-geometryattached');g=next(w for w in row['wires'] if w['kind']=='geometry-facts-request')['requestId'];events.append(native(read('geometry-facts',g,bound)));return probe(label+'-initial-reads')
 def run_scopes(bound,seq,label):
  client=Client(bound,seq)
  def send(frame):
   if frame['kind']=='host-reservation-released':
    cert=next(v for v in store.ledger.delivery_snapshot()['certificates'] if v['record']==frame['record']);check(label+'-persisted-certificate-before-wire-'+frame['record']['intent']['request'],frame['release']=={k:cert[k] for k in ['id','proof','observation']})
   events.append(native(frame));serial.append(copy.deepcopy(frame))
  c=Reconciliation(client,store.ledger,send);c.announce();row=probe(label+'-announced');turn=0
  while c.active is not None:
   turn+=1;assert turn<=2;ready=next(w for w in row['wires'] if w['kind']=='reconciliation-ready');check(label+'-scope'+str(turn)+'-ready-before-reads',[w['kind'] for w in row['wires']]==['reconciliation-ready','projection-request','geometry-facts-request']);c.proof_ready(ready)
   pair=[w for w in row['wires'] if w['kind'] in ['projection-request','geometry-facts-request']]
   for d,w in zip(['action','geometry'],pair):
    c.requested_read(d,w['requestId']);f=read('action-projection' if d=='action' else 'geometry-facts',w['requestId'],bound);events.append(native(f));probe(label+'-turn'+str(turn)+'-'+d);ctx=f['context'] if d=='action' else {'lifetime':bound['lifetime'],'epoch':bound['frontend'],'output':f['outputGeneration'],'revision':f['revision']};c.delivered_read(d,w['requestId'],ctx)
   row=probe(label+'-after-turn'+str(turn))
   if label=='mixed' and turn==1:check('informational-A-does-not-unblock-unrelated-B-or-reblock-A',row['unresolved']==1 and len(row['history'])==2 and sum(v['released'] for v in row['history'])==1)
  check(label+'-all-serial-scopes-complete',not(c.pending) and turn==2 and len(client.requests)==2)
  check(label+'-no-effect-counter-change-or-outcome-invention',(row['effectRequest'],row['effectGeneration'])==counter_before and all(v['status']=='Unknown' and v['released'] for v in row['history']) and row['unresolved']==0)
  check(label+'-immutable-original-archives-conserved',store.ledger.snapshot()['releases']==anchors)
  return row
 reconnect(nextbound,'mixed');run_scopes(nextbound,1000,'mixed')
 # Reopen actual store and repeat with both UI origins already delivered.
 store.close();store=RecoveryStore(str(runtime),'Test',OLD['lifetime']);again={**nextbound,'frontend':'5'};reconnect(again,'repeat');run_scopes(again,2000,'repeat');check('second-restart-sidecar-still-exactly-two-current-anchored-certificates',len(store.ledger.delivery_snapshot()['certificates'])==2 and all(c['proof']['binding']==again and any(c['anchorId']==a['id'] and c['record']==a['record'] for a in anchors) for c in store.ledger.delivery_snapshot()['certificates']));store.close()
 (OUT/'serial-wire.json').write_text(json.dumps(serial,indent=2)+'\n');report={'passed':True,'assertions':len(checks),'checks':checks,'commands':commands,'nativeAcceptance':False,'nativeAuthentication':False,'newCExecution':False,'powerLossSimulation':False,'scope':'Actual630 coordinator/624 filesystem sidecar and newly compiled642 public controller with synthetic typed proof/read transport; copied historical C admission fixture','sourceHashes':{str(p):sha(p) for p in [SOURCE/'adapter/reconciliation.py',SOURCE/'adapter/delivery_ledger.py',worker,pathlib.Path(__file__)]},'frontendSourceHashes':{p.name:sha(p) for p in (ROOT/'src').glob('*.elm')}}
except BaseException as e:report={'passed':False,'error':repr(e),'checks':checks,'commands':commands};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
