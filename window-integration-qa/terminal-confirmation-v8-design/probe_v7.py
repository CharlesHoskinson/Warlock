import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');sys.path.insert(0,str(B))
import service_observer
import test_actual_binding as tests
import module_binding as binding
O=Path(__file__).parent/'actual-v7-counterexample-v1';O.mkdir(mode=0o700)
t=tests.OwnerKernelTests();t.setUp()
try:
 with t.package() as (factory,initial,destination,digest):
  t.bound(factory,initial,destination,digest)
  t.handler=lambda c,d:c.sendall(b'[{')
  try:t.query()
  except ValueError:pass
  else:raise AssertionError('real query must be refused')
  journal=t.store.read();journal['helperOwnership']={'keeper':{'servicePID':os.getpid(),'serviceStart':tests.service_runtime.process_start(os.getpid()),'rootIdentity':list(t.lease.root_identity)}};t.store.write(journal);t.lease.close()
  service=type('CpuTerminal',(),{'lease':t.lease,'store':t.store,'closed':True,'failure':None})()
  modules=binding._observe('terminal',previous=initial)
  try:binding.archive_final(factory,service,destination/'actual-terminal-binding.json',modules)
  except ValueError:pass
  else:raise AssertionError('refused query cannot grant acceptance')
  raw=json.loads((destination/'actual-terminal-binding.json').read_text());confirm=json.loads((destination/'actual-terminal-binding-confirmation.json').read_text())
  assert raw['errors']==[{'type':'ValueError','message':'complete closed actual query proof required'}]
  assert any(e['type']=='UnboundLocalError' for e in confirm['errors'])
  row={'result':'counterexample reproduced','nativeLaunch':False,'actualKernelQueryOutcome':t.reader.snapshot()['history'][-1]['outcome'],'raw':raw,'confirmation':confirm,'sourceSHA256':hashlib.sha256((B/'module_binding.py').read_bytes()).hexdigest()}
  with (O/'counterexample.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  print(json.dumps({'result':row['result'],'rawErrors':raw['errors'],'confirmationErrors':confirm['errors']}))
finally:t.tearDown()
