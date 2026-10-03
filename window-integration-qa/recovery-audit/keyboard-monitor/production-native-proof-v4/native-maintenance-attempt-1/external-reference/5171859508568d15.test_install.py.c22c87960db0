import hashlib,json,stat,subprocess,tempfile,unittest
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
  (self.source/'payload-manifest.json').write_text(json.dumps({str(p.relative_to(self.source)):{'sha256':install.sha(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in self.source.iterdir() if p.is_file() and p.name!='payload-manifest.json'}))
 def apply(self):return install.apply(self.source,self.home,install.planned(self.source,self.home),self.home/'.local/state/omarchy-a11y')
 def test_install_and_byte_exact_guarded_rollback(self):
  launcher=self.home/'.local/bin/omarchy-orca';original=b'#!/bin/sh\nprintf original-launcher\n';launcher.write_bytes(original);launcher.chmod(0o700)
  receipt=self.apply();self.assertNotEqual(launcher.read_bytes(),original)
  install.rollback(receipt);self.assertEqual(launcher.read_bytes(),original);self.assertFalse((self.home/'.local/bin/omarchy-a11y-control').exists());self.assertEqual(launcher.stat().st_mode&0o7777,0o700);self.assertEqual(subprocess.check_output([str(launcher)]),b'original-launcher')
  self.assertTrue((self.home/'.local/lib/omarchy-a11y/sandbox-v2').exists())
 def test_real_executable_payload_preserves_mode_and_runs(self):
  helper=self.source/'actual-helper';helper.write_bytes(b'#!/bin/sh\nprintf payload-mode-proof\n');helper.chmod(0o755);self.closure()
  receipt=self.apply();version=Path(json.loads(receipt.read_text())['version']);installed=version/'actual-helper'
  self.assertEqual(installed.stat().st_mode&0o7777,0o755);self.assertEqual(subprocess.check_output([str(installed)]),b'payload-mode-proof')
  self.assertEqual((version/'control.py').stat().st_mode&0o7777,0o644)
  install.rollback(receipt);self.assertEqual(subprocess.check_output([str(installed)]),b'payload-mode-proof')
 def test_source_mode_drift_refused_before_mutation(self):
  (self.source/'control.py').chmod(0o755)
  with self.assertRaises(Refused):self.apply()
  self.assertFalse((self.home/'.local/lib').exists())
 def test_unsafe_payload_mode_refused_before_mutation(self):
  for mode in (0o777,0o4755,0o2755,0o1755):
   with self.subTest(mode=oct(mode)):
    (self.source/'control.py').chmod(mode);self.closure()
    with self.assertRaises(Refused):self.apply()
    self.assertFalse((self.home/'.local/lib').exists())
 def test_changed_installed_launcher_mode_refuses_rollback(self):
  receipt=self.apply();launcher=self.home/'.local/bin/omarchy-orca';launcher.chmod(0o700)
  with self.assertRaises(Refused):install.rollback(receipt)
  self.assertEqual(launcher.stat().st_mode&0o7777,0o700)
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
