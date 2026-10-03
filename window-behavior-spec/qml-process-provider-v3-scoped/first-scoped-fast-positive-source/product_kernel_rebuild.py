from pathlib import Path
import hashlib,json,subprocess,sys,time,shutil
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();old=json.loads((B/'product-capture-build.json').read_text());changed=str(B/'ProcessKernel.cpp');assert old['result']=='pass';assert all(sha(p)==h for p,h in old['sources'].items()if p!=changed);assert all(sha(p)==h for p,h in old['dependencies'].items()if p!=changed);shutil.copy2(B/'product-capture-build.json',B/f'product-build-before-kernel-{time.time_ns()}.json');before={str(p):sha(p)for p in B.iterdir()if p.suffix in('.cpp','.hpp','.py')};commands=[next(v['command']for v in old['commands']if '-c'in v['command']and changed in v['command']),old['commands'][-1]['command']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=stable and len(rows)==2 and all(v['exitCode']==0 for v in rows);report=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,commands=rows,priorBuild=old,explicitKernelSourceDelta={'before':old['sources'][changed],'after':sha(changed)},GUI=False)
 if good:report.update(binarySHA256=sha(B/'cpu-product-capture'),objectSHA256={str(p):sha(p)for p in(B/'process-build').glob('*.o')})
 p=B/('product-capture-build.json'if good else f'product-kernel-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(result=report['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
