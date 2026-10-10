"""UI-006 overview-cancel model; no native input, pixels or AT verdict."""
import hashlib,json,pathlib,re,subprocess,time,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
initial=sys.argv[1:]==['--initialization'];assert initial or not sys.argv[1:]
out=root/'qa/runs'/('overview-transfer-cancel-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['overview-transfer-cancel.qnt']+([] if initial else ['overview-transfer-cancel_test.qnt'])
report={'passed':False,'protectedScope':scope,'initializationOnly':initial,'commands':[],'inputs':{str(root/'qa'/name):sha(root/'qa'/name) for name in names},'scope':'Exact eligible current transfer opener focus on cancellation, valid workspace/All fallback, duplicate/stale/closed/coherence/availability/reservation/capability lifetime. Source revision abstracts current view stamp; no native dispatch, real pixels/input, AT or timing verdict.','nativeAcceptance':False,'fullReleaseAccepted':False}
for name in names:(out/name).write_bytes((root/'qa'/name).read_bytes())
commands=[('typecheck','overview-transfer-cancel.qnt',['typecheck'])]
if initial:commands.append(('initialization','overview-transfer-cancel.qnt',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=82710']))
else:commands += [('tests-typecheck','overview-transfer-cancel_test.qnt',['typecheck']),('named','overview-transfer-cancel_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=82711']),('witness-safety','overview-transfer-cancel.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','originReturnWitness','filterReturnWitness','allReturnWitness','staleHeldWitness','fullDismissalWitness','--max-samples=1000','--max-steps=25','--seed=82712'])]
try:
 for name,path,args in commands:
  command=['quint',args[0],str(root/'qa'/path),*args[1:]];result=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr);report['commands'].append({'name':name,'command':command,'exitCode':result.returncode});assert result.returncode==0,result.stdout+result.stderr
  if name=='witness-safety':
   counts={name:int(count) for name,count in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',result.stdout)};assert len(counts)==5 and all(counts.values());report['witnesses']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
