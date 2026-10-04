#!/usr/bin/python3
import ctypes,hashlib,json,os,pathlib,resource,shutil,socket,subprocess,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys_path='/home/hoskinson/window-integration-qa'
import sys
sys.path.insert(0,sys_path)
from qa_launch import require_qa_scope,runtime_base
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/f'guard-{time.time_ns()}';out.mkdir();capt=out/'inputs';capt.mkdir();report={'passed':False,'nativeAcceptance':False,'scope':'actual runtime/client guards with owned temporary directory/socket and kernel peer UID; actual module invalid entry with NULL compositor, no Wayland request/display','checks':[]}
 runtime=None;listener=None
 try:
  selected=sorted(ROOT.glob('build-*/report.json'))[-1];build=json.loads(selected.read_text());assert build['passed']
  for p in (ROOT/'native').iterdir():shutil.copyfile(p,capt/p.name)
  source=capt/'guard.c';source.write_text('#define _GNU_SOURCE\n#define main inert_client_main\n#include "parent-input-client.c"\n#undef main\nbool test_runtime(const char*p){return canonical_private_runtime(p);}\nbool test_socket(void){return private_socket();}\n')
  flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client'],text=True).split();binary=out/'guard.so';p=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared','-I'+str(selected.parent/'generated'),'-I'+str(capt),str(source),str(selected.parent/'generated/parent-input-protocol.c'),*flags,'-o',str(binary)],capture_output=True);(out/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  guard=ctypes.CDLL(str(binary));guard.test_runtime.argtypes=[ctypes.c_char_p];guard.test_runtime.restype=ctypes.c_bool;guard.test_socket.restype=ctypes.c_bool
  def check(name,actual,expected):report['checks'].append({'name':name,'passed':actual==expected,'actual':actual,'expected':expected});assert actual==expected,name
  runtime=pathlib.Path(tempfile.mkdtemp(prefix='g247-',dir=runtime_base()));private=str(runtime)
  check('actual-canonical-private-runtime',guard.test_runtime(private.encode()),True)
  bad=[None,'',f'/run/user/{os.geteuid()}',f'/run/user/{os.geteuid()}/wqa/.',f'/run/user/{os.geteuid()}/wqa/..',private+'/',private+'/../'+runtime.name,'/tmp',private+'/child',private.replace('/wqa/','//wqa/')]
  for i,path in enumerate(bad):check('runtime-refusal-'+str(i),guard.test_runtime(None if path is None else path.encode()),False)
  link=runtime.parent/(runtime.name+'-link');link.symlink_to(runtime)
  try:check('symlink-leaf-refused',guard.test_runtime(str(link).encode()),False)
  finally:link.unlink()
  runtime.chmod(0o755);check('nonprivate-mode-refused',guard.test_runtime(private.encode()),False);runtime.chmod(0o700)
  listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);listener.bind(str(runtime/'wayland-guard'));listener.listen(8)
  os.environ.update(ELM_PARENT_INPUT_QA='1',XDG_RUNTIME_DIR=private,WAYLAND_DISPLAY='wayland-guard')
  check('actual-owned-socket-peer-uid',guard.test_socket(),True);connection,_=listener.accept();connection.close()
  for i,display in enumerate(['', '.', '..','/absolute',str(runtime/'wayland-guard'),'child/wayland-guard','./wayland-guard','wayland-guard/../wayland-guard']):
   os.environ['WAYLAND_DISPLAY']=display;check('display-basename-refusal-'+str(i),guard.test_socket(),False)
  os.environ['WAYLAND_DISPLAY']='wayland-guard';os.environ['ELM_PARENT_INPUT_QA']='0';check('missing-optin-refused',guard.test_socket(),False);os.environ['ELM_PARENT_INPUT_QA']='1'
  os.environ['WAYLAND_DISPLAY']='socket-link';(runtime/'socket-link').symlink_to(runtime/'wayland-guard');check('socket-symlink-refused',guard.test_socket(),False);(runtime/'socket-link').unlink()
  (runtime/'not-socket').write_text('x');os.environ['WAYLAND_DISPLAY']='not-socket';check('regular-file-refused',guard.test_socket(),False);(runtime/'not-socket').unlink()
  os.environ['WAYLAND_DISPLAY']='wayland-guard'
  # Exact entrypoint loaded from actual ABI build. Every invalid runtime must return before dereferencing compositor.
  module_source=out/'module-entry.c';module_source.write_text('#include <dlfcn.h>\n#include <stdio.h>\nstruct weston_compositor;\nint main(int argc,char**argv){if(argc!=2)return 2;void*module=dlopen(argv[1],RTLD_NOW);if(!module){fputs(dlerror(),stderr);return 3;}int(*entry)(struct weston_compositor*,int*,char**)=dlsym(module,"wet_module_init");if(!entry)return 4;int result=entry(NULL,NULL,NULL);dlclose(module);return result==-1?0:5;}\n')
  p=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(module_source),'-ldl','-o',str(out/'module-entry')],capture_output=True);(out/'module-compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  env=dict(os.environ,LD_LIBRARY_PATH='/home/hoskinson/window-integration-qa/private-weston-host-v2/prefix/usr/lib')
  for i,path in enumerate([f'/run/user/{os.geteuid()}',f'/run/user/{os.geteuid()}/wqa/..','/tmp',private+'/child']):
   env['XDG_RUNTIME_DIR']=path;p=subprocess.run([str(out/'module-entry'),build['module']],env=env,capture_output=True,timeout=3);(out/f'module-{i}.stderr').write_bytes(p.stderr);check('actual-module-pre-seat-refusal-'+str(i),p.returncode,0)
  report.update(passed=True,buildReport=str(selected),buildReportSHA256=sha(selected),moduleSHA256=build['moduleSHA256'],clientSourceSHA256=sha(ROOT/'native/parent-input-client.c'),guardSourceSHA256=sha(ROOT/'native/private-runtime.h'),inputs={str(p.relative_to(capt)):sha(p) for p in capt.iterdir() if p.is_file()})
 except Exception as e:report['error']=repr(e)
 finally:
  if listener:listener.close()
  if runtime:
   if (runtime/'wayland-guard').exists():(runtime/'wayland-guard').unlink()
   runtime.rmdir()
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
