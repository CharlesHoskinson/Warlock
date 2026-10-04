import ast,json,os,tempfile,threading,unittest
from pathlib import Path
import phase_trace as t
class TraceTest(unittest.TestCase):
 def tearDown(self):t.active=None
 def test_bounded_private_publication(self):
  t.active=t.Trace(2)
  for _ in range(4):t.active.emit('query','observed')
  with tempfile.TemporaryDirectory() as root:
   p=Path(root)/'trace.json';t.active.publish(p);data=json.loads(p.read_text())
   self.assertEqual(len(data['records']),2);self.assertEqual(data['dropped'],2);self.assertEqual(p.stat().st_mode&0o777,0o600)
   with self.assertRaises(FileExistsError):t.active.publish(p)
 def test_reject_permissions_and_symlink(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root);path.chmod(0o755)
   with self.assertRaises(ValueError):t.Trace().publish(path/'x')
   path.chmod(0o700);(path/'link').symlink_to(path,target_is_directory=True)
   with self.assertRaises(ValueError):t.Trace().publish(path/'link'/'x')
 def test_exception_preserves_lock_and_semantics(self):
  t.active=t.Trace();lock=threading.RLock()
  with self.assertRaisesRegex(RuntimeError,'fixture'):
   with t.measured_lock(lock,'capture_lock'):raise RuntimeError('fixture')
  self.assertTrue(lock.acquire(blocking=False));lock.release()
  self.assertIn('error',[r['status'] for r in t.active.records]);self.assertEqual(t.active.records[0]['phase'],'capture_lock_wait')
 def test_call_preserves_kwargs_and_return_without_recording_payload(self):
  t.active=t.Trace();secret='private fixture pixels'
  self.assertEqual(t.measured_call('helper',lambda argv,**kw:kw['payload'],['grim',secret],payload=secret),secret)
  self.assertNotIn(secret,json.dumps(t.active.records));self.assertEqual(t.active.records[0]['phase'],'capture_helper')
 def test_labels_distinguish_queue_and_receipt(self):
  t.active=t.Trace();t.observed_command({'command':'seed'});t.observed_event({'event':'seeded'});t.observed_event({'event':'presented'});t.observed_event({'event':'private-title'})
  labels=[r['phase'] for r in t.active.records]
  self.assertEqual(labels,['renderer_seed_queued','renderer_seeded_receipt','renderer_presented_receipt','renderer_other_receipt'])
 def test_disabled_does_not_read_clock(self):
  from unittest.mock import patch
  with patch.object(t.time,'monotonic_ns',side_effect=AssertionError('disabled clock')):
   self.assertEqual(t.measured_call('query',lambda:17),17)
 def test_derivatives_parse_and_original_hashes_hold(self):
  import hashlib
  root=Path(__file__).parent;manifest=json.loads((root/'source-manifest.json').read_text())
  for row in manifest['files']:
   ast.parse((root/row['name']).read_text());self.assertEqual(hashlib.sha256((Path(manifest['original_root'])/row['name']).read_bytes()).hexdigest(),row['original_sha256'])
if __name__=='__main__':unittest.main()
