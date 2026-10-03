"""Actual file/mode fixtures for output exclusion and retained descriptor closure."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,tempfile,unittest
MODULE=Path(__file__).with_name('freeze_bounded.py')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ClosureTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.b=self.root/'stage';self.old=self.root/'v21';self.design=self.root/'design'
  for p in (self.b,self.old,self.design):p.mkdir()
  spec=importlib.util.spec_from_file_location('fixture_bounded_freezer',MODULE);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.m.B=self.b;self.m.V21=self.old;self.m.DESIGN=self.design
  self.m.READY21=self.old/'ready.json';self.m.DESIGN_READY=self.design/'ready.json';self.m.MANIFEST=self.b/'manifest-readonly-bounded-v22.json';self.m.CHECKPOINT=self.b/'checkpoint-readonly-bounded-v22.json'
  provider=self.old/'closure_tools/freeze_longevity.py';provider.parent.mkdir();provider.write_text("def inventory():return {'inputs':{},'inputModes':{},'links':{}}\n")
  self.nested=self.old/'retained-baseline-v3/frozen-inputs.json';self.nested.parent.mkdir();self.nested.write_text('{"retained":true}\n');self.nested.chmod(0o600)
  self.m.READY21.write_text(json.dumps({'localSources':{str(p):{'sha256':digest(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in (provider,self.nested)}}))
  self.m.DESIGN_READY.write_text(json.dumps({'localSources':{}}));self.m.READY21_SHA=digest(self.m.READY21);self.m.DESIGN_READY_SHA=digest(self.m.DESIGN_READY)
  original={}
  for n in ('readonly_ipc.py','test_readonly_longevity.py'):
   (self.old/n).write_text('original\n');(self.b/n).write_text('changed\n');original[n]={'sha256':digest(self.old/n),'mode':0o644}
  (self.b/'runtime-authorized-provenance.json').write_text(json.dumps({'inheritedTopSources':original}))
  (self.b/'bounded-source-typed-final-offline-checkpoint.json').write_text(json.dumps({'pythonTests':388,'quintNamedScenarios':383,'quintModels':33,'sourceUnchangedDuringProof':True,'sourceSHA256':{}}))
 def tearDown(self):self.temp.cleanup()
 def test_nested_manifest_included_with_declared_bytes_and_mode(self):
  packet=self.m.inventory();key=str(self.nested)
  self.assertEqual(packet['inputs'][key],digest(self.nested));self.assertEqual(packet['inputModes'][key],0o600)
 def test_only_own_root_descriptors_are_excluded(self):
  for p in (self.m.MANIFEST,self.m.CHECKPOINT):p.write_text('root output\n')
  nested=self.b/'retained/frozen-inputs.json';nested.parent.mkdir();nested.write_text('nested retained\n');nested.chmod(0o600)
  packet=self.m.inventory();self.assertIn(str(nested),packet['inputs']);self.assertEqual(packet['inputModes'][str(nested)],0o600)
  self.assertNotIn(str(self.m.MANIFEST),packet['inputs']);self.assertNotIn(str(self.m.CHECKPOINT),packet['inputs'])
 def test_declared_ancestral_mode_change_refuses(self):
  self.nested.chmod(0o644)
  with self.assertRaisesRegex(ValueError,'declared source mode replaced'):self.m.inventory()
 def test_exclusive_publication_refuses_replacement(self):
  target=self.b/'exclusive.json';self.m.exclusive(target,{'original':True});before=target.read_bytes()
  self.assertEqual(stat.S_IMODE(target.stat().st_mode),0o600)
  with self.assertRaises(FileExistsError):self.m.exclusive(target,{'replaced':True})
  self.assertEqual(target.read_bytes(),before)
if __name__=='__main__':unittest.main(verbosity=2)
