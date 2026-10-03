"""Build native observer against exact owning headers; all inputs frozen per attempt."""
import hashlib,json,os,resource,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PAIR=ROOT/'native-build-report.json'
CORE=Path(json.loads(PAIR.read_text())['binary'])
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
inputs={}
for base in ['native','adapter','frontend/src','qa','spec']:
 for p in sorted((ROOT/base).glob('*')):
  if not p.is_file() or (base=='qa' and p.suffix not in ('.py','.cjs')):continue
  relative=p.relative_to(ROOT);dest=OUT/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);inputs[str(relative)]=digest(p)
shutil.copy2(ROOT/'frontend/elm.json',OUT/'inputs/frontend/elm.json');inputs['frontend/elm.json']=digest(ROOT/'frontend/elm.json')
include=OUT/'include';include.mkdir();(include/'hyprland').symlink_to(OWNER,target_is_directory=True)
rows=[]
def run(name,cmd,cwd=OUT):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);rows.append({'name':name,'command':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
result={'passed':False,'scope':'Native plugin and actual nullable-state Elm build; no native loading claim','inputs':inputs}
try:
 pair=json.loads(PAIR.read_text());assert pair['result']=='pass' and digest(CORE)==pair['sha256']
 flags=shlex.split(run('flags',['pkg-config','--cflags','json-glib-1.0','pixman-1','libdrm','libinput','wayland-server','libeis-1.0']))
 libs=shlex.split(run('libs',['pkg-config','--libs','json-glib-1.0']))
 binary=OUT/'elm-observation-authority.so'
 run('compile',['g++','-std=c++23','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-isystem',str(include),'-isystem',str(OWNER),'-isystem',str(OWNER/'src'),'-isystem',str(OWNER/'protocols'),*flags,'-MD','-MF',str(OUT/'authority.d'),str(OUT/'inputs/native/authority.cpp'),'-o',str(binary),*libs])
 deps=shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1]);dependencies={}
 for file in deps:
  p=Path(file).resolve()
  if str(p).startswith('/usr/include/hyprland'):raise RuntimeError('Installed header leak')
  dependencies[str(p)]=digest(p)
 result.update(binary=str(binary),binarySHA256=digest(binary),core={'path':str(CORE),'sha256':digest(CORE),'versionHeaderSHA256':digest(OWNER/'src/version.h')},dependencies=dependencies)
 run('elm-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(OUT/'replay.js')],OUT/'inputs/frontend')
 env=dict(os.environ,ELM_REPLAY=str(OUT/'replay.js'),ELM_REPORT=str(OUT/'elm-report.json'),ELM_TRANSCRIPTS=str(OUT/'elm-transcripts.json'))
 p=subprocess.run(['node',str(OUT/'inputs/qa/replay.cjs')],cwd=OUT,env=env,capture_output=True,text=True,timeout=30)
 (OUT/'elm-checks.stdout').write_text(p.stdout);(OUT/'elm-checks.stderr').write_text(p.stderr);assert p.returncode==0,p.stdout+p.stderr
 quint='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
 traces=OUT/'traces';traces.mkdir()
 run('quint-tests',[quint,'test',str(OUT/'inputs/spec/observer.qnt'),'--match','Test$','--seed','610401','--max-samples','1','--out-itf',str(traces/'named-{test}-{seq}.itf.json')])
 run('quint-invariants',[quint,'run',str(OUT/'inputs/spec/observer.qnt'),'--invariants','safety','--seed','610402','--max-samples','1000','--max-steps','40','--out-itf',str(traces/'sample-{seq}.itf.json')])
 env.update(QUINT_TRACES=str(traces),CONFORMANCE_REPORT=str(OUT/'conformance-report.json'))
 p=subprocess.run(['node',str(OUT/'inputs/qa/conformance.cjs')],cwd=OUT,env=env,capture_output=True,text=True,timeout=30)
 (OUT/'conformance.stdout').write_text(p.stdout);(OUT/'conformance.stderr').write_text(p.stderr);assert p.returncode==0,p.stdout+p.stderr
 result['passed']=True
except Exception as e:result['error']=repr(e)
result['commands']=rows
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not result['passed'])
