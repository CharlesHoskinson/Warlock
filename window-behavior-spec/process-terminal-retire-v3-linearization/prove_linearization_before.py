from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
OLD=Path('/home/hoskinson/window-integration-qa/process-terminal-retire-v2-source-proposal-handoff-v1.json')
def rec(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 require_qa_scope();inputs={str(p):rec(p)for p in [B/'LINEARIZATION_CONTRACT.md',B/'terminal_linearization.qnt',Path(__file__),OLD,B/'proposal/desired/ProcessRegistry.cpp',B/'proposal/desired/PinWindowMenu.qml']}
 ancestor=json.loads(OLD.read_text());exact=all(rec(Path(p))=={'sha256':h,'mode':ancestor['inputModes'][p]}for p,h in ancestor['inputs'].items());assert exact
 rows=[]
 for c in [['quint','test',str(B/'terminal_linearization.qnt')],['quint','run',str(B/'terminal_linearization.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append({'command':c,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 stable=all(rec(Path(p))==v for p,v in inputs.items());good=stable and all(r['exitCode']==0 for r in rows)
 row={'result':'pass'if good else'fail','inputs':inputs,'commands':rows,'sourceStableDuringProof':stable,'original63Exact':exact,'runtimeApplied':False,'compiled':False,'GUI':False}
 target=B/('formal-linearization-before-source-revision.json'if good else f'linearization-model-failure-{time.time_ns()}.json');assert not target.exists();target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'report':str(target)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
