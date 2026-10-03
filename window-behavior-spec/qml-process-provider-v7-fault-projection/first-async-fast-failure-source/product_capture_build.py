from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();old=json.loads((B/'process-cpu-build.json').read_text());assert old['result']=='pass'
 assert all(sha(p)==h for p,h in old['sources'].items());assert all(sha(p)==h for p,h in old['dependencies'].items());before={str(p):sha(p)for p in B.iterdir()if p.suffix in('.cpp','.hpp','.py')}
 template=next(v['command']for v in old['commands']if '-c'in v['command']and str(B/'cpu_process_runtime.cpp')in v['command']);compile_command=[v.replace('cpu_process_runtime.cpp','cpu_product_capture.cpp')for v in template]
 link=[v.replace('cpu_process_runtime.cpp.o','cpu_product_capture.cpp.o').replace('/cpu-process-runtime','/cpu-product-capture')for v in old['commands'][-1]['command']];rows=[]
 for c in [compile_command,link]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=len(rows)==2 and all(v['exitCode']==0 for v in rows)and stable;r=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,commands=rows,GUI=False,verifiedCurrentRegistryBuild=str(B/'process-cpu-build.json'),registryBuildSHA256=sha(B/'process-cpu-build.json'))
 if good:r['binarySHA256']=sha(B/'cpu-product-capture')
 p=B/('product-capture-build.json'if good else f'product-capture-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(result=r['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
