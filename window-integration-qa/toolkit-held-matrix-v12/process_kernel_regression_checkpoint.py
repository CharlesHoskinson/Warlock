from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
import helper_observer as observer
from proc_disappearance_fixture import observe
B=Path(__file__).resolve().parent;scope=require_qa_scope();selected=observe(observer);registration=observe(observer,'process');command=['/usr/bin/python3','-m','unittest','discover','-s',str(B),'-p','test_process_disappearance.py','-v'];run=subprocess.run(command,capture_output=True,text=True,timeout=20)
passed=run.returncode==0 and selected['result'] is False and selected['error'] is None and selected['actualChildExit']==0 and selected['pidfdExitObserved'] and registration['error']['errno']==3 and registration['actualChildExit']==0 and registration['pidfdExitObserved']
report=dict(result='pass' if passed else 'fail',scope=scope,actualSelectedObservation=selected,actualStrictRegistration=registration,command=command,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'helper_observer.py',B/'proc_disappearance_fixture.py',B/'test_process_disappearance.py')},syntheticProcReadError=False,nativeLaunch=False)
p=B/'process-kernel-regression-checkpoint.json'
with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
p.chmod(0o600);print(report['result']);raise SystemExit(int(not passed))
