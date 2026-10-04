"""Capture actual installed service definitions without activating any service."""
import hashlib,json,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from private_bus import Activations
ROOT=Path(__file__).resolve().parent;out=ROOT/('overlay-'+str(time.time_ns()));out.mkdir();runtime=private_runtime();report={'passed':False,'nativeAcceptance':False,'servicesActivated':False}
try:
 manager=Activations(runtime,out);config=manager.install();assert manager.records
 report['services']=manager.records;report['sourceConfiguration']='/usr/share/dbus-1/session.conf'
 (out/'generated-session.conf').write_bytes(config.read_bytes())
 for record in manager.records:
  assert hashlib.sha256(Path(record['source']).read_bytes()).hexdigest()==record['sourceSHA256']
  assert hashlib.sha256(Path(record['argv'][0]).read_bytes()).hexdigest()==record['binarySHA256']
 report['passed']=True
finally:
 shutil.rmtree(runtime)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'private_bus.py',ROOT/'activation-supervisor.py',ROOT/'activation_import.py']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
