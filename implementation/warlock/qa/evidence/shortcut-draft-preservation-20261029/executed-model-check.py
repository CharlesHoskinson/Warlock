import hashlib,json,os,re,resource,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');D=Path(__file__).resolve().parent;NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node');TOOL=Path('/home/charles/.local/state/warlock-team/20261028/tooling/node_modules/.bin/quint').resolve();SPEC=R/'implementation/warlock/qa/shortcut-draft.qnt';TEST=R/'implementation/warlock/qa/shortcut-draft_test.qnt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
scope=require_qa_scope()
if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit')
expected={NODE:'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943',SPEC:'87bbbdc9610ecf93445ead0d4cf12f1609405a0568e09c4afdf2c8122dd97018',TEST:'665ec15f43b80b3e0066de5f4deae0d9aaf36cac5a46bb695b3ad78eecfff450'}
for p,h in expected.items():
 if sha(p)!=h:raise RuntimeError('Reviewed input differs '+str(p))
O=D/'output';O.mkdir(exist_ok=False);(O/'shortcut-draft.qnt').write_bytes(SPEC.read_bytes());(O/'shortcut-draft_test.qnt').write_bytes(TEST.read_bytes())
paths=[NODE,TOOL,SPEC,TEST,TOOL.parents[2]/'package.json',Path('/home/charles/.local/state/warlock-team/20261028/tooling/package-lock.json')];pins={str(p):sha(p) for p in paths};report={'passed':False,'scope':scope,'inputs':pins,'commands':[],'seed':20261029,'sampleBudgetPerInvariant':1000,'stepBudget':20,'limit':'Bounded local editor model and explicit named witnesses, not exhaustive proof or native implementation acceptance.'}
env={'PATH':str(NODE.parent)+':/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
try:
 names=re.findall(r'^  run ([A-Za-z0-9_]+) =',TEST.read_text(),re.M)
 if len(names)!=26:raise RuntimeError('Named witness inventory differs')
 invariantNames=['readPreservesIntent','readNeverSubmits','readNeverRollsBack','pendingIntentStable','conflictBlocksSave','pendingBlocksSave']
 commands=[('typecheck',['typecheck',str(SPEC)]),('initial-run',['run',str(SPEC),'--main','ShortcutDraft','--invariant','readPreservesIntent','--max-samples=1','--max-steps=1','--backend=typescript','--seed=20261029']),('typecheck-tests',['typecheck',str(TEST)])]
 commands += [('test-'+name,['test',str(TEST),'--main','ShortcutDraft_test','--backend=typescript','--match','^'+name+'$']) for name in names]
 commands += [('sample-'+name,['run',str(SPEC),'--main','ShortcutDraft','--invariant',name,'--max-samples=1000','--max-steps=20','--backend=typescript','--seed=20261029']) for name in invariantNames]
 for name,args in commands:
  cmd=[str(NODE),str(TOOL),*args];a=O/(name+'.stdout');b=O/(name+'.stderr')
  try:p=subprocess.run(cmd,cwd=R,env=env,capture_output=True,timeout=120)
  except subprocess.TimeoutExpired as e:
   a.write_bytes(e.stdout or b'');b.write_bytes(e.stderr or b'');report['commands'].append({'name':name,'argv':cmd,'timedOut':True,'timeoutSeconds':120,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)});raise
  a.write_bytes(p.stdout);b.write_bytes(p.stderr);report['commands'].append({'name':name,'argv':cmd,'exit':p.returncode,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
  if p.returncode:raise RuntimeError(name+' failed')
 for p,h in pins.items():
  if sha(p)!=h:raise RuntimeError('Input changed '+p)
 report.update(passed=True,namedWitnesses=names,sampledInvariants=invariantNames)
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['outputs']={str(p):sha(p) for p in O.iterdir() if p.is_file()};(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(O/'report.json'),'error':report.get('error')}));sys.exit(0 if report['passed'] else 1)
