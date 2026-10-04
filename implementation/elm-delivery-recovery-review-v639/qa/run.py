import copy,hashlib,json,pathlib,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-recovery-delivery-integration-v630';FRONT=REPO/'implementation/elm-reconciliation-accepted-read-v619';PACK=SOURCE/'qa/integration-1791152781571263529';OUT=ROOT/'qa'
sys.path.insert(0,str(SOURCE/'adapter'))
from reconciliation import Reconciliation
from grant_endpoint import RetirementProof,NativeBinding
checks=[];commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def probe(name,events):
 inp=OUT/(name+'-events.json');out=OUT/(name+'-rows.json');inp.write_text(json.dumps(events,indent=2)+'\n');cmd=['node',str(FRONT/'qa/probe.cjs'),str(PACK/'worker.js'),str(inp),str(out)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=15);(OUT/(name+'.log')).write_text(p.stdout+p.stderr);commands.append({'name':name,'command':cmd,'exit':p.returncode});assert p.returncode==0;return json.loads(out.read_text())
manifest=json.loads((SOURCE/'component-manifest.json').read_text())
for name in ['adapter/reconciliation.py','adapter/delivery_ledger.py','adapter/daemon.py','adapter/recovery_store.py']:
 check('frozen630-source-'+name,sha(SOURCE/name)==manifest['files'][name]['sha256'])
check('heldcompiled619-worker',sha(PACK/'worker.js')==manifest['files'][str((PACK/'worker.js').relative_to(SOURCE))]['sha256'])
base=json.loads((PACK/'13-strict-trio-restored-events.json').read_text());rows=probe('baseline-local-first-released',base)
check('baseline-exact-origin-is-locally-released',rows[-1]['unresolved']==0 and rows[-1]['history'][0]['released'])
original=json.loads((PACK/'original-release.json').read_text());old=original['record']['binding'];current=base[-1]['frame']['binding'];nextbound={**current,'frontend':'4'}
other=copy.deepcopy(original['record']);other['binding']['session']='999';other['intent'].update(request='13',generation='15',incarnation='1')
native=lambda f:{'kind':'native','frame':copy.deepcopy(f)}
base.append(native({'protocolVersion':3,'kind':'host-reservation-unknown','binding':current,'record':other}));rows=probe('mixed-local-released-and-unknown',base)
check('mixed-local-history-is-one-released-one-retained-Unknown',len(rows[-1]['history'])==2 and sum(r['released'] for r in rows[-1]['history'])==1 and rows[-1]['unresolved']==1)
templates={item['frame']['kind']:item['frame'] for item in json.loads((PACK/'captured573.json').read_text())}
def read(kind,id):
 f=copy.deepcopy(templates[kind]);f.update(binding=copy.deepcopy(nextbound),requestId=id)
 if kind=='action-projection':f['context'].update(lifetime=nextbound['lifetime'],epoch=nextbound['frontend'])
 if kind=='geometry-facts':f['sequence']=str(int(f['sequence'])+int(id))
 return f
base.extend([native({'protocolVersion':3,'kind':'host-disconnected'}),{'kind':'reconnect'},native({**templates['attached'],'binding':nextbound})]);rows=probe('reconnect-next-binding',base)
a=next(w for w in rows[-1]['wires'] if w['kind']=='projection-request')['requestId'];base.extend([native(read('action-projection',a)),native(templates['host-geometry-negotiate'])]);rows=probe('negotiate',base)
g=next(w for w in rows[-1]['wires'] if w['kind']=='geometry-attach')['requestId'];base.append(native(read('geometry-attached',g)));rows=probe('attach-geometry',base)
g=next(w for w in rows[-1]['wires'] if w['kind']=='geometry-facts-request')['requestId'];base.append(native(read('geometry-facts',g)));probe('initial-reads-completed',base)
class Client:
 def __init__(self):self.bound=copy.deepcopy(nextbound);self.proofs=[]
 def retire(self,request,bound):
  p=RetirementProof(NativeBinding.parse(self.bound),NativeBinding.parse(bound),request,str(1000+int(request)),'retire','Retired');self.proofs.append(p.as_dict());return p
class SnapshotFixture:
 def __init__(self,records):self.records=records
 def synchronization_snapshot(self):return {'entries':[],'releases':[{'record':copy.deepcopy(r),'phase':'Released'} for r in self.records]}
for name,records,expect_ready in [('already-delivered-scope-first',[original['record'],other],False),('lost-scope-first-control',[other,original['record']],True)]:
 client=Client();wire=[];c=Reconciliation(client,SnapshotFixture(records),wire.append);c.announce();rows=probe(name,base+[native(f) for f in wire]);ready=[w for w in rows[-1]['wires'] if w['kind']=='reconciliation-ready'];check(name+'-actual-coordinator-announces-only-first-serial-proof',len(client.proofs)==2 and [f['kind'] for f in wire]==['host-reservation-unknown','host-reservation-unknown','binding-retirement'])
 if expect_ready:
  check(name+'-retained-Unknown-scope-emits-ready',len(ready)==1 and ready[0]['queriedBinding']==other['binding']);c.proof_ready(ready[0]);check(name+'-backend-readiness-progresses',c.ready)
 else:
  check(name+'-CONFIRMED-no-ready-for-locally-released-origin',ready==[] and not(c.ready) and c.active.queried_binding.as_dict()==old and len(c.pending)==2 and rows[-1]['unresolved']==1)
  (OUT/'confirmed-counterexample.json').write_text(json.dumps({'finding':'RECOVERY-639-001','activeProof':c.active.as_dict(),'pendingOrigins':[r[0] for r in c.pending.values()],'frontendWires':rows[-1]['wires'],'frontendHistory':rows[-1]['history'],'unresolved':rows[-1]['unresolved'],'fixtureScope':'actual frozen630 coordinator and held compiled619 public reducer, synthetic validated-shape historical snapshot and typed proof transport; no filesystem/native acceptance'},indent=2)+'\n')
report={'passed':True,'confirmedFinding':'RECOVERY-639-001','assertions':len(checks),'checks':checks,'commands':commands,'nativeAcceptance':False,'newFrontendCompilation':False,'realFilesystemCampaign':False,'sourceHashes':{str(p):sha(p) for p in [SOURCE/'component-manifest.json',SOURCE/'adapter/reconciliation.py',FRONT/'src/ReconciliationTracking.elm',PACK/'worker.js',pathlib.Path(__file__)]},'scope':'New actual630 coordinator/held compiled619 executions with synthetic historical census/nativeproofs; historical worker compilation not rerun'};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'assertions':len(checks),'confirmedFinding':report['confirmedFinding']}))
