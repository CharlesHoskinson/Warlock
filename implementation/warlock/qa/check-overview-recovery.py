"""UI-006 original refusal recovery, single-choice abstraction; no GUI verdict."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa/runs'/('overview-recovery-'+str(time.time_ns()));out.mkdir(parents=True)
model=root/'qa/overview-recovery.qnt';tests=root/'qa/overview-recovery_test.qnt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'protectedScope':scope,'inputs':{str(p):sha(p) for p in [model,tests]},'commands':[],'scope':'One explicit overview choice and its exact issued intent; refusal recovery, preserved workspace, no replay, foreign/duplicate/Unknown/authority/occupied negatives. Native grants/transport/deadlines/paint/AT excluded.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name,path,args in [('typecheck',model,['typecheck']),('tests-typecheck',tests,['typecheck']),('named',tests,['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79553']),('witness-safety',model,['run','--backend=typescript','--invariants=safety','--witnesses','choiceWitness','issuedWitness','refusalWitness','recoveryWitness','unknownWitness','foreignWitness','replacedWitness','occupiedWitness','--max-samples=1000','--max-steps=30','--seed=79554'])]:
  command=['quint',args[0],str(path),*args[1:]];p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr+p.stdout)
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',p.stdout)};assert len(counts)==8 and all(counts.values()),p.stdout;report['witnesses']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
