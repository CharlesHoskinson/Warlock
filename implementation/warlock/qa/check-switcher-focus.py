"""Quint focus-request abstraction; native keyboard/AT acceptance is separate."""
import hashlib,json,pathlib,re,subprocess,sys,time,shutil
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
initial=sys.argv[1:]==['--initialization'];assert initial or not sys.argv[1:]
out=root/'qa/runs'/('switcher-focus-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['switcher-focus.qnt']+([] if initial else ['switcher-focus_test.qnt'])
report={'passed':False,'protectedScope':scope,'initializationOnly':initial,'inputs':{str(root/'qa'/n):sha(root/'qa'/n) for n in names},'commands':[],'scope':'Admitted immutable browsing-selection reconciliation and exact changed-incarnation focus requests; no native mutation, physical focus, speech/braille or AT claim.','nativeAcceptance':False,'fullReleaseAccepted':False}
for n in names:shutil.copyfile(root/'qa'/n,out/n)
commands=[('typecheck','switcher-focus.qnt',['typecheck'])]
if initial:commands.append(('initialization','switcher-focus.qnt',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=82910']))
else:commands += [('tests-typecheck','switcher-focus_test.qnt',['typecheck']),('named','switcher-focus_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=82911']),('witness-safety','switcher-focus.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','retirementFocusWitness','physicalStepFocusWitness','quietLabelWitness','emptyDismissalWitness','--max-samples=1000','--max-steps=25','--seed=82912'])]
try:
 for name,path,args in commands:
  cmd=['quint',args[0],str(root/'qa'/path),*args[1:]];r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(r.stdout);(out/(name+'.stderr')).write_text(r.stderr);report['commands'].append({'name':name,'command':cmd,'exitCode':r.returncode});assert r.returncode==0,r.stdout+r.stderr
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',r.stdout)};assert len(counts)==4 and all(counts.values());report['witnesses']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
