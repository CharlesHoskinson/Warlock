from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();before={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}for p in B.iterdir()if p.is_file()and p.suffix in('.qnt','.md','.py','.json')};commands=[['quint','test',str(B/'terminal_retire.qnt')],['quint','run',str(B/'terminal_retire.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 stable=all(sha(p)==h['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==h['mode']for p,h in before.items());baseline=json.loads((B/'SOURCE_BASELINE.json').read_text());runtimeExact=all(sha(p)==h for p,h in baseline['inputs'].items());good=stable and runtimeExact and all(r['exitCode']==0 for r in rows);row=dict(result='pass'if good else'fail',inputs=before,commands=rows,sourceUnchanged=stable,V7AndFrontendExact=runtimeExact,runtimeImplemented=False,GUI=False,reviewRequiredBeforeRuntime=True)
 p=B/('formal-before-runtime.json'if good else f'model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
