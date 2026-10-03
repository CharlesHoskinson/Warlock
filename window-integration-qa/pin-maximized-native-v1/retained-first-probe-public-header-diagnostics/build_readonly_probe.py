"""Compile exact observational probe against selected core; never load/launch it."""
from pathlib import Path
import hashlib,json,shlex,subprocess,time,shutil,stat
B=Path(__file__).resolve().parent;C=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback');O=B/'readonly-probe';O.mkdir(exist_ok=True)
source=B/'inverses/readonly-probe.cpp';dest=O/'probe.cpp';shutil.copy2(source,dest)
flags=subprocess.check_output(['pkg-config','--cflags','hyprland','lua','libeis-1.0','libinput','xkbcommon'],text=True).split()
args=['c++','-std=c++26','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(O/'probe.d'),'-I'+str(C/'include'),'-I'+str(C/'core/src'),'-I'+str(C/'core/protocols'),'-I'+str(C/'build-core-make'),'-isystem',str(C/'build-inputs/glaze-src/include'),*flags,str(dest),'-o',str(O/'libqt-modal-probe.so')]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic()
with (O/'compile.log').open('wb') as f:r=subprocess.run(args,cwd=B,stdout=f,stderr=subprocess.STDOUT,timeout=120)
deps={}
if r.returncode==0:
 for entry in shlex.split((O/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1]):
  p=Path(entry).resolve();deps[str(p)]=dict(sha256=h(p),mode=stat.S_IMODE(p.stat().st_mode),mtimeNs=p.stat().st_mtime_ns)
record=dict(nativeLoaded=False,coreExecuted=False,sourceByteExact=dest.read_bytes()==source.read_bytes(),sourceSHA256=h(source),command=args,exitCode=r.returncode,elapsed=time.monotonic()-start,logSHA256=h(O/'compile.log'),dependencies=deps,binarySHA256=h(O/'libqt-modal-probe.so')if r.returncode==0 else None,corePolicyBuild='59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3',compilerOnlyCompatibility=True)
(O/'build-report.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(exitCode=r.returncode,dependencies=len(deps),binarySHA256=record['binarySHA256'])));raise SystemExit(r.returncode)
