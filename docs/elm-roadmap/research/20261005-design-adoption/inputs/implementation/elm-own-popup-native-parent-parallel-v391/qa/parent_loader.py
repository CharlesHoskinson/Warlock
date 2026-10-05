"""Verified-source parent collector; no map/hash/process cache or authority grant."""
import hashlib,importlib.util,json,os,pathlib,sys,types
import concurrent.futures,concurrent.futures.thread,concurrent.futures._base,threading
import stdlib_origin
ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST_SHA='76d9194b31524e658b164f4c70b9c39bc48c5a8146a8a1b88746642fa3f361e3'
COLLECTOR_SHA='ae370586e5957100e13d1b940f8bc59c8f52fc6864b8721b833429719572f6e9'
GUARD_SHA='785a2c3b1717e949ed5628eb7048479c6c8897560be55b50117f098625bb71a9'
STDLIB_ORIGIN_SHA='c806a9c89f22dc43d9e70d4bb59fd924b17d6dbc73ea5141853325d2b71432a4'
class Refused(ValueError):pass
def require(value,message):
 if not value:raise Refused(message)
def verified(path,digest):
 raw=stdlib_origin.read(path);require(hashlib.sha256(raw).hexdigest()==digest,'parent loader source changed: '+str(path));return raw
def qualify_module(module,raw,path,critical):
 expected=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
 previous=stdlib_origin.CRITICAL
 stdlib_origin.CRITICAL={**previous,module.__name__:critical}
 try:return stdlib_origin.loaded_code(module,expected,path,pathlib.Path(importlib.util.cache_from_source(str(path))),raw)
 finally:stdlib_origin.CRITICAL=previous

def checked_parent(guard,guard_files,*,wrapper):
 """Before allocation, execute only the exact once-read held collector buffer."""
 origin=json.loads((ROOT/'adoption-origin.json').read_bytes());manifest_path=pathlib.Path(origin['collectorManifest']);require(manifest_path==ROOT.parent/'elm-own-popup-parent-map-parallel-v382/component-manifest.json','parent manifest origin');require(origin['collectorManifestSHA256']==MANIFEST_SHA,'parent manifest pin');manifest_raw=verified(manifest_path,MANIFEST_SHA);manifest=json.loads(manifest_raw);require(manifest['sourceHeld'] and manifest['evidenceIntegrityPassed'] and manifest['nativeAcceptance'] is False,'parent manifest held scope')
 path=manifest_path.parent/'parent_maps.py';require(manifest['files']['parent_maps.py']['sha256']==COLLECTOR_SHA,'parent source manifest row');raw=verified(path,COLLECTOR_SHA)
 # Bytecode is never imported/executed for this module. A present cache must
 # independently equal the verified source so it cannot masquerade as origin.
 cache=pathlib.Path(importlib.util.cache_from_source(str(path)));files={**guard_files,str(manifest_path):MANIFEST_SHA,str(path):COLLECTOR_SHA}
 expected=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
 if cache.exists() or cache.is_symlink():
  cached=stdlib_origin.read(cache);stdlib_origin.cache_code(cached,expected);files[str(cache)]=hashlib.sha256(cached).hexdigest()
 spec=importlib.util.spec_from_file_location('held_parent_collector382',path);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;exec(expected,module.__dict__)
 guard_path=pathlib.Path(guard.__file__);require(guard_files.get(str(guard_path))==GUARD_SHA,'parent guard not checked');guard_raw=verified(guard_path,GUARD_SHA);files[str(guard_path)]=GUARD_SHA
 origin_path=pathlib.Path(stdlib_origin.__file__);require(origin_path==ROOT/'qa/stdlib_origin.py','parent stdlib qualifier origin');origin_raw=verified(origin_path,STDLIB_ORIGIN_SHA);qualify_module(stdlib_origin,origin_raw,origin_path,('read','same_code','loaded_code','qualify'));files[str(origin_path)]=STDLIB_ORIGIN_SHA
 qualified=QualifiedParent(module,raw,path,guard,guard_raw,guard_path,files,wrapper)
 qualified.qualify(None)
 return qualified,files

class QualifiedParent:
 def __init__(self,module,raw,path,guard,guard_raw,guard_path,files,wrapper):
  self.module=module;self.raw=raw;self.path=path;self.guard=guard;self.guard_raw=guard_raw;self.guard_path=guard_path;self.files=dict(files);self.wrapper=wrapper
 def qualify(self,deadline):
  g=self.guard
  require(type(self.wrapper) is tuple and len(self.wrapper)==3,'parent wrapper proof missing')
  wrapper,wrapper_raw,wrapper_path=self.wrapper
  require(wrapper is sys.modules[__name__] and type(wrapper_raw) is bytes and wrapper_path==pathlib.Path(__file__),'parent wrapper proof owner')
  qualify_module(wrapper,wrapper_raw,wrapper_path,('checked_parent','QualifiedParent','qualify_module','verified'))
  if deadline is not None:g.remaining(deadline)
  collector=qualify_module(self.module,self.raw,self.path,('collect','_parallel_rows','Refused'))
  functions=qualify_module(g,self.guard_raw,self.guard_path,('fingerprint','process_identity','parse_maps','map_identity','read_text_bounded','remaining','_MountInfo','Refused','UncertainWorkers'))
  thread=concurrent.futures.thread;base=concurrent.futures._base
  require(g.ThreadPoolExecutor is concurrent.futures.ThreadPoolExecutor is thread.ThreadPoolExecutor,'parent executor graph differs')
  require(g._STDLIB_SHUTDOWN is thread.ThreadPoolExecutor.shutdown,'parent captured shutdown differs')
  require(g.threading is thread.threading is threading is sys.modules['threading'],'parent threading graph differs')
  require(thread._base is base is sys.modules['concurrent.futures._base'],'parent Future graph differs')
  require(g.Path is pathlib.Path and g.os is os and self.module.pathlib is pathlib and self.module.os is os,'parent path/process dependency graph differs')
  require(type(self.module.MAX_LIBRARY_WORKERS) is int and self.module.MAX_LIBRARY_WORKERS==8 and type(self.module.MAX_ROWS) is int and self.module.MAX_ROWS==16384 and type(g.MAX_LIBRARY_WORKERS) is int and g.MAX_LIBRARY_WORKERS==8,'parent bounds differ')
  # Revalidate substantive pinned source/current-cache/loaded-code stdlib
  # ownership before every actual call; retain the original deadline.
  pin_path=self.guard_path.parent/'stdlib-pin.json';require(str(pin_path) in self.files,'parent stdlib pin absent from checked graph');pin_raw=verified(pin_path,self.files[str(pin_path)])
  supplement_path=ROOT/'stdlib-supplement.json';supplement_raw=verified(supplement_path,'6b32070e236588da66e611999ad3cb4ef103970e00c987e91bbaa676d4db32f3')
  pinned={str(pin_path):hashlib.sha256(pin_raw).hexdigest(),str(supplement_path):hashlib.sha256(supplement_raw).hexdigest()};evidence=stdlib_origin.qualify(pin_raw,pin_path,pinned,supplement_raw,supplement_path)
  if deadline is not None:g.remaining(deadline)
  return {'collectorCode':collector,'guardCode':functions,'stdlib':evidence,'nativeAcceptance':False}
 def collect(self,*,pid,start,pgid,deadline):
  self.qualify(deadline)
  return self.module.collect(self.guard,pid=pid,start=start,pgid=pgid,deadline=deadline)
