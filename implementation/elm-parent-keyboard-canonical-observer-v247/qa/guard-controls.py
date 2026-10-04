#!/usr/bin/python3
import hashlib,json,pathlib,shutil,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/f'guard-controls-{time.time_ns()}';out.mkdir();selected=sorted(ROOT.glob('build-*/report.json'))[-1];build=json.loads(selected.read_text());runtime=(ROOT/'native/private-runtime.h').read_text();client=(ROOT/'native/parent-input-client.c').read_text();suite=(ROOT/'qa/guard-test.py').read_text()
 controls=[('missing-private-mode',runtime.replace(' && (info.st_mode&0777)==0700',''),client),('dotdot-plus-canonical-bypass',runtime.replace(' || !strcmp(leaf,".") || !strcmp(leaf,"..")','').replace('return !strcmp(resolved,runtime);','return true;'),client),('slash-display-bypass',runtime,client.replace(" || strchr(display,'/')",''))]
 report={'passed':False,'nativeAcceptance':False,'controls':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'native/private-runtime.h',ROOT/'native/parent-input-client.c',ROOT/'native/parent-input-module.c',ROOT/'qa/guard-test.py']}}
 try:
  for name,r,c in controls:
   directory=out/name;(directory/'qa').mkdir(parents=True);shutil.copytree(ROOT/'native',directory/'native');(directory/'native/private-runtime.h').write_text(r);(directory/'native/parent-input-client.c').write_text(c);(directory/'qa/guard-test.py').write_text(suite);fake=directory/'build-pinned';fake.mkdir();(fake/'report.json').write_text(json.dumps(build));(fake/'generated').symlink_to(selected.parent/'generated',target_is_directory=True)
   p=subprocess.run(['/usr/bin/python3','-B',str(directory/'qa/guard-test.py')],capture_output=True,timeout=8);(directory/'stdout').write_bytes(p.stdout);(directory/'stderr').write_bytes(p.stderr)
   evidence=sorted((directory/'qa').glob('guard-*/report.json'))[-1];result=json.loads(evidence.read_text());failed=[x for x in result['checks'] if not x['passed']];assert p.returncode!=0 and failed,name
   report['controls'].append({'name':name,'behaviorallyRejected':True,'exit':p.returncode,'oracle':failed[0]['name'],'report':str(evidence),'reportSHA256':sha(evidence)})
  # Compile actual module with only its early runtime gate removed, then call actual entry with NULL compositor.
  directory=out/'module-entry-bypass';directory.mkdir();source=directory/'parent-input-module.c';source.write_text((ROOT/'native/parent-input-module.c').read_text().replace(' || !canonical_private_runtime(getenv("XDG_RUNTIME_DIR"))',''))
  flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-server','pixman-1','xkbcommon'],text=True).split();prefix=pathlib.Path('/home/hoskinson/window-integration-qa/private-weston-host-v2');module=directory/'unsafe.so'
  command=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-fPIC','-shared','-I'+str(selected.parent/'generated'),'-I'+str(ROOT/'native'),'-I'+str(prefix/'prefix/usr/include/libweston-15'),'-I'+str(prefix/'primary/weston-15.0.1'),str(source),str(selected.parent/'generated/parent-input-protocol.c'),'-L'+str(prefix/'prefix/usr/lib'),'-lweston-15',*flags,'-Wl,-z,defs','-o',str(module)]
  p=subprocess.run(command,capture_output=True);(directory/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  import os
  harness=sorted((ROOT/'qa').glob('guard-*/module-entry'))[-1]
  p=subprocess.run([str(harness),str(module)],env=dict(os.environ,ELM_PARENT_INPUT_QA='1',XDG_RUNTIME_DIR='/tmp',LD_LIBRARY_PATH=str(prefix/'prefix/usr/lib')),capture_output=True,timeout=3);(directory/'stdout').write_bytes(p.stdout);(directory/'stderr').write_bytes(p.stderr);assert p.returncode!=0
  report['controls'].append({'name':'module-entry-bypass','behaviorallyRejected':True,'exit':p.returncode,'oracle':'actual NULL-compositor early-refusal entry','sourceSHA256':sha(source),'artifactSHA256':sha(module)})
  report['passed']=True
 except Exception as e:report['error']=repr(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'controls':len(report['controls']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
