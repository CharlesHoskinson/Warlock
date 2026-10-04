import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/join.qnt',OUT/'join.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'join.qnt').read_text();names=re.findall(r'(?m)^\s*run (\w+) =',source);assert len(names)==10 and len(set(names))==9
r={'passed':False,'nativeAcceptance':False,'scope':'Abstract two-observation pending-choice join, scope/deadline/once-only guards; no native/Elm refinement claim','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','join.qnt'])
 run('named',['test','join.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=81201','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','join.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=81202'])
 mutants=[('old-projection-only',"action geometry = (s'={...s,geometry:true}).then(settle)","action geometry = s'={...s,geometry:true}",'projectionFirstTest'),('geometry-guard','and s.geometry ','','projectionFirstTest'),('binding-guard','and s.binding ','','bindingChangeTest'),('output-guard','and s.output ','','outputChangeTest'),('target-guard','and s.target ','','retiredTargetTest'),('once-only','and s.pending ','','duplicateTest')]

 for name,before,after,test in mutants:
  assert source.count(before)==1;mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=81301'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/join.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
