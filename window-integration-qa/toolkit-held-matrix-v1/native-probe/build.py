from pathlib import Path
import hashlib,json,resource,subprocess,sys
B=Path(__file__).resolve().parent;Q=B.parent.parent
sys.path.insert(0,str(Q))
from qa_launch import require_qa_scope
scope=require_qa_scope();flags=subprocess.check_output(['pkg-config','--cflags','hyprland','lua','libeis-1.0','libinput','xkbcommon'],text=True).split()
command=['c++','-std=c++23','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(B/'probe.d'),*flags,str(B/'probe.cpp'),'-o',str(B/'libtoolkit-held-probe.so')]
run=subprocess.run(command,capture_output=True,text=True,timeout=120)
headers=[]
if run.returncode==0:
 for path in (B/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(path)
  if p.is_file():headers.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'result':'pass' if run.returncode==0 else 'fail','scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'command':command,'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'sourceDependencies':headers,'binarySHA256':hashlib.sha256((B/'libtoolkit-held-probe.so').read_bytes()).hexdigest() if run.returncode==0 else None,'nativeLoaded':False}
p=B/'build-final-report.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'headers':len(headers),'binarySHA256':report['binarySHA256'],'scope':scope}));raise SystemExit(run.returncode)
