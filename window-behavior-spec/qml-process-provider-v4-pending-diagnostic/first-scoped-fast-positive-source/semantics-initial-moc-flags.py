from pathlib import Path
import hashlib,json,stat,subprocess,time,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py')}
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split()
 cs=[['/usr/lib/qt6/moc',*flags,'cpu_popup_semantics.cpp','-o','cpu_popup_semantics.moc'],['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','cpu_popup_semantics.cpp','-o','cpu-popup-semantics',*flags], [str(B/'cpu-popup-semantics')]];rows=[]
 for c in cs:
  r=subprocess.run(c,cwd=B,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 unchanged=all(sha(p)==h for p,h in before.items());good=unchanged and len(rows)==len(cs)and all(r['exitCode']==0 for r in rows)
 result={'result':'pass'if good else'fail','sources':before,'sourceUnchanged':unchanged,'commands':rows,'popupRuntimeImplemented':False,'GUI':False,'actualInstalledQSPopupAccepted':False}
 out=B/('qt-semantics-before-popup-runtime.json'if good else f'qt-semantics-failure-{time.time_ns()}.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(result=result['result'],report=str(out))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
