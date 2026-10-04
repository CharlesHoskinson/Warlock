import json,pathlib,subprocess,time,re,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
source=(ROOT/'spec/registry.qnt').read_text();(OUT/'registry.qnt').write_text(source)
r={'passed':False,'commands':[]}
def run(label,args,expected=0):
 p=subprocess.run(['quint',*args],cwd=OUT,text=True,capture_output=True,timeout=90)
 (OUT/(label+'.stdout')).write_text(p.stdout);(OUT/(label+'.stderr')).write_text(p.stderr)
 r['commands'].append({'label':label,'argv':['quint',*args],'exit':p.returncode})
 assert p.returncode==expected,(label,p.stderr[-1500:],p.stdout[-1500:])
try:
 run('typecheck',['typecheck','registry.qnt'])
 names=re.findall(r'run (\w+Test)',source)
 run('named',['test','registry.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=58801'])
 run('invariants',['run','registry.qnt','--backend=typescript','--invariant=safety','--max-samples=1000','--max-steps=40','--seed=58802'])
 mutations=[('caller-bypass','callerValid and targetValid','true and targetValid','foreignCallerTest'),('lifetime-bypass','and sameLifetime and','and true and','foreignLifetimeTest'),('self-retire','and callerId != targetId','and true','currentCallerTest'),('stale-frontend','targetFrontend == s.bf','true','staleTargetTest'),('id-exhaustion','s.last < 4','true','allocatorExhaustionTest'),('frontend-exhaustion','frontend < 4','true','frontendExhaustionTest'),('query-future-session','id > st.last or','false or','queryFutureSessionTest'),('query-future-frontend','current > 0 and frontend > current','false','queryFutureFrontendTest'),('query-auth','not(auth) or not(sameLifetime)','false or not(sameLifetime)','queryForeignCallerTest'),('query-lifetime','not(auth) or not(sameLifetime)','not(auth) or false','queryForeignLifetimeTest')]
 for label,before,after,test in mutations:
  assert source.count(before)==1
  (OUT/(label+'.qnt')).write_text(source.replace(before,after))
  run(label+'-typecheck',['typecheck',label+'.qnt'])
  run(label+'-rejected',['test',label+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=58803'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutations),modelSHA256=hashlib.sha256(source.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
