import importlib.util,json,os,tempfile,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pin_config_candidate',B/'pin_config.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ConfigTests(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);runtime=Path(t.name);runtime.chmod(0o700);home=runtime/'private-home';home.mkdir(mode=0o700);return runtime,home
 def test_fresh_exact_reviewed_helper_and_capture_install(self):
  runtime,home=self.fixture();entries=m.install(home,runtime);self.assertEqual(m.digest(entries['entry']['path']),m.ROOT_HELPER_SHA);self.assertEqual(m.digest(entries['captureEntry']['path']),m.digest(B/'pin_capture.py'));self.assertEqual(Path(entries['entry']['path']).stat().st_mode&0o7777,0o700);self.assertEqual(Path(entries['evidenceDirectory']).stat().st_mode&0o7777,0o700);self.assertFalse(Path(entries['path']).exists())
 def test_existing_helper_never_overwritten(self):
  runtime,home=self.fixture();m.install(home,runtime)
  with self.assertRaises(ValueError):m.install(home,runtime)
 def test_named_symlink_private_path_refused(self):
  runtime,home=self.fixture();link=runtime/'linked-home';link.symlink_to(home)
  with self.assertRaises(ValueError):m.install(link,runtime)
 def test_wrong_home_mode_refused_before_entries(self):
  runtime,home=self.fixture();home.chmod(0o755)
  with self.assertRaises(ValueError):m.install(home,runtime)
  self.assertFalse((home/'.local').exists())
 def test_final_actual_process_registration_and_selected_environment(self):
  row=m.source_process(os.getpid(),{'PATH':os.environ.get('PATH')},'harness');self.assertEqual(row['identity']['pid'],os.getpid());self.assertEqual(row['argv'][0],'/usr/bin/python3');self.assertEqual(row['executable'],str(Path('/proc/self/exe').resolve()));self.assertEqual(row['environment'],{'PATH':os.environ.get('PATH')})
 def test_wrong_actual_selected_environment_refused(self):
  with self.assertRaises(ValueError):m.source_process(os.getpid(),{'PATH':'wrong-private-source'},'harness')
 def test_bool_pid_and_unknown_role_refused(self):
  with self.assertRaises(ValueError):m.source_process(True,{'PATH':os.environ.get('PATH')},'harness')
  with self.assertRaises(ValueError):m.source_process(os.getpid(),{'PATH':os.environ.get('PATH')},'foreign')
if __name__=='__main__':unittest.main(verbosity=2)
