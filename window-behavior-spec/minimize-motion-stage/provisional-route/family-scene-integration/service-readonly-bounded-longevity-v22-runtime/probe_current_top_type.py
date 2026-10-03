"""CPU-only typed-current snapshot counterexample, no effects/native API."""
from pathlib import Path
import json,hashlib
import test_readonly_ipc as fixture
from readonly_ipc import validate_storage
f=fixture.ReadonlyKernelTests();f.setUp()
try:
 f.reader.epoch=False
 snapshot=f.reader.snapshot();full_error=None
 try:validate_storage(snapshot,root=f.root,environment=f.reader.issuer['environment'],guard=f.guard)
 except BaseException as e:full_error={'type':type(e).__name__,'message':str(e)}
 reply=f.query(timeout=1)
 r={'version':1,'changedField':'epoch','type':'bool','value':False,'fullHistoricalRefusal':full_error,
    'actualFreshReplyHex':reply.hex(),'freshBytesAccepted':reply==b'[]','actualPeerRequests':f.control.requests.count(b'j/clients'),
    'sourceSHA256':{n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in ['readonly_ipc.py','readonly_current.py']},
    'nativeLaunch':False,'originalQueryTimeoutSeconds':1}
 Path('current-top-typed-counterexample.json').write_text(json.dumps(r,indent=2)+'\n')
 assert full_error is not None and r['freshBytesAccepted'] and r['actualPeerRequests']==1
 print(json.dumps(r))
finally:f.reader.current.close(force=True);f.tearDown()
