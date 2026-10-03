"""Actual focused CPU/kernel source proof with retained timing evidence."""
import hashlib,json,os,sys,time,unittest
from pathlib import Path
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26');P=Path('/home/hoskinson/window-integration-qa/housekeeping-admission-v26-focused-proof-v2');sys.path.insert(0,str(B));import test_housekeeping_admission as tests
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 P.mkdir(mode=0o700);paths=[Path(__file__),B/'test_housekeeping_admission.py',B/'native_runtime.py',B/'readonly_ipc.py',B/'test_actor_resources.py',B/'scene_controller.py',B/'scene_manager.py',B/'owned_commands.py',B/'service_runtime.py',B/'test_readonly_ipc.py',B/'test_scene_controller.py'];sources={str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o7777}for p in paths};start=time.monotonic();log=P/'cpu.log'
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests));f.flush();os.fsync(f.fileno())
 unchanged=all(sha(p)==r['sha256']and Path(p).stat().st_mode&0o7777==r['mode']for p,r in sources.items());passed=result.wasSuccessful()and result.testsRun==14 and unchanged
 report={'result':'pass'if passed else'fail','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'sourceUnchanged':unchanged,'sources':sources,'cpuEvidence':tests.EVIDENCE,'log':str(log),'logSHA256':sha(log),'wallSeconds':time.monotonic()-start,'scope':Path('/proc/self/cgroup').read_text().strip(),'originalQueryTimeoutSeconds':.6,'nativeAccepted':False,'mainChanged':False}
 with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:v for k,v in report.items()if k not in ('sources','cpuEvidence')}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
