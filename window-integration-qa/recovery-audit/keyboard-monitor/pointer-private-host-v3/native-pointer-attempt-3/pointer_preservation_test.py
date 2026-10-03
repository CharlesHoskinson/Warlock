import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import lifecycle_preservation as p

class PreservationTests(unittest.TestCase):
 def test_client_full_projection_and_set(self):
  base={'address':'0x1','stableId':'a','pid':2,'at':[1,2],'size':[3,4]}
  expected=p.project_clients([base])
  for field,value in [('workspace',{'id':9}),('pinned',True),('fullscreen',1),('fullscreenClient',2),('tags',['x']),('grouped',['0x2']),('floating',True),('monitor',3)]:
   self.assertNotEqual(expected,p.project_clients([{**base,field:value}]),field)
  self.assertNotEqual(expected,p.project_clients([base,{**base,'stableId':'b'}]))
 def test_order_independent_exact_output_set(self):
  rows=[{'name':'left','x':0},{'name':'right','x':100}]
  self.assertEqual(p.project_outputs(rows),p.project_outputs(rows[::-1]))
  self.assertNotEqual(p.project_outputs(rows),p.project_outputs([{**rows[0],'scale':1.5},rows[1]]))
 def test_catalog_backup_private_exact_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);out=root/'out';out.mkdir();catalog=root/'.config/omarchy';catalog.mkdir(parents=True)
   (catalog/p.CATALOG_NAMES[0]).write_bytes(b'private\x00bytes')
   rows=p.backup_catalogs(out,root);destination=out/'catalog-before.json'
   self.assertEqual(destination.stat().st_mode & 0o777,0o600)
   saved=json.loads(destination.read_text());self.assertEqual(len(saved),4)
   import base64
   self.assertEqual(base64.b64decode(saved[str(catalog/p.CATALOG_NAMES[0])]['base64']),b'private\x00bytes')
   self.assertTrue(p.settle_catalogs(rows,seconds=0)[str(catalog/p.CATALOG_NAMES[0])]['exactBytes'])
   (catalog/p.CATALOG_NAMES[0]).write_bytes(b'changed')
   self.assertFalse(p.settle_catalogs(rows,seconds=0)[str(catalog/p.CATALOG_NAMES[0])]['exactBytes'])
   self.assertEqual((catalog/p.CATALOG_NAMES[0]).read_bytes(),b'changed')
   with self.assertRaises(FileExistsError):p.backup_catalogs(out,root)
 def test_files_hashes_pid_and_hidden_are_observations(self):
  pid=os.getpid()
  def command(*args):
   if 'list' in args:return json.dumps([{'pid':pid,'id':'original'}])
   return json.dumps({'state':{'view':'home'},'uiState':{'visible':False,'selection':['kept']},'migrationStatus':{'ready':True,'pid':pid,'instance':'original'}}[args[-1]])
  with patch.object(p,'command',side_effect=command):
   before=p.files_state(Path('/unused'));self.assertFalse(before['visible']);self.assertEqual(before['pid'],pid)
   self.assertEqual(before,p.files_state(Path('/unused')))
if __name__=='__main__':unittest.main()
