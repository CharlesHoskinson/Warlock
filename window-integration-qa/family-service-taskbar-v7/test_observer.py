from pathlib import Path
import hashlib,json,tempfile,unittest,os
from unittest.mock import patch
from service_observer import ObservedFactory
class RetentionTests(unittest.TestCase):
 def setup_capture(self,folder):
  root=Path(folder)/'actor';root.mkdir(mode=0o700);evidence=Path(folder)/'evidence';evidence.mkdir(mode=0o700)
  path=root/'0123456789ab-1.png';pixels=b'\x89PNG\r\n\x1a\n'+b'real-test-bytes'*4;path.write_bytes(pixels);path.chmod(0o600)
  source={'path':str(path),'digest':hashlib.sha256(pixels).hexdigest(),'captureEpoch':path.stem,'sceneToken':'abcdef012345-1','stableId':'18000000','pid':42,'pixels':[1,1]}
  factory=object.__new__(ObservedFactory);factory.evidence_root=evidence;factory.observed_sources=[];factory.observed_controllers=[];factory.observed_retirements=[]
  import threading
  factory.source_lock=threading.Lock();return factory,root,path,source,pixels
 def test_actual_bytes_retained_after_release(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder);before=dict(source);factory.retain_source(1,root,source);path.unlink();row=factory.observed_sources[0];self.assertEqual(Path(row['retainedPath']).read_bytes(),pixels);self.assertEqual(row['sha256'],source['digest']);self.assertEqual(source,before)
 def test_named_path_swap_after_read_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder);real=os.fstat;calls=0
   def changed(descriptor):
    nonlocal calls
    calls+=1;value=real(descriptor)
    if calls==2:
     temporary=root/'replacement';temporary.write_bytes(pixels);temporary.chmod(0o600);temporary.replace(path)
    return value
   with patch('service_observer.os.fstat',side_effect=changed),self.assertRaisesRegex(ValueError,'changed'):factory.retain_source(1,root,source)
   self.assertEqual(factory.observed_sources,[])
 def test_observation_delegates_capture_once_returns_same_object(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder)
   from types import SimpleNamespace
   desktop=SimpleNamespace(root=root);calls=[]
   def capture(*args,**kwargs):calls.append((args,kwargs));return source
   desktop.capture_source=capture;transport=SimpleNamespace(process=SimpleNamespace(pid=os.getpid()),bind_controller=lambda controller:None);factory.observed_transports=[]
   with patch('service_observer.native_runtime.NativeFactory.__call__',return_value=(desktop,transport)):
    returned,unused=factory(1);actual=returned.capture_source('window','token',0)
   self.assertIs(actual,source);self.assertEqual(len(calls),1);self.assertEqual(len(factory.observed_sources),1)
 def test_binding_delegate_and_return_preserved_outside_product_registry(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder)
   from types import SimpleNamespace
   sentinel=object();calls=[];controller=object()
   def original(value):calls.append(value);return sentinel
   desktop=SimpleNamespace(root=root,capture_source=lambda:source)
   transport=SimpleNamespace(process=SimpleNamespace(pid=os.getpid()),bind_controller=original)
   factory.observed_transports=[]
   with patch('service_observer.native_runtime.NativeFactory.__call__',return_value=(desktop,transport)):
    factory(7)
   self.assertIs(transport.bind_controller(controller),sentinel)
   self.assertEqual(calls,[controller]);self.assertEqual(factory.observed_controllers,[(7,controller)])
 def test_normal_retirement_observed_after_original_registry_removal(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder)
   from types import SimpleNamespace
   desktop=SimpleNamespace(root=root);transport=SimpleNamespace(closed=True,process=SimpleNamespace(poll=lambda:0))
   controller=SimpleNamespace(transport=transport);factory.observed_controllers=[(7,controller)];factory.desktops=[desktop]
   path.unlink();root.rmdir();sentinel=object();calls=[]
   def retire(number,value):calls.append((number,value));factory.desktops.remove(value);return sentinel
   with patch('service_observer.native_runtime.NativeFactory.retired',side_effect=retire):
    self.assertIs(factory.retired(7,desktop),sentinel)
   self.assertEqual(calls,[(7,desktop)]);self.assertEqual(factory.desktops,[])
   self.assertTrue(factory.observed_retirements[0]['actorDirectoryGone']);self.assertTrue(factory.observed_retirements[0]['productRegistryRemoved'])
   self.assertEqual(factory.observed_controllers,[(7,controller)])
 def test_wrong_digest_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder);source['digest']='0'*64
   with self.assertRaisesRegex(ValueError,'digest'):factory.retain_source(1,root,source)
   self.assertEqual(factory.observed_sources,[])
 def test_foreign_actor_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder)
   with self.assertRaisesRegex(ValueError,'actor root'):factory.retain_source(1,root/'different',source)
 def test_unsafe_permissions_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder);path.chmod(0o644)
   with self.assertRaisesRegex(ValueError,'Unsafe'):factory.retain_source(1,root,source)
 def test_wrong_epoch_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   factory,root,path,source,pixels=self.setup_capture(folder);source['captureEpoch']='0123456789ab-2'
   with self.assertRaisesRegex(ValueError,'epoch'):factory.retain_source(1,root,source)
if __name__=='__main__':unittest.main()
