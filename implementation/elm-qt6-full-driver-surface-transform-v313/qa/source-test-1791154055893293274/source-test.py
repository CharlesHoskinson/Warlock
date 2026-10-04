"""Inert production imports and unchanged complete phase oracles; no GUI."""
import ast,hashlib,importlib,json,pathlib,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent/'elm-qt6-full-driver-v295';out=ROOT/'qa'/('source-test-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,value):assert value,name;report['checks'].append(name)
def methods(p,cls):
 tree=ast.parse(p.read_text());c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
 return {n.name:ast.dump(n,include_attributes=False) for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
try:
 sys.path.insert(0,str(ROOT/'qa/helpers'));sys.path.insert(0,str(ROOT/'qa'))
 import native,driver,shell,coordinates
 check('actual-four-production-imports-inert',all(m is not None for m in (native,driver,shell,coordinates)))
 old=methods(BASE/'qa/driver.py','Driver');new=methods(ROOT/'qa/driver.py','Driver');check('same-entire-driver-method-set',old.keys()==new.keys())
 for name in old:
  if name!='pair':check('original-driver-method-'+name,new[name]==old[name])
 old=methods(BASE/'qa/shell.py','Shell');new=methods(ROOT/'qa/shell.py','Shell');check('same-shell-method-set',old.keys()==new.keys())
 for name in old:
  if name!='popup_guard':check('original-shell-method-'+name,new[name]==old[name])
 for name in ('geometry.py','scene.py','observer.py','protocol.py','journal.py'):
  check('exact-held309-'+name,(ROOT/'qa/helpers'/name).read_bytes()==(ROOT.parent/'elm-qt6-surface-transform-consumer-v309/qa'/name).read_bytes())
 for name in ('keyboard.py','capture_scope.py','fault-native.py','observer_endpoint.py'):
  check('original-boundary-'+name,(ROOT/'qa'/name).read_bytes()==(BASE/'qa'/name).read_bytes())
 report['passed']=True
except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [pathlib.Path(__file__),ROOT/'qa/driver.py',ROOT/'qa/shell.py',ROOT/'qa/native.py',BASE/'qa/driver.py',BASE/'qa/shell.py']}
(out/'source-test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
