"""Build the changed navigation authority against the unchanged owning ABI.

Frozen capture/policy dependencies are referenced by hash; no copied lineage.
This report proves compilation/closure only. Actual native journeys are separate.
"""
import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PRIOR=REPO/'implementation/warlock-family-style-crop-capture-v19/qa/build-1791342038926680323'
HELD=PRIOR.parents[1]
OUT=ROOT/'qa/runs'/('native-authority-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'installed':False,'protectedScope':scope,'commands':[],
   'scope':'Changed navigation authority TU and modal preflight against unchanged owning core/capture inputs; strict strong-symbol closure; native acceptance separate'}
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'name':name,'command':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr[-4000:])
 return p.stdout
try:
 prior=json.loads((PRIOR/'report.json').read_text());assert prior['passed'] and sha(prior['binary'])==prior['binarySHA256']
 # Every previously compiled dependency and library remains exact, including
 # retained native policy headers and the owning core's exported ABI.
 preserved={**prior['dependencies'],**prior['linkedLibraries'],**prior['tools']}
 for p,h in preserved.items():assert sha(p)==h,p
 core=prior['core'];assert sha(core['path'])==core['sha256']
 source=OUT/'inputs/native';source.mkdir(parents=True)
 inputs={}
 for name in ('authority.cpp','navigation-modal.hpp'):
  p=ROOT/'native'/name;inputs['native/'+name]=sha(p);shutil.copyfile(p,source/name)
 command=next(c['command'] for c in prior['commands'] if c['name']=='compile').copy()
 for i,arg in enumerate(command):
  if arg==str(PRIOR/'inputs/native/authority.cpp'):command[i]=str(source/'authority.cpp')
  elif i and command[i-1]=='-o':command[i]=str(OUT/'elm-window-geometry-authority.so')
  elif i and command[i-1]=='-MF':command[i]=str(OUT/'authority.d')
 command[1:1]=['-I'+str(PRIOR/'inputs/native')]
 run('navigation-authority-compile',command)
 binary=OUT/'elm-window-geometry-authority.so'
 deps=shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1])
 dependencies={str(pathlib.Path(p).resolve()):sha(p) for p in deps}
 for p,h in dependencies.items():
  if p.startswith(str(source)):
   assert pathlib.Path(p).name in ('authority.cpp','navigation-modal.hpp')
  else:assert preserved.get(p)==h,('Unrecorded or changed inherited dependency',p)
 exports=set()
 for command_row in prior['commands']:
  if not command_row['name'].startswith('provider-symbols-'):continue
  path=PRIOR/(command_row['name']+'.stdout');assert sha(path)==prior['artifacts'][path.name]
  provider=command_row['command'][-1];assert sha(provider)==(core['sha256'] if provider==core['path'] else prior['linkedLibraries'][provider])
  for line in path.read_text().splitlines():
   words=line.split()
   if len(words)>=3:
    symbol=words[-1].replace('@@','@');exports.add(symbol);exports.add(symbol.split('@')[0])
 missing=[]
 for line in run('plugin-undefined',['nm','-D','--undefined-only',str(binary)]).splitlines():
  words=line.split()
  if len(words)==2 and words[0]=='U' and words[1] not in exports:missing.append(words[1])
 assert not missing,missing
 for rel,h in inputs.items():assert sha(ROOT/rel)==h
 for p,h in preserved.items():assert sha(p)==h,p
 assert sha(core['path'])==core['sha256']
 r.update(passed=True,inputs=inputs,dependencies=dependencies,inheritedBuild=str(PRIOR/'report.json'),
          inheritedBuildSHA256=sha(PRIOR/'report.json'),core=core,binary=str(binary),binarySHA256=sha(binary),missingSymbols=missing)
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
