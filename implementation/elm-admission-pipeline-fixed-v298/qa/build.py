"""Actual shared GTK/WebKit host and compiled admission owner helper."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
files=[*sorted((ROOT/'native').glob('*')),Path(__file__)];hashes={};commands=[]
for p in files:
 if not p.is_file():continue
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Actual shared-host compilation/self-test and C helper; no native GUI acceptance','inputs':hashes,'commands':commands}
def run(name,args):
 r=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(r.stdout);(OUT/(name+'.stderr')).write_text(r.stderr);commands.append({'name':name,'argv':args,'exitCode':r.returncode});print(name,r.returncode,flush=True);assert r.returncode==0,r.stdout+r.stderr;return r.stdout
try:
 flags=shlex.split(run('pkg-config',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('shared-host',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/shared-host.c','-o',str(OUT/'elm-host'),*flags]);run('host-tests',[str(OUT/'elm-host'),'--self-test'])
 run('handoff-helper',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','native/handoff-test.c','-o',str(OUT/'handoff-helper'),*flags]);report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
