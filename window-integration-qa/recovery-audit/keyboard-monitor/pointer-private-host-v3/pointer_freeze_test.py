"""Fresh attempt/hash/mode gates; no compositor or application launch."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import native_probe_pointer as runner

class FreezeTest(unittest.TestCase):
 def fixture(self,root):
  content=b'frozen actual executable bytes'
  source=root/'native-input';source.write_bytes(content);source.chmod(0o755)
  manifest={'dependencies':{'native-input':hashlib.sha256(content).hexdigest()},'externalDependencies':{}}
  (root/'pointer-frozen-stage-report.json').write_text(json.dumps(manifest))
  return source
 def test_exact_copy_mode_and_exclusive_attempt(self):
  with tempfile.TemporaryDirectory() as directory:
   stage=Path(directory);source=self.fixture(stage);attempt=stage/'native-pointer-attempt-test'
   with patch.object(runner,'STAGE',stage),patch.object(runner,'HERE',stage),patch.object(runner,'LIB',source),patch.object(runner,'REPORT',stage/'report'):
    runner.freeze_attempt(attempt)
    self.assertEqual((attempt/'native-input').read_bytes(),source.read_bytes())
    self.assertEqual(attempt.stat().st_mode&0o777,0o700)
    self.assertEqual((attempt/'native-input').stat().st_mode&0o777,0o700)
    self.assertEqual((attempt/'frozen-command.json').stat().st_mode&0o777,0o600)
    command=json.loads((attempt/'frozen-command.json').read_text())
    self.assertEqual(command['command'][-1],str(attempt))
    with self.assertRaises(FileExistsError):runner.freeze_attempt(attempt)
    self.assertEqual((attempt/'native-input').read_bytes(),source.read_bytes())
 def test_changed_actual_source_rejected_before_attempt_creation(self):
  with tempfile.TemporaryDirectory() as directory:
   stage=Path(directory);source=self.fixture(stage);source.write_bytes(b'changed')
   attempt=stage/'native-pointer-attempt-test'
   with patch.object(runner,'STAGE',stage):
    with self.assertRaises(AssertionError):runner.freeze_attempt(attempt)
   self.assertFalse(attempt.exists())
 def test_changed_external_loader_link_rejected_before_attempt_creation(self):
  with tempfile.TemporaryDirectory() as directory:
   stage=Path(directory);self.fixture(stage)
   link=stage/'libaquamarine.so';link.symlink_to('unexpected-library.so')
   manifest_path=stage/'pointer-frozen-stage-report.json'
   manifest=json.loads(manifest_path.read_text());manifest['externalSymlinks']={str(link):'reviewed-library.so'}
   manifest_path.write_text(json.dumps(manifest));attempt=stage/'native-pointer-attempt-test'
   with patch.object(runner,'STAGE',stage):
    with self.assertRaises(AssertionError):runner.freeze_attempt(attempt)
   self.assertFalse(attempt.exists())

if __name__=='__main__':unittest.main()
