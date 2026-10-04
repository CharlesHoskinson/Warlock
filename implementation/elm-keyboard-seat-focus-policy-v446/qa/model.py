import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/focus.qnt',OUT/'focus.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'focus.qnt').read_text();names=re.findall(r'  run (\w+) =',source)
r={'passed':False,'nativeAcceptance':False,'scope':'First keyboard/committed seat focus abstraction; no native input or C++ refinement claim','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','focus.qnt'])
 run('named',['test','focus.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','focus.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[('old-unconditional','s.count == 0 and s.focus == 0 and s.desktop != 0','s.count == 0 and s.desktop != 0','popupPreservedTest'),('missing-fallback','s.count == 0 and s.focus == 0 and s.desktop != 0','false','missingSeatFallsBackTest'),('additional-focus','s.count == 0 and s.focus == 0 and s.desktop != 0','s.focus == 0 and s.desktop != 0','additionalKeyboardNoFocusChangeTest')]
 for name,before,after,test in mutants:
  assert source.count(before)==1;mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/focus.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
