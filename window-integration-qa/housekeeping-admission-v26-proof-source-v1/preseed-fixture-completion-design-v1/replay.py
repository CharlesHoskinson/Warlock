"""Actual inherited preseed deadline/history cue before final PNG unlink; CPU only."""
import hashlib,json,os,sys,tempfile,threading,time
from pathlib import Path
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26');D=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from scene_controller import SceneController
from test_capture_lease import FileDesktop
from test_scene_controller import Transport
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 paths=[Path(__file__),B/'scene_controller.py',B/'test_preview_admission.py',B/'test_capture_lease.py'];sources={str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o7777}for p in paths};gate=threading.Event();permit=threading.Event();result={}
 with tempfile.TemporaryDirectory(prefix='preseed-finally-cpu-')as root:
  desktop=FileDesktop(Path(root));transport=Transport();controller=SceneController(desktop,transport);original_outputs=transport.ensure_outputs;original_release=desktop.release_sources
  def outputs(*a,**kw):
   r=controller.current;time.sleep(max(0,(r.profile['receivedNs']+2000000000-time.monotonic_ns())/1000000000)+.01);return original_outputs(*a,**kw)
  def release(sources):
   if sources:gate.set();assert permit.wait(2),'explicit CPU final-unlink permit missing'
   return original_release(sources)
  transport.ensure_outputs=outputs;desktop.release_sources=release;desktop.finish_capture_previews=lambda*a,**kw:None
  start=time.monotonic_ns()
  try:
   w=desktop.windows[0];controller.request('minimize',w['address'],w['stableId'],w['pid'],context=1);assert gate.wait(3)
   initial={'historyCount':len(controller.history),'failure':controller.history[0].profile['failure'],'removedCount':len(desktop.removed),'createdCount':len(desktop.created),'actualPNGStillExists':[p.exists()for p in desktop.created],'seeded':any(m['command']=='seed'for m in transport.sent),'observedNs':time.monotonic_ns()}
   assert initial['historyCount']==1 and initial['removedCount']==0 and initial['createdCount']==3 and all(initial['actualPNGStillExists'])and not initial['seeded'];assert initial['failure']=='original scene receipt deadline before seed'
   permit.set();controller.workers.shutdown(wait=True,cancel_futures=True)
   final={'removedCount':len(desktop.removed),'actualPNGStillExists':[p.exists()for p in desktop.created],'observedNs':time.monotonic_ns()};assert final['removedCount']==3 and not any(final['actualPNGStillExists']);assert final['observedNs']-start<3000000000
   result={'result':'pass','counterexampleConfirmed':True,'initial':initial,'final':final,'originalDeadlineSeconds':2,'originalFixtureWaitSeconds':3,'gateIsExplicitCPUFixture':True,'noProductEdits':True,'nativeAccepted':False,'scope':Path('/proc/self/cgroup').read_text().strip(),'sources':sources}
  finally:permit.set();controller.workers.shutdown(wait=True,cancel_futures=True)
 assert all(sha(p)==r['sha256']for p,r in sources.items());result['sourceUnchanged']=True
 with os.fdopen(os.open(D/'actual-counterexample.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':result['result'],'initialRemoved':initial['removedCount'],'finalRemoved':final['removedCount'],'actualLocalCaptureFiles':initial['createdCount']}))
if __name__=='__main__':main()
