"""Immutable-source Elm/native host build; protected launcher required."""
import hashlib,json,os,resource,shlex,shutil,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
files={}
for base in ['src','native','adapter','assets','qa']:
 for p in (ROOT/base).glob('*'):
  if not p.is_file():continue
  target=OUT/'inputs'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);files[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(ROOT/'elm.json',OUT/'inputs/elm.json')
files['elm.json']=hashlib.sha256((ROOT/'elm.json').read_bytes()).hexdigest()
from toolchain import verify,command as pin_command,checks as toolchain_checks
heldToolchain=verify()
rows=[]
def run(name,cmd):
 verify();cmd=pin_command(cmd);build_env=dict(os.environ,ELM_HOME=str(ROOT/heldToolchain['elmHome']));p=subprocess.run(cmd,cwd=OUT/'inputs',capture_output=True,text=True,timeout=180,env=build_env);verify();toolchain_checks.append({'name':name,'beforeAfterVerified':True});(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);rows.append({'name':name,'command':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
report={'elmToolchain':heldToolchain,'elmToolchainBeforeAfterChecks':toolchain_checks,'passed':False,'inputs':files,'scope':'Actual shared-controller Elm and admission C host compilation only; native, GPU and recovery replay qualification separate'}
try:
 run('context-syntax',['node','--check','assets/context.js'])
 run('adapter-syntax',['node','--check','assets/adapter.js'])
 run('popup-adapter-syntax',['node','--check','assets/popup-adapter.js'])
 run('popup-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Popup.elm','--optimize','--output=assets/popup.js'])
 run('bar-adapter-syntax',['node','--check','assets/bar-adapter.js'])
 run('bar-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Bar.elm','--optimize','--output=assets/bar.js'])
 run('elm-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--optimize','--output=assets/elm.js'])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('host-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host.d'),'native/shared-host.c','-o',str(OUT/'elm-host'),*flags])
 run('geometry-carrier-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/geometry-carrier-test.c','-o',str(OUT/'geometry-carrier-tests'),*flags])
 run('geometry-carrier-tests',[str(OUT/'geometry-carrier-tests')])
 run('reconciliation-carrier-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/reconciliation-carrier-test.c','-o',str(OUT/'reconciliation-carrier-tests'),*flags])
 run('reconciliation-carrier-tests',[str(OUT/'reconciliation-carrier-tests')])
 run('context-guard-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/shared-context-test.c','-o',str(OUT/'context-guard-tests'),*flags])
 run('context-guard-tests',[str(OUT/'context-guard-tests')])
 run('context-keys-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/context-keys-test.c','-o',str(OUT/'context-key-tests')])
 run('context-keys-tests',[str(OUT/'context-key-tests')])
 run('host-tests',[str(OUT/'elm-host'),'--self-test'])
 run('surface-test-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/surface-test.c','-o',str(OUT/'surface-tests'),*flags])
 run('surface-tests',[str(OUT/'surface-tests')])
 def inventory(paths):
  rows={}
  for path in paths:
   p=Path(path).absolute();target=p.resolve(strict=True)
   rows[str(p)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'resolved':str(target)}
  return rows
 dependency_text=(OUT/'host.d').read_text().replace('\\\n',' ')
 deps=shlex.split(dependency_text.split(':',1)[1])
 report['compilerDependencies']=inventory([str((OUT/'inputs'/p).resolve()) if not Path(p).is_absolute() else p for p in deps])
 toolpaths=[shutil.which(name) for name in ['cc','pkg-config','node','npm','as','ld']]
 toolpaths+=[subprocess.check_output(['cc','-print-prog-name=cc1'],text=True).strip()]
 report['tools']=inventory(toolpaths)
 libs=run('linked-libraries',['ldd',str(OUT/'elm-host')]);library_paths=[]
 for line in libs.splitlines():
  fields=line.split()
  if '=>' in fields:
   path=fields[fields.index('=>')+1]
   if path.startswith('/'):library_paths.append(path)
  elif fields and fields[0].startswith('/'):library_paths.append(fields[0])
 report['linkedLibraries']=inventory(library_paths)
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'inputs/assets').glob('*') if p.is_file()}
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['commands']=rows
if (OUT/'elm-host').exists():report['binarySHA256']=hashlib.sha256((OUT/'elm-host').read_bytes()).hexdigest()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
