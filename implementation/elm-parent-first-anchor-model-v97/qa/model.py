import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/anchor.qnt',OUT/'anchor.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'anchor.qnt').read_text();names=re.findall(r'  run (\w+)\s*=',source);assert len(names)==10
r={'passed':False,'nativeAcceptance':False,'scope':'Bounded first-anchor/floor-dedup/normal-policy abstraction; native transport separate','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','anchor.qnt'])
 run('named',['test','anchor.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','anchor.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[('missing-refresh','val refresh=newSource','val refresh=false','firstStationaryAnchorTest'),('ordinary-focus','val refresh=newSource','val refresh=true','ordinaryWarpPreservesProgramFocusTest'),('output-identity',' or s.lastOutput!=s.output','','outputStationaryAnchorTest'),('readiness','s.ready and ','','inactiveParentRefusedTest'),('shutdown','s.live and ','','shutdownRefusedTest'),('normal-policy','refresh and s.allowFocus','refresh','normalGrabPolicyTest')]
 for name,before,after,test in mutants:
  assert source.count(before)==1;mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/anchor.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
