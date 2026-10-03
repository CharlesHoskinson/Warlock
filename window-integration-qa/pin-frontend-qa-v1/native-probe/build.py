from pathlib import Path
import hashlib,json,os,stat,subprocess,time,sys
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope()
 original=QA/'toolkit-held-matrix-v14/native-probe/probe.cpp'
 old=original.read_text();new=(B/'probe.cpp').read_text()
 inverse=new.replace(' const auto keyboardSurface=g_pSeatManager->m_state.keyboardFocus.lock();\n const auto keyboardLayer=keyboardSurface?Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_LAYER_SURFACE).surface(keyboardSurface).runLayer():nullptr;\n std::string keyboardOwner="null";\n','',1).replace('if(layer==keyboardLayer)keyboardOwner=row;','',1).replace('+",\\\"keyboardSurfacePresent\\\":"+(keyboardSurface?"true":"false")+",\\\"keyboardLayerOwner\\\":"+keyboardOwner','',1)
 assert inverse==old,'inherited probe source inverse differs'
 command=json.loads((original.parent/'build-final-report.json').read_text())['command']
 command=[str(B/'probe.cpp')if x.endswith('/native-probe/probe.cpp')else str(B/'probe.d')if x.endswith('/native-probe/probe.d')else str(B/'libpin-frontend-probe.so')if x.endswith('/native-probe/libtoolkit-held-probe.so')else x for x in command]
 before=digest(B/'probe.cpp');r=subprocess.run(command,capture_output=True,text=True,timeout=120)
 deps=[]
 if r.returncode==0:
  for path in (B/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(path);deps.append(dict(path=path,sha256=digest(p),mode=stat.S_IMODE(p.stat().st_mode)))
 row=dict(result='pass'if r.returncode==0 else'fail',command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr,sourceSHA256=before,sourceUnchanged=digest(B/'probe.cpp')==before,inheritedProbeExactOutsideAdditions=True,sourceDependencies=deps,binarySHA256=digest(B/'libpin-frontend-probe.so')if r.returncode==0 else None,nativeLoaded=False)
 out=B/('build-report.json'if r.returncode==0 else f'build-failure-{time.time_ns()}.json');out.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k!='sourceDependencies'}));raise SystemExit(r.returncode!=0)
if __name__=='__main__':main()
