from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def rec(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 require_qa_scope();old=Path('/home/hoskinson/window-integration-qa/process-terminal-v8-first-disconnect-failure-handoff-v1.json');a=json.loads(old.read_text());assert all(rec(Path(p))=={'sha256':h,'mode':a['inputModes'][p]}for p,h in a['inputs'].items())
 inputs={str(p):rec(p)for p in [old,B/'CONTRACT.md',B/'disconnect_fixture.qnt',Path(__file__)]};rows=[]
 for c in [['quint','test',str(B/'disconnect_fixture.qnt')],['quint','run',str(B/'disconnect_fixture.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append({'command':c,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 stable=all(rec(Path(p))==v for p,v in inputs.items());good=stable and all(r['exitCode']==0 for r in rows);row={'result':'pass'if good else'fail','inputs':inputs,'commands':rows,'failedV8Exact':True,'sourceStable':stable,'runtimeChanged':False,'GUI':False}
 p=B/('formal-before-fixture-change.json'if good else f'model-failure-{time.time_ns()}.json');assert not p.exists();p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'report':str(p)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
