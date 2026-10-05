"""Actual plan, sealed FD, independent PNG and explicitly coupled source-kind model."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
inputs={str(p.relative_to(ROOT)):sha(p) for folder in ['native','spec'] for p in (ROOT/folder).glob('*') if p.is_file()};inputs.update({str(p.relative_to(ROOT)):sha(p) for p in [pathlib.Path(__file__),ROOT/'qa/checks.cpp']})
for rel in inputs:
 p=OUT/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'inputs':inputs,'commands':[],'projection':'Pure source-kind admission only; native context, authentication, GPU fence and all product policy outside this five-scenario model; actual memory/FD controls separately checked'}
def run(name,argv,**kw):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=180,**kw);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libpng'],text=True));binary=OUT/'checks';run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'inputs/native'),str(OUT/'inputs/qa/checks.cpp'),'-o',str(binary),*flags]);r['compiledChecks']=json.loads(run('actual-controls',[str(binary)]).stdout)['checks']
 model=OUT/'inputs/spec/planes.qnt';run('typecheck',[str(TOOL),'typecheck',str(model)]);names=re.findall(r'run (\w+)\s*=',model.read_text());assert len(names)==5;r['selectedNames']=names
 run('named',[str(TOOL),'test',str(model),'--main=planes','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=720002','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')]);assert len(list(OUT.glob('named-*.itf.json')))==5
 run('sampling',[str(TOOL),'run',str(model),'--main=planes','--backend=typescript','--invariant=safety','--seed=720003','--max-samples=300','--max-steps=40','--n-traces=12','--out-itf='+str(OUT/'sample-{seq}.itf.json')])
 traces=[]
 for p in sorted(OUT.glob('*.itf.json')):
  states=json.loads(p.read_text())['states'];values=[int(s['flags']['#bigint']) for s in states];out=run('replay-'+p.stem,[str(binary),'--flags'],input='\n'.join(map(str,values))+'\n').stdout;actual=[tuple(map(int,line.split())) for line in out.splitlines()];assert actual==[(int(0<f<=7),int(8<=f<=11)) for f in values];traces.append({'trace':p.name,'statesCompared':len(states)})
 assert len(traces)==17;r.update(passed=True,coupledTraces=traces,namedScenarios=5,invariantSamples=300,maxSteps=40);assert all(sha(ROOT/p)==h for p,h in inputs.items())
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
