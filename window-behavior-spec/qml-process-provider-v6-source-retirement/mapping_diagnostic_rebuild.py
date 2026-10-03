from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();old=json.loads((B/'process-cpu-build.json').read_text());assert old['result']=='pass'
 modified={str(B/'MappingDiagnostic.cpp')}
 assert all(sha(p)==h for p,h in old['sources'].items()if p not in modified)
 assert all(sha(p)==h for p,h in old['dependencies'].items()if p not in modified)
 compile_command=next(r['command']for r in old['commands']if '-c'in r['command']and str(B/'MappingDiagnostic.cpp')in r['command'])
 commands=[compile_command,old['commands'][-1]['command']];rows=[];before={str(p):sha(p)for p in B.iterdir()if p.suffix in('.cpp','.hpp','.py')}
 for command in commands:
  r=subprocess.run(command,capture_output=True,text=True,timeout=120);rows.append(dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=len(rows)==2 and all(r['exitCode']==0 for r in rows)and stable
 row=dict(result='pass'if good else'fail',sourceUnchanged=stable,sources=before,commands=rows,GUI=False,verifiedUnchangedInheritedBuild=old)
 if good:
  row['dependencies']={p:sha(p)for p in old['dependencies']};row['binarySHA256']=sha(B/'cpu-process-runtime')
 p=B/f'mapping-diagnostic-build-{time.time_ns()}.json';p.write_text(json.dumps(row,indent=2)+'\n')
 if good:(B/'process-cpu-build.json').write_text(json.dumps(row,indent=2)+'\n')
 print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
