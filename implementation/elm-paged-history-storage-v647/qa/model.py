import json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa'/('model-'+str(time.time_ns()));out.mkdir()
commands=[['quint','typecheck',str(root/'spec/storage.qnt')],['quint','test',str(root/'spec/storage.qnt'),'--main=storage','--match=Test$','--max-samples=1','--seed=64701'],['quint','run',str(root/'spec/storage.qnt'),'--main=storage','--invariant=safety','--max-samples=500','--max-steps=50','--seed=64702']]
results=[]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,capture_output=True,text=True);(out/f'{i}.log').write_text(p.stdout+p.stderr);results.append({'command':cmd,'exitCode':p.returncode})
 if p.returncode: print(p.stdout+p.stderr);break
mutations=[('expose-visible-before-root-barrier','ready and durable.contains(k)','visible.contains(k)'),('drop-durable-history-on-restart',"durable'=visible, visible'=visible", "durable'=Set(), visible'=visible"),('skip-capacity-charge',"charge'=charge+1","charge'=charge")]
controls=[]
if len(results)==3 and all(x['exitCode']==0 for x in results):
 source=(root/'spec/storage.qnt').read_text()
 for name,old,new in mutations:
  assert old in source
  mutant=out/(name+'.qnt');changed=source.replace(old,new)
  if name=='expose-visible-before-root-barrier':
   witness='run unsafeExposureWitnessTest = init.then(reserve(1)).then(advance).then(advance).then(advance).then(advance).then(expose(1)).then(all {assert(safety),reset})'
   changed=changed[:changed.rindex('}')]+witness+'\n}'
  mutant.write_text(changed)
  cmd=['quint','run',str(mutant),'--main=storage','--invariant=safety','--max-samples=500','--max-steps=50','--seed=64702'] if name!='drop-durable-history-on-restart' else ['quint','test',str(mutant),'--main=storage','--match=conservationTest','--max-samples=1','--seed=64701']
  if name=='expose-visible-before-root-barrier':cmd=['quint','test',str(mutant),'--main=storage','--match=unsafeExposureWitnessTest','--max-samples=1','--seed=64701']
  typed=subprocess.run(['quint','typecheck',str(mutant)],capture_output=True,text=True)
  observed=subprocess.run(cmd,capture_output=True,text=True)
  (out/(name+'.log')).write_text(typed.stdout+typed.stderr+observed.stdout+observed.stderr)
  controls.append({'mutation':name,'typecheckExit':typed.returncode,'counterexampleExit':observed.returncode})
r={'passed':len(results)==3 and all(x['exitCode']==0 for x in results) and len(controls)==3 and all(x['typecheckExit']==0 and x['counterexampleExit']!=0 for x in controls),'commands':results,'mutationControls':controls,'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(out/'report.json');sys.exit(0 if r['passed'] else 1)
