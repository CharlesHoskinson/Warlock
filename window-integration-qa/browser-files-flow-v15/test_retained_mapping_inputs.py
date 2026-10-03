import base64,copy,hashlib,json,os,stat,tempfile,unittest
from pathlib import Path
from retained_mapping_inputs import enumerate_inputs,from_packet
B=Path(__file__).resolve().parent
def sample(raw):return [{'processes':[{'identity':{'pid':11,'start':'31'},'maps':raw.decode(),'rawMapsBase64':base64.b64encode(raw).decode(),'rawMapsBytes':len(raw),'rawMapsSHA256':hashlib.sha256(raw).hexdigest(),'lifetimeBefore':True,'lifetimeAfter':True}]}]
class RetainedMappingInputsTest(unittest.TestCase):
 def test_all_actual_missing_paths_match_root_exact_list(self):
  value=from_packet(B);root=json.loads((B/'retained-v6-failure/root-mapping-attribution.json').read_text());self.assertEqual(sorted(r['path'] for r in value['missingStableInputs']),root['missingStableDiskPaths']);self.assertEqual(len(value['missingStableInputs']),32);self.assertEqual(len(value['deletedMappings']),2);self.assertFalse(value['priorMappingAccepted']);self.assertFalse(value['newDataAuthorityGranted'])
 def test_raw_hash_change_refused(self):
  value=sample(b'');value[0]['processes'][0]['rawMapsSHA256']='0'*64
  with self.assertRaisesRegex(RuntimeError,'bytes/hash/decode'):enumerate_inputs(value,{},'/owned/runtime')
 def test_raw_decoded_text_change_refused(self):
  value=sample(b'');value[0]['processes'][0]['maps']='other'
  with self.assertRaisesRegex(RuntimeError,'bytes/hash/decode'):enumerate_inputs(value,{},'/owned/runtime')
 def test_read_error_or_stale_lifetime_refused(self):
  for mutation in [{'readError':{'errno':13}},{'lifetimeAfter':False}]:
   value=sample(b'');value[0]['processes'][0].update(mutation)
   with self.assertRaisesRegex(RuntimeError,'Incomplete'):enumerate_inputs(value,{},'/owned/runtime')
 def test_deleted_and_anonymous_retained_never_seeded(self):
  raw=b'1000-2000 r-xp 0 00:21 5 /usr/lib/unknown.so (deleted)\n2000-3000 r--p 0 00:01 4 /memfd:data (deleted)\n';value=enumerate_inputs(sample(raw),{},'/owned/runtime');self.assertEqual(len(value['deletedMappings']),1);self.assertEqual(len(value['anonymousMappings']),1);self.assertFalse(value['missingStableInputs'])
 def test_missing_non_system_path_refused(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'code';p.write_bytes(b'fixture');raw=f'1000-2000 r--p 0 00:21 {p.stat().st_ino} {p}\n'.encode()
   with self.assertRaisesRegex(RuntimeError,'non-system'):enumerate_inputs(sample(raw),{},'/owned/runtime')
 def test_changed_frozen_mode_refused(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'code';p.write_bytes(b'fixture');raw=f'1000-2000 r--p 0 00:21 {p.stat().st_ino} {p}\n'.encode();expected={str(p):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':0}}
   with self.assertRaisesRegex(RuntimeError,'already-frozen'):enumerate_inputs(sample(raw),expected,'/owned/runtime')
 def test_changed_mapped_inode_refused(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'code';p.write_bytes(b'fixture');raw=f'1000-2000 r--p 0 00:21 {p.stat().st_ino+1} {p}\n'.encode()
   with self.assertRaisesRegex(RuntimeError,'inode/type'):enumerate_inputs(sample(raw),{},'/owned/runtime')
if __name__=='__main__':unittest.main()
