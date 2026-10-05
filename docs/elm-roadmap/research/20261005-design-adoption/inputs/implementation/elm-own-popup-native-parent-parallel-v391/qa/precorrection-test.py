import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));import stdlib_origin as s
OUT=ROOT/'qa'/('precorrection-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
try:
 for name in ('stdlib_origin.py','preflight.py'):(OUT/name).write_bytes((ROOT/'qa'/name).read_bytes())
 pin=ROOT.parent/'elm-own-popup-parallel-runtime-guard-bounded-v353/stdlib-pin.json';raw=pin.read_bytes();verified={str(pin):sha(pin)}
 import threading,concurrent.futures.thread as th,concurrent.futures._base as base
 original=th.ThreadPoolExecutor.shutdown
 try:th.ThreadPoolExecutor.shutdown=th.ThreadPoolExecutor.__init__;s.qualify(raw,pin,verified);r['checks'].append('wrong legitimate shutdown slot accepted')
 finally:th.ThreadPoolExecutor.shutdown=original
 original=th.ThreadPoolExecutor.__module__
 try:th.ThreadPoolExecutor.__module__='foreign';s.qualify(raw,pin,verified);r['checks'].append('foreign class owner skipped accepted')
 finally:th.ThreadPoolExecutor.__module__=original
 original=threading.current_thread
 try:threading.current_thread=lambda:None;s.qualify(raw,pin,verified);r['checks'].append('foreign critical function skipped accepted')
 finally:threading.current_thread=original
 original=base.Future.done
 try:base.Future.done=base.Future.running;s.qualify(raw,pin,verified);r['checks'].append('unqualified Future.done alternate slot accepted')
 finally:base.Future.done=original
 r.update(passed=True,sourceSHA256=sha(ROOT/'qa/stdlib_origin.py'))
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
