"""Observation-only error boundary/API dispatch, not reader compatibility proof."""
import ast,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
class Object:
 path='/own/peer';app=types.SimpleNamespace(bus_name=':own')
 def get_name(self):return 'Rename'
 def get_role_name(self):return 'text'
 def get_accessible_id(self):return 'own-edit'
 def get_application(self):return types.SimpleNamespace(get_name=lambda:'copied-files')
 def get_text_iface(self):raise AssertionError('Accessible.get_text alias must never be used')
class AdapterTest(unittest.TestCase):
 def method(self):
  p=Path(__file__).parent/'reader-profile/data/orca/orca-customizations.py';node=next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='describe');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-private-describe','exec'),ns);return ns['describe']
 def test_exact_explicit_interface_call_and_core_identity(self):
  calls=[];obj=Object();fake=types.SimpleNamespace(Text=types.SimpleNamespace(get_character_count=lambda o:11,get_text=lambda o,start,end:(calls.append((o,start,end)) or 'sandbox.txt')))
  with patch.dict(sys.modules,{'gi.repository':types.SimpleNamespace(Atspi=fake)}):result=self.method()(obj)
  self.assertEqual(calls,[(obj,0,11)]);self.assertEqual(result['text'],'sandbox.txt');self.assertEqual(result['name'],'Rename');self.assertEqual(result['object_path'],'/own/peer')
 def test_optional_text_error_cannot_erase_reader_focus_identity(self):
  def fail(*args):raise RuntimeError('optional query failed')
  fake=types.SimpleNamespace(Text=types.SimpleNamespace(get_character_count=lambda o:11,get_text=fail))
  with patch.dict(sys.modules,{'gi.repository':types.SimpleNamespace(Atspi=fake)}):result=self.method()(Object())
  self.assertEqual(result['name'],'Rename');self.assertEqual(result['role'],'text');self.assertIn('text_error',result);self.assertNotIn('error',result)
if __name__=='__main__':unittest.main()
