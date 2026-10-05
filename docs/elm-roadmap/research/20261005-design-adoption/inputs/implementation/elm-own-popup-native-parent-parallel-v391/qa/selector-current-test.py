"""Actual retained native log selector replay; hostile rendered scope controls."""
import json,pathlib,sys,time,copy,resource,ast
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import selector
from preflight import sha
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('selector-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,fn):assert fn(),name;r['checks'].append({'name':name,'passed':True})
def denied(raw):
 try:selector.select(raw)
 except ValueError:return True
 return False
try:
 origin=json.loads((ROOT/'origin.json').read_text());report=pathlib.Path(origin['nativeReport']);assert sha(report)==origin['nativeReportSHA256'];logfile=report.parent/'native-evidence/elm-webview.log';raw=logfile.read_text();(OUT/'actual325.log').write_text(raw)
 lines=raw.splitlines(keepends=True);positive=None;disabled=None
 for n,line in enumerate(lines):
  if line.startswith('surface-report: origin=bar '):
   o=json.loads(line[len('surface-report: origin=bar '):]);b=o['body']
   if b['publication']=='6':positive=''.join(lines[:n+1])
   if b['publication']=='4':disabled=''.join(lines[:n+1])
 assert positive and disabled
 actual=selector.select(positive);r['actualPoint']=actual;check('actual-enabled-publication6',lambda:actual==[217,21]);check('actual-disabled-publication4',lambda:selector.select(disabled) is None);check('actual-final-awaiting7-not-old-coherent6',lambda:selector.select(raw) is None)
 inspection=[json.loads(l[len('surface-inspection: '):]) for l in positive.splitlines() if l.startswith('surface-inspection: ')][-1]
 rendered=[json.loads(l[len('surface-report: origin=bar '):]) for l in positive.splitlines() if l.startswith('surface-report: origin=bar ')][-1]
 def wire(i,b):return 'surface-inspection: '+json.dumps(i)+'\nsurface-report: origin=bar '+json.dumps(b)+'\n'
 def control(change):
  i,b=copy.deepcopy(inspection),copy.deepcopy(rendered);change(i,b);return wire(i,b)
 check('matching-frame-roundtrip',lambda:selector.select(wire(inspection,rendered))==actual)
 for name,change in [('stale-publication',lambda i,b:b['body'].update(publication='5')),('stale-lease',lambda i,b:b['body'].update(lease='1')),('disabled',lambda i,b:b['body']['buttons'][1].update(disabled=True)),('changed-dom-id',lambda i,b:i['body']['groups'][0].update(domId='wrong')),('current-awaiting',lambda i,b:i['body'].update(phase='Awaiting')),('outstanding',lambda i,b:i['body'].update(outstanding=1)),('registry',lambda i,b:i['body'].update(registry=1)),('picker-open',lambda i,b:i['body'].update(mode='picker',picker={})),('pending',lambda i,b:i['body'].update(transaction='Pending'))]:
  check(name+'-no-point',lambda change=change:selector.select(control(change)) is None)
 for name,change in [('duplicate-control',lambda i,b:b['body']['buttons'].append(copy.deepcopy(b['body']['buttons'][1]))),('ambiguous-group',lambda i,b:i['body']['groups'].append(copy.deepcopy(i['body']['groups'][0]))),('bool-disabled',lambda i,b:b['body']['buttons'][1].update(disabled=0)),('nan-geometry',lambda i,b:b['body']['buttons'][1].update(x=float('nan'))),('bool-geometry',lambda i,b:b['body']['buttons'][1].update(width=True)),('huge-geometry',lambda i,b:b['body']['buttons'][1].update(x=10**500)),('offscreen',lambda i,b:b['body']['buttons'][1].update(x=799)),('zero-width',lambda i,b:b['body']['buttons'][1].update(width=0)),('numeric-publication',lambda i,b:i.update(publication=6)),('leadingzero-lease',lambda i,b:i.update(lease='00')),('boolean-ledger',lambda i,b:i['body'].update(outstanding=False))]:
  check(name+'-refused',lambda change=change:denied(control(change)))
 check('partial-future-write-not-parsed',lambda:selector.select(positive+'surface-inspection: {bad')==actual)
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

 old=ast.parse((pathlib.Path(origin['ancestor'])/'qa/native.py').read_text());new=Normalize().visit(ast.parse((ROOT/'qa/native.py').read_text()))
 old.body=[n for n in old.body if not isinstance(n,ast.FunctionDef) or n.name!='point'];new.body=[n for n in new.body if not isinstance(n,ast.FunctionDef) or n.name!='point']
 check('native-body-except-selector-and-declared-failure-archive-normalization-unchanged',lambda:ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False))
 # Actual original guessed-prefix function must fail the same retained positive witness.
 import preflight
 ancestor=preflight.load('retained_original325_native',pathlib.Path(origin['ancestor'])/'qa/native.py')
 prefix_file=OUT/'positive-prefix.log';prefix_file.write_text(positive)
 check('actual-unsafe-old-prefix-killed-by-positive-log',lambda:ancestor.point(prefix_file,time.monotonic()+1) is None)
 r['inputs']={str(logfile):sha(logfile),str(report):sha(report),str(ROOT/'qa/selector.py'):sha(ROOT/'qa/selector.py')};r['passed']=True
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
