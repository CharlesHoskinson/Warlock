"""Bounded exact frozen V19 CPU guard observations, no native endpoint."""
import hashlib,json,os,sys,tempfile,time
from pathlib import Path
SOURCE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-query-v19')
sys.path.insert(0,str(SOURCE))
import recovery_resources as resources
from owned_commands import SealedFile
original_read=Path.read_bytes;original_verify=resources.verify_process
samples=[];seen=[]
keys=['XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY']
def read(self,*a,**kw):
 raw=original_read(self,*a,**kw)
 if str(self).startswith('/proc/') and str(self).endswith('/environ'):
  env=dict(v.split(b'=',1) for v in raw.split(b'\0') if b'=' in v)
  seen.append({'path':str(self),'length':len(raw),'hash':hashlib.sha256(raw).hexdigest(),'selected':{k:env.get(k.encode(),b'').decode(errors='replace') for k in keys}})
 return raw
Path.read_bytes=read
def verify(row):
 try:return original_verify(row)
 except BaseException:
  sample={'pid':row['pid'],'start':row['start'],'expected':row['environment'],'actualEnvironmentReads':list(seen)}
  for name in ['stat','cmdline']:
   try:
    raw=original_read(Path(f'/proc/{row["pid"]}/{name}'));sample[name]=raw.decode(errors='replace')
   except OSError as e:sample[name]={'error':repr(e)}
  try:sample['exe']=os.readlink(f'/proc/{row["pid"]}/exe')
  except OSError as e:sample['exe']={'error':repr(e)}
  samples.append(sample);raise
resources.verify_process=verify
results=[]
with tempfile.TemporaryDirectory(prefix='legacy-proc-observation-') as raw:
 env=dict(os.environ,XDG_RUNTIME_DIR=raw,HYPRLAND_INSTANCE_SIGNATURE='cpu-no-compositor',WAYLAND_DISPLAY='never-connect')
 with SealedFile('/usr/bin/true') as executable:
  for i in range(64):
   seen.clear();child=None;start=time.monotonic_ns()
   try:
    child=resources.gated_process('/proc/self/fd/'+str(executable.fd),env=env,pass_fds=(executable.fd,),record=lambda row:None)
    child.wait(timeout=2);results.append({'index':i,'returned':True,'code':child.returncode,'reads':list(seen)})
   except Exception as e:results.append({'index':i,'returned':False,'error':repr(e),'reads':list(seen)})
   finally:
    if child:
     if child.poll() is None:child.terminate();child.wait(timeout=2)
     for stream in (child.stdin,child.stdout,child.stderr):stream.close()
result={'nativeLaunch':False,'guardUnchanged':True,'sourceManifestSHA256':hashlib.sha256((SOURCE/'manifest-family-query-v19.json').read_bytes()).hexdigest(),'guardSourceSHA256':hashlib.sha256((SOURCE/'recovery_resources.py').read_bytes()).hexdigest(),'count':len(results),'failures':samples,'results':results}
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'count':len(results),'failures':len(samples),'resultSHA256':hashlib.sha256(Path(__file__).with_name('result.json').read_bytes()).hexdigest()}))
