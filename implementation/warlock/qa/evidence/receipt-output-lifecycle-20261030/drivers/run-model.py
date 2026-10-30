"""Root protected bounded model validation; no native acceptance."""
import hashlib,json,os,re,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
SRC=B/'receipt-lifecycle-root-model-v2'
NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
TOOL=Path('/home/charles/.local/state/warlock-team/20261028/tooling')
CLI=TOOL/'node_modules/@informalsystems/quint/dist/src/cli.js'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope()
 pins={NODE:'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943',CLI:'952a50a28932282528b5c9b86ac5542405d85da4f80876aabe8cb8c7d5a6d0e8',TOOL/'node_modules/@informalsystems/quint/package.json':'c73e78964221e9e8cbe273568ccdad152370fc35786fb82219c64347c71e57dc',TOOL/'package-lock.json':'630f4926b18579f08be780630a94a7c4d398b4bcc6f9844def990ff6a7112903',SRC/'receipt-lifecycle.qnt':'ce5978f5e226ca40281bd6140861aa765d79c194620c63bb9c6b4af40256cdcb',SRC/'receipt-lifecycle_test.qnt':'e27fcdde2317a2b799f886a35930cb54ac11e6e9602a4679bc9a13b257550722'}
 out=B/('receipt-lifecycle-model-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report=dict(passed=False,scope=scope,inputs={str(p):h for p,h in pins.items()},driverSHA256=sha(Path(__file__)),commands=[],seed=20261030,nativeAcceptance=False,fullCorrectnessProved=False,toolDependencyClosureClaimed=False)
 def run(name,args,test=None):
  argv=[str(NODE),str(CLI),*map(str,args)]
  try:p=subprocess.run(argv,cwd=SRC,env={**os.environ,'PATH':str(NODE.parent)+':/usr/bin:/bin','LC_ALL':'C','TZ':'UTC'},capture_output=True,timeout=90)
  except subprocess.TimeoutExpired as e:
   (out/(name+'.stdout')).write_bytes(e.stdout or b'');(out/(name+'.stderr')).write_bytes(e.stderr or b'');report['commands'].append(dict(name=name,argv=argv,timedOut=True));raise
  (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
  report['commands'].append(dict(name=name,argv=argv,exit=p.returncode,stdoutSHA256=sha(out/(name+'.stdout')),stderrSHA256=sha(out/(name+'.stderr'))))
  if p.returncode:raise RuntimeError(name+' failed')
  if test and (test.encode() not in p.stdout or b'passed 1 test(s)' not in p.stdout):raise RuntimeError('Named test not positively selected: '+test)
 try:
  for p,h in pins.items():assert sha(p)==h,str(p)
  run('version',['--version'])
  for f in ['receipt-lifecycle.qnt','receipt-lifecycle_test.qnt']:run('typecheck-'+f,['typecheck',SRC/f])
  invariants=['receiptPreservesSceneCounters','otherCurrentPreserved','exactCurrentTerminalSettled','pendingHasReservation','bounded']
  run('initial-run',['run',SRC/'receipt-lifecycle.qnt','--main','ReceiptLifecycle','--invariant',invariants[0],'--max-samples=1','--max-steps=1','--backend=typescript','--seed=20261030'])
  tests=re.findall(r'^  run (\w+) =', (SRC/'receipt-lifecycle_test.qnt').read_text(),re.M);assert len(tests)==12
  for test in tests:run('test-'+test,['test',SRC/'receipt-lifecycle_test.qnt','--main','ReceiptLifecycle_test','--backend=typescript','--match','^'+test+'$'],test)
  for inv in invariants:run('sample-'+inv,['run',SRC/'receipt-lifecycle.qnt','--main','ReceiptLifecycle','--invariant',inv,'--max-samples=1000','--max-steps=20','--backend=typescript','--seed=20261030'])
  for p,h in pins.items():assert sha(p)==h,str(p)
  report['passed']=True
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),error=report.get('error'))));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
