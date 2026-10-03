"""External nongraphical reachable-contention replay; no native IPC or GUI."""
import errno,fcntl,hashlib,json,os,subprocess,sys,time
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa')
B=Q/'family-preparation-thumbnail-v9'
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
D=Path(__file__).parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(S))
from test_batch_preview import BatchTests
from owned_commands import SealedFile
from pipe_transport import PipeTransport
from native_runtime import FailureBinding

def save(name,row):
 with os.fdopen(os.open(D/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n')
def main():
 case=BatchTests();case.setUp();writer=None;transport=None;permit=None
 result={'scope':'reachable kernel contention only; native attempt lock holder and exact site unproved','result':'fail'}
 try:
  case.stage([(80,50,3,4,False,1),(80,50,3,4,False,1),(80,50,3,4,False,1)])
  source=S/'renderer_role_cpu_fixture.c';executable=case.root/'cpu-renderer'
  subprocess.run(['/usr/bin/gcc','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(executable)],check=True,timeout=10)
  with SealedFile(executable)as sealed:
   transport=PipeTransport('/proc/self/fd/'+str(sealed.fd),env=case.env,failure=FailureBinding(),pass_fds=(sealed.fd,),keeper=case.keeper,actor=17)
  case.batch.bind_renderer(transport,hashlib.sha256(executable.read_bytes()).hexdigest())
  deadline=time.monotonic()+2
  while not transport.outputs()and time.monotonic()<deadline:time.sleep(.002)
  assert transport.outputs()and case.batch._closed()
  live_renderer=json.loads(json.dumps(next(iter(case.keeper.jobs.values()))))
  shim=case.root/'fixture-bin';shim.mkdir(mode=0o700)
  marker=case.root/'writer-holds-lock';permit=case.root/'permit-writer'
  target=dict(case.members[1],mapped=True,hidden=False,workspace={'name':'1'})
  query='#!/usr/bin/python3\nimport json,pathlib,time\np=pathlib.Path('+repr(str(marker))+')\np.write_text("query entered after actual production flock")\nd=time.monotonic()+1.8\nwhile not pathlib.Path('+repr(str(permit))+').exists():\n if time.monotonic()>d:raise TimeoutError("CPU fixture permit missing")\n time.sleep(.002)\nprint('+repr(json.dumps([target]))+')\n'
  export='#!/usr/bin/python3\nimport shutil,sys\nshutil.copyfile('+repr(case.sources[1]['path'])+',sys.argv[-1])\n'
  for name,text in [('hyprctl',query),('grim',export)]:
   (shim/name).write_text(text);(shim/name).chmod(0o700)
  env=dict(case.env,PATH=str(shim)+':/usr/bin');env['XDG_RUNTIME_DIR']=str(case.root)
  # Product script derives precisely this preview path; same batch instance.
  case.preview=case.root/'hypr-window-previews';case.batch.preview=case.preview
  script=B/'payload/home/.local/bin/hypr-window-preview'
  writer=subprocess.Popen(['/usr/bin/bash',str(script),'capture-both',target['address'],'0'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  deadline=time.monotonic()+2
  while not marker.exists()and time.monotonic()<deadline:time.sleep(.002)
  assert marker.exists()and writer.poll()is None
  failure=None;began=time.monotonic_ns()
  try:case.finish()
  except BlockingIOError as e:failure={'type':type(e).__name__,'errno':e.errno,'message':str(e)}
  elapsed=time.monotonic_ns()-began
  assert failure and failure['errno']==errno.EAGAIN
  assert not list(case.preview.glob('0x*.png'))and len(case.batch.pending)==3
  assert len(case.keeper.jobs)==1 and case.batch._closed()and transport.process.poll()is None
  permit.write_text('release explicit CPU query fixture')
  stdout,stderr=writer.communicate(timeout=3);assert writer.returncode==0
  assert all((case.preview/(target['address']+'-'+str(slot)+'.png')).is_file()for slot in (0,1))
  writer_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in case.preview.glob('0x*.png')}
  case.finish();assert not case.batch.pending
  publication={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in case.preview.glob('0x*.png')};assert len(publication)==6
  assert transport.close()==0;case.keeper.stop()
  result.update(result='pass',failure=failure,refusalElapsedNs=elapsed,rendererAtObservation=live_renderer,
    writer={'argv':['/usr/bin/bash',str(script),'capture-both',target['address'],'0'],'sourceSHA256':hashlib.sha256(script.read_bytes()).hexdigest(),'exitCode':writer.returncode,'stdout':stdout,'stderr':stderr,'fixtureBoundary':'unchanged production script with explicit CPU-only hyprctl JSON and PNG export fixtures; real shell flock, ImageMagick and filesystem'},
    writerPixels=writer_files,batchPixels=publication,keeperNormalStop=case.keeper.ownership['terminal']['normalStop'],rendererExitCode=transport.process.returncode)
 finally:
  if permit is not None:permit.touch(exist_ok=True)
  if writer is not None and writer.poll()is None:writer.communicate(timeout=3)
  if transport is not None and not transport.closed:transport.close()
  case.tearDown()
  save('contention-replay.json',result)
 assert result['result']=='pass'
main()
