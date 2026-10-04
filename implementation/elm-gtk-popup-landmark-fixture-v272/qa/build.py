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
  for p in [ROOT/'native/gtk-role-client.c',ROOT/'native/commands.h',pathlib.Path(__file__),ROOT/'REQUIREMENTS.md',ROOT/'SPEC.md']:
   q=inputs/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[str(p.relative_to(ROOT))]={'sha256':digest(q),'capture':str(q)}
  flags=run(['/usr/bin/pkg-config','--cflags','--libs','gtk4','json-glib-1.0','wayland-client'],out/'pkg-config').split()
  versions=run(['/usr/bin/pkg-config','--modversion','gtk4','json-glib-1.0','wayland-client'],out/'versions').splitlines()
  command=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(inputs/'native/gtk-role-client.c'),'-o',str(out/'gtk-role-client'),*flags]
  run(command,out/'compile')
  deps=run(['/usr/bin/cc','-std=c11','-M',str(inputs/'native/gtk-role-client.c'),*flags],out/'dependencies')
  paths=deps.replace('\\\n',' ').split(':',1)[1].split();dependency={}
  for name in paths:
   p=pathlib.Path(name).resolve();dependency[str(p)]={'sha256':digest(p)}
  ldd=run(['/usr/bin/ldd',str(out/'gtk-role-client')],out/'ldd');libraries={}
  for line in ldd.splitlines():
   for word in line.split():
    if word.startswith('/') and pathlib.Path(word).is_file():
     p=pathlib.Path(word).resolve();libraries[str(p)]={'sha256':digest(p)}
  run([str(out/'gtk-role-client'),'--describe'],out/'describe')
  for name,row in sources.items():
   if digest(ROOT/name)!=row['sha256']:raise RuntimeError('source changed during build')
  tools={}
  for name in ['/usr/bin/cc','/usr/bin/pkg-config','/usr/bin/ldd','/usr/bin/python3','/usr/bin/as','/usr/bin/ld']:
   p=pathlib.Path(name).resolve();tools[str(p)]={'sha256':digest(p)}
  cc1=pathlib.Path(run(['/usr/bin/cc','-print-prog-name=cc1'],out/'cc1').strip()).resolve();tools[str(cc1)]={'sha256':digest(cc1)}
  report.update(passed=True,tools=tools,sources=sources,dependencies=dependency,libraries=libraries,command=command,versions=versions,artifact={'path':str(out/'gtk-role-client'),'sha256':digest(out/'gtk-role-client')})
 except Exception as e:report['error']=str(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}))
 if report['passed']:(ROOT/'client-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
