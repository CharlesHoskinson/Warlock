from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();assert not(B/'ProcessRegistry.cpp').exists();p=B/'cpu_process_semantics.cpp';before=sha(p);flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml'],text=True).split();mocflags=[x for x in flags if not x.startswith('-l')]
 rows=[]
 for c in [['/usr/lib/qt6/moc',*mocflags,str(p),'-o',str(B/'cpu_process_semantics.moc')],['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(B/'cpu-process-semantics'),*flags],[str(B/'cpu-process-semantics')]]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=90);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 good=len(rows)==3 and all(r['exitCode']==0 for r in rows)and sha(p)==before
 row=dict(result='pass'if good else'fail',source=str(p),sourceSHA256=before,sourceUnchanged=sha(p)==before,commands=rows,GUI=False,registryStillAbsent=not(B/'ProcessRegistry.cpp').exists(),installedQSProcessAccepted=False)
 out=B/('semantic-before-registry.json'if good else f'semantic-failure-{time.time_ns()}.json');out.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(out))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
