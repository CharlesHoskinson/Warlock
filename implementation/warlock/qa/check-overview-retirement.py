"""UI-006 overview-retire model; no native presentation or AT verdict."""
import hashlib,json,pathlib,re,subprocess,time,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa/runs'/('overview-retirement-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'protectedScope':scope,'commands':[],'inputs':{str(root/'qa'/name):sha(root/'qa'/name) for name in ['overview-retirement.qnt','overview-retirement_test.qnt']},'scope':'Exact coherent transfer-member retirement and valid workspace/All browse-focus fallback; no implicit replacement or native mutation, duplicate/incomplete/closed/authority lifecycle. Native/AT input, pixels, grant identity and transport timing are separate.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name,path,args in [('typecheck','overview-retirement.qnt',['typecheck']),('tests-typecheck','overview-retirement_test.qnt',['typecheck']),('named','overview-retirement_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=82412']),('witness-safety','overview-retirement.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','filterReturnWitness','allReturnWitness','incoherentHeldWitness','--max-samples=1000','--max-steps=25','--seed=82413'])]:
  command=['quint',args[0],str(root/'qa'/path),*args[1:]];result=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr);report['commands'].append({'name':name,'command':command,'exitCode':result.returncode});assert result.returncode==0,result.stdout+result.stderr
  if name=='witness-safety':
   counts={name:int(count) for name,count in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',result.stdout)};assert len(counts)==3 and all(counts.values());report['witnesses']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
