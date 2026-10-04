import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1];STAGE=Path('/home/hoskinson/window-integration-qa/private-weston-host-v2');PREFIX=STAGE/'prefix';OWNER=STAGE/'primary/weston-15.0.1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/('observer-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'commands':[],'inputs':{}}
 def run(name,argv,expected=0):
  result=subprocess.run(argv,capture_output=True,timeout=20,env={**os.environ,'LD_LIBRARY_PATH':str(PREFIX/'usr/lib')});(out/(name+'.stdout')).write_bytes(result.stdout);(out/(name+'.stderr')).write_bytes(result.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':result.returncode});assert result.returncode==expected,(name,result.stderr.decode(errors='replace'));return result
 try:
  for p in (Path(__file__),ROOT/'qa/observer-test.c',ROOT/'native/surface-observer.h',ROOT/'native/parent-input-module.c',ROOT/'native/parent-input.xml'):report['inputs'][str(p)]=sha(p)
  generated=out/'generated';generated.mkdir()
  for mode,name in [('server-header','parent-input-server.h'),('private-code','parent-input-protocol.c')]:run('scanner-'+mode,['/usr/bin/wayland-scanner',mode,str(ROOT/'native/parent-input.xml'),str(generated/name)])
  module=(ROOT/'native/parent-input-module.c').read_text();declaration=re.search(r'struct probe \{.*?\n\};',module,re.S).group(0)
  (generated/'probe-struct.h').write_text(declaration+'\n');(generated/'surface-observer.h').write_bytes((ROOT/'native/surface-observer.h').read_bytes())
  flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-server','pixman-1','xkbcommon']).decode())
  def compile_header(name):
   binary=out/name
   run(name+'-compile',['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(generated),'-I'+str(PREFIX/'usr/include/libweston-15'),'-I'+str(OWNER),str(ROOT/'qa/observer-test.c'),str(generated/'parent-input-protocol.c'),'-L'+str(PREFIX/'usr/lib'),'-lweston-15',*flags,'-o',str(binary)])
   return binary
  binary=compile_header('actual-observer');result=run('actual-observer',[str(binary)])
  lines=result.stdout.decode().splitlines();packet=json.loads(lines[0]);assert packet['corners']==[[13,17],[813,17],[13,617],[813,617]] and packet['output']['id']==0 and packet['pointer']['focusedViewId']==1
  report['actualChecks']=int(lines[-1].split('=')[1]);report['mockScope']='Actual production private header/struct and actual owning ABI compile; wl_resource credentials/view selection and coordinate API are explicit CPU stubs, no native geometry observations.'
  original=(ROOT/'native/surface-observer.h').read_text();controls={
   'missing-uniqueness':('if (count != 1 || !selected)','if (count < 1 || !selected)'),
   'missing-revision-bound':('probe->observation_revision == UINT32_MAX || ','')}
  for name,(before,after) in controls.items():
   assert before in original;(generated/'surface-observer.h').write_text(original.replace(before,after,1));mutant=compile_header(name)
   result=subprocess.run([str(mutant)],capture_output=True,timeout=20,env={**os.environ,'LD_LIBRARY_PATH':str(PREFIX/'usr/lib')});(out/(name+'.stdout')).write_bytes(result.stdout);(out/(name+'.stderr')).write_bytes(result.stderr);assert result.returncode!=0;report.setdefault('unsafeControls',[]).append({'name':name,'rejected':True,'exitCode':result.returncode})
  (generated/'surface-observer.h').write_text(original)
  for path,value in report['inputs'].items():assert sha(Path(path))==value,path
  report['passed']=True
 except Exception as error:report['error']=repr(error)
 report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
