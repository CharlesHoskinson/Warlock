"""Eight explicit source-kind scenarios, compared to actual compiled Elm."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[],'projection':'one fixed binding/incarnation/publication, one request: entry count, active/demand, source-clock delta, known/cancelling, emitted acquire/cancel identities; source domain observed through subsequent changed-clock source admission; no physical/packet/full native model'}
def run(name,cmd,input=None,cwd=None):
 p=subprocess.run(cmd,input=input,cwd=cwd or OUT,capture_output=True,text=True,timeout=60);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':cmd,'exitCode':p.returncode});assert p.returncode==0,p.stderr or p.stdout;return p
try:
 provider=REPO/'implementation/warlock-preview-provider-v10';reports=sorted(provider.glob('qa/build-*/report.json'));assert len(reports)==1;build=reports[0];built=json.loads(build.read_text());assert built['passed']
 worker=build.parent/'inputs/assets/preview-replay.js';fixture=build.parent/'inputs/qa/native-source-fixture.json';assert sha(worker)==built['compiledAssetPackage']['files'][worker.name]
 inputs={str(p):sha(p) for p in [build,worker,fixture,ROOT/'SPEC.md',ROOT/'qa/replay.js',pathlib.Path(__file__),*ROOT.joinpath('spec').glob('*.qnt')]}
 for rel,h in built['inputs'].items():
  if rel.startswith('src/') or rel=='elm.json':assert sha(provider/rel)==h;inputs[str(provider/rel)]=h
 r['inputs']=inputs;r['toolSHA256']=sha(TOOL.resolve());shutil.copytree(ROOT/'spec',OUT/'spec');shutil.copy2(ROOT/'qa/replay.js',OUT/'replay.js')
 names=re.findall(r'run (\w+)\s*=',(OUT/'spec/tests.qnt').read_text());assert len(names)==len(set(names))==8;r['selectedNames']=names
 run('typecheck',[str(TOOL),'typecheck','tests.qnt'],cwd=OUT/'spec')
 run('selected',[str(TOOL),'test','tests.qnt','--main=source_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=711001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=OUT/'spec')
 def decode(v):
  if isinstance(v,list):return [decode(x) for x in v]
  if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
  return v
 traces=[]
 for p in sorted(OUT.glob('named-*.itf.json')):
  states=[s['s'] for s in decode(json.loads(p.read_text()))['states']];events=states[-1]['history']
  response=run('replay-'+p.stem,['node',str(OUT/'replay.js'),str(worker),str(fixture)],input='\n'.join(events)+'\n')
  actual=[json.loads(line) for line in response.stdout.splitlines()];expected=[];count=0
  for s in states:
   if len(s['history'])==count:continue
   count=len(s['history']);exists=s['domain']!=-1
   expected.append({'entries':int(exists),'now':s['now'],'active':exists and s['open'],'demand':exists and s['open'],'known':int(s['known']),'cancelling':int(s['known'] and not s['open']),'commands':s['commands']})
  assert actual==expected,(p.name,actual,expected);traces.append({'trace':p.name,'statesCompared':len(actual)})
 assert len(traces)==8;r['coupledTraces']=traces;assert all(sha(path)==h for path,h in inputs.items());r['passed']=True
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error'),'statesCompared':sum(x['statesCompared'] for x in r.get('coupledTraces',[]))}));raise SystemExit(not r['passed'])
