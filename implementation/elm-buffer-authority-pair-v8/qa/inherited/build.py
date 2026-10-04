"""Build fresh effect authority against the exact new owning core and headers."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
files=[ROOT/'native/authority.cpp',ROOT/'candidate/WindowPolicy.hpp',ROOT/'candidate/SceneModal.hpp',ROOT/'candidate/SceneTrace.hpp',ROOT/'adapter/endpoint.py',ROOT/'candidate_host.py',ROOT/'native-build-report.json',*sorted((ROOT/'qa').glob('*.py'))]
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
include=OUT/'include';include.mkdir();(include/'hyprland').symlink_to(OWNER,target_is_directory=True)
report={'passed':False,'scope':'Exact core/plugin compile only; no native effects acceptance','inputs':inputs,'commands':[]}
def run(name,command):
 p=subprocess.run(command,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p.stdout
try:
 pair=json.loads((ROOT/'native-build-report.json').read_text());assert pair['result']=='pass' and sha(pair['binary'])==pair['sha256'];assert sha(pair['buildReport'])==pair['buildReportSHA256']
 flags=shlex.split(run('flags',['pkg-config','--cflags','json-glib-1.0','pixman-1','libdrm','libinput','wayland-server','libeis-1.0']));libs=shlex.split(run('libs',['pkg-config','--libs','json-glib-1.0']))
 binary=OUT/'elm-window-effect-authority.so'
 run('compile',['g++','-std=c++23','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-isystem',str(include),'-isystem',str(OWNER),'-isystem',str(OWNER/'src'),'-isystem',str(OWNER/'protocols'),'-I'+str(OUT/'inputs/candidate'),*flags,'-MD','-MF',str(OUT/'authority.d'),str(OUT/'inputs/native/authority.cpp'),'-o',str(binary),*libs])
 dependencies={str(Path(p).resolve()):sha(Path(p).resolve()) for p in shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1])}
 assert not any(p.startswith('/usr/include/hyprland') for p in dependencies)
 symbols=run('core-symbols',['nm','-D','-C',pair['binary']]);assert 'Desktop::WindowPolicy::applyMinimized' in symbols and 'Desktop::WindowPolicy::isMinimized' in symbols and 'Render::SceneTrace::snapshots' in symbols
 report.update(passed=True,binary=str(binary),binarySHA256=sha(binary),core={'path':pair['binary'],'sha256':pair['sha256'],'versionHeaderSHA256':sha(OWNER/'src/version.h')},dependencies=dependencies)
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
