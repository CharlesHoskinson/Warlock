"""Protected isolated build of unchanged plugin against owning candidate core."""
from pathlib import Path
import hashlib,json,os,shlex,shutil,subprocess,time
ROOT=Path(__file__).resolve().parent
CORE=ROOT/'native-core-v2';ORIGINAL=Path('/home/hoskinson/src/hyprbars-dragend-initfix');BUILD=ROOT/'plugin-build-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(command,**kwargs):
 print('RUN',shlex.join(command),flush=True)
 return subprocess.run(command,check=True,**kwargs)
def main():
 if BUILD.exists():raise ValueError('fresh build directory required')
 if subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD'],text=True).strip()!='efb50993780079460b0cbed1363e2166a2de1d9f':raise ValueError('wrong owning core')
 renderer=ROOT/'candidate/src/render/Renderer.cpp'
 if sha(renderer)!=sha(CORE/'src/render/Renderer.cpp'):raise ValueError('candidate renderer mismatch')
 BUILD.mkdir(mode=0o700);source=BUILD/'source';source.mkdir()
 originals=[]
 for path in sorted(ORIGINAL.iterdir()):
  if path.is_file() and path.suffix in ('.cpp','.hpp','.h') or path.name in ('Makefile','CMakeLists.txt','meson.build','LICENSE'):
   shutil.copy2(path,source/path.name);originals.append({'original':str(path),'copy':str(source/path.name),'sha256':sha(path)})
 headers=BUILD/'include';headers.mkdir();(headers/'hyprland').symlink_to(CORE,target_is_directory=True)
 raw=subprocess.check_output(['pkg-config','--cflags','pixman-1','libdrm','hyprland','libinput','libudev','wayland-server','xkbcommon','libeis-1.0'],text=True).strip()
 flags=[token for token in shlex.split(raw) if not token.startswith('-I/usr/include/hyprland')]
 compiler=Path(shutil.which('g++')).resolve();version=subprocess.check_output([str(compiler),'--version'],text=True)
 includes=['-I'+str(headers),'-I'+str(CORE),'-I'+str(CORE/'src'),'-I'+str(CORE/'protocols'),*flags]
 arguments=[str(compiler),'-O2','-fPIC','-std=c++2b','-Wno-c++11-narrowing','-fno-gnu-unique',*includes]
 dependencies={};commands=[];objects=[];version_header_sha=sha(CORE/'src/version.h');started=time.monotonic()
 try:
  for name in ('main.cpp','barDeco.cpp','BarPassElement.cpp','dragBridge.cpp','familyBridge.cpp'):
   obj=BUILD/(Path(name).stem+'.o');dep=obj.with_suffix('.d');command=[*arguments,'-MD','-MF',str(dep),'-c',str(source/name),'-o',str(obj)];commands.append(command);run(command);objects.append(str(obj))
   text=dep.read_text().replace('\\\n',' ');paths=shlex.split(text.split(':',1)[1])
   for value in paths:
    path=Path(value).resolve()
    if path.is_relative_to('/usr/include/hyprland'):raise ValueError('installed Hyprland header leak '+str(path))
    if path.is_file():dependencies[str(path)]=sha(path)
  output=BUILD/'hyprbars-maximized-stack-v1.so';command=[str(compiler),'-shared','-fno-gnu-unique',*objects,'-o',str(output)];commands.append(command);run(command)
  if sha(CORE/'src/version.h')!=version_header_sha:raise ValueError('owning version header changed during compile')
  if any(sha(Path(row['original']))!=row['sha256'] or sha(Path(row['copy']))!=row['sha256'] for row in originals):raise ValueError('plugin source changed during build')
  for path,digest in dependencies.items():
   if sha(Path(path))!=digest:raise ValueError('header changed during compile '+path)
  report={'accepted_build_only':True,'native_load':False,'core_commit':'efb50993780079460b0cbed1363e2166a2de1d9f','renderer_sha256':sha(renderer),'core_version_header':str(CORE/'src/version.h'),'core_version_header_sha256':version_header_sha,'compiler':str(compiler),'compiler_sha256':sha(compiler),'compiler_version':version,'original_pkgconfig_cflags':raw,'effective_includes':includes,'sources':originals,'compiler_dependency_headers':dependencies,'commands':commands,'elapsed_seconds':time.monotonic()-started,'plugin':str(output),'plugin_sha256':sha(output)}
  binary=CORE/'build/Hyprland'
  if binary.is_file():report['candidate_core_binary_sha256_at_plugin_build']=sha(binary)
  (BUILD/'pair-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({'plugin':str(output),'sha256':sha(output),'dependencies':len(dependencies),'elapsed_seconds':report['elapsed_seconds']}),flush=True)
 except BaseException as e:
  (BUILD/'failed-build.json').write_text(json.dumps({'error':str(e),'commands':commands,'native_load':False},indent=2)+'\n');raise
if __name__=='__main__':main()
