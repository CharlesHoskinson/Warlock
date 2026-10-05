import ast,hashlib,json,marshal,os,pathlib,resource,sys,tempfile,time,types
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));OUT=ROOT/'qa'/('loader-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
try:
 import preflight,parent_loader as p,stdlib_origin as s,native
 g,files=preflight.checked_guard();source_path=ROOT.parent/'elm-own-popup-parent-map-parallel-v382/parent_maps.py';raw=source_path.read_bytes();expected=compile(raw,str(source_path),'exec',dont_inherit=True,optimize=sys.flags.optimize);cache=pathlib.Path(__import__('importlib').util.cache_from_source(str(source_path)));read=s.read;exists=pathlib.Path.exists
 def reject(name,callback):
  try:callback()
  except ValueError:r['checks'].append(name);return
  raise AssertionError('unsafe acceptance '+name)
 def altered_source(path):return raw+b'\n# changed source\n' if pathlib.Path(path)==source_path else read(path)
 s.read=altered_source
 try:reject('actual loader refuses altered source buffer before execution',lambda:native.checked_parent(g,files))
 finally:s.read=read
 # Simulated filesystem presence/acquired cache bytes only. No frozen cache is
 # created or modified; the actual checked_parent cache branch is executed.
 def present(path):return True if path==cache else exists(path)
 pathlib.Path.exists=present
 try:
  import importlib.util
  header=importlib.util.MAGIC_NUMBER+b'\0'*12
  poison={'truncated':b'x','wrong-code':header+marshal.dumps(compile('pass',str(source_path),'exec')),'extra-record':header+marshal.dumps(expected)+b'junk','wrong-code-stack':header+marshal.dumps(expected.replace(co_stacksize=expected.co_stacksize+1))}
  for name,body in poison.items():
   s.read=lambda path,body=body:body if pathlib.Path(path)==cache else read(path)
   reject('actual loader cache branch '+name,lambda:native.checked_parent(g,files))
  s.read=read
 finally:pathlib.Path.exists=exists;s.read=read
 assert s.same_code(s.cache_code(header+marshal.dumps(expected),expected),expected);r['checks'].append('actual cache validator accepts exact compiled collector source')
 # Existing import cache is ignored: execute the verified buffer, never the
 # prior cached object's callback or a .pyc loader.
 foreign=types.ModuleType('held_parent_collector382');foreign.collect=lambda *a:(_ for _ in ()).throw(AssertionError('foreign cached callback executed'));previous=sys.modules.get(foreign.__name__);sys.modules[foreign.__name__]=foreign
 q,_=native.checked_parent(g,files);assert q.module is not foreign and q.module.collect.__globals__ is q.module.__dict__;r['checks'].append('foreign sys.modules collector never executes or survives loader')
 if previous is not None:sys.modules[foreign.__name__]=previous
 original_path=q.module.__file__;q.module.__file__='/foreign/collector.py'
 try:reject('actual executed collector file origin mismatch',lambda:q.qualify(time.monotonic()+3.))
 finally:q.module.__file__=original_path
 original_cache=q.module.__cached__;q.module.__cached__='/foreign/cache.pyc'
 try:reject('actual executed collector cache origin mismatch',lambda:q.qualify(time.monotonic()+3.))
 finally:q.module.__cached__=original_cache
 # Execute the actual native wrapper in an inert namespace: correct parent
 # owner evidence is archived, primary is retained, no GUI/native calls occur.
 from parent_source import PARENT_MAP,original
 from budget_timing import BudgetTiming
 import map_failure
 pid=os.getpid();start=g.process_identity(pathlib.Path('/proc/self/stat').read_text(),pid=pid);body=b'actual acquired diagnostic bytes\n';marker=FileNotFoundError('parent proc retired');marker.map_evidence={'pid':pid,'start':start,'mapsSHA256':hashlib.sha256(body).hexdigest(),'raw':body}
 class Failed:
  def collect(self,**kwargs):raise marker
 record={};env={'parent_collect':lambda candidate,guard,**kwargs:candidate.collect(**kwargs),'guard':g,'timing':BudgetTiming(record),'boot':time.monotonic()+6.,'parent_collector':Failed(),'parent':{'pid':pid,'start':str(start),'pgid':os.getpgrp()},'r':record,'map_failure':map_failure,'out':OUT}
 exec(compile(ast.parse(PARENT_MAP),'<actual-parent-map-wrapper>','exec'),env)
 try:env['parent_map']()
 except BaseException as e:assert e is marker and record['sameReadParentMapFailure']['pid']==pid and (OUT/'parent-map-failure/maps.raw').read_bytes()==body;r['checks'].append('actual native wrapper archives parent owner bytes and preserves primary')
 else:raise AssertionError('failed parent accepted')
 with tempfile.TemporaryDirectory(prefix='parent-archive-error-') as tmp:
  record={};env.update(r=record,timing=BudgetTiming(record),out=pathlib.Path(tmp));(pathlib.Path(tmp)/'parent-map-failure').mkdir()
  exec(compile(ast.parse(PARENT_MAP),'<actual-parent-map-wrapper>','exec'),env)
  try:env['parent_map']()
  except BaseException as e:assert e is marker and 'parentMapFailureArchiveError' in record;r['checks'].append('archive I/O failure cannot replace original parent error')
  else:raise AssertionError('archive failure accepted')
 text=(ROOT/'qa/native.py').read_text();original(text)
 for name,change in [('deadline-reset',text.replace('deadline=boot))','deadline=time.monotonic()+6))')),('lost-archive-primary',text.replace("      raise\n    pm=parent_map()","      raise RuntimeError('replacement')\n    pm=parent_map()")),('guard-skip',text.replace('after=process_guard(bounded.deadline)','after=before'))]:
  try:original(change)
  except AssertionError:r['checks'].append('actual native AST unsafe '+name+' rejected')
  else:raise AssertionError('unsafe native change accepted '+name)
 r['passed']=True
except BaseException as e:
 import traceback;r['error']=repr(e);r['traceback']=traceback.format_exc()
r['inputs']={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'qa/native.py',ROOT/'qa/parent_loader.py',ROOT/'qa/parent_source.py',pathlib.Path(__file__)]};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
