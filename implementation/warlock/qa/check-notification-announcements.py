"""Incremental quint-llm-kit checks; bounded transport model, never GUI acceptance."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
smoke=sys.argv[1:]==['--smoke'];assert smoke or not sys.argv[1:]
out=root/'qa/runs'/('notification-announcements-model-'+str(time.time_ns()));out.mkdir(parents=True)
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'protectedScope':scope,'commands':[],'inputs':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['qa/notification-announcements.qnt']+([] if smoke else ['qa/notification-announcements_test.qnt'])}}
commands=[('typecheck',['quint','typecheck','qa/notification-announcements.qnt'])]
if not smoke:commands += [('tests-typecheck',['quint','typecheck','qa/notification-announcements_test.qnt']),('named',['quint','test','qa/notification-announcements_test.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79501'])]
witnesses=['arrivalWitness'] if smoke else ['arrivalWitness','suppressedWitness','politeCriticalWitness','interruptWitness','dndWitness','optInWitness','repeatWitness','baselineWitness']
commands += [('witness-safety',['quint','run','qa/notification-announcements.qnt','--backend=typescript','--invariants=safety','--witnesses',*witnesses,'--max-samples='+('10' if smoke else '1000'),'--max-steps='+('5' if smoke else '30'),'--seed=79502'])]
try:
 for name,args in commands:
  p=subprocess.run(args,cwd=root,capture_output=True,text=True,timeout=120);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'args':args,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 counts={name:int(count) for name,count in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',p.stdout)}
 if set(counts)!=set(witnesses) or not all(counts.values()):raise RuntimeError('Unreachable selected witness: '+repr(counts))
 report['witnesses']=counts
 report['passed']=True
except Exception as e:report['error']=str(e)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
