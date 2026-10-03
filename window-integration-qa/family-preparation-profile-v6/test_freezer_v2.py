"""Actual complete source-only freezer regression; no native launches."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,json,stat,unittest
import native_integration as n
class FreezerV2(unittest.TestCase):
 def test_nested_retained_manifest_and_declared_modes_survive_actual_freezer(self):
  with TemporaryDirectory() as d:
   b=Path(d);(b/'payload-manifest.json').write_bytes((n.B/'payload-manifest.json').read_bytes());nested=b/'retained-baseline-v3/frozen-inputs.json';nested.parent.mkdir();nested.write_bytes((n.B/'retained-baseline-v3/frozen-inputs.json').read_bytes());nested.chmod(0o600)
   own=b/'frozen-inputs.json';own.write_text('self descriptor must be excluded')
   rows=[]
   with patch.object(n,'B',b),patch.object(n,'save',side_effect=lambda path,row:rows.append(row)),patch.object(n,'verify',side_effect=lambda:rows[0]):row=n.freeze()
   self.assertNotIn(str(own),row['inputs']);self.assertEqual(row['inputs'][str(nested)],hashlib.sha256(nested.read_bytes()).hexdigest());self.assertEqual(row['inputModes'][str(nested)],0o600)
   for packet in (n.SERVICE/'manifest-readonly-ipc-v20.json',n.QA/'family-continuous-reversal-v3/frozen-inputs.json',n.QA/'family-recovery-cancel-v1/frozen-inputs.json'):
    old=json.loads(packet.read_text())
    for name,mode in old['inputModes'].items():self.assertEqual(row['inputModes'][name],mode,name)
 def test_changed_declared_ancestral_mode_refuses_instead_of_restat_blessing(self):
  text=(n.SERVICE/'manifest-readonly-ipc-v20.json').read_text();real=json.loads;packet=real(text);name=next(iter(packet['inputModes']))
  def changed(data,*args,**kw):
   row=real(data,*args,**kw)
   if data==text:row['inputModes'][name]^=0o100
   return row
  with TemporaryDirectory() as d,patch.object(n,'B',Path(d)),patch.object(n.json,'loads',side_effect=changed),patch.object(n,'save',side_effect=AssertionError('must refuse before publishing')):
   with self.assertRaisesRegex(ValueError,'Inherited input mode changed'):n.freeze()
if __name__=='__main__':unittest.main()
