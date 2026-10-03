from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();files=[B/n for n in ['SourceAliases.hpp','Lifetime.hpp','cpu_source_aliases.cpp',Path(__file__).name]];before={str(p):sha(p)for p in files};flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();commands=[['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(B/'cpu_source_aliases.cpp'),'-o',str(B/'cpu-source-aliases'),*flags],[str(B/'cpu-source-aliases')]];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 good=len(rows)==2 and all(x['exitCode']==0 for x in rows)and all(sha(p)==h for p,h in before.items());p=B/f'source-aliases-cpu-{time.time_ns()}.json';p.write_text(json.dumps(dict(result='pass'if good else'fail',sources=before,commands=rows,GUI=False),indent=2)+'\n');print(json.dumps(dict(result='pass'if good else'fail',report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
