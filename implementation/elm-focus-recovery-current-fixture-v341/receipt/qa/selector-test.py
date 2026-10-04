"""Distinct full-native-key receipt ordinal selection, external forwarding oracles."""
import copy,hashlib,importlib.util,json,os,resource,shutil,sys,time,traceback
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('selector-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[*sorted((ROOT/'qa').glob('*.py')),ROOT/'parent.json',ROOT/'upstream.json']
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
sys.path.insert(0,str(OUT/'inputs/qa'));import wrapper as w
spec=importlib.util.spec_from_file_location('entry',OUT/'inputs/qa/broker-entrypoint.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
R={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':{'lifetime':'11','session':'12','frontend':'13'},'intent':{'request':'14','generation':'15','incarnation':'16','operation':'restore-geometry','context':{'lifetime':'11','epoch':'13','output':'17','revision':'18'}},'status':'Committed','reason':'applied','revision':'19','outputGeneration':'17'}
checks=[];seq=0
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:fn()
 except (w.HoldFailure,OSError,ValueError):return True
 return False
def control():
 global seq
 seq+=1;p=OUT/('control'+str(seq));p.mkdir(mode=0o700);(p/'gate.json').write_text('{"action":"hold"}');(p/'gate.json').chmod(0o600);return p
def holder(ordinal=2,**kwargs):
 p=control();sent=[];h=w.ReceiptHold(p,'16',sent.append,operation='restore-geometry',selector_ordinal=ordinal,**kwargs);return p,h,sent
report={'passed':False,'inputs':inputs,'checks':checks,'qaScope':scope,'nativeAcceptance':False,'full09Accepted':False,'scope':'Actual wrapper/controller with synthetic native receipt objects, filesystem gate and actual held backend import. Distinct selector CPU only; no native execution.'}
try:
 backend=w.load_backend();check('exact held shared380 backend still imports',callable(backend.main))
 p,h,sent=holder();first=copy.deepcopy(R);h.intercept(first)
 check('ordinal2 first distinct fullkey committed passes unchanged and starts no timer',sent==[R] and len(h.matching_keys)==1 and not h.seen and h.deadline is None and not (p/'held.json').exists())
 duplicate=copy.deepcopy(R);duplicate.update(revision='20',reason='same native key');h.intercept(duplicate)
 check('outer receipt metadata does not change full native key or advance count',sent[-1]==duplicate and len(h.matching_keys)==1 and not h.seen)
 for status in ['Unknown','Refused']:
  other=copy.deepcopy(R);other['status']=status;other['intent']['request']='30';h.intercept(other)
  check(status+' passes unchanged without ordinal increment',sent[-1]==other and len(h.matching_keys)==1 and not h.seen)
 for name,alter in [('target',lambda r:r['intent'].update(incarnation='99')),('protocol',lambda r:r.update(effectProtocol=1)),('operation',lambda r:r['intent'].update(operation='maximize'))]:
  other=copy.deepcopy(R);alter(other);h.intercept(other)
  check(name+' mismatch passes unchanged without counting',sent[-1]==other and len(h.matching_keys)==1 and not h.seen)
 second=copy.deepcopy(R);second['binding'].update(session='90',frontend='91');second['intent']['context']['epoch']='91';second['intent'].update(request='31',generation='32');second['intent']['context']['revision']='23';h.intercept(second)
 check('second distinct fullkey across reconnect is held exactly without delivery',h.seen and h.receipt==second and second not in sent and len(h.matching_keys)==2)
 marker=json.loads((p/'held.json').read_text());check('held file records full original second binding intent and receipt',marker['receipt']==second and marker['binding']==second['binding'] and marker['intent']==second['intent'])
 check('duplicate selected fullkey refuses instead of bypassing receipt hold',refused(lambda:h.intercept(second)) and second not in sent and len(h.matching_keys)==2)
 third=copy.deepcopy(second);third['intent']['request']='40';h.intercept(third)
 check('after selecting one hold unrelated further key passes without unbounded metadata',sent[-1]==third and len(h.matching_keys)==2)
 w.write_release(p);h.poll_gate();h.poll_gate();check('selected ordinal2 original receipt releases exactly once',sum(r==second for r in sent)==1 and h.released);h.close()
 # A physical reconnect replaces the broker actor. Counts are intentionally
 # process-local: use a new recorded private config only after old EOF/exit.
 p,a,forwarded=holder(2);a.intercept(R);a.close()
 p,b,delivered=holder(1);new=copy.deepcopy(R);new['binding'].update(session='88',frontend='89');new['intent']['context']['epoch']='89';new['intent'].update(request='41',generation='42');b.intercept(new)
 check('retired actorA ordinal2 forwards06 while fresh actorB ordinal1 holds09',forwarded==[R] and not a.seen and b.seen and b.receipt==new and delivered==[])
 w.write_release(p);b.poll_gate();b.close();check('fresh actor exact09 releases once without retargeting old holder',delivered==[new] and a.matching_keys!=b.matching_keys)
 # Both ordinal modes use uniform uncertainty/refusal pass-through semantics.
 for ordinal in [1,2]:
  p,h,s=holder(ordinal)
  for status in ['Unknown','Refused']:
   r=copy.deepcopy(R);r['status']=status;h.intercept(r)
   check('uniform ordinal'+str(ordinal)+' '+status+' never counts or fabricatesCommitted',s[-1]==r and len(h.matching_keys)==0 and h.receipt is None)
  h.close()
 for ordinal in [True,False,0,3,-1,1.0,'2',None]:check('closed ordinal type/value '+repr(ordinal),refused(lambda o=ordinal:holder(o)))
 for name,alter in [('bindingzero',lambda r:r['binding'].update(session='0')),('requestzero',lambda r:r['intent'].update(request='0')),('generationBool',lambda r:r['intent'].update(generation=True)),('generationOverflow',lambda r:r['intent'].update(generation='18446744073709551616')),('contextMismatch',lambda r:r['intent']['context'].update(epoch='99')),('extraIntent',lambda r:r['intent'].update(extra=1)),('extraEnvelope',lambda r:r.update(extra=1)),('invalidStatus',lambda r:r.update(status='Pending')),('badReason',lambda r:r.update(reason='x'*257))]:
  p,h,s=holder();r=copy.deepcopy(R);alter(r)
  check('malformed selected candidate does not consume ordinal '+name,refused(lambda:h.intercept(r)) and not s and not h.matching_keys)
  h.close()
 # Selected receipt alone starts bounded watchdog; earlier committed delivery
 # does not spend that budget or reset the external native scenario deadline.
 now=[10.];p,h,s=holder(clock=lambda:now[0]);h.intercept(R);now[0]=99.
 r=copy.deepcopy(R);r['intent']['request']='50';h.intercept(r);check('watchdog starts at selected original receipt and has original5sec bound',h.deadline==104.)
 now[0]=104.;check('deadline not extended by locked or unchanged gate',refused(h.poll_gate));check('late release cannot bypass deadline',refused(lambda:w.write_release(p) or h.poll_gate()))
 # Private four-field entrypoint remains default1; explicit fifth-field2.
 p=control();authority=OUT/'authority.json';authority.write_text('{}');authority.chmod(0o600);cfg=OUT/'wrapper.json'
 value={'authorityConfig':str(authority),'controlDirectory':str(p),'incarnation':'16','effectOperation':'restore-geometry'}
 for ordinal in [None,1,2]:
  packet=copy.deepcopy(value)
  if ordinal is not None:packet['selectorOrdinal']=ordinal
  cfg.write_text(json.dumps(packet));cfg.chmod(0o600);check('exact config optional ordinal '+str(ordinal),entry.configuration(cfg)==packet)
  args=[]
  def capture():args.extend(sys.argv);return 0
  with patch.object(entry,'wrapper_main',capture),patch.object(sys,'argv',['broker-entrypoint',str(cfg)]):code=entry.main()
  check('entrypoint forwards explicit ordinal '+str(ordinal),code==0 and (args[-2:]==['--selector-ordinal',str(ordinal)] if ordinal is not None else '--selector-ordinal' not in args))
 for ordinal in [True,0,3,'2',2.0,None]:
  cfg.write_text(json.dumps(dict(value,selectorOrdinal=ordinal)));check('private config rejects wrong ordinal '+repr(ordinal),refused(lambda:entry.configuration(cfg)))
 # Preserve parent artifacts and original source exactly; no original claims
 # are inferred from the deliberately changed Unknown receipt fixture policy.
 parent=json.loads((ROOT/'parent.json').read_text());base=next(p for p in ROOT.parents if (p/'AGENTS.md').is_file())/parent['path'];check('frozen255 ancestor manifest exact',sha(base/'qa/held-source-manifest.json')==parent['heldManifestSHA256'])
 for rel,digest in parent['files'].items():assert sha(base/rel)==digest
 for rel,digest in inputs.items():assert sha(ROOT/rel)==digest
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
