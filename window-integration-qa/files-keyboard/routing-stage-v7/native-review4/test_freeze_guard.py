import json,tempfile,unittest
from pathlib import Path
from freeze_guard import digest,verify_manifest,prepare_attempt
class FrozenAttemptTest(unittest.TestCase):
 def setup_stage(self,p):
  for name in ['home','state','reader-profile/data/orca']: (p/name).mkdir(parents=True)
  (p/'home/alpha').write_bytes(b'sandbox real bytes')
  (p/'state/dashboard.json').write_text(json.dumps({'pins':[str(p/'home')]}))
  profile=p/'reader-profile/data/orca/orca-customizations.py';profile.write_text('# frozen observation only\n')
  (p/'frozen-inputs.json').write_text(json.dumps({'files':[{'path':str(profile),'sha256':digest(profile)}]}))
  return profile
 def test_exclusive_private_attempt_and_mutable_sandbox(self):
  with tempfile.TemporaryDirectory() as t:
   stage=Path(t);self.setup_stage(stage);out=prepare_attempt(stage,stage/'attempt-one')
   self.assertEqual(out.stat().st_mode&0o777,0o700)
   self.assertEqual((out/'frozen-command.json').stat().st_mode&0o777,0o600)
   self.assertEqual(json.loads((out/'state/dashboard.json').read_text())['pins'],[str(out/'home')])
   (out/'home/alpha').rename(out/'home/renamed')
   self.assertTrue(verify_manifest(out/'executed-inputs.json'))
   with self.assertRaises(FileExistsError):prepare_attempt(stage,out)
 def test_frozen_profile_and_actual_executed_copy_reject_change(self):
  with tempfile.TemporaryDirectory() as t:
   stage=Path(t);profile=self.setup_stage(stage);out=prepare_attempt(stage,stage/'attempt-one')
   (out/'reader-profile/data/orca/orca-customizations.py').write_text('# changed\n')
   self.assertFalse(verify_manifest(out/'executed-inputs.json',False))
   profile.write_text('# changed shared source\n')
   with self.assertRaises(AssertionError):verify_manifest(stage/'frozen-inputs.json')
 def test_persistent_catalog_difference_remains_failed(self):
  import preservation
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'catalog';p.write_bytes(b'changed')
   report=preservation.settle_catalogs({str(p):b'before'},seconds=0)
   self.assertFalse(report[str(p)]['exactBytes']);self.assertEqual(p.read_bytes(),b'changed')
if __name__=='__main__':unittest.main()
