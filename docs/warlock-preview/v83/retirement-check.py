"""Selected Quint traces coupled to the exact compiled plugin18 classifier."""
import hashlib, json, pathlib, re, resource, shutil, subprocess, sys, time
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parent
repo=root.parents[2]
native=repo/'implementation/warlock-family-style-crop-capture-v18'
out=root/('retirement-check-'+str(time.time_ns()));out.mkdir()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sources=[root/name for name in ['retirement.qnt','retirement_tests.qnt','retirement-checks.cpp','retirement-check.py']]+[native/'native/incarnation-retirement.hpp',native/'native/authority.cpp']
inputs={str(path):sha(path) for path in sources}
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Exact plugin18 native classifier coupled to synthetic issuance/membership/minimization traces. No authenticated socket, compositor membership, physical retirement or whole-actor turnover acceptance.'}
def run(name,args,stdin=None,cwd=None):
 result=subprocess.run(args,input=stdin,cwd=cwd or out,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':result.returncode});print(name,result.returncode,flush=True)
 assert result.returncode==0,result.stderr or result.stdout
 return result.stdout
def decode(value):
 if isinstance(value,list):return [decode(row) for row in value]
 if isinstance(value,dict):
  if '#bigint' in value:return int(value['#bigint'])
  if '#set' in value:return sorted(decode(value['#set']))
  return {key:decode(row) for key,row in value.items()}
 return value
try:
 build=next(native.glob('qa/build-*/report.json'));compiled=json.loads(build.read_text());assert compiled['passed']
 for name,value in compiled['inputs'].items():assert sha(native/name)==value,name
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 folder=out/'inputs';folder.mkdir()
 for path in sources:shutil.copy2(path,folder/path.name)
 run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(folder),str(folder/'retirement-checks.cpp'),'-o',str(out/'checks')])
 names=re.findall(r'run (\w+)\s*=',(folder/'retirement_tests.qnt').read_text());assert len(names)==8
 run('typecheck',[str(tool),'typecheck','retirement_tests.qnt'],cwd=folder)
 run('selected',[str(tool),'test','retirement_tests.qnt','--main=retirement_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=830001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==8
 run('samples',[str(tool),'run','retirement.qnt','--main=retirement','--backend=typescript','--invariant=safety','--seed=830002','--max-samples=150','--max-steps=35','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({key:value for key,value in state.items() if key!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n';actual=[json.loads(line) for line in run('replay-'+path.stem,[str(out/'checks')],stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual)});witnesses[path.name]=(stdin,wanted)
 caught=[]
 for name,old,new,witness in [('future-retired','if (subject > issued) return State::Future;','if (false) return State::Future;','futureBeyondFrontier'),('owned-retired','return owned ? State::Active : State::Retired;','return State::Retired;','minimizedStillOwned')]:
  changed=out/name;shutil.copytree(folder,changed);header=changed/'incarnation-retirement.hpp';text=header.read_text();assert text.count(old)==1;header.write_text(text.replace(old,new))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(changed),str(changed/'retirement-checks.cpp'),'-o',str(changed/'checks')])
  trace=next(key for key in witnesses if witness in key);stdin,wanted=witnesses[trace]
  actual=[json.loads(line) for line in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()];assert actual!=wanted
  caught.append({'name':name,'trace':trace,'differentObservableState':True})
 assert all(sha(pathlib.Path(name))==value for name,value in inputs.items())
 report.update(passed=True,selectedNames=names,namedScenarios=8,invariantSamples=150,coupledTraces=traces,statesCompared=sum(row['statesCompared'] for row in traces),mutants=caught,unsafeMutantsDetected=2)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(path.relative_to(out)):sha(path) for path in out.rglob('*') if path.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True)
sys.exit(not report['passed'])
