#!/usr/bin/python3
import hashlib,json,pathlib,subprocess,time,shutil,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,out):
 p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 out.with_suffix('.stdout').write_text(p.stdout);out.with_suffix('.stderr').write_text(p.stderr)
 if p.returncode:raise RuntimeError(f'{args[0]} exit {p.returncode}')
 return p.stdout

def main():
 out=ROOT/'qa'/f'build-{time.time_ns()}';out.mkdir(mode=0o700);inputs=out/'inputs';inputs.mkdir()
 report={'passed':False,'nativeAcceptance':False,'sourceRoot':str(ROOT),'buildRoot':str(out)}
 try:
  sources={}
  for p in [ROOT/'native/qt-role-client.cpp',ROOT/'native/commands.hpp',ROOT/'native/private-runtime.h',pathlib.Path(__file__),ROOT/'REQUIREMENTS.md',ROOT/'SPEC.md']:
   q=inputs/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[str(p.relative_to(ROOT))]={'sha256':digest(q),'capture':str(q)}
  flags=run(['/usr/bin/pkg-config','--cflags','--libs','Qt6Widgets','Qt6Gui','Qt6Core','Qt6WaylandClient','wayland-client'],out/'pkg-config').split()
  versions=run(['/usr/bin/pkg-config','--modversion','Qt6Widgets','Qt6Gui','Qt6Core','Qt6WaylandClient','wayland-client'],out/'versions').splitlines()
  version=versions[0]; private=['-I/usr/include/qt6/QtGui/'+version,'-I/usr/include/qt6/QtGui/'+version+'/QtGui','-I/usr/include/qt6/QtCore/'+version,'-I/usr/include/qt6/QtCore/'+version+'/QtCore'];flags+=private
  command=['/usr/bin/c++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(inputs/'native/qt-role-client.cpp'),'-o',str(out/'qt-role-client'),*flags]
  run(command,out/'compile')
  deps=run(['/usr/bin/c++','-std=c++20','-M',str(inputs/'native/qt-role-client.cpp'),*flags],out/'dependencies')
  paths=deps.replace('\\\n',' ').split(':',1)[1].split();dependency={}
  for name in paths:
   p=pathlib.Path(name).resolve();dependency[str(p)]={'sha256':digest(p)}
  plugin=pathlib.Path('/usr/lib/qt6/plugins/platforms/libqwayland.so');ldd=run(['/usr/bin/ldd',str(out/'qt-role-client')],out/'ldd')+run(['/usr/bin/ldd',str(plugin)],out/'plugin-ldd');libraries={str(plugin.resolve()):{'sha256':digest(plugin)}}
  for line in ldd.splitlines():
   for word in line.split():
    if word.startswith('/') and pathlib.Path(word).is_file():
     p=pathlib.Path(word).resolve();libraries[str(p)]={'sha256':digest(p)}
  run([str(out/'qt-role-client'),'--describe'],out/'describe')
  for name,row in sources.items():
   if digest(ROOT/name)!=row['sha256']:raise RuntimeError('source changed during build')
  tools={}
  for name in ['/usr/bin/c++','/usr/bin/pkg-config','/usr/bin/ldd','/usr/bin/python3','/usr/bin/as','/usr/bin/ld']:
   p=pathlib.Path(name).resolve();tools[str(p)]={'sha256':digest(p)}
  cc1=pathlib.Path(run(['/usr/bin/c++','-print-prog-name=cc1plus'],out/'cc1').strip()).resolve();tools[str(cc1)]={'sha256':digest(cc1)}
  report.update(passed=True,tools=tools,sources=sources,dependencies=dependency,libraries=libraries,command=command,versions=versions,artifact={'path':str(out/'qt-role-client'),'sha256':digest(out/'qt-role-client')})
 except Exception as e:report['error']=str(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}))
 if report['passed']:(ROOT/'client-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
