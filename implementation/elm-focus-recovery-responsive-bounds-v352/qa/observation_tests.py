import ast,hashlib,json,resource,time
from pathlib import Path
from types import SimpleNamespace
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('observations-'+str(time.time_ns()));OUT.mkdir()
old=REPO/'implementation/elm-focus-recovery-responsive-bounds-v351/qa/gui.py';current=ROOT/'qa/gui.py';amendments=json.loads((ROOT/'qa/observation-amendment.json').read_text());checks=[]
def test(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def predicate(text):return eval(compile(ast.parse(text,mode='eval'),'<actual-coherent-predicate>','eval'),{})
def sample(fn,values):
 calls=[]
 def read():
  calls.append(True);return values[len(calls)-1] if len(calls)<=len(values) else None
 return fn.__call__(),calls
try:
 shapes=[({'groups':[{'disabled':False}]},{'groups':[{'disabled':True}]}),({'menu':{'incarnation':'16'}},{'menu':None}),({'menu':None},{'menu':{'incarnation':'16'}}),({'menu':None,'outstanding':0},{'menu':None,'outstanding':1})]
 for i,((before,after),(valid,invalid)) in enumerate(zip(amendments,shapes)):
  assert old.read_text().count(before)==1 and current.read_text().count(after)==1
  def invoke(text,states):
   calls=[]
   def read():calls.append(True);return states[len(calls)-1] if len(calls)<=len(states) else None
   fn=eval(compile(ast.parse(text,mode='eval'),'<actual-owned-predicate>','eval'),{'self':SimpleNamespace(coherent=read)});return fn(),len(calls)
  expected=valid['menu'] if i==1 else valid
  try:result,calls=invoke(before,[valid,None]);detected=result!=expected or calls!=1
  except (TypeError,KeyError):detected=True
  test(str(i)+'-old-changing-observation-counterexample',detected)
  result,calls=invoke(after,[valid,None]);test(str(i)+'-single-snapshot-accepts-exact-valid-facts',result==expected and calls==1)
  result,calls=invoke(after,[None,valid]);test(str(i)+'-unavailable-snapshot-refused-without-mixing',result is None and calls==1)
  result,calls=invoke(after,[invalid,valid]);test(str(i)+'-ineligible-snapshot-refused-without-mixing',result is None and calls==1)
 r={'passed':True,'checks':checks,'nativeAcceptance':False,'productionChanged':False,'scope':'Actual four owned polling predicates under declared changing observation fixtures; original checks/deadlines remain native obligations','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old,current,Path(__file__),ROOT/'qa/observation-amendment.json']}}
except Exception as e:r={'passed':False,'error':repr(e),'checks':checks}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+chr(10));print(json.dumps({'passed':r['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
