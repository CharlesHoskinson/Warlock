from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.qnt','.md','.py')}
 commands=[]
 for name in ['mapping_device.qnt','device_relation.qnt']:
  commands += [['quint','test',str(B/name)],['quint','run',str(B/name),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]
 rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 stable=all(sha(p)==h for p,h in before.items());good=stable and all(r['exitCode']==0 for r in rows);row=dict(result='pass'if good else'fail',inputs=before,commands=rows,sourceUnchanged=stable,mappingPredicateChanged=False,GUI=False,rootReviewBeforeRuntime=True)
 p=B/('formal-complete-before-guard-change.json'if good else f'model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
