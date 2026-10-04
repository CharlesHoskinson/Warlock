import hashlib,json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];o=r/'qa'/('model-'+str(time.time_ns()));o.mkdir()
commands=[['quint','typecheck',str(r/'spec/admission.qnt')],['quint','test',str(r/'spec/admission.qnt'),'--main=admission','--match=Test$','--max-samples=1','--seed=66501'],['quint','run',str(r/'spec/admission.qnt'),'--main=admission','--invariant=safety','--max-samples=500','--max-steps=50','--seed=66502']]
results=[]
for i,c in enumerate(commands):
 p=subprocess.run(c,capture_output=True,text=True,timeout=90);(o/f'{i}.log').write_text(p.stdout+p.stderr);results.append({'command':c,'exitCode':p.returncode})
 if p.returncode:break
controls=[]
if len(results)==3 and all(x['exitCode']==0 for x in results):
 src=(r/'spec/admission.qnt').read_text()
 for name,old,new in [('skip-reservation','durable.reserved+3','durable.reserved'),('skip-generation-replay','generation>durable.generation','generation>0'),('expose-without-restart-barrier','ready and phase==0,exposed','phase==0,exposed')]:
  assert old in src;s=src.replace(old,new)
  if name=='skip-generation-replay':
   witness='run staleGenerationWitnessTest=init.then(admit(1,1,2)).then(commit).then(admit(2,2,1)).then(commit).then(all{assert(safety),reset})'
   s=s[:s.rindex('}')]+witness+'\n}'
  f=o/(name+'.qnt');f.write_text(s)
  t=subprocess.run(['quint','typecheck',str(f)],capture_output=True,text=True,timeout=90)
  cmd=['quint','run',str(f),'--main=admission','--invariant=safety','--max-samples=1000','--max-steps=60','--seed=66503']
  if name=='skip-generation-replay':cmd=['quint','test',str(f),'--main=admission','--match=staleGenerationWitnessTest','--max-samples=1','--seed=66503']
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=90);(o/(name+'.log')).write_text(t.stdout+t.stderr+p.stdout+p.stderr)
  controls.append({'name':name,'typecheckExit':t.returncode,'counterexampleExit':p.returncode,'command':cmd})
v={'passed':len(results)==3 and all(x['exitCode']==0 for x in results) and len(controls)==3 and all(x['typecheckExit']==0 and x['counterexampleExit']!=0 for x in controls),'commands':results,'mutations':controls,'specSHA256':hashlib.sha256((r/'spec/admission.qnt').read_bytes()).hexdigest(),'nativeAcceptance':False};(o/'report.json').write_text(json.dumps(v,indent=2)+'\n');print(o/'report.json');sys.exit(0 if v['passed'] else 1)
