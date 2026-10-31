#!/usr/bin/env python3
import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('checker',Path(__file__).with_name('check-site.py')); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Checks(unittest.TestCase):
 def run_case(self,html,files=None):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'index.html').write_text(html)
   for name,content in (files or {}).items():
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
   c=mod.Check(root,'/Warlock/');c.run();return c.errors
 def test_reviewed_dynamic_reference(self):
  script='fetch(path)'; entry={'source':'script.js','sourceSha256':hashlib.sha256(script.encode()).hexdigest(),'assets':['data.json'],'review':'Fixed local asset'}
  files={'script.js':script,'data.json':'{}','metadata/dynamic-assets.json':json.dumps({'references':[entry]})}
  self.assertFalse(self.run_case('',files))
  files['script.js']='fetch(other)'
  self.assertTrue(self.run_case('',files))
  files['script.js']=script;del files['data.json']
  self.assertTrue(self.run_case('',files))
 def test_fragment(self):self.assertTrue(self.run_case('<a href="#missing">x</a>'))
 def test_css_import(self):self.assertTrue(self.run_case('<link href="x.css" rel="stylesheet">',{'x.css':'@import "missing.css";'}))
 def test_srcset(self):self.assertTrue(self.run_case('<img srcset="ok.png 1x, missing.png 2x">',{'ok.png':''}))
 def test_escape(self):self.assertTrue(self.run_case('<a href="../outside">x</a>'))
 def test_case(self):self.assertTrue(self.run_case('<img src="image.png">',{'Image.png':''}))
 def test_query_and_hash(self):self.assertFalse(self.run_case('<a href="page.html?q=x#ok">x</a>',{'page.html':'<h1 id="ok">Hello</h1>'}))
 def test_catalog_hash(self):self.assertFalse(self.run_case('<a href="reference/catalog/v6/index.html#component/native-fallback">x</a>',{'reference/catalog/v6/index.html':'<h1>Catalog</h1>'}))
 def test_catalog_suffix(self):self.assertTrue(self.run_case('<a href="reference/catalog/v6/index.html#component/menu/unknown/extra">x</a>',{'reference/catalog/v6/index.html':'<h1>Catalog</h1>'}))
 def test_catalog_section(self):self.assertTrue(self.run_case('<a href="reference/catalog/v6/index.html#component/menu/unknown">x</a>',{'reference/catalog/v6/index.html':'<h1>Catalog</h1>'}))
 def test_external(self):self.assertTrue(self.run_case('<script src="https://example.com/x.js"></script>'))
 def test_scenario(self):self.assertTrue(self.run_case('<a href="test-drive/index.html?scenario=bad">x</a>',{'test-drive/index.html':''}))
if __name__=='__main__':unittest.main()
