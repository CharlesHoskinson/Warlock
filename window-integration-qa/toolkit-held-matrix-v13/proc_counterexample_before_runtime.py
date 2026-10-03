from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
import helper_observer as observer
from proc_disappearance_fixture import observe
B=Path(__file__).resolve().parent;scope=require_qa_scope();row=observe(observer)
passed=row['error'] is not None and row['error']['errno']==3 and row['error']['type']=='ProcessLookupError' and row['actualChildExit']==0 and row['pidfdExitObserved'] and row['procPathGone']
report=dict(result='counterexample-established' if passed else 'unexpected',scope=scope,actualProcFDRead=row,sourceSHA256=hashlib.sha256((B/'helper_observer.py').read_bytes()).hexdigest(),noNative=True,syntheticReadError=False)
p=B/'process-kernel-counterexample-before-runtime.json'
with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
p.chmod(0o600);print(json.dumps(dict(result=report['result'],actualKernelErrno=row['error']['errno'] if row['error'] else None)));raise SystemExit(int(not passed))
