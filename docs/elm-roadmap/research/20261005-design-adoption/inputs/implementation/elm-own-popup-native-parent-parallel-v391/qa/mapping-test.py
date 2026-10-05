"""Exact successor native/source preservation; inert334 adoption, no GUI."""
import json,pathlib,sys,time,resource,hashlib,ast,copy
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
from preflight import sha,checked_guard
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mapping-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,fn):assert fn(),name;r['checks'].append({'name':name,'passed':True})
try:
 origin=json.loads((ROOT/'mapping-origin.json').read_text());old=pathlib.Path(origin['ancestor']);check('exact-ancestor-manifest',lambda:sha(old/'component-manifest.json')==origin['manifestSHA256'])
 report=pathlib.Path(origin['nativeReport']);check('exact-original-native-failure',lambda:sha(report)==origin['nativeReportSHA256']);failure=json.loads(report.read_text());check('original-failure-remains-failure',lambda:failure['passed'] is False and failure['cleanupPassed'] is True and 'mapping inode changed' in failure['error'])
 for name in ['selector.py','stamp.py','target.py','join.py','ancestor-shell.py','ancestor-observer_endpoint.py']:
  check('exact-original-'+name,lambda name=name:(ROOT/'qa'/name).read_bytes()==(old/'qa'/name).read_bytes())
 for p in sorted((old/'qa/helpers').glob('*.py')):check('exact-helper-'+p.name,lambda p=p:(ROOT/'qa/helpers'/p.name).read_bytes()==p.read_bytes())
 for p in sorted((old/'runtime').rglob('*')):
  if p.is_file():check('exact-runtime-'+str(p.relative_to(old/'runtime')),lambda p=p:(ROOT/p.relative_to(old)).read_bytes()==p.read_bytes())
 # Normalize ONLY the declared failure archive wrapper/import/outer fallback.
 class Normalize(ast.NodeTransformer):
  def visit_Import(self,node):
   node.names=[n for n in node.names if n.name!='map_failure'];return node if node.names else None
  def visit_FunctionDef(self,node):
   if node.name=='process_guard':return None
   return self.generic_visit(node)
  def visit_Call(self,node):
   node=self.generic_visit(node)
   if isinstance(node.func,ast.Name) and node.func.id=='process_guard':
    assert len(node.args)==1 and not node.keywords
    original=ast.parse("guard.verify_process(pid=owned['pid'],start=int(owned['start']),tuple_evidence=tuple_evidence,deadline=deadline)").body[0].value
    original.keywords[-1].value=node.args[0];return original
   return node
  def visit_ExceptHandler(self,node):
   node=self.generic_visit(node)
   if node.name=='e' and len(node.body)==2 and isinstance(node.body[1],ast.Try):node.body=node.body[:1]
   return node
 current=ast.parse((ROOT/'qa/native.py').read_text());original=ast.parse((old/'qa/native.py').read_text())
 normalized=Normalize().visit(copy.deepcopy(current));check('native-body-exact-after-declared-failure-archive-normalization',lambda:ast.dump(normalized,include_attributes=False)==ast.dump(original,include_attributes=False))
 guard,files=checked_guard();check('held338-API-unchanged',lambda:callable(guard.verify_tuple) and callable(guard.verify_process));r['guardFiles']=files
 r['sourceInputs']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'qa').glob('*.py')};r['passed']=True
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
