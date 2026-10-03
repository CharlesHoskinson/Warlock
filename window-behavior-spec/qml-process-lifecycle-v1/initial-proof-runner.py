from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not list(B.glob('*.cpp'))
 before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.qnt','.md','.py')};rows=[]
 for c in [['quint','test',str(B/'process_lifecycle.qnt')],['quint','run',str(B/'process_lifecycle.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 stable=all(sha(p)==h for p,h in before.items());good=stable and all(r['exitCode']==0 for r in rows);row=dict(result='pass'if good else'fail',inputs=before,commands=rows,sourceUnchanged=stable,registryImplemented=False,GUI=False,rootReviewBeforeRuntime=True)
 p=B/('formal-before-runtime.json'if good else f'model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
