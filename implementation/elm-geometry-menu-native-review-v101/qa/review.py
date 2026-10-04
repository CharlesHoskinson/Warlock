"""Read-only protected source equivalence verification; no native qualification."""
import ast,copy,hashlib,json,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100'
ENDPOINT=REPO/'implementation/elm-geometry-family-staged-build-v91/qa/build-1791108716010794735/inputs/adapter/endpoint.py'
OUT=ROOT/'qa'/('review-'+str(time.time_ns()));(OUT/'inputs').mkdir(parents=True);checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def dump(x):return ast.dump(x,include_attributes=False)
def method(tree,cls,fn):return next(n for c in tree.body if isinstance(c,ast.ClassDef) and c.name==cls for n in c.body if isinstance(n,ast.FunctionDef) and n.name==fn)
paths=[Path(__file__),SOURCE/'qa/native.py',SOURCE/'qa/observer_endpoint.py',SOURCE/'qa/client_evidence.py',SOURCE/'candidate_host.py',SOURCE/'qa/held-source-manifest.json',SOURCE/'upstream.json',ENDPOINT]
report={'passed':False,'scope':'Independent read-only source/AST and original-deadline boundary review, no GUI/native acceptance','nativeAcceptance':False,'full09Accepted':False,'checks':checks}
try:
 inputs={str(p):{'sha256':sha(p),'size':p.stat().st_size} for p in paths}
 for i,p in enumerate(paths):dest=OUT/'inputs'/str(i)/p.name;dest.parent.mkdir();shutil.copy2(p,dest)
 m=json.loads((SOURCE/'qa/held-source-manifest.json').read_text());check('V100 owner published source hold',m['sourceHeld'] is True and m['evidenceIntegrityPassed'] is True)
 # Exact body equivalence; normalize only explicitly approved initializer.
 original=method(ast.parse(ENDPOINT.read_text()),'Endpoint','request');candidate=method(ast.parse((SOURCE/'qa/observer_endpoint.py').read_text()),'ObserverEndpoint','request')
 expected=copy.deepcopy(original);expected.body[0].value=ast.parse('min(time.monotonic()+3,self.parentDeadline)',mode='eval').body
 check('request body exact except bounded deadline initializer',dump(candidate)==dump(expected))
 original_expr=original.body[0].value;candidate_expr=candidate.body[0].value
 check('original transport budget remains three seconds',dump(original_expr)==dump(ast.parse('time.monotonic()+3',mode='eval').body))
 import types
 code=compile(ast.Expression(candidate_expr),'<actual-deadline-initializer>','eval')
 for parent,wanted,name in [(12,12,'parent smaller'),(20,13,'transport smaller'),(float('inf'),13,'bootstrap'),(9,9,'expired parent')]:
  value=eval(code,{'min':min,'time':types.SimpleNamespace(monotonic=lambda:10),'self':types.SimpleNamespace(parentDeadline=parent)})
  check('actual initializer '+name,value==wanted)
 native=ast.parse((SOURCE/'qa/native.py').read_text());text=(SOURCE/'qa/native.py').read_text()
 check('parent09 deadline supplied and restored without clock monkeypatch','observer.parentDeadline=deadline' in text and "finally:observer.parentDeadline=float('inf')" in text and 'time.monotonic=' not in text)
 check('cleanup empty native census precedes plugin unload',text.index("check('nativeFixtureClientsEmptyBeforeUnload'")<text.rindex("session.ctl('plugin','unload',plugin)"))
 binding_check=next(n for n in ast.walk(native) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='observerHasIndependentPeerBinding')
 check('explicit observer distinct session assertion present',dump(binding_check.args[1])==dump(ast.parse("observer_hello['binding']['lifetime']==hello['binding']['lifetime'] and observer_hello['binding']['session']!=hello['binding']['session']",mode='eval').body))
 check('all ten original scenario identities retained',all('GEOMETRY-MENU-'+str(i).zfill(2) in text for i in range(1,11)))
 for p,e in inputs.items():check('stable reviewed source '+str(Path(p).relative_to(REPO)) if Path(p).is_relative_to(REPO) else 'stable external source',sha(Path(p))==e['sha256'])
 report['inputs']=inputs;report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
