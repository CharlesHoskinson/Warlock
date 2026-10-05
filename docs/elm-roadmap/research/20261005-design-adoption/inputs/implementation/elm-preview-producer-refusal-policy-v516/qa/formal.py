"""Actual named lifecycle tests, sampled invariants and precise mutant diagnostics."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('formal-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['source.qnt','tests.qnt']:shutil.copy2(ROOT/'spec'/name,OUT/name)
inputs=[ROOT/'spec/source.qnt',ROOT/'spec/tests.qnt',pathlib.Path(__file__),TOOL.resolve(),pathlib.Path(shutil.which('node')).resolve()]
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Seven producer failure, reservation, physical ownership, cancellation, stable receipt, exhaustion and original deadline scenarios. Finite model only, no actual broker trace coupling or native acceptance','inputs':{str(p):sha(p) for p in inputs},'commands':[]}
def run(name,args,expected=0):
 cmd=[str(TOOL),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,text=True,timeout=240)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expectedExitCode':expected});print(name,p.returncode,flush=True)
 assert p.returncode==expected,p.stderr or p.stdout
 return p
try:
 run('typecheck',['typecheck','tests.qnt'])
 names=re.findall(r'run (\w+)\s*=',(OUT/'tests.qnt').read_text());assert len(names)==len(set(names))==7
 report['selectedNames']=names
 run('named',['test','tests.qnt','--main=source_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=201010','--max-samples=1','--out-itf=named-{test}-{seq}.itf.json'])
 assert len(list(OUT.glob('named-*.itf.json')))==7
 for seed in [201011,201012]:
  run('invariants-'+str(seed),['run','source.qnt','--main=source','--backend=typescript','--invariant=safety','--seed='+str(seed),'--max-samples=500','--max-steps=50','--n-traces=12','--out-itf=sample-'+str(seed)+'-{seq}.itf.json'])
  assert len(list(OUT.glob('sample-'+str(seed)+'-*.itf.json')))==12
 mutants=[
  ('physical-owner','st.phase==1 and st.physical==0','(st.phase==1 or st.phase==2)','physicalBufferCannotRefuseTest'),
  ('retained-budget','phase:3,bytes:0','phase:3,bytes:st.bytes','reservedFailureClearsChargeTest'),
  ('cancel-proof','List(st.seq,st.seq+1)','List(st.seq)','cancellationRaceBothProofsTest'),
 ]
 source=(OUT/'source.qnt').read_text()
 for name,old,new,selector in mutants:
  assert source.count(old)==1; (OUT/(name+'.qnt')).write_text(source.replace(old,new,1))
  (OUT/(name+'-tests.qnt')).write_text((OUT/'tests.qnt').read_text().replace('"./source"','"./'+name+'"'))
  run(name+'-typecheck',['typecheck',name+'-tests.qnt'])
  p=run(name+'-counterexample',['test',name+'-tests.qnt','--main=source_tests','--backend=typescript','--match=^'+selector+'$','--seed=201013','--max-samples=1'],1)
  assert selector+' failed after 1 test(s)' in p.stdout and 'Error [QNT508]: Assertion failed' in p.stdout
 report['unsafeMutantsDetected']=len(mutants)
 assert all(sha(pathlib.Path(p))==h for p,h in report['inputs'].items()),'Input changed'
 report.update(passed=True,namedScenarios=7,invariantSamples=1000,maxSteps=50,retainedSampleTraces=24)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'),flush=True);raise SystemExit(not report['passed'])
