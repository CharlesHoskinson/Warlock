"""Only focused new source/guard CPU tests, with retained failed reports."""
from pathlib import Path
import json,subprocess,sys,time
from io_guard import publish_json,sha
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from qa_launch import require_qa_scope
def main():
 require_qa_scope();files=[p for p in B.rglob('*')if p.is_file()and p.suffix in('.py','.qml','.cpp')and '__pycache__'not in p.parts];before={str(p):sha(p)for p in files};rows=[]
 for name in ('test_guards.py','test_source_overlay.py'):
  cmd=['/usr/bin/python3','-B',str(B/name),'-v'];r=subprocess.run(cmd,capture_output=True,text=True,timeout=30);rows.append(dict(command=cmd,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());ok=all(r['exitCode']==0 for r in rows)and len(rows)==2 and stable;report=dict(result='pass'if ok else'fail',commands=rows,sourceSHA256=before,sourceStable=stable,GUI=False,QtRuntimePositive=False,NativeHelpersExecuted=False)
 path=B/('cpu-report.json'if ok else'cpu-failure-'+str(time.time_ns())+'.json');publish_json(path,report);print(json.dumps(dict(result=report['result'],path=str(path),GUI=False)));return int(not ok)
if __name__=='__main__':raise SystemExit(main())
