from pathlib import Path
import hashlib,json,resource,shlex,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;C=B/'native-candidate';scope=require_qa_scope();out=B/'build-report.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={str(p):sha(p) for p in C.iterdir() if p.suffix in ('.cpp','.hpp') or p.name=='Makefile'}
command=['make','-B','-j2','-C',str(C)];process=subprocess.run(command,text=True,capture_output=True)
report={'result':'compiled' if process.returncode==0 else 'fail','command':command,'exitCode':process.returncode,'stdout':process.stdout,'stderr':process.stderr,'scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'sourceHashes':source,'nativeExecuted':False,'mainLoaded':False,'sourceDependencies':{}}
if process.returncode==0:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','pixman-1','libdrm','hyprland','libinput','libudev','wayland-server','xkbcommon','libeis-1.0'],text=True))
 for name in ('main.cpp','barDeco.cpp','BarPassElement.cpp','dragBridge.cpp','familyBridge.cpp','ancestorHit.cpp','snapshotBridge.cpp','atlasRenderer.cpp','atlasAdapter.cpp'):
  deps=subprocess.check_output(['g++','-std=c++2b','-M',*flags,str(C/name)],text=True)
  for name in deps.replace('\\\n',' ').split(':',1)[1].split():
   path=Path(name)
   if path.is_file():report['sourceDependencies'][str(path.resolve())]=sha(path)
 binary=C/'hyprbars-v19-modal-candidate.so';report['binarySHA256']=sha(binary)
 assert source=={p:sha(Path(p)) for p in source}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'binarySHA256':report.get('binarySHA256'),'dependencies':len(report['sourceDependencies']),'scope':scope}));raise SystemExit(process.returncode)
