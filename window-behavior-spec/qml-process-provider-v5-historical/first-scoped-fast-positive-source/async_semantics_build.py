from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();paths=[B/'cpu_async_semantics.cpp',Path(__file__)]+[Path('/usr/include/qt6/QtCore')/n for n in ('qpromise.h','qfuture.h','qfuturewatcher.h','qfutureinterface.h')]+[Path('/usr/include/pthread.h')];inputs={str(p):sha(p)for p in paths};rows=[]
 command=['pkg-config','--cflags','--libs','Qt6Core'];p=subprocess.run(command,capture_output=True,text=True,timeout=20);rows.append(dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0
 commands=[['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-pthread',str(B/'cpu_async_semantics.cpp'),'-o',str(B/'cpu-async-semantics')]+p.stdout.split(),[str(B/'cpu-async-semantics')]]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=30);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in inputs.items());good=stable and all(r['exitCode']==0 for r in rows);report=dict(result='pass'if good else'fail',inputs=inputs,commands=rows,sourceUnchanged=stable,GUI=False,productionRuntimeAccepted=False)
 if good:report.update(actualChecks=json.loads(rows[-1]['stdout'])['checks'],binarySHA256=sha(B/'cpu-async-semantics'))
 p=B/('async-semantics-proof.json'if good else f'async-semantics-failure-{time.time_ns()}.json');p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(result=report['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
