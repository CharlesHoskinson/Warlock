"""One protected fresh three-root build and real receipt regression batch."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,traceback
R=Path('/home/charles/Warlock');B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
LOCK=B/'receipt-lifecycle-frontend-lock-root-v1.json';LOCK_SHA='5f4f11fd1ea60de151083decbb6741b7f676aefce9ad7dd9bf1c72edee1ea7bf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope()
 assert sha(R/'implementation/warlock/adapter/current_build.py')=='d4e5af280a275f9a777322ee60f1f34bf21751b6726edcaa4e4105a02da4dbc7'
 sys.path.insert(0,str(R/'implementation/warlock/adapter'));import current_build
 out=B/('receipt-current-build-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report=dict(passed=False,scope=scope,driverSHA256=sha(Path(__file__)),nativeAcceptance=False,fullReleaseAccepted=False)
 try:
  built=current_build.build(LOCK,LOCK_SHA,out/'frontend')
  if not built.get('passed'):raise RuntimeError('Three-root build failed')
  receipt=out/'frontend/report.json';digest=sha(receipt);current_build.validate_report(receipt,digest)
  report['buildReceipt']=dict(path=str(receipt),sha256=digest)
  argv=['/usr/bin/python3','-B',str(B/'receipt-lifecycle-root-v1/run-candidate.py'),'--build-report',str(receipt),'--build-sha256',digest]
  try:result=subprocess.run(argv,env=os.environ.copy(),capture_output=True,timeout=240)
  except subprocess.TimeoutExpired as e:
   (out/'candidate.stdout').write_bytes(e.stdout or b'');(out/'candidate.stderr').write_bytes(e.stderr or b'');report['timedOut']=True;raise
  (out/'candidate.stdout').write_bytes(result.stdout);(out/'candidate.stderr').write_bytes(result.stderr)
  report['command']=dict(argv=argv,exit=result.returncode,driverSHA256=sha(B/'receipt-lifecycle-root-v1/run-candidate.py'))
  if result.returncode:raise RuntimeError('Compiled production regression failed')
  report['candidate']=json.loads(result.stdout)
  current_build.validate_report(receipt,digest)
  report['passed']=True
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),error=report.get('error'))));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
