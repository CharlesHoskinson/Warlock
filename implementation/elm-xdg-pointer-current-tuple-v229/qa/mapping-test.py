"""Execute actual runner's point branch AST; independent expected integer coordinates."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'qa'/('mapping-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[],'inputs':{}}
 def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
 try:
  path=ROOT/'qa/native.py';source=path.read_text();tree=ast.parse(source)
  node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=="buffer['geometry'][:2] == [0, 0]" and any(isinstance(v,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='point' for t in v.targets) for v in n.body))
  module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));code=compile(module,str(path),'exec');(out/'actual-point-branch.py').write_text(ast.unparse(module)+'\n')
  def invoke(code,real,geometry,local,origin):
   values={'fact':{'visualGeometry':real},'buffer':{'geometry':geometry},'local':local,'requested':{'origin':origin}}
   exec(code,values);return values['point']
  cases=[('zero-ordinary',[-1,-1,800,600],[0,0,800,600],[4,4],[0,0],[3,3]),('zero-MAX',[1,1,798,598],[0,0,798,598],[4,4],[0,0],[5,5]),('origin-corner',[-1,-1,800,600],[16,24,800,600],[20,28],[16,24],[3,3]),('origin-center',[-1,-1,800,600],[16,24,800,600],[416,324],[16,24],[399,299]),('origin-far-corner',[-1,-1,800,600],[16,24,800,600],[812,620],[16,24],[795,595])]
  for name,real,geometry,local,origin,expected in cases:check(name,invoke(code,real,geometry,local,origin)==expected)
  for name,real,geometry,origin in [('non-Q1',[0,0,799,600],[16,24,800,600],[16,24]),('mismatched-committed-origin',[0,0,800,600],[16,24,800,600],[17,24])]:
   try:invoke(code,real,geometry,[20,28],origin)
   except AssertionError:check(name+'-refuses',True)
   else:raise AssertionError(name)
  mutant=ast.unparse(module).replace(" - buffer['geometry'][i]",'');check('actual-unsafe-missing-origin-rejected',invoke(compile(mutant,'unsafe','exec'),[-1,-1,800,600],[16,24,800,600],[20,28],[16,24])!=[3,3])
  (out/'unsafe-missing-origin.py').write_text(mutant+'\n')
  for name in ('pointer.py','parent_observation.py','pixels.py'):
   check(name+'-byte-exact-owned224',(ROOT/'qa'/name).read_bytes()==(ROOT/'original/qa'/name).read_bytes())
  report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (path,Path(__file__))};report['passed']=True
 except Exception as error:report['error']=repr(error)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
