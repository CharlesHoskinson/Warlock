"""Actual command_for and held backend closure; no endpoint/native execution."""
import ast,copy,hashlib,importlib.util,json,os,resource,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('binding-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refuses(fn):
 try:fn();return False
 except (Exception,):return True
w=load('current654wrapper',ROOT/'receipt/qa/wrapper.py');r=load('current654relay',ROOT/'relay/qa/relay.py');sys.path.insert(0,str(ROOT/'receipt/qa'));e=load('current654entry',ROOT/'receipt/qa/broker-entrypoint.py')
report={'passed':False,'checks':checks,'nativeAcceptance':False,'scope':'CPU actual production fixture command selection, strict backend byte closure and AST equivalence; no native transport'}
try:
 captured=w.verified_backend_root();check('actual captured640 backend selected',captured==REPO/'implementation/elm-recovery-delivery-integrated-gui-v640/qa/build-1791153819143987946/inputs/adapter')
 check('all captured640 adapter siblings equal current source',all(p.read_bytes()==(w.SOURCE/'adapter'/p.name).read_bytes() for p in captured.glob('*.py')))
 old=REPO/'implementation/elm-picker-ready-broker-fixture-v255';ow=ast.parse((old/'receipt/qa/wrapper.py').read_text());nw=ast.parse((ROOT/'receipt/qa/wrapper.py').read_text())
 for n in [x for x in ow.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name!='verified_backend_root']:
  other=next(x for x in nw.body if isinstance(x,type(n)) and x.name==n.name);check('receipt behavior unchanged '+n.name,ast.dump(n,include_attributes=False)==ast.dump(other,include_attributes=False))
 check('host receipt entrypoint byte exact255',sha(ROOT/'receipt/qa/broker-entrypoint.py')==sha(old/'receipt/qa/broker-entrypoint.py'))
 ot=ast.parse((old/'relay/qa/relay.py').read_text());nt=ast.parse((ROOT/'relay/qa/relay.py').read_text())
 for n in [x for x in ot.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name!='command_for']:
  other=next(x for x in nt.body if isinstance(x,type(n)) and x.name==n.name);check('relay behavior unchanged '+n.name,ast.dump(n,include_attributes=False)==ast.dump(other,include_attributes=False))
 # The only command_for AST change is the fixture-owned receipt path literal.
 expected=ast.dump(next(x for x in ot.body if isinstance(x,ast.FunctionDef) and x.name=='command_for'),include_attributes=False).replace('elm-picker-ready-broker-fixture-v255/receipt','elm-recovery-delivery-current-fixture-v654/receipt')
 normalized=copy.deepcopy(next(x for x in nt.body if isinstance(x,ast.FunctionDef) and x.name=='command_for'));normalized.body=[n for n in normalized.body if not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='existing' for t in n.targets)) and not (isinstance(n,ast.If) and 'Foreign cached receipt wrapper' in ast.dump(n))];check('both profile selection behavior unchanged except owned path and failclosed cache guard',expected==ast.dump(normalized,include_attributes=False))
 runtime=OUT/'runtime';runtime.mkdir(mode=0o700);ctl=OUT/'control';ctl.mkdir(mode=0o700);receipt_ctl=OUT/'receipt-control';receipt_ctl.mkdir(mode=0o700)
 authority=OUT/'authority.json';authority.write_text(json.dumps({'runtime':str(runtime),'instance':'current654'}));authority.chmod(0o600)
 receipt=OUT/'receipt.json';receipt.write_text(json.dumps({'authorityConfig':str(authority),'controlDirectory':str(receipt_ctl),'incarnation':'16','effectOperation':'restore-geometry','selectorOrdinal':2}));receipt.chmod(0o600)
 common={'runtime':str(runtime),'instance':'current654','controlDirectory':str(ctl)}
 broker=dict(common,profile='broker',authorityConfig=str(authority));held=dict(common,profile='receipt',receiptConfig=str(receipt))
 check('actual broker command targets626 daemon',r.command_for(broker,REPO)==['/usr/bin/python3','-B',str(captured/'daemon.py'),str(authority)])
 check('actual receipt command targets634 entrypoint',r.command_for(held,REPO)==['/usr/bin/python3','-B',str(ROOT/'receipt/qa/broker-entrypoint.py'),str(receipt)])
 check('receipt entrypoint accepts genuine full private config',e.configuration(receipt)['selectorOrdinal']==2)
 for cfg,label in [(dict(broker,instance='foreign'),'foreign instance'),(dict(broker,runtime=str(ctl)),'foreign runtime'),(dict(broker,profile='other'),'foreign profile'),(dict(broker,extra=True),'extra field'),(dict(broker,authorityConfig=True),'bool config')]:check(label+' refuses',refuses(lambda:r.command_for(cfg,REPO)))
 before=w.MANIFEST_SHA;w.MANIFEST_SHA='0'*64;check('foreign manifest refuses backend',refuses(w.verified_backend_root));w.MANIFEST_SHA=before
 before=w.MANIFEST_SHA;w.MANIFEST_SHA='b0889b29e3b37a1dba678717d93db63e8b1604fdd33b2f0fe39a9806279703f2';check('stale626 producer hash refuses640 backend',refuses(w.verified_backend_root));w.MANIFEST_SHA=before
 before=r.RECEIPT_MANIFEST;r.RECEIPT_MANIFEST='0'*64;check('foreign receipt manifest refuses both profiles',refuses(lambda:r.command_for(broker,REPO)) and refuses(lambda:r.command_for(held,REPO)));r.RECEIPT_MANIFEST=before
 saved=sys.modules.get('wrapper');foreign=types.ModuleType('wrapper');foreign.__file__=str(old/'receipt/qa/wrapper.py');sys.modules['wrapper']=foreign;check('cached231 wrapper cannot select stale broker',refuses(lambda:r.command_for(broker,REPO)));sys.modules['wrapper']=saved
 foreign.__file__=str(REPO/'implementation/elm-reconciliation-current-fixture-v634/receipt/qa/wrapper.py');sys.modules['wrapper']=foreign;check('cached626 wrapper cannot select stale broker',refuses(lambda:r.command_for(broker,REPO)));sys.modules['wrapper']=saved
 backend=w.load_backend();check('actual verified640 daemon imports authoritative coordinator',callable(backend.main) and callable(backend.publish_startup) and hasattr(backend,'Reconciliation'))
 report.update(passed=True,capturedBackend=str(captured),backendManifestSHA256=w.MANIFEST_SHA,backendAdapter={p.name:sha(p) for p in captured.glob('*.py')})
except Exception as ex:report['error']=repr(ex)
report['inputs']={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'receipt/qa/wrapper.py',ROOT/'receipt/qa/broker-entrypoint.py',ROOT/'receipt/qa/held-source-manifest.json',ROOT/'relay/qa/relay.py']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
