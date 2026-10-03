from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();records=[]
for c in [['quint','typecheck',str(B/'reduction_validation_v18.qnt')],['quint','test',str(B/'reduction_validation_v18_test.qnt')],['quint','run',str(B/'reduction_validation_v18.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(c,capture_output=True,text=True,timeout=120);records.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
epoch=json.loads((B/'reduced-observation-before-correction-epoch.json').read_text());same=all(hashlib.sha256((B/n).read_bytes()).hexdigest()==v for n,v in epoch.items());ok=same and len(records)==3 and all(r['exitCode']==0 for r in records)
with (B/'reduced-observation-formal-before-correction.json').open('x')as f:json.dump(dict(result='pass'if ok else'fail',scope=scope,records=records,runtimeStillDraftBeforeCorrection=same,sources={n:hashlib.sha256((B/n).read_bytes()).hexdigest()for n in ('REDUCTION_VALIDATION_CONTRACT.md','reduction_validation_v18.qnt','reduction_validation_v18_test.qnt')},nativeGUI=False),f,indent=2);f.write('\n')
print('PASS35 formal before correction'if ok else'FAIL');raise SystemExit(int(not ok))
