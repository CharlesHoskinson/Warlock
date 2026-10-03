"""Build only byte-exact composition observation against the selected owning ABI."""
from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess,sys,time
from io_guard import publish_json,sha
B=Path(__file__).resolve().parent;QA=B.parent
OLD=QA/'pin-frontend-composition-v2';CORE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
def main():
 require_qa_scope();p=B/'native-probe';p.mkdir(mode=0o700)
 source=OLD/'native-probe/probe.cpp';(p/'probe.cpp').write_bytes(source.read_bytes());(p/'probe.cpp').chmod(stat.S_IMODE(source.stat().st_mode));before=sha(source)
 old=json.loads((QA/'pin-maximized-native-v2/readonly-probe/build-report.json').read_bytes());cmd=[]
 for v in old['command']:
  if v.endswith('/readonly-probe/probe.cpp'):v=str(p/'probe.cpp')
  elif v.endswith('/readonly-probe/probe.d'):v=str(p/'probe.d')
  elif v.endswith('/readonly-probe/libqt-modal-probe.so'):v=str(p/'libpin-layer-episode-probe.so')
  cmd.append(v)
 cmd[0]=str(Path(shutil.which(cmd[0])));commands=[];started=time.monotonic()
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);commands.append(dict(command=cmd,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr,elapsedSeconds=time.monotonic()-started))
 inputs={};links={};dirs={}
 def add(path):
  path=Path(path)
  for part in [path,*path.parents]:
   if part.is_symlink():links[str(part)]=os.readlink(part)
   elif part.is_dir():dirs[str(part)]=stat.S_IMODE(part.stat().st_mode)
  if path.is_file():inputs[str(path)]=dict(sha256=sha(path),mode=stat.S_IMODE(path.stat().st_mode))
  if path.resolve()!=path and path.resolve().is_file():add(path.resolve())
 add(cmd[0]);deps=[]
 for tool in ['cc1plus','as','ld']:
  c=[cmd[0],'-print-prog-name='+tool];v=subprocess.run(c,capture_output=True,text=True,timeout=10);commands.append(dict(command=c,exitCode=v.returncode,stdout=v.stdout,stderr=v.stderr))
  if v.returncode:raise RuntimeError('Compiler tool discovery failed')
  add(Path(v.stdout.strip())if Path(v.stdout.strip()).is_absolute()else shutil.which(v.stdout.strip()))
 if r.returncode==0:
  deps=(p/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1].split()
  for d in deps:add(d)
  add(p/'probe.d');add(p/'libpin-layer-episode-probe.so')
  c=['/usr/bin/ldd',str(p/'libpin-layer-episode-probe.so')];v=subprocess.run(c,capture_output=True,text=True,timeout=15);commands.append(dict(command=c,exitCode=v.returncode,stdout=v.stdout,stderr=v.stderr));add(c[0])
  import re
  if v.returncode or 'not found'in v.stdout:raise RuntimeError('Current probe loader closure unresolved')
  for d in re.findall(r'(?:=>\s*)?(/[^\s()]+)',v.stdout):
   if Path(d).is_file():add(d)
 own=all(not str(Path(d).resolve()).startswith('/usr/include/hyprland/')for d in deps)
 own=own and any(str(Path(d).resolve()).startswith(str(CORE/'core/src')+'/')for d in deps)
 ok=r.returncode==0 and own and sha(source)==before and sha(p/'probe.cpp')==before
 report=dict(result='pass'if ok else'fail',commands=commands,inputs=inputs,symlinks=links,directoryModes=dirs,selectedDependencies=deps,sourceSHA256=before,compositionSourceByteExact=sha(p/'probe.cpp')==before,owningCoreHeadersOnly=own,selectedCore=str(CORE/'build-core-make/Hyprland'),binary=str(p/'libpin-layer-episode-probe.so'),binarySHA256=sha(p/'libpin-layer-episode-probe.so')if ok else None,installedHeaderBuildAncestor=str(OLD/'probe-build-report.json'),installedHeaderBuildSelected=False,nativeLoaded=False,GUI=False)
 target=B/('probe-build-report.json'if ok else'probe-build-failure-'+str(time.time_ns())+'.json');publish_json(target,report)
 print(json.dumps(dict(result=report['result'],path=str(target),dependencies=len(deps),GUI=False)));return int(not ok)
if __name__=='__main__':raise SystemExit(main())
