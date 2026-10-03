"""Immutable-source Elm/native host build; protected launcher required."""
import hashlib,json,os,resource,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
files={}
for base in ['src','native','adapter','assets','qa']:
 for p in (ROOT/base).glob('*'):
  if not p.is_file():continue
  target=OUT/'inputs'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);files[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(ROOT/'elm.json',OUT/'inputs/elm.json')
files['elm.json']=hashlib.sha256((ROOT/'elm.json').read_bytes()).hexdigest()
rows=[]
def run(name,cmd):
 p=subprocess.run(cmd,cwd=OUT/'inputs',capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);rows.append({'name':name,'command':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
report={'passed':False,'inputs':files,'scope':'Build only; GUI, GPU and complete native qualification separate'}
try:
 run('adapter-syntax',['node','--check','assets/adapter.js'])
 run('elm-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--optimize','--output=assets/elm.js'])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('host-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/host.c','-o',str(OUT/'elm-host'),*flags])
 run('host-tests',[str(OUT/'elm-host'),'--self-test']);report['passed']=True
except Exception as error:report['error']=repr(error)
report['commands']=rows
if (OUT/'elm-host').exists():report['binarySHA256']=hashlib.sha256((OUT/'elm-host').read_bytes()).hexdigest()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
