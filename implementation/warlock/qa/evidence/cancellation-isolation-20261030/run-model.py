"""Protected model qualification, pinned frozen candidate and explicit selections."""
import hashlib,json,os,re,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock')
B=Path('/home/charles/.local/state/warlock-team/20261028')
NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
TOOL=B/'tooling';CLI=TOOL/'node_modules/@informalsystems/quint/dist/src/cli.js'
CONFIG=Path(__file__).with_name('model-inputs.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope();cfg=json.loads(CONFIG.read_text());src=Path(cfg['source'])
 out=Path(__file__).parent/('model-'+str(time.time_ns()));out.mkdir(mode=0o700)
 pins={NODE:'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943',CLI:'952a50a28932282528b5c9b86ac5542405d85da4f80876aabe8cb8c7d5a6d0e8',TOOL/'node_modules/@informalsystems/quint/package.json':'c73e78964221e9e8cbe273568ccdad152370fc35786fb82219c64347c71e57dc',TOOL/'package-lock.json':'630f4926b18579f08be780630a94a7c4d398b4bcc6f9844def990ff6a7112903',**{src/k:v for k,v in cfg['files'].items()}}
 report={'passed':False,'scope':scope,'inputs':{str(k):v for k,v in pins.items()},'driverSHA256':sha(Path(__file__)),'configSHA256':sha(CONFIG),'commands':[],'seed':20261030,'nativeAcceptance':False,'fullCorrectnessProved':False,'toolDependencyClosureClaimed':False,'limits':'Three opaque full keys, legacy-vs-typed retirement isolation; noReplay/projection are bookkeeping, not transport proofs. No actual native/OS/fsync/cardinality proof.'}
 def run(name,args,test=None):
  argv=[str(NODE),str(CLI),*map(str,args)]
  try:p=subprocess.run(argv,cwd=src,env={**os.environ,'PATH':str(NODE.parent)+':/usr/bin:/bin','LC_ALL':'C','TZ':'UTC'},capture_output=True,timeout=60)
  except subprocess.TimeoutExpired as e:
   (out/(name+'.stdout')).write_bytes(e.stdout or b'');(out/(name+'.stderr')).write_bytes(e.stderr or b'');report['commands'].append({'name':name,'argv':argv,'timedOut':True});raise
  (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
  report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode,'stdoutSHA256':sha(out/(name+'.stdout')),'stderrSHA256':sha(out/(name+'.stderr'))})
  if p.returncode:raise RuntimeError(name+' failed')
  if test and (test.encode() not in p.stdout or b'passed 1 test(s)' not in p.stdout):raise RuntimeError('Named test not positively selected: '+test)
 try:
  for p,h in pins.items():assert sha(p)==h,str(p)
  run('version',['--version'])
  for f in cfg['files']:run('typecheck-'+f,['typecheck',src/f])
  run('initial-run',['run',src/'typed-retirement-isolation.qnt','--main','TypedRetirementIsolation','--invariant','typedCustody','--max-samples=1','--max-steps=1','--backend=typescript','--seed=20261030'])
  tests=re.findall(r'^\s*run\s+(\w+)\s*=',(src/'typed-retirement-isolation_test.qnt').read_text(),re.M)
  assert len(tests)==cfg['testCount'] and len(set(tests))==len(tests)
  report['namedTests']=tests
  for name in tests:run('test-'+name,['test',src/'typed-retirement-isolation_test.qnt','--main','TypedRetirementIsolation_test','--match','^'+name+'$','--backend=typescript','--max-samples=1','--seed=20261030'],name)
  for inv in cfg['invariants']:
   run('sample-'+inv,['run',src/'typed-retirement-isolation.qnt','--main','TypedRetirementIsolation','--invariant',inv,'--max-samples=1000','--max-steps=30','--backend=typescript','--seed=20261030'])
  for p,h in pins.items():assert sha(p)==h,str(p)
  report['passed']=True
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
