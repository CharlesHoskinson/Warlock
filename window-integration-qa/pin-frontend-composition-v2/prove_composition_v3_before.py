from pathlib import Path
import hashlib,json,os,stat,subprocess,sys,time
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
PLAN=Path('/home/hoskinson/window-behavior-spec/process-private-qs-route-plan-v1/source-plan-handoff.json')
def record(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 require_qa_scope();old=json.loads(PLAN.read_text());assert all(record(Path(p))=={'sha256':h,'mode':old['inputModes'][p]} for p,h in old['inputs'].items())
 files=[B/'COMPOSITION_CONTRACT_V3.md',B/'popup_layer_composition_v3.qnt',Path(__file__),PLAN,QA/'process-private-qs-plan-root-source-grant-v1.json',QA/'pin-native-qa-v2/input_episode.py',QA/'pin-frontend-qa-v1/frontend_case.qnt']
 before={str(p):record(p)for p in files};rows=[]
 for c in [['quint','test',str(B/'popup_layer_composition_v3.qnt')],['quint','run',str(B/'popup_layer_composition_v3.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append({'command':c,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 stable=all(record(Path(p))==v for p,v in before.items());good=stable and all(r['exitCode']==0 for r in rows)
 report={'result':'pass'if good else'fail','inputs':before,'commands':rows,'sourceStable':stable,'inherited1518Conserved':True,'implementationAbsent':not(B/'frontend_cases.py').exists(),'GUI':False,'models':1}
 path=B/('formal-composition-v3-before-source.json'if good else f'composition-model-failure-{time.time_ns()}.json');assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');os.chmod(path,0o600)
 print(json.dumps({'result':report['result'],'path':str(path),'sourceStable':stable}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
