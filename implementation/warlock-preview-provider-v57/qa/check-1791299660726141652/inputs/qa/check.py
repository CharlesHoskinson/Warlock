"""Protected compiled native-authority component checks and selected trace replay."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={str(p.relative_to(ROOT)):sha(p) for base in ['native','spec'] for p in (ROOT/base).glob('*') if p.is_file()}
for p in [ROOT/'qa/checks.cpp',pathlib.Path(__file__)]:source[str(p.relative_to(ROOT))]=sha(p)
for rel in source:
 target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
report={'passed':False,'scope':scope,'inputs':source,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[],'projection':'latest/captured/issuedLease,busy,broker activeItems,visible,native-now,last-start,lease and broker floor for one fixed native lifetime/domain/entry; exact scope/auth/fence/deadline/bytes outside abstraction covered separately, not complete concrete-field refinement','fixedFixture':{'binding':[1,2,3],'incarnation':4,'output':5,'privacy':6,'rendering':7,'scene':8,'clock':10,'origin':11,'cost':32,'items':2,'bytes':64,'interval':2,'freshDeadline':'native now+100 for a NEW job; no old deadline renewed'},'toolSHA256':sha(TOOL.resolve())}
def run(name,cmd,expected=0,input=None,cwd=None):
 p=subprocess.run(cmd,cwd=cwd or OUT,capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True)
 assert p.returncode==expected,p.stderr or p.stdout
 return p
try:
 binary=OUT/'checks';compile=['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'inputs/native'),str(OUT/'inputs/qa/checks.cpp'),'-o',str(binary)]
 run('compile',compile);p=run('compiled-controls',[str(binary)]);assert not p.stderr;report['compiledChecks']=json.loads(p.stdout)['checks']
 folder=OUT/'inputs/spec';run('quint-typecheck',[str(TOOL),'typecheck','tests.qnt'],cwd=folder)
 names=re.findall(r'run (\w+)\s*=',(folder/'tests.qnt').read_text());assert len(names)==len(set(names))==10;report['selectedNames']=names
 run('quint-named',[str(TOOL),'test','tests.qnt','--main=demand_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=710001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==10
 run('quint-sampling',[str(TOOL),'run','demand.qnt','--main=demand','--backend=typescript','--invariant=safety','--seed=710002','--max-samples=300','--max-steps=40','--n-traces=12','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 def decode(v):
  if isinstance(v,list):return [decode(x) for x in v]
  if isinstance(v,dict):
   if '#bigint' in v:return int(v['#bigint'])
   return {k:decode(x) for k,x in v.items()}
  return v
 coupled=[]
 for trace in sorted(OUT.glob('*.itf.json')):
  j=decode(json.loads(trace.read_text()));states=[x['s'] for x in j['states']];events=states[-1]['history'];p=run('replay-'+trace.stem,[str(binary),'--replay'],input='\n'.join(events)+'\n');actual=[json.loads(line) for line in p.stdout.splitlines()]
  # Named tests append check transitions which do not append events.
  expected=[];length=0
  for state in states:
   if len(state['history'])==length:continue
   length=len(state['history']);expected.append({k:v for k,v in state.items() if k!='history'})
  assert actual==expected,(trace.name,actual,expected);coupled.append({'trace':trace.name,'statesCompared':len(actual)})
 report['coupledTraces']=coupled;assert len(coupled)==22
 original=(OUT/'inputs/native/demand.hpp').read_text()
 mutants=[('pacing','d.scope.now-*lastAttempt_<policy_.minimumInterval','false','continuous changes remain paced'),('closed-lease','(!s.open && d.visible)','false','closed lease cannot reopen'),('producer-owner','if(r.producerDone) slot.capture.reset();','slot.capture.reset();','pending producer identity retained until native completion')]
 for name,old,new,oracle in mutants:
  assert original.count(old)==1;mutant=OUT/name;mutant.mkdir();(mutant/'demand.hpp').write_text(original.replace(old,new,1));shutil.copy2(OUT/'inputs/native/preview_broker.hpp',mutant/'preview_broker.hpp')
  command=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(mutant),str(OUT/'inputs/qa/checks.cpp'),'-o',str(mutant/'checks')]
  run(name+'-compile',command);p=run(name+'-control',[str(mutant/'checks')],1);assert p.stderr.strip()==oracle,(name,p.stderr)
 report['unsafeMutantsDetected']=3
 assert all(sha(ROOT/rel)==h for rel,h in source.items())
 report.update(passed=True,namedScenarios=10,invariantSamples=300,maxSteps=40)
except Exception as exc:report['error']=repr(exc)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
