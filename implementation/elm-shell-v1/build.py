"""Pinned Elm asset and C host build. Run through protected QA."""
import json,shlex,subprocess,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'build';OUT.mkdir(exist_ok=True)
packages=['gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0']
rows=[]
def run(name,cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 rows.append(dict(name=name,command=cmd,exitCode=p.returncode));print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
result={'scope':'Build and CPU checks only; native/GPU acceptance separate','observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False}
try:
 result['versions']=run('native-versions',['pkg-config','--modversion',*packages]).splitlines()
 result['elmVersion']=run('elm-version',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','--version']).strip()
 run('adapter-syntax',['node','--check','assets/adapter.js'])
 run('elm-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--output=assets/elm.js','--optimize'])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs',*packages]))
 run('host-build',['cc','-std=c11','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-O2','native/host.c','-o',str(OUT/'elm-host'),*flags])
 run('host-tests',[str(OUT/'elm-host'),'--self-test'])
 run('elm-test-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Tests.elm','--output=build/tests.js'])
 run('elm-tests',['node','qa/elm_tests.cjs'])
 result['passed']=True
except Exception as error:result['error']=str(error)
result['commands']=rows
result['files']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ['src','assets','native'] for p in (ROOT/base).rglob('*') if p.is_file()}
(OUT/'build-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(not result['passed'])
