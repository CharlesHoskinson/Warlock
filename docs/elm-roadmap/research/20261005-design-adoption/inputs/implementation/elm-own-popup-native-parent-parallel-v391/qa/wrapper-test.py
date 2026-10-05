import ast,hashlib,importlib.util,json,marshal,pathlib,resource,shutil,struct,subprocess,sys,time,types
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));OUT=ROOT/'qa'/('wrapper-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
try:
 import native,preflight
 fixture=OUT/'fixture';(fixture/'qa').mkdir(parents=True)
 for p in (ROOT/'qa').glob('*.py'):shutil.copyfile(p,fixture/'qa'/p.name)
 shutil.copytree(ROOT/'qa/helpers',fixture/'qa/helpers')
 source=fixture/'qa/parent_loader.py';tree=ast.parse(source.read_bytes());target=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='checked_parent');target.body=[ast.Return(value=ast.Tuple(elts=[ast.Constant('cache-poison'),ast.Dict(keys=[],values=[])],ctx=ast.Load()))];ast.fix_missing_locations(tree);st=source.stat();cache=pathlib.Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir();cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(st.st_mtime)&0xffffffff,st.st_size)+marshal.dumps(compile(tree,str(source),'exec')))
 driver=OUT/'driver.py';driver.write_text("import sys;sys.path[:0]=[sys.argv[1],sys.argv[1]+'/helpers'];import native;assert 'parent_loader' not in sys.modules;\ntry:native.checked_parent(None,{})\nexcept ValueError as e:print(type(e).__name__);assert 'verified_parent_wrapper391' not in sys.modules\nelse:raise AssertionError('poisoned wrapper cache accepted')\n")
 result=subprocess.run(['/usr/bin/python3','-B',str(driver),str(fixture/'qa')],capture_output=True,timeout=8);(OUT/'cache.stdout').write_bytes(result.stdout);(OUT/'cache.stderr').write_bytes(result.stderr);assert result.returncode==0,(result.returncode,result.stderr.decode());r['checks'].append('actual native import never executes ordinary wrapper cache; verified path refuses it before execution')
 guard,files=preflight.checked_guard();foreign=types.ModuleType('parent_loader');foreign.checked_parent=lambda *a:('foreign',{});old=sys.modules.get('parent_loader');sys.modules['parent_loader']=foreign
 try:q,_=native.checked_parent(guard,files);assert q.wrapper[0] is not foreign and q.wrapper[0].__name__=='verified_parent_wrapper391';r['checks'].append('actual native factory ignores foreign ordinary wrapper module/slot')
 finally:
  if old is None:sys.modules.pop('parent_loader',None)
  else:sys.modules['parent_loader']=old
 module=q.wrapper[0];original=module.checked_parent;module.checked_parent=lambda *a:('foreign',{})
 try:
  try:q.qualify(time.monotonic()+3.)
  except ValueError:r['checks'].append('own wrapper checked_parent foreign slot refuses on actual next qualification')
  else:raise AssertionError('wrapper foreign slot accepted')
 finally:module.checked_parent=original
 original=module.QualifiedParent.collect;module.QualifiedParent.collect=lambda *a,**k:{'maps':'','files':{}}
 try:
  try:q.qualify(time.monotonic()+3.)
  except ValueError:r['checks'].append('own wrapper collector method foreign slot refuses')
  else:raise AssertionError('wrapper method accepted')
 finally:module.QualifiedParent.collect=original
 original=module.qualify_module;original_collect=q.module.collect;module.qualify_module=lambda *a,**k:{};q.module.collect=lambda *a,**k:{'maps':'forged','files':{}}
 try:
  try:native.parent_collect(q,guard,pid=-1,start=-1,pgid=-1,deadline=time.monotonic()+3.)
  except ValueError:r['checks'].append('actual external entry rejects compromised self-verifier before forged collector call')
  else:raise AssertionError('compromised self-verifier accepted forged maps')
 finally:module.qualify_module=original;q.module.collect=original_collect
 q.collect=lambda **k:{'maps':'forged','files':{}}
 try:
  try:native.parent_collect(q,guard,pid=-1,start=-1,pgid=-1,deadline=time.monotonic()+3.)
  except ValueError:r['checks'].append('actual external entry rejects instance method shadow')
  else:raise AssertionError('instance shadow accepted')
 finally:del q.collect
 original_collect=q.module.collect;q.module.collect=lambda *a,**k:{'maps':'forged','files':{}}
 try:
  try:native.parent_collect(q,guard,pid=-1,start=-1,pgid=-1,deadline=time.monotonic()+3.)
  except ValueError:r['checks'].append('actual external entry rejects forged collector with genuine wrapper verifier')
  else:raise AssertionError('collector shadow accepted')
 finally:q.module.collect=original_collect
 q.qualify(time.monotonic()+3.);r['checks'].append('restored own wrapper actual full qualification succeeds')
 import os
 started=guard.process_identity(pathlib.Path('/proc/self/stat').read_text(),pid=os.getpid())
 value=native.parent_collect(q,guard,pid=os.getpid(),start=started,pgid=os.getpgrp(),deadline=time.monotonic()+3.)
 assert value['maps'] and value['files'];r['checks'].append('actual external entry accepts genuine full-row self collect');r['passed']=True
except BaseException as e:
 import traceback;r['error']=repr(e);r['traceback']=traceback.format_exc()
r['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'qa/native.py',ROOT/'qa/parent_loader.py',ROOT/'qa/parent_source.py',pathlib.Path(__file__)]};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
