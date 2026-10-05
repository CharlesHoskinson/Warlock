"""Nineteen explicit scenarios: real Elm plus the changed C++ source transport."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[],'projection':'fixed original native job/domain/clock; single packet; actual changed C++ observation/Broker/proof and actual optimized Elm states/commands. Synthetic owned PNG storage, no native capture/FD/hardware claim.'}
def run(name,cmd,input=None,cwd=None):
 p=subprocess.run(cmd,input=input,cwd=cwd or OUT,capture_output=True,text=True,timeout=60)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p
try:
 provider=REPO/'implementation/warlock-preview-provider-v16';reports=list(provider.glob('qa/build-*/report.json'));assert len(reports)==1
 build=reports[0];built=json.loads(build.read_text());assert built['passed']
 worker=build.parent/'inputs/assets/preview-replay.js';fixture=build.parent/'inputs/qa/native-source-fixture.json'
 assert sha(worker)==built['compiledAssetPackage']['files'][worker.name]
 inputs={str(p):sha(p) for p in [build,worker,fixture,ROOT/'SPEC.md',ROOT/'ANCESTRY.json',*ROOT.joinpath('qa').glob('*.*'),*ROOT.joinpath('spec').glob('*.qnt')] if p.is_file()}
 for rel,h in built['inputs'].items():
  if rel.startswith(('src/','native/')) or rel=='elm.json':assert sha(provider/rel)==h;inputs[str(provider/rel)]=h
 r['inputs']=inputs;r['toolSHA256']=sha(TOOL.resolve());shutil.copytree(ROOT/'spec',OUT/'spec');shutil.copytree(provider/'native',OUT/'native')
 for name in ['replay.js','observations.js','observations.cpp']:shutil.copy2(ROOT/'qa'/name,OUT/name)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','json-glib-1.0','gio-unix-2.0']).stdout)
 binary=OUT/'observations'
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'native'),str(OUT/'observations.cpp'),str(OUT/'native/preview_uri.cpp'),'-o',str(binary),*flags])
 def decode(v):
  if isinstance(v,list):return [decode(x) for x in v]
  if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
  return v
 traces=[];selected=[]
 for spec,main,count in [('tests.qnt','source_tests',8),('observation-tests.qnt','observation_tests',11)]:
  names=re.findall(r'run (\w+)\s*=',(OUT/'spec'/spec).read_text());assert len(names)==len(set(names))==count;selected+=names
  run(main+'-typecheck',[str(TOOL),'typecheck',spec],cwd=OUT/'spec')
  run(main+'-selected',[str(TOOL),'test',spec,'--main='+main,'--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=711002','--max-samples=1','--out-itf='+str(OUT/(main+'-{test}-{seq}.itf.json'))],cwd=OUT/'spec')
  paths=list(OUT.glob(main+'-*.itf.json'));assert len(paths)==count
  for p in sorted(paths):
   states=[s['s'] for s in decode(json.loads(p.read_text()))['states']];events=states[-1]['history']
   script='replay.js' if main=='source_tests' else 'observations.js'
   command=['node',str(OUT/script),str(worker),str(fixture)]
   if main=='observation_tests':command.append(str(binary))
   result=run('replay-'+p.stem,command,input='\n'.join(events)+'\n');actual=[json.loads(line) for line in result.stdout.splitlines()];expected=[];length=0
   for s in states:
    if len(s['history'])==length:continue
    length=len(s['history'])
    if main=='source_tests':
     exists=s['domain']!=-1;expected.append({'entries':int(exists),'now':s['now'],'active':exists and s['open'],'demand':exists and s['open'],'known':int(s['known']),'cancelling':int(s['known'] and not s['open']),'commands':s['commands']})
    else:
     state=('live' if s['fresh'] else 'historical') if s['accepted'] and s['open'] else 'loading' if s['capturing'] and s['open'] else 'unavailable'
     expected.append({'state':state,'known':int(s['known']),'capturing':s['capturing'],'accepted':s['accepted'],'retiring':int(s['retiring']),'demand':s['seeded'] and s['open'],'commands':s['commands'],'broker':{'readable':s['accepted'] and not s['revoked'],'charged':s['charged'],'records':s['records'],'cleanup':s['cleanup']}})
   assert actual==expected,(p.name,actual,expected);traces.append({'trace':p.name,'statesCompared':len(actual),'actualCppAndElm':main=='observation_tests'})
 r.update(selectedNames=selected,coupledTraces=traces);assert len(selected)==19 and len(traces)==19
 assert all(sha(p)==h for p,h in inputs.items());r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error'),'statesCompared':sum(x['statesCompared'] for x in r.get('coupledTraces',[]))}));raise SystemExit(not r['passed'])
