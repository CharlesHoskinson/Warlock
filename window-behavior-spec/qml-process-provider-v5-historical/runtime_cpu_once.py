from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();build=json.loads((B/'process-cpu-build.json').read_text());assert build['result']=='pass';assert all(sha(p)==h for p,h in build['sources'].items());assert sha(B/'cpu-process-runtime')==build['binarySHA256']
 argv=[str(B/'cpu-process-runtime'),str(B/'cpu_registry_child.py'),'/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup/source-ready-inputs.json'];r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
 row=dict(result='pass'if r.returncode==0 else'fail',command=argv,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr,buildPath=str(B/'process-cpu-build.json'),buildSHA256=sha(B/'process-cpu-build.json'),currentRegistryCPPCompiled=True,productionNativeCPPCompiled=False,GUI=False,sourceUnchanged=all(sha(p)==h for p,h in build['sources'].items()))
 p=B/f'process-runtime-{time.time_ns()}.json';p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p),exitCode=r.returncode)));return int(r.returncode!=0)
if __name__=='__main__':raise SystemExit(main())
