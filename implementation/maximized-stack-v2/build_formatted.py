"""Recompile formatted renderer into a fresh archive/binary; preserve v1 build."""
import hashlib,json,re,shlex,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent;V1=B.parent/'maximized-stack-v1';old=V1/'native-core-v2/build';out=B/'native-build';out.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((B/'source-manifest.json').read_text());source=B/'candidate/src/render/Renderer.cpp'
assert sha(source)==manifest['candidate']['sha256']
prior=json.loads((V1/'native-build-v2-report.json').read_text());assert prior['result']=='pass' and sha(prior['binary'])==prior['sha256']
flags={}
for line in (old/'CMakeFiles/hyprland_lib.dir/flags.make').read_text().splitlines():
 for k in ('CXX_DEFINES','CXX_INCLUDES','CXX_FLAGS'):
  if line.startswith(k+' = '):flags[k]=shlex.split(line.split(' = ',1)[1])
compile=['/usr/bin/c++',*flags['CXX_DEFINES'],*flags['CXX_INCLUDES'],*flags['CXX_FLAGS'],'-I'+str(V1/'native-core-v2/src/render'),'-MD','-MF',str(out/'Renderer.d'),'-c',str(source),'-o',str(out/'Renderer.cpp.o')]
commands=[compile]
report={'scope':scope,'installed':False,'result':'fail','priorBinarySHA256':prior['sha256'],'rendererSHA256':sha(source),'commands':commands,'priorArchiveSHA256':sha(old/'libhyprland_lib.a')}
try:
 with (B/'native-build.log').open('wb') as log:
  subprocess.run(compile,cwd=old,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
  shutil.copy2(old/'libhyprland_lib.a',out/'libhyprland_lib.a')
  ar=['/usr/bin/ar','r',str(out/'libhyprland_lib.a'),str(out/'Renderer.cpp.o')];commands.append(ar);subprocess.run(ar,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=30)
  link=shlex.split((old/'CMakeFiles/Hyprland.dir/link.txt').read_text())
  for i,arg in enumerate(link):
   if i>0 and link[i-1]=='-o':link[i]=str(out/'Hyprland')
   elif arg=='libhyprland_lib.a':link[i]=str(out/'libhyprland_lib.a')
   elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(out/'link.d')
  commands.append(link);subprocess.run(link,cwd=old,stdout=log,stderr=subprocess.STDOUT,timeout=120,check=True)
 plugin=json.loads((V1/'plugin-build-report.json').read_text())
 assert sha(plugin['binary'])==plugin['sha256']
 report.update(result='pass',binary=str(out/'Hyprland'),sha256=sha(out/'Hyprland'),plugin=plugin,
               priorBinaryPreserved=sha(prior['binary'])==prior['sha256'],priorArchivePreserved=sha(old/'libhyprland_lib.a')==report['priorArchiveSHA256'])
except Exception as e:report['error']=repr(e)
(B/'native-build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('commands','plugin')}));raise SystemExit(report['result']!='pass')
