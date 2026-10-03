from pathlib import Path
import hashlib,json,os,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');sys.path.insert(0,str(B))
import service_observer,module_binding as binding
from test_batch_binding import BatchBindingKernelTests
fixture=BatchBindingKernelTests();rows=[]
for symbol,replacement in [('stage','finish'),('finish','stage'),('discard','require_releasable'),('require_releasable','discard'),('require_disposable','require_idle')]:
 fixture.setUp()
 try:
  with fixture.package()as(factory,initial,destination,digest):
   fixture.bound(factory,initial,destination,digest);desktop,transport,controller=fixture.genuine_actor(factory)
   original=getattr(desktop.preview_batch,symbol);foreign=getattr(desktop.preview_batch,replacement);setattr(desktop.preview_batch,symbol,foreign)
   try:raw=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json');accepted=raw['usable'];error=None
   except BaseException as failure:accepted=False;error=dict(type=type(failure).__name__,message=str(failure));raw=json.loads((destination/'actor.json').read_text())
   assert original.__func__ is not foreign.__func__
   rows.append(dict(symbol=symbol,replacement=replacement,originalFunctionID=id(original.__func__),actualFunctionID=id(foreign.__func__),accepted=accepted,error=error,raw=raw))
 finally:fixture.tearDown()
row=dict(result='concrete missing initial callback identity guard'if any(r['accepted']for r in rows)else'no counterexample',scope=scope,collector=str(B),sourceSHA256=hashlib.sha256((B/'module_binding.py').read_bytes()).hexdigest(),cases=rows,nativeLaunch=False,candidateEdited=False,scopeLimit='Owned CPU RuntimeLease/reader/actor fixture, initial real frozen-method replacement before actual linked_actor; no timing/native feature conclusion')
p=Path(__file__).with_name('initial-callback-counterexample.json')
with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k!='cases'}));print(json.dumps([dict(symbol=r['symbol'],replacement=r['replacement'],accepted=r['accepted'])for r in rows]))
