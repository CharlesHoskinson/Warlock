"""Hash-bound actual revision helpers and explicitly selected coupled Quint traces."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
TOOL='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[ROOT/'qa/check.py',ROOT/'qa/checks.cpp',ROOT/'spec/tree.qnt',REPO/'implementation/warlock-client-source-revisions-v1/native/tree_revision.hpp',REPO/'implementation/warlock-client-source-revisions-v1/native/source_epoch.hpp',REPO/'implementation/warlock-core-surface-revision-v2/candidate/src/protocols/core/AppliedSurfaceRevision.hpp']
inputs={str(p.relative_to(REPO)):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'inputs':inputs,'commands':[], 'projection':'Actual pure AppliedRevision/TreeRevision helpers; no compositor registry, weak-resource identity, GPU, IPC, native child pixels or complete release acceptance.'}
def run(name,args,**kw):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180,**kw);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p
try:
 binary=OUT/'checks';run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT),str(OUT/'checks.cpp'),'-o',str(binary)])
 report['actualControls']=json.loads(run('controls',[str(binary)]).stdout)['checks']
 model=OUT/'tree.qnt';run('typecheck',[TOOL,'typecheck',str(model)]);names=re.findall(r'run (\w+)\s*=',model.read_text());assert len(names)==9;report['selectedNames']=names
 run('named',[TOOL,'test',str(model),'--main=tree','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=730001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')]);assert len(list(OUT.glob('named-*.itf.json')))==9
 run('sampling',[TOOL,'run',str(model),'--main=tree','--backend=typescript','--invariant=safety','--seed=730002','--max-samples=300','--max-steps=40','--n-traces=12','--out-itf='+str(OUT/'sample-{seq}.itf.json')])
 traces=[]
 for path in sorted(OUT.glob('*.itf.json')):
  states=[s for s in json.loads(path.read_text())['states'] if int(s['kind']['#bigint'])!=-1];data='\n'.join(str(int(s['kind']['#bigint'])) for s in states)+'\n';actual=run('replay-'+path.stem,[str(binary),'--replay'],input=data).stdout;rows=[tuple(map(int,line.split())) for line in actual.splitlines()];expected=[(int(s['revision']['#bigint']) if s['complete'] else 0,int(s['complete'])) for s in states];assert rows==expected,(path.name,rows,expected);traces.append({'trace':path.name,'statesCompared':len(states)})
 assert len(traces)==21;assert all(sha(REPO/rel)==h for rel,h in inputs.items());report.update(passed=True,coupledTraces=traces,namedScenarios=9,invariantSamples=300,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
