import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/seat.qnt',OUT/'seat.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'seat.qnt').read_text();names=re.findall(r'  run (\w+) =',source)
r={'passed':False,'nativeAcceptance':False,'scope':'Bounded capability/idle ownership abstraction; actual two-kind C++ replay and native QA separate','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','seat.qnt'])
 run('named',['test','seat.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','seat.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[('retired','s.cap and ','','retiredDeviceRefusedTest'),('device-id',' and s.q.head().id==s.id','','replacementOnlyTest'),('backend-owner',' and s.q.head().owner==s.owner','','backendOwnerReuseRefusedTest'),('dead-backend','s.live and ','','deadBackendRefusedTest'),('dead-core','s.core and ','','deadCoreRefusedTest'),('readiness','s.ready and ','','notReadyRefusedTest'),('transport','s.transport and ','','failedTransportRefusedTest')]
 admitted=next(line for line in source.splitlines() if line.startswith('  val admitted'))
 for name,before,after,test in mutants:
  assert admitted.count(before)==1;mutated=source.replace(admitted,admitted.replace(before,after));(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/seat.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
