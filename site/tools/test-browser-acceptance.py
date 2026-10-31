#!/usr/bin/env python3
import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('acceptance',Path(__file__).with_name('browser-acceptance.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Acceptance(unittest.TestCase):
 def test_negative_results(self):
  self.assertTrue(m.evaluate_result('settings','operation unsupported',None,False))
  self.assertTrue(m.evaluate_result('settings','scenario timed out',None,False))
  self.assertTrue(m.evaluate_result('settings','', 'system',False))
  self.assertTrue(m.evaluate_result('transfer','',None,False))
  self.assertTrue(m.evaluate_result('settings','','settings',True,False))
 def test_every_scenario_has_a_specific_entry_probe(self):
  self.assertEqual(set(m.SCENARIOS),set(m.ACTIONS))
  self.assertEqual(m.ACTIONS['transfer'],('popup','overview:destination:2'))
  self.assertEqual(m.ACTIONS['launcher'],('field','control:search'))
 def test_browser_gate_requires_every_engine(self):
  self.assertFalse(m.browser_failed([{'result':'PASS'}]))
  self.assertTrue(m.browser_failed([{'result':'PASS'},{'result':'NOT RUN'}]))
  self.assertTrue(m.browser_failed([{'result':'FAIL'}]))
 def test_good_mode(self):self.assertIsNone(m.evaluate_result('settings','','settings',True))
 def test_jump_and_behavior(self):
  self.assertEqual(m.MODES['application-actions'], 'jump')
  self.assertTrue(m.evaluate_result('application-actions','','jump',False))
  self.assertIsNone(m.evaluate_result('application-actions','','jump',True))
if __name__=='__main__':unittest.main()
