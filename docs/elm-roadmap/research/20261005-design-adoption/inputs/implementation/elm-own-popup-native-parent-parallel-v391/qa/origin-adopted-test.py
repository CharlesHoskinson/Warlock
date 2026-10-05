import ast,copy,hashlib,importlib.util,json,marshal,pathlib,resource,sys,tempfile,time,types
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));import stdlib_origin as s
OUT=ROOT/'qa'/('origin-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def reject(name,fn):
 try:fn()
 except (s.Refused,AssertionError):r['checks'].append(name);return
 raise AssertionError('unsafe acceptance '+name)
def qualified(data,pin,verified):
 supplement=ROOT/'stdlib-supplement.json';body=supplement.read_bytes();proof={**verified,str(supplement):sha(supplement)};return s.qualify(data,pin,proof,body,supplement)
try:
 pin=ROOT.parent/'elm-own-popup-runtime-index-guard-v364/stdlib-pin.json';raw=pin.read_bytes();verified={str(pin):sha(pin)};proof=qualified(raw,pin,verified);r['proof']=proof;r['checks'].append('actual source/cache/loaded runtime code qualified before guard import')
 import threading,concurrent.futures.thread as th,concurrent.futures._base as base
 original_slot=th.ThreadPoolExecutor.shutdown
 try:th.ThreadPoolExecutor.shutdown=th.ThreadPoolExecutor.__init__;reject('wrong legitimate shutdown slot',lambda:qualified(raw,pin,verified))
 finally:th.ThreadPoolExecutor.shutdown=original_slot
 # Exact binding and descriptor controls use the actual imported stdlib.
 import concurrent.futures as aggregator,_thread
 for replacement in (object(),lambda *args:None):
  try:th.ThreadPoolExecutor.shutdown=replacement;reject('nonfunction declared shutdown '+type(replacement).__name__,lambda:qualified(raw,pin,verified))
  finally:th.ThreadPoolExecutor.shutdown=original_slot
 old_executor=aggregator.ThreadPoolExecutor
 try:aggregator.ThreadPoolExecutor=type('Foreign',(),{});reject('aggregator foreign executor',lambda:qualified(raw,pin,verified))
 finally:aggregator.ThreadPoolExecutor=old_executor
 old_threading=th.threading
 try:th.threading=types.ModuleType('threading');reject('executor foreign threading module',lambda:qualified(raw,pin,verified))
 finally:th.threading=old_threading
 old_code=original_slot.__code__
 try:original_slot.__code__=old_code.replace(co_stacksize=old_code.co_stacksize+1);reject('actual loaded stack metadata differs',lambda:qualified(raw,pin,verified))
 finally:original_slot.__code__=old_code
 clone=types.FunctionType(old_code,dict(original_slot.__globals__),original_slot.__name__,original_slot.__defaults__,original_slot.__closure__);clone.__qualname__=original_slot.__qualname__;clone.__module__=original_slot.__module__
 try:th.ThreadPoolExecutor.shutdown=clone;reject('exact code foreign globals owner',lambda:qualified(raw,pin,verified))
 finally:th.ThreadPoolExecutor.shutdown=original_slot
 old_hook=_thread._excepthook;old_public=threading.excepthook;old_saved=threading.__excepthook__
 try:
  _thread._excepthook=_thread.get_ident;threading.excepthook=_thread.get_ident;threading.__excepthook__=_thread.get_ident
  reject('native fallback wrong imported symbol',lambda:qualified(raw,pin,verified))
 finally:_thread._excepthook=old_hook;threading.excepthook=old_public;threading.__excepthook__=old_saved
 original_owner=th.ThreadPoolExecutor.__module__
 try:th.ThreadPoolExecutor.__module__='foreign';reject('foreign class owner cannot skip',lambda:qualified(raw,pin,verified))
 finally:th.ThreadPoolExecutor.__module__=original_owner
 original_fn=threading.current_thread
 try:threading.current_thread=lambda:None;reject('foreign critical function cannot skip',lambda:qualified(raw,pin,verified))
 finally:threading.current_thread=original_fn
 original_done=base.Future.done
 try:base.Future.done=base.Future.running;reject('Future.done exact member slot',lambda:qualified(raw,pin,verified))
 finally:base.Future.done=original_done
 original_base=th._base
 try:th._base=types.ModuleType('fake');reject('Future _base module exact identity',lambda:qualified(raw,pin,verified))
 finally:th._base=original_base
 original=th.ThreadPoolExecutor.shutdown.__code__
 try:
  th.ThreadPoolExecutor.shutdown.__code__=(lambda self,wait=True,cancel_futures=False:None).__code__
  reject('modified loaded shutdown code',lambda:qualified(raw,pin,verified))
 finally:th.ThreadPoolExecutor.shutdown.__code__=original
 old=threading.__file__
 try:threading.__file__='/tmp/alternate-threading.py';reject('loaded source origin alias',lambda:qualified(raw,pin,verified))
 finally:threading.__file__=old
 old=th.__cached__
 try:th.__cached__='/tmp/alternate-thread.pyc';reject('loaded cache origin alias',lambda:qualified(raw,pin,verified))
 finally:th.__cached__=old
 for field,value in [('pythonVersion','wrong'),('files',{})]:
  bad=json.loads(raw);bad[field]=value;data=json.dumps(bad).encode();reject('pin '+field,lambda data=data:qualified(data,pin,{str(pin):hashlib.sha256(data).hexdigest()}))
 reject('unvalidated pin bytes',lambda:qualified(raw+b' ',pin,verified))
 source=pathlib.Path(th.__file__);expected=compile(source.read_bytes(),str(source),'exec',dont_inherit=True,optimize=sys.flags.optimize);valid=importlib.util.MAGIC_NUMBER+b'\0'*12+marshal.dumps(expected);s.cache_code(valid,expected);r['checks'].append('synthetic correct cache compiled from exact verified source')
 nested=next(c for c in expected.co_consts if type(c) is types.CodeType)
 altered=expected.replace(co_consts=tuple(c.replace(co_stacksize=c.co_stacksize+1) if c is nested else c for c in expected.co_consts))
 reject('nested cached code metadata',lambda:s.cache_code(importlib.util.MAGIC_NUMBER+b'\0'*12+marshal.dumps(altered),expected))
 reject('trailing cache data',lambda:s.cache_code(valid+b'junk',expected));reject('short cache',lambda:s.cache_code(b'',expected));reject('bad magic cache',lambda:s.cache_code(b'xxxx'+valid[4:],expected));reject('unknown cache flag',lambda:s.cache_code(valid[:4]+b'\2\0\0\0'+valid[8:],expected))
 badcode=compile('raise RuntimeError("wrong")',str(source),'exec');bad=importlib.util.MAGIC_NUMBER+b'\0'*12+marshal.dumps(badcode);reject('different semantic cache code',lambda:s.cache_code(bad,expected));reject('cache nonmodule code type',lambda:s.cache_code(importlib.util.MAGIC_NUMBER+b'\0'*12+marshal.dumps(1),expected))
 # Actual pathname cache acquisition is injected read-only: keep all system
 # files unchanged and demonstrate qualifying code cannot trust source alone.
 original_read=s.read;cache=str(pathlib.Path(importlib.util.cache_from_source(str(source))))
 def changed(path):return bad if str(path)==cache else original_read(path)
 s.read=changed
 try:
  if pathlib.Path(cache).exists():reject('actual cache path altered bytes before import',lambda:qualified(raw,pin,verified))
 finally:s.read=original_read
 final=qualified(raw,pin,verified);r['checks'].append('restored actual loaded source/cache qualifies')
 from preflight import checked_guard
 guard,files=checked_guard();assert guard.MAX_LIBRARY_WORKERS==8 and guard.MAX_LIBRARIES==256 and issubclass(guard.UncertainWorkers,BaseException);assert str(source) in files;r['checks'].append('actual checked_guard imports only after full origin qualification')
 from timing_source import original_ast
 original_ast(ast.unparse(__import__('parent_source').original((ROOT/'qa/native.py').read_text())));r['checks'].append('whole native original365 AST except exact declared timestamp statements')
 r.update(passed=True,inputs={str(p):sha(p) for p in [ROOT/'qa/stdlib_origin.py',ROOT/'qa/preflight.py',ROOT/'qa/native.py',pathlib.Path(__file__),pin]})
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
