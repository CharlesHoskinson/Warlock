"""UI-016 immutable paint gate; sampled transport safety, not physical paint."""
import hashlib,json,pathlib,re,subprocess,time,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
initial=sys.argv[1:]==['--initialization'];assert initial or not sys.argv[1:]
out=root/'qa/runs'/('preview-paint-gate-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['preview-paint-gate.qnt']+([] if initial else ['preview-paint-gate_test.qnt'])
report={'passed':False,'protectedScope':scope,'initializationOnly':initial,'commands':[],'inputs':{str(root/'qa'/n):sha(root/'qa'/n) for n in names},'scope':'Immutable single-use paint ticket for original Acquire, exact-job cancellation before dispatch, immediate control processing and independent job isolation. No native authorization, pixels, AT, clock or GPU presentation proof.','nativeAcceptance':False,'fullReleaseAccepted':False}
for n in names:(out/n).write_bytes((root/'qa'/n).read_bytes())
commands=[('typecheck','preview-paint-gate.qnt',['typecheck'])]
if initial:commands.append(('initialization','preview-paint-gate.qnt',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=82810']))
else:commands += [('tests-typecheck','preview-paint-gate_test.qnt',['typecheck']),('named','preview-paint-gate_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=82811']),('witness-safety','preview-paint-gate.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','paintDispatchWitness','cancelledUnsentWitness','independentDispatchWitness','--max-samples=1000','--max-steps=25','--seed=82812'])]
try:
 for name,path,args in commands:
  cmd=['quint',args[0],str(root/'qa'/path),*args[1:]];r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(r.stdout);(out/(name+'.stderr')).write_text(r.stderr);report['commands'].append({'name':name,'command':cmd,'exitCode':r.returncode});assert r.returncode==0,r.stdout+r.stderr
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',r.stdout)};assert len(counts)==3 and all(counts.values());report['witnesses']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
