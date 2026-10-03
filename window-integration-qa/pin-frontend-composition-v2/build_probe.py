"""Compile only the fresh read-only B probe; never load it."""
from pathlib import Path
import hashlib,json,os,re,shutil,stat,subprocess,sys,time
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;P=B/'native-probe'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'sha256':digest(p),'mode':stat.S_IMODE(Path(p).stat().st_mode)}
def main():
 require_qa_scope();before=record(P/'probe.cpp');old=json.loads((QA/'pin-frontend-qa-v1/native-probe/build-report.json').read_text());commands=[]
 command=[str(P/'probe.cpp')if x.endswith('/native-probe/probe.cpp')else str(P/'probe.d')if x.endswith('/native-probe/probe.d')else str(P/'libpin-layer-episode-probe.so')if x.endswith('/native-probe/libpin-frontend-probe.so')else x for x in old['command']]
 compiler=Path(shutil.which(command[0]));command[0]=str(compiler)
 r=subprocess.run(command,capture_output=True,text=True,timeout=120);commands.append({'command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 files={};links={}
 def add(p):
  p=Path(p)
  for parent in [p,*p.parents]:
   if parent.is_symlink():links[str(parent)]=os.readlink(parent)
  if p.is_file():files[str(p)]=record(p)
  if p.resolve()!=p and p.resolve().is_file():files[str(p.resolve())]=record(p.resolve())
 add(compiler)
 for name in('cc1plus','as','ld'):
  c=[str(compiler),'-print-prog-name='+name];v=subprocess.run(c,capture_output=True,text=True,timeout=10);commands.append({'command':c,'exitCode':v.returncode,'stdout':v.stdout,'stderr':v.stderr});assert v.returncode==0
  tool=v.stdout.strip();resolved=Path(tool)if Path(tool).is_absolute()else Path(shutil.which(tool));add(resolved)
 dependencies=[]
 if r.returncode==0:
  for name in (P/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   add(name);dependencies.append(name)
  add(P/'probe.d');add(P/'libpin-layer-episode-probe.so')
  c=['/usr/bin/ldd',str(P/'libpin-layer-episode-probe.so')];v=subprocess.run(c,capture_output=True,text=True,timeout=15);commands.append({'command':c,'exitCode':v.returncode,'stdout':v.stdout,'stderr':v.stderr});assert v.returncode==0 and 'not found'not in v.stdout
  add('/usr/bin/ldd')
  for name in re.findall(r'(?:=>\s*)?(/[^\s()]+)',v.stdout):
   if Path(name).is_file():add(name)
 stable=record(P/'probe.cpp')==before;good=r.returncode==0 and stable
 report={'result':'pass'if good else'fail','commands':commands,'inputs':files,'symlinks':links,'depfile':str(P/'probe.d'),'selectedDependencies':dependencies,'sourceBefore':before,'sourceStable':stable,'binary':str(P/'libpin-layer-episode-probe.so'),'binarySHA256':digest(P/'libpin-layer-episode-probe.so')if good else None,'nativeLoaded':False,'GUI':False}
 target=B/('probe-build-report.json'if good else f'probe-build-failure-{time.time_ns()}.json');assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');os.chmod(target,0o600)
 print(json.dumps({'result':report['result'],'path':str(target),'dependencies':len(dependencies),'commands':len(commands),'nativeLoaded':False}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
