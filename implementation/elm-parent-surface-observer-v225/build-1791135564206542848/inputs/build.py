import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
STAGE=Path('/home/hoskinson/window-integration-qa/private-weston-host-v2');PREFIX=STAGE/'prefix';OWNER=STAGE/'primary/weston-15.0.1'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'installed':False,'nativeAcceptance':False,'scope':'Actual private Weston additive readonly surface observer/input module/client compile; no GUI or recipient observation acceptance','commands':[]}
def run(name,args):
 proc=subprocess.run(args,capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(proc.stdout);(OUT/(name+'.stderr')).write_bytes(proc.stderr)
 report['commands'].append({'name':name,'command':args,'exitCode':proc.returncode});print(name,proc.returncode,flush=True)
 assert proc.returncode==0,proc.stderr.decode(errors='replace')[-4000:]
 return proc.stdout
try:
 inputs=[ROOT/'build.py',ROOT/'REQUIREMENTS.md',ROOT/'SPEC.md',ROOT/'origin.json',*sorted((ROOT/'native').glob('*'))]
 report['inputs']={str(p.relative_to(ROOT)):digest(p) for p in inputs if p.is_file()}
 for relative in report['inputs']:
  target=OUT/'inputs'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
 report['owningFiles']={str(p):digest(p) for p in (OWNER/'libweston/backend.h',OWNER/'libweston/libweston-internal.h',OWNER/'libweston/input.c',OWNER/'libweston/compositor.c',OWNER/'libweston/desktop/xdg-shell.c',PREFIX/'usr/include/libweston-15/libweston/libweston.h',PREFIX/'usr/include/libweston-15/libweston/matrix.h',OWNER/'frontend/main.c',OWNER/'libweston/backend-headless/headless.c',PREFIX/'usr/lib/libweston-15.so.0.0.1',PREFIX/'usr/bin/weston',Path('/usr/bin/wayland-scanner'))}

 generated=OUT/'generated';generated.mkdir();xml=OUT/'inputs/native/parent-input.xml'
 for mode,name in [('server-header','parent-input-server.h'),('client-header','parent-input-client.h'),('private-code','parent-input-protocol.c')]:run('protocol-'+mode,['/usr/bin/wayland-scanner',mode,str(xml),str(generated/name)])
 server=shlex.split(run('server-flags',['/usr/bin/pkg-config','--cflags','--libs','wayland-server','pixman-1','xkbcommon']).decode())
 client=shlex.split(run('client-flags',['/usr/bin/pkg-config','--cflags','--libs','wayland-client']).decode())
 common=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(generated)]
 module=OUT/'parent-input.so';helper=OUT/'parent-input-client'
 run('module-build',[*common,'-fPIC','-shared','-I'+str(PREFIX/'usr/include/libweston-15'),'-I'+str(OWNER),str(OUT/'inputs/native/parent-input-module.c'),str(generated/'parent-input-protocol.c'),'-L'+str(PREFIX/'usr/lib'),'-lweston-15',*server,'-Wl,-z,defs','-Wl,--dependency-file='+str(OUT/'module-link.d'),'-MMD','-MF',str(OUT/'module.d'),'-o',str(module)])
 run('client-build',[*common,str(OUT/'inputs/native/parent-input-client.c'),str(generated/'parent-input-protocol.c'),*client,'-Wl,--dependency-file='+str(OUT/'client-link.d'),'-MMD','-MF',str(OUT/'client.d'),'-o',str(helper)])
 symbols=run('module-symbols',['/usr/bin/nm','-D','--defined-only',str(module)]).decode();assert any(line.split()[-1]=='wet_module_init' for line in symbols.splitlines())
 report['dependencies']={}
 # GCC -MF for a multi-source link retains only the last unit; compile each production unit separately for complete dependency closure.
 for name,source,flags in [('module',OUT/'inputs/native/parent-input-module.c',['-I'+str(PREFIX/'usr/include/libweston-15'),'-I'+str(OWNER),*server]),('client',OUT/'inputs/native/parent-input-client.c',client),('protocol',generated/'parent-input-protocol.c',server)]:
  dep=OUT/(name+'-closure.d');run(name+'-closure',[*common,*flags,'-M',str(source),'-MF',str(dep)])
  for path in shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]):
   path=Path(path).resolve();report['dependencies'][str(path)]=digest(path)
 for relative,sha in report['inputs'].items():assert digest(ROOT/relative)==sha and digest(OUT/'inputs'/relative)==sha,relative
 for path,sha in report['owningFiles'].items():assert digest(path)==sha,path
 report['tools']={str(p):digest(p) for p in (Path('/usr/bin/cc').resolve(),Path('/usr/bin/pkg-config').resolve(),Path('/usr/bin/nm').resolve(),Path('/usr/bin/wayland-scanner').resolve())}
 report['linkedLibraries']={}
 for name,binary in [('module',module),('client',helper)]:
  import os
  result=subprocess.run(['/usr/bin/ldd',str(binary)],capture_output=True,timeout=20,env={**os.environ,'LD_LIBRARY_PATH':str(PREFIX/'usr/lib')});assert result.returncode==0
  (OUT/(name+'-libraries.stdout')).write_bytes(result.stdout)
  for line in result.stdout.decode().splitlines():
   words=line.split();path=next((word for word in words if word.startswith('/') and Path(word).is_file()),None)
   if path:report['linkedLibraries'][str(Path(path).resolve())]=digest(Path(path).resolve())
  assert b'not found' not in result.stdout
 report.update(passed=True,module=str(module),moduleSHA256=digest(module),client=str(helper),clientSHA256=digest(helper))
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True);raise SystemExit(not report['passed'])
