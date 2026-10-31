#!/usr/bin/env python3
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('contracts',Path(__file__).with_name('check-contracts.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Contracts(unittest.TestCase):
 def test_invalid_inputs_fail(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/'assets/shared').mkdir(parents=True);(root/'test-drive/scenarios').mkdir(parents=True);(root/'metadata').mkdir()
   (root/'assets/shared/routes.json').write_text(json.dumps({'routes':[{'path':'index.html'}]}))
   (root/'test-drive/scenarios/taskbar.json').write_text(json.dumps({'id':'wrong'}))
   (root/'package-manifest.json').write_text(json.dumps({'package':'T10','assets':[{'destination':'assets/shared/foreign.css'}]}))
   (root/'metadata/dynamic-assets.json').write_text(json.dumps({'references':[{'source':'missing.js','assets':['../escape']}]}))
   errors,_,_,_=m.validate(root); text='\n'.join(errors)
   for expected in ('incomplete route metadata','invalid scenario schema','asset missing source','outside T10 ownership','missing or escaped dynamic asset','missing mandatory artifact'):self.assertIn(expected,text)
 def test_canonical_preview_import(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); runtime=root/'test-drive/runtime'; (runtime/'theme').mkdir(parents=True)
   (runtime/'popup.html').write_text('<link href="theme/preview.css">')
   (runtime/'theme/preview.css').write_text('copy')
   self.assertEqual(len(m.canonical_stylesheet_errors(root)),3)
   (runtime/'theme/preview.css').unlink()
   (runtime/'popup.html').write_text('<link href="../../design/previews-snap/preview.css">')
   self.assertEqual(m.canonical_stylesheet_errors(root),[])
 def test_disjoint_ownership(self):
  for path,owner in [('test-drive/stage/index.js','T06'),('test-drive/host/index.js','T07'),('test-drive/previews/index.js','T08'),('test-drive/scenarios/index.js','T09'),('components/files/index.html','T04'),('components/taskbar/index.html','T03')]:self.assertEqual(m.owner_of(path),owner)
 def test_altered_bundle(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/'test-drive/stage').mkdir(parents=True)
   (root/'test-drive/stage/source.elm').write_text('source')
   (root/'test-drive/stage/bundle.js').write_text('altered')
   import hashlib
   h=lambda x:hashlib.sha256(x.encode()).hexdigest()
   (root/'test-drive/stage/package-manifest.json').write_text(json.dumps({'package':'T06','assets':[],'build':{'source':'test-drive/stage/source.elm','source_sha256':h('source'),'bundle':'test-drive/stage/bundle.js','bundle_sha256':h('original'),'compiler':'Elm','command':'elm make'}}))
   errors,*_=m.validate(root);self.assertTrue(any('build hash mismatch' in e for e in errors))
if __name__=='__main__':unittest.main()
