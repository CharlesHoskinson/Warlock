from pathlib import Path
import hashlib,json,resource,shlex,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;C=B/'native-candidate';out=B/'helper-report.json';assert not out.exists();scope=require_qa_scope();D=B/'helper-build';D.mkdir();commands=[];deps={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True))
for name in ('test_atlas_coordinates','test_caption_cache'):
 command=['g++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(D/(name+'.d')),str(C/(name+'.cpp')),'-o',str(D/name),*flags]
 for actual in (command,[str(D/name)]):
  p=subprocess.run(actual,capture_output=True,text=True);commands.append({'command':actual,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,commands[-1]
 for path in (D/(name+'.d')).read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(path)
  if p.is_file():deps[str(p.resolve())]=sha(p)
report={'result':'pass','scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'commands':commands,'dependencies':deps,'nativeGUI':False,'mainLoaded':False};out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':'pass','outputs':[r['stdout'].strip() for r in commands if len(r['command'])==1],'dependencies':len(deps),'scope':scope}))
