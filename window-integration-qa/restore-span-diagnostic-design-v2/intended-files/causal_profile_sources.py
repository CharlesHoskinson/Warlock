"""Finite exact code labels for the unchanged diagnostic BoundaryProfile."""
import hashlib,json,os,stat,sys,types
from pathlib import Path
TARGETS={
 'scene_controller':('SceneController.prepare','SceneController.fresh','SceneController.commit_members','SceneController.watchdog','SceneController.settle'),
 'native_desktop':('NativeDesktop.plan_destinations','NativeDesktop.plan_destinations.<locals>.plan','NativeDesktop.plan_destinations.<locals>.guard','NativeDesktop.plan_destination','NativeDesktop.apply_destination','NativeDesktop.refresh_destination','NativeDesktop.capture_source','NativeDesktop._capture_source_impl','NativeDesktop.target','NativeDesktop.retire_gestures','NativeDesktop.finish_capture_previews'),
 'production_motion_6d9':('BasicDesktop.capture','BasicDesktop.clients','BasicDesktop.ipc','BasicDesktop.target','BasicDesktop.reduced','BasicDesktop.monitors','Desktop.capture','Desktop.capture_locked','Desktop.check_current','Desktop.publish_crop'),
 'owned_commands':('OwnedCommands.run','OwnedCommands.check_output'),
 'owned_launch':('OwnedLaunch.__init__','OwnedLaunch.complete'),
 'helper_supervisor':('Keeper.register','Keeper.complete','Keeper.exchange'),
 'readonly_ipc':('ReadonlyIPC.query',),
 'snapshot_cache':('SnapshotCache.restore','SnapshotCache.publish'),
 'batch_preview':('BatchPreviews.stage','BatchPreviews.finish'),
 'pipe_transport':('PipeTransport.ensure_outputs','PipeTransport.send'),
 'service_runtime':('RuntimeService.persist',)}
OBSERVER=('ObservedFactory.retain_source','ObservedFactory.retain_cache_pair','ObservedFactory.__call__.<locals>.capture_and_observe')

def nested(code):
 yield code
 for child in code.co_consts:
  if type(child) is types.CodeType:yield from nested(child)

class SpanSelection:
 def __init__(self,service,service_manifest,observer,collector_manifest):
  self.sources={};self.roots=[];self.refs=[];self.expected={};self.identities=[]
  if sum(map(len,TARGETS.values()))+len(OBSERVER)>64:raise ValueError('bounded selection required')
  for name,symbols in TARGETS.items():
   module=sys.modules.get(name);path=service/(name+'.py')
   if type(module) is not types.ModuleType or Path(module.__file__)!=path:raise ValueError('actual selected module differs')
   self._select(path,symbols,vars(module),service_manifest)
  path=Path(observer.__dict__['__call__'].__code__.co_filename)
  self._select(path,OBSERVER,{'ObservedFactory':observer},collector_manifest)
  self.initial=self._current()
 def _select(self,path,symbols,namespace,manifest):
  name=str(path);before=path.lstat();digest=hashlib.sha256(path.read_bytes()).hexdigest();after=path.lstat()
  identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns,x.st_mode)
  if path.resolve()!=path or not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or identity(before)!=identity(after) or manifest['inputs'].get(name)!=digest or manifest['inputModes'].get(name)!=stat.S_IMODE(before.st_mode):raise ValueError('selected diagnostic source differs')
  self.sources[name]={'sha256':digest,'mode':stat.S_IMODE(before.st_mode),'symbols':list(symbols)}
  for symbol in symbols:
   cls_name,method,*tail=symbol.split('.');cls=namespace[cls_name]
   fn=vars(cls).get(method)
   if type(fn) is not types.FunctionType:raise ValueError('exact genuine code-bearing method required')
   matches=[c for c in nested(fn.__code__) if c.co_qualname==symbol and c.co_filename==name]
   if len(matches)!=1:raise ValueError('exact selected code symbol missing/ambiguous')
   code=matches[0];self.refs.append(code);self.roots.append((cls,method,fn))
   self.expected[(name,symbol)]=id(code)
   self.identities.append({'path':name,'symbol':symbol,'codeObjectID':id(code),'functionID':id(fn),'ownerClassID':id(cls)})
 def _current(self):
  return [(id(cls),method,id(vars(cls).get(method)),id(vars(cls).get(method).__code__) if type(vars(cls).get(method)) is types.FunctionType else None) for cls,method,fn in self.roots]
 def project(self,raw,destination):
  errors=[]
  if self._current()!=self.initial:errors.append('selected callable/code bindings changed')
  for row in raw['events']:
   if row['event']=='call' and self.expected.get((row['path'],row['symbol']))!=row['codeObjectID']:errors.append('foreign/unexpected code object label')
  result={'version':1,'complete':raw['traceComplete'] and not errors,'errors':errors,'expectedCodeObjects':self.identities,'sourceSelection':self.sources,'rawProfileTraceComplete':raw['traceComplete'],'timingPerturbation':True,'nativeAuthority':False,'returnEventProvesSuccess':False,'originalDeadlineUnchanged':True}
  with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  return result
