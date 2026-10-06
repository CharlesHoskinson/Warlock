"""Preliminary trace review against identical compiled74 Elm; final75 checks required."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v75';prior=r/'implementation/warlock-preview-provider-v74';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=r/'docs/warlock-preview/v77'/('trace-review-'+str(time.time_ns()));out.mkdir();tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
for p in (root/'src').glob('*'):assert sha(p)==sha(prior/'src'/p.name)
compiled=next(prior.glob('qa/feedback-check-*/feedback-replay.js'));assert compiled.is_file()
for rel in ['spec/feedback.qnt','spec/feedback_tests.qnt','qa/feedback-replay.js','qa/native-source-fixture.json']:
 dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,dst)
report={'passed':False,'claim':'Preliminary exact source-equivalent compiled74 replay; final current75 build/check required.','commands':[]}
def run(name,argv,input=None,cwd=None):
 p=subprocess.run(argv,input=input,cwd=cwd or out,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 names=re.findall(r'run (\w+)\s*=',(out/'spec/feedback_tests.qnt').read_text())
 run('selected',[tool,'test','feedback_tests.qnt','--main=feedback_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=720001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=out/'spec')
 run('samples',[tool,'run','feedback.qnt','--main=feedback','--backend=typescript','--invariant=safety','--seed=720002','--max-samples=100','--max-steps=32','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=out/'spec')
 def decode(v):
  if isinstance(v,list):return [decode(x) for x in v]
  if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
  return v
 for p in sorted(out.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(p.read_text()))['states']];trace=states[-1]['history'];actual=json.loads(run('replay-'+p.stem,['node',str(out/'qa/feedback-replay.js'),str(compiled),str(out/'qa/native-source-fixture.json'),'--replay'],input=json.dumps(trace)))
  expected=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);expected.append({**state,'history':[]})
  assert actual==expected,(p.name,actual,expected)
 report['passed']=True
except Exception as e:report['error']=repr(e)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
