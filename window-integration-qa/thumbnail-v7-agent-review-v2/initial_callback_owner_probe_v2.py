from pathlib import Path
import hashlib,json,os,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');sys.path.insert(0,str(B))
import service_observer,module_binding as binding
from test_batch_binding import BatchBindingKernelTests
from batch_preview import BatchPreviews
fixture=BatchBindingKernelTests();rows=[]
for symbol in ('batch.stage','desktop.finish_capture_previews'):
 fixture.setUp()
 try:
  with fixture.package()as(factory,initial,destination,digest):
   fixture.bound(factory,initial,destination,digest);desktop,transport,controller=fixture.genuine_actor(factory)
   if symbol=='batch.stage':
    original=desktop.preview_batch.stage;other=BatchPreviews(desktop.root.with_name('other-actor'),desktop.preview_batch.preview,desktop.commands);foreign=other.stage;desktop.preview_batch.stage=foreign
   else:
    original=desktop.finish_capture_previews;other=object.__new__(type(desktop));other.__dict__.update(desktop.__dict__);foreign=other.finish_capture_previews;desktop.finish_capture_previews=foreign
   assert original.__func__ is foreign.__func__ and original.__self__ is not foreign.__self__
   try:raw=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json');accepted=raw['usable'];error=None
   except BaseException as failure:accepted=False;error=dict(type=type(failure).__name__,message=str(failure));raw=json.loads((destination/'actor.json').read_text())
   rows.append(dict(symbol=symbol,exactExpectedFunction=True,expectedOwnerID=id(original.__self__),actualOwnerID=id(foreign.__self__),accepted=accepted,error=error,raw=raw))
 finally:fixture.tearDown()
row=dict(result='concrete missing initial callback owner guard'if any(r['accepted']for r in rows)else'no counterexample',scope=scope,collector=str(B),sourceSHA256=hashlib.sha256((B/'module_binding.py').read_bytes()).hexdigest(),cases=rows,nativeLaunch=False,candidateEdited=False)
p=Path(__file__).with_name('initial-callback-owner-counterexample.json')
with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps([dict(symbol=r['symbol'],accepted=r['accepted'])for r in rows]))
