from pathlib import Path
import hashlib,json,os,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def main():
 require_qa_scope();files=[p for p in B.glob('*.py')]+[B/'frontend/PinWindowMenu.qml'];before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
 command=['/usr/bin/python3','-m','unittest','-v','test_controller_receipt_episode'];r=subprocess.run(command,cwd=B,capture_output=True,text=True,timeout=30)
 stable=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items());good=r.returncode==0 and stable
 report={'result':'pass'if good else'fail','sourceSHA256':before,'sourceStable':stable,'command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'actualUnprojectedCPU':True,'controlledDataNotNativeAuthority':True,'GUI':False}
 target=B/('cpu-receipt-loop-report.json'if good else f'cpu-failure-{time.time_ns()}.json');assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');os.chmod(target,0o600)
 print(json.dumps({'result':report['result'],'path':str(target),'sourceStable':stable}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
