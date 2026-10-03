import unittest
from source_relevance import resolve_expected,selected_aliases
class ReferenceGraph(unittest.TestCase):
 def test_matching_terminal_and_intermediary_aliases(self):
  links={'/lib':'usr/lib','/usr/lib/a.so':'a.so.1','/usr/lib/a.so.1':'a.so.2','/headers/core':'core-v2'}
  selected,_=selected_aliases({'/usr/lib/a.so.2'},set(),links);self.assertEqual(selected,['/lib','/usr/lib/a.so','/usr/lib/a.so.1'])
 def test_relative_dotdot_processed_after_component_expansion(self):
  self.assertEqual(resolve_expected('/alias/../image',{'/alias':'/usr/lib'}),('/usr/image',('/alias',)))
 def test_launcher_chain_mandatory_without_map_alias(self):
  selected,_=selected_aliases({'/usr/lib/libc.so.6'},{'/usr/bin/python3'},{'/usr/bin/python3':'python3.14','/headers/only':'v3'});self.assertEqual(selected,['/usr/bin/python3'])
 def test_added_image_expands_scope(self):
  links={'/usr/lib/a.so':'a.so.1','/usr/lib/b.so':'b.so.1'}
  old,_=selected_aliases({'/usr/lib/a.so.1'},set(),links);new,_=selected_aliases({'/usr/lib/a.so.1','/usr/lib/b.so.1'},set(),links);self.assertEqual(old,['/usr/lib/a.so']);self.assertEqual(new,['/usr/lib/a.so','/usr/lib/b.so'])
 def test_noncanonical_selected_image_refuses(self):
  with self.assertRaises(ValueError):selected_aliases({'/usr/lib/a.so'},set(),{'/usr/lib/a.so':'a.so.1'})
 def test_required_launcher_cycle_refuses(self):
  with self.assertRaises(ValueError):selected_aliases(set(),{'/entry'},{'/entry':'next','/next':'entry'})
 def test_required_launcher_root_escape_refuses(self):
  with self.assertRaises(ValueError):selected_aliases(set(),{'/entry'},{'/entry':'../out'})
 def test_empty_literal_refuses_required_chain(self):
  with self.assertRaises(ValueError):selected_aliases(set(),{'/entry'},{'/entry':''})
 def test_inventory_values_are_not_live_proof(self):
  links={'/entry':'actual'};before=dict(links);self.assertEqual(resolve_expected('/entry',links),('/actual',('/entry',)));self.assertEqual(links,before)
 def test_development_alias_unrelated_to_selected_image_is_not_claimed(self):
  selected,_=selected_aliases({'/usr/bin/python3.14'},set(),{'/headers/qobject.h':'../qt/qobject.h'});self.assertEqual(selected,[])
if __name__=='__main__':unittest.main()
