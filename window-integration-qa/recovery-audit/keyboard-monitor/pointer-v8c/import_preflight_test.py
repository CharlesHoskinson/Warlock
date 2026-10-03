import hashlib,shutil,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import native_probe_pointer as runner
class Imports(unittest.TestCase):
 def copied(self,root):
  fixture=root/'native-fixture';fixture.mkdir();source=Path(__file__).resolve().parent/'native-fixture'
  for name in ('pointer_cases.py','popup_geometry.py'):shutil.copy2(source/name,fixture/name)
  return fixture
 def test_exact_runner_owned_copied_import_without_fixture_search_path(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);fixture=self.copied(root);poison=types.ModuleType('popup_geometry');poison.ready_popup=lambda row:False
   with patch.dict(sys.modules,{'popup_geometry':poison}),patch.object(sys,'path',[p for p in sys.path if 'native-fixture' not in p]):
    result=runner.import_preflight(root);cases=runner.load_cases(root)
   self.assertTrue(result['pass_']);self.assertEqual(result['helper'],str(fixture/'popup_geometry.py'))
   self.assertEqual(result['helperSHA256'],hashlib.sha256((fixture/'popup_geometry.py').read_bytes()).hexdigest())
   row=dict(nativeMapped=True,centerPickedButton='Actual popup target A',position=[75,-42],surfaceTransform=[0,0],button=dict(x=12,y=11,width=186,height=34),popoverAllocation=[210,68],buttonAllocation=[186,34])
   self.assertEqual(cases.popup_target({'at':[96,120]},row),(276,106))
 def test_missing_copied_helper_refused_before_native(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);fixture=self.copied(root);(fixture/'popup_geometry.py').unlink()
   with patch.object(runner,'execute',side_effect=AssertionError('native must not run')) as native:
    with self.assertRaises(AssertionError):runner.import_preflight(root)
    native.assert_not_called()
 def test_symlink_helper_refused(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);fixture=self.copied(root);helper=fixture/'popup_geometry.py';helper.rename(root/'other.py');helper.symlink_to(root/'other.py')
   with self.assertRaises(AssertionError):runner.import_preflight(root)
if __name__=='__main__':unittest.main()
