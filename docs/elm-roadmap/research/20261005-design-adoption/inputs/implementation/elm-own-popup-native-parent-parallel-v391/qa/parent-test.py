import ast,hashlib,importlib.util,json,os,pathlib,resource,sys,time,types
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));OUT=ROOT/'qa'/('parent-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
try:
 import preflight,parent_loader
 import native
 guard,files=preflight.checked_guard();qualified,more=native.checked_parent(guard,files);r['qualifiedFiles']={**files,**more};r['checks'].append('actual verified source collector and full passed guard module qualify')
 pid=os.getpid();start=guard.process_identity(pathlib.Path('/proc/self/stat').read_text(),pid=pid);deadline=time.monotonic()+6.;value=qualified.collect(pid=pid,start=start,pgid=os.getpgrp(),deadline=deadline);assert value['maps'] and value['files'] and time.monotonic()<deadline;r['checks'].append('actual self full-row collector executes under original six-second deadline')
 def refused(name,mutate,restore):
  mutate()
  try:
   try:qualified.qualify(time.monotonic()+3.)
   except (qualified.wrapper[0].Refused,parent_loader.Refused,parent_loader.stdlib_origin.Refused,guard.Refused):r['checks'].append(name)
   else:raise AssertionError('unsafe accepted '+name)
  finally:restore()
 original=guard.fingerprint;refused('foreign fingerprint function',lambda:setattr(guard,'fingerprint',lambda *a:None),lambda:setattr(guard,'fingerprint',original))
 original=guard.map_identity;refused('foreign mount mapper function',lambda:setattr(guard,'map_identity',lambda *a:None),lambda:setattr(guard,'map_identity',original))
 original=qualified.module.collect;refused('foreign collector function',lambda:setattr(qualified.module,'collect',lambda *a:None),lambda:setattr(qualified.module,'collect',original))
 original=guard._MountInfo.__dict__['__init__'];refused('foreign mount metadata constructor',lambda:setattr(guard._MountInfo,'__init__',lambda *a:None),lambda:setattr(guard._MountInfo,'__init__',original))
 original=guard.ThreadPoolExecutor;refused('foreign guard executor class',lambda:setattr(guard,'ThreadPoolExecutor',object),lambda:setattr(guard,'ThreadPoolExecutor',original))
 original=guard.threading;refused('foreign guard threading namespace',lambda:setattr(guard,'threading',types.SimpleNamespace()),lambda:setattr(guard,'threading',original))
 original=qualified.module.MAX_ROWS;refused('altered collector bound',lambda:setattr(qualified.module,'MAX_ROWS',16385),lambda:setattr(qualified.module,'MAX_ROWS',original))
 original=guard.fingerprint;clone=types.FunctionType(original.__code__,dict(original.__globals__),name=original.__name__);clone.__module__=original.__module__;clone.__qualname__=original.__qualname__;refused('same-code foreign globals fingerprint',lambda:setattr(guard,'fingerprint',clone),lambda:setattr(guard,'fingerprint',original))
 original=qualified.module.collect;wrong=types.FunctionType(original.__code__.replace(co_stacksize=original.__code__.co_stacksize+1),original.__globals__,name=original.__name__);wrong.__module__=original.__module__;wrong.__qualname__=original.__qualname__;refused('collector recursive code metadata differs',lambda:setattr(qualified.module,'collect',wrong),lambda:setattr(qualified.module,'collect',original))
 import concurrent.futures,concurrent.futures.thread,concurrent.futures._base
 original=concurrent.futures.ThreadPoolExecutor;refused('executor aggregator foreign linkage',lambda:setattr(concurrent.futures,'ThreadPoolExecutor',object),lambda:setattr(concurrent.futures,'ThreadPoolExecutor',original))
 original=concurrent.futures._base.Future.done;refused('Future.done foreign callable',lambda:setattr(concurrent.futures._base.Future,'done',lambda *a:True),lambda:setattr(concurrent.futures._base.Future,'done',original))
 try:qualified.collect(pid=pid,start=start,pgid=os.getpgrp(),deadline=time.monotonic()-1.)
 except guard.Refused:r['checks'].append('no qualification deadline reset')
 else:raise AssertionError('expired accepted')
 from parent_source import original
 original((ROOT/'qa/native.py').read_text());r['checks'].append('entire native AST exact373 except exact declared qualification/parent callback/evidence archive')
 r['passed']=True
except BaseException as e:
 import traceback;r['error']=repr(e);r['traceback']=traceback.format_exc()
r['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'qa/parent_loader.py',ROOT/'qa/native.py',ROOT/'qa/preflight.py',ROOT/'qa/stdlib_origin.py',pathlib.Path(__file__)]};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
