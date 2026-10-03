import tempfile,unittest
from pathlib import Path
from nss_inputs import configured_services,enumerate_modules

class NSSInputsTest(unittest.TestCase):
 def test_actions_comments_all_databases(self):
  self.assertEqual(configured_services('# comment\nhosts: resolve [!UNAVAIL=return] files dns # stop\ngroup: files [SUCCESS=merge] systemd\n'),{'hosts':['resolve','files','dns'],'group':['files','systemd']})
 def test_invalid_service_refused(self):
  for raw in ['hosts: ../outside','hosts: resolve [unfinished','hosts: files/path']:
   with self.assertRaises(RuntimeError):configured_services(raw)
 def test_empty_duplicate_or_invalid_database_refused(self):
  for raw in ['hosts:','hosts: files\nhosts: dns','broken line']:
   with self.assertRaises(RuntimeError):configured_services(raw)
 def test_configured_absent_module_refused(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'nsswitch.conf';p.write_text('hosts: resolve\n')
   with self.assertRaisesRegex(RuntimeError,'Configured NSS module absent'):enumerate_modules(p,td)
 def test_installed_extra_and_symlink_enumerated(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);config=root/'nsswitch.conf';config.write_text('hosts: resolve\n');actual=root/'actual';actual.write_bytes(b'fixture');(root/'libnss_resolve.so.2').symlink_to(actual.name);(root/'libnss_extra.so.2').write_bytes(b'extra')
   evidence,modules=enumerate_modules(config,root);self.assertEqual([p.name for p in modules],['libnss_extra.so.2','libnss_resolve.so.2']);self.assertFalse(evidence['moduleInitializationExecuted'])
 def test_actual_configured_resolve_source_enumerated_no_activation(self):
  evidence,modules=enumerate_modules('/etc/nsswitch.conf','/usr/lib');self.assertEqual(evidence['configuredModules']['resolve'],'/usr/lib/libnss_resolve.so.2');self.assertIn(Path('/usr/lib/libnss_resolve.so.2'),modules);self.assertFalse(evidence['moduleInitializationExecuted'])

if __name__=='__main__':unittest.main()
