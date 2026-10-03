import base64,json,tempfile,unittest
from pathlib import Path
from mapping_evidence import capture,validate
from runtime_inputs import mapping_authority

class MappingEvidenceTest(unittest.TestCase):
 def identities(self):return [{'pid':11,'start':'31'},{'pid':12,'start':'32'}]
 def test_all_snapshots_before_authority(self):
  reads=[];batch=capture(self.identities(),lambda r:True,lambda pid:reads.append(pid) or b'raw\n','phase')
  self.assertFalse(batch['validationStarted'])
  def authority(raw):self.assertEqual(reads,[11,12]);return {'frozenFiles':{}}
  validate(batch,lambda r:True,authority);self.assertTrue(batch['accepted'])
 def test_missing_closure_full_raw_batch_durable_before_error(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);disk=root/'code.so';disk.write_bytes(b'fixture');raw=f'1000-2000 r-xp 0 00:00 {disk.stat().st_ino} {disk}\n'.encode()
   batch=capture(self.identities(),lambda r:True,lambda pid:raw,'missing');p=root/'saved.json';p.write_text(json.dumps(batch));p.chmod(0o600)
   def authority(raw):
    self.assertEqual(len(json.loads(p.read_text())['processes']),2)
    return mapping_authority(raw,{},root/'runtime',[])
   with self.assertRaisesRegex(RuntimeError,'absent from frozen closure'):validate(batch,lambda r:True,authority)
   self.assertTrue(all(r['maps'] and r['validationError'] and not r['accepted'] for r in batch['processes']))
   self.assertFalse(batch['accepted'])
 def test_unreadable_live_retained_other_snapshots(self):
  def read(pid):
   if pid==11:raise PermissionError(13,'denied')
   return b'other\n'
  batch=capture(self.identities(),lambda r:True,read,'denied');self.assertEqual(batch['processes'][1]['maps'],'other\n')
  with self.assertRaisesRegex(RuntimeError,'unreadable'):validate(batch,lambda r:True,lambda raw:{})
  self.assertEqual(batch['processes'][0]['readError']['errno'],13);self.assertTrue(batch['processes'][1]['accepted'])
 def test_missing_live_refused(self):
  def read(pid):raise FileNotFoundError(2,'gone')
  batch=capture(self.identities(),lambda r:True,read,'missing')
  with self.assertRaisesRegex(RuntimeError,'unreadable'):validate(batch,lambda r:True,lambda raw:{})
 def test_missing_exited_during_observation_normal(self):
  calls={}
  def same(r):calls[r['pid']]=calls.get(r['pid'],0)+1;return calls[r['pid']]==1
  def read(pid):raise FileNotFoundError(2,'gone')
  batch=capture(self.identities(),same,read,'normal exit');validate(batch,same,lambda raw:self.fail('no maps'))
  self.assertTrue(batch['accepted']);self.assertTrue(all(r['exitedDuringObservation'] for r in batch['processes']))
 def test_successful_read_lifetime_changed_refused(self):
  calls={}
  def same(r):calls[r['pid']]=calls.get(r['pid'],0)+1;return calls[r['pid']]==1
  batch=capture(self.identities(),same,lambda pid:b'raw','race')
  with self.assertRaisesRegex(RuntimeError,'during capture'):validate(batch,same,lambda raw:{})
  self.assertTrue(all(r['maps']=='raw' for r in batch['processes']))
 def test_lifetime_changed_during_validation_refused(self):
  batch=capture(self.identities(),lambda r:True,lambda pid:b'raw','race')
  with self.assertRaisesRegex(RuntimeError,'during validation'):validate(batch,lambda r:False,lambda raw:{})
  self.assertFalse(batch['accepted'])
 def test_invalid_utf8_raw_bytes_retained_refused(self):
  batch=capture(self.identities(),lambda r:True,lambda pid:b'\xff\x00','invalid')
  self.assertEqual(base64.b64decode(batch['processes'][0]['rawMapsBase64']),b'\xff\x00')
  with self.assertRaisesRegex(RuntimeError,'unreadable'):validate(batch,lambda r:True,lambda raw:{})
 def test_exited_before_observation_never_read(self):
  batch=capture(self.identities(),lambda r:False,lambda pid:self.fail('stale PID read'),'exited');validate(batch,lambda r:False,lambda raw:self.fail('stale validation'))
  self.assertTrue(all(r['exitedBeforeObservation'] for r in batch['processes']))
 def test_each_validation_failure_retained(self):
  batch=capture(self.identities(),lambda r:True,lambda pid:str(pid).encode(),'two errors')
  def authority(raw):raise RuntimeError('error '+raw)
  with self.assertRaisesRegex(RuntimeError,'error 11'):validate(batch,lambda r:True,authority)
  self.assertEqual([r['validationError']['error'] for r in batch['processes']],['error 11','error 12'])

if __name__=='__main__':unittest.main()
