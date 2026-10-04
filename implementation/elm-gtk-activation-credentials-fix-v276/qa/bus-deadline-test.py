"""Actual silent private UNIX bus rejects authentication inside original deadline."""
import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from private_bus import Activations,Refused
from activation_import import identity
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('bus-deadline-'+str(time.time_ns()));OUT.mkdir();runtime=private_runtime();proc=None;report={'passed':False,'nativeAcceptance':False,'silentActualUnixPeerOnly':True}
try:
 source=OUT/'silent-peer.py';source.write_text('''import socket,sys,time
s=socket.socket(socket.AF_UNIX);s.bind(sys.argv[1]);s.listen();connections=[]
while True:connections.append(s.accept()[0])
''')
 with (OUT/'stdout').open('wb') as out,(OUT/'stderr').open('wb') as err:
  proc=subprocess.Popen([sys.executable,'-B',str(source),str(runtime/'bus')],stdout=out,stderr=err,start_new_session=True)
  readiness=time.monotonic()+1
  while not (runtime/'bus').exists():assert time.monotonic()<readiness and proc.poll() is None;time.sleep(.01)
  manager=Activations(runtime,OUT);started=time.monotonic();deadline=started+.2
  try:manager.connect(identity(proc.pid),deadline)
  except Refused as error:report['refused']=repr(error)
  else:raise AssertionError('silent authentication must refuse')
  elapsed=time.monotonic()-started;assert elapsed<.8 and manager.connection is None
  report['elapsed']=elapsed;report['deadlineBudget']=.2;report['passed']=True
finally:
 if proc and proc.poll() is None:proc.terminate();report['helperExitCode']=proc.wait(timeout=1)
 shutil.rmtree(runtime)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'private_bus.py',ROOT/'activation-supervisor.py']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
