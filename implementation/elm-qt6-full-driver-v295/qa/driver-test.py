"""Actual Qt driver hidden-target and freshness boundaries; no toolkit/display."""
import copy,hashlib,json,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('driver-test-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(ROOT/'qa/helpers'));sys.path.insert(0,str(ROOT/'qa'));from driver import Driver,Refused
report={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(n,v):assert v,n;report['checks'].append({'name':n,'passed':True})
def refused(n,fn):
 try:fn()
 except Refused:check(n,True)
 else:check(n,False)
try:
 d=Driver.__new__(Driver);d.deadline=time.monotonic()+1;d.read_id=0;pid=123;ident={'role':'A','instance':1,'mapGeneration':1,'surfaceId':21,'pid':pid,'processStarted':456};bound={'identity':ident,'native':{'address':'0x123','pid':pid},'factIncarnation':'31'}
 rows=[{'role':'A','instance':1,'mapGeneration':1,'surfaceId':21,'event':'window-state','visible':False}];client={'address':'0x123','pid':pid,'title':'ELM-QT6-A-123','hidden':True};fact={'incarnation':'31','minimized':True,'shouldRenderAny':False}
 d.targets={'A':bound};d.actor=SimpleNamespace(pid=pid,read=lambda:rows);d.session=SimpleNamespace(guard=lambda:None,data=lambda kind:[client]);d.endpoint=SimpleNamespace(snapshot=lambda rid:{'windows':[{'label':'ELM-QT6-A-123','incarnation':'31'}]});d.observe=lambda:{'facts':{'windows':[fact]}};d.binding=lambda *args:(_ for _ in ()).throw(AssertionError('hidden facts cannot require visible scene'))
 check('actual-hidden-fact-read-without-visible-binding',d.fact('A') is fact)
 fact['incarnation']='32';refused('replacement-native-incarnation-refused',lambda:d.fact('A'));fact['incarnation']='31'
 rows.append({'role':'A','instance':2,'event':'create'});refused('replacement-QObject-refused',lambda:d.fact('A'));rows.pop()
 rows.append({'role':'A','instance':1,'event':'destroy-request'});refused('retired-QObject-refused',lambda:d.fact('A'));rows.pop()
 client['address']='0x124';refused('replacement-address-refused',lambda:d.fact('A'));client['address']='0x123'
 # Full eight executable method entries and original final-close deadline guard.
 check('all-eight-concrete-Qt-phase-methods',all(callable(getattr(Driver,'QT%02d'%i,None)) for i in range(1,9)))
 import ast
 tree=ast.parse((ROOT/'qa/driver.py').read_text());run=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='run');text=ast.unparse(run);check('final-close-stays-under-original-deadline','self.parent.close(self.deadline)\n                remaining(self.deadline)' in text or 'self.parent.close(self.deadline)\n                    remaining(self.deadline)' in text)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'qa/driver.py']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
