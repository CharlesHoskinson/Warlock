import hashlib,json,tempfile,unittest
from pathlib import Path
import install
from control import Refused

class InstallTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.home=self.root/'user';self.home.mkdir(mode=0o700)
  (self.home/'.local/bin').mkdir(parents=True);(self.home/'.local/state').mkdir();self.source=self.root/'payload';self.source.mkdir()
  (self.source/'package.json').write_text(json.dumps(dict(packageID='sandbox-v2',productionAccepted=True,nativeAccepted=True,privateProbeAbsent=True)))
  (self.source/'control.py').write_text('print("sandbox")\n');(self.source/'launch_reader.py').write_text('print("reader sandbox")\n')
  self.closure()
 def tearDown(self):self.temp.cleanup()
 def closure(self):
  (self.source/'payload-manifest.json').write_text(json.dumps({str(p.relative_to(self.source)):install.sha(p) for p in self.source.iterdir() if p.is_file() and p.name!='payload-manifest.json'}))
 def apply(self):return install.apply(self.source,self.home,install.planned(self.source,self.home),self.home/'.local/state/omarchy-a11y')
 def test_install_and_byte_exact_guarded_rollback(self):
  launcher=self.home/'.local/bin/omarchy-orca';original=b'#!/bin/sh\n# existing user bytes\n';launcher.write_bytes(original);launcher.chmod(0o755)
  receipt=self.apply();self.assertNotEqual(launcher.read_bytes(),original)
  install.rollback(receipt);self.assertEqual(launcher.read_bytes(),original);self.assertFalse((self.home/'.local/bin/omarchy-a11y-control').exists())
  self.assertTrue((self.home/'.local/lib/omarchy-a11y/sandbox-v2').exists())
 def test_unapproved_apply_never_writes_version_or_launchers(self):
  (self.source/'package.json').write_text(json.dumps(dict(packageID='sandbox-v2',productionAccepted=False)));self.closure()
  with self.assertRaises(Refused):self.apply()
  self.assertFalse((self.home/'.local/lib').exists())
 def test_changed_prior_launcher_refuses_before_install(self):
  plan=install.planned(self.source,self.home);(self.home/'.local/bin/omarchy-orca').write_bytes(b'user changed')
  with self.assertRaises(Refused):install.apply(self.source,self.home,plan,self.home/'.local/state/omarchy-a11y')
  self.assertFalse((self.home/'.local/lib').exists())
 def test_rollback_preserves_unrelated_newer_edit(self):
  receipt=self.apply();launcher=self.home/'.local/bin/omarchy-orca';launcher.write_bytes(b'user newer')
  with self.assertRaises(Refused):install.rollback(receipt)
  self.assertEqual(launcher.read_bytes(),b'user newer');self.assertTrue((self.home/'.local/bin/omarchy-a11y-control').exists())
 def test_symlink_launcher_refused(self):
  target=self.root/'other';target.write_bytes(b'other');(self.home/'.local/bin/omarchy-orca').symlink_to(target)
  with self.assertRaises(Refused):self.apply()
  self.assertEqual(target.read_bytes(),b'other')
 def test_modified_payload_refused(self):
  (self.source/'control.py').write_bytes(b'altered')
  with self.assertRaises(Refused):self.apply()
 def test_preexisting_version_never_overwritten(self):
  receipt=self.apply();version=Path(json.loads(receipt.read_text())['version']);before=install.sha(version/'control.py')
  with self.assertRaises(Refused):self.apply()
  self.assertEqual(install.sha(version/'control.py'),before)
if __name__=='__main__':unittest.main()
