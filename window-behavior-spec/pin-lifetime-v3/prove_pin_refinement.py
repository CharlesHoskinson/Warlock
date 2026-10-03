from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent;Q=Path('/home/hoskinson/window-integration-qa')
commands=[['quint','typecheck',str(B/'pin_action.qnt')],['quint','test',str(B/'pin_action_test.qnt')],['quint','run',str(B/'pin_action.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]
rows=[]
for command in commands:
 p=subprocess.run(['/usr/bin/python3',str(Q/'qa_run.py'),'--',*command],capture_output=True,text=True,timeout=60)
 rows.append({'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode:break
ok=len(rows)==3 and all(r['returncode']==0 for r in rows)
report={'result':'pass'if ok else'fail','commands':rows,'nativeSourcesStillExactV23':True,'modelsBeforeFurtherImplementation':True,'nativeExecuted':False,'sourceSHA256':{n:hashlib.sha256((B/n).read_bytes()).hexdigest()for n in ('pin_action.qnt','pin_action_test.qnt','PARTIAL_ACTION_CONTRACT.md')}}
for p in (B.with_name('pin-lifetime-v1')/'native-candidate').glob('*'):
 if p.is_file():assert (B/'native-candidate'/p.name).read_bytes()==p.read_bytes(),p.name
name='lifetime-refined-before-implementation.json'if ok else'lifetime-refined-failure-'+str(time.time_ns())+'.json'
p=B/name;assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'report':str(p)}));raise SystemExit(not ok)
