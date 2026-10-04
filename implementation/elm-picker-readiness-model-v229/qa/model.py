import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/readiness.qnt',OUT/'readiness.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'readiness.qnt').read_text();names=re.findall(r'(?m)^\s*run (\w+) =',source);assert len(names)==22 and len(set(names))==22
r={'passed':False,'nativeAcceptance':False,'scope':'Validated paired-observation readiness, choice/focus identity and original timer abstraction; actual Elm/native refinement separate','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','readiness.qnt'])
 run('named',['test','readiness.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','readiness.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[
 ('missing-geometry-trigger','val completion = match and ready','val completion = match and ready and kind == 1','projectionFirstTest'),
 ('missing-projection-trigger','val completion = match and ready','val completion = match and ready and kind == 2','geometryFirstTest'),
 ('invalid-admitted','val match = valid and s.connected','val match = s.connected','invalidGeometryTest'),
 ('foreign-binding-admitted','binding == s.binding and request ==','true and request ==','wrongBindingTest'),
 ('wrong-request-admitted','request == (if (kind == 1) s.pr else s.gr) and not','true and not','wrongRequestTest'),
 ('missing-geometry-readiness','val ready = p and g and s.connected','val ready = p and s.connected','projectionOnlyTest'),
 ('missing-projection-readiness','val ready = p and g and s.connected','val ready = g and s.connected','geometryOnlyTest'),
 ('retired-root-admitted','and s.live and (s.mode','and true and (s.mode','retiredRootTest'),
 ('foreign-output-admitted','s.output == s.savedOutput and s.root','true and s.root','wrongOutputTest'),
 ('changed-app-admitted','s.app == s.savedApp and s.live','true and s.live','changedApplicationTest'),
 ('deadline-ignored','pending:if (token == s.token) false else s.pending','pending:s.pending','expiredChoiceTest'),
 ('choice-retained','pending:if (completion) false else s.pending','pending:s.pending','duplicateCompletionTest'),
 ('popup-focus-steal','(s.mode != 2 or not s.popup)','true','focusPopupNoStealTest')]
 for name,before,after,test in mutants:
  assert source.count(before)==1;mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/readiness.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
