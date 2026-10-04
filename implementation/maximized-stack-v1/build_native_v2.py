"""Build a fresh exact-source compositor derivative; never install or restart."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent
manifest=json.loads((B/'source-manifest.json').read_text());commit=manifest['owning_core'];target=B/'native-core-v2'
if target.exists():raise RuntimeError('Fresh build destination already exists')
report={'scope':scope,'owningCore':commit,'result':'fail','commands':[],'installed':False}
def run(args,timeout=300):
 with (B/'native-build-v2.log').open('ab') as out:
  result=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
 report['commands'].append({'command':args,'exitCode':result.returncode})
 if result.returncode:raise RuntimeError('Native build command failed: '+args[0])
try:
 candidate=B/'candidate/src/render/Renderer.cpp'
 if hashlib.sha256(candidate.read_bytes()).hexdigest()!=manifest['candidate']['sha256']:raise RuntimeError('Candidate changed')
 run(['git','clone','--depth','1','--branch','v0.56.2','https://github.com/hyprwm/Hyprland',str(target)])
 if subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],text=True).strip()!=commit:raise RuntimeError('Remote tag differs from exact owning commit')
 run(['git','-C',str(target),'checkout','--detach',commit])
 run(['git','-C',str(target),'submodule','update','--init','--depth','1'],600)
 (target/'src/render/Renderer.cpp').write_bytes(candidate.read_bytes())
 run(['cmake','-S',str(target),'-B',str(target/'build'),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG'],180)
 run(['cmake','--build',str(target/'build'),'--parallel','8'],1800)
 binary=target/'build/Hyprland'
 report.update(result='pass',binary=str(binary),sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),rendererSHA256=manifest['candidate']['sha256'])
except Exception as error:report['error']=repr(error)
(B/'native-build-v2-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='commands'}))
raise SystemExit(0 if report['result']=='pass' else 1)
