#!/usr/bin/env python3
"""Root-only pure fixed-profile controls; no compiler or target execution."""
import ast,importlib.util,json,sys,unittest
from pathlib import Path
QA,RUNNER,REPO=map(Path,sys.argv[1:4]);sys.argv=[sys.argv[0],*sys.argv[4:]]
sys.path.insert(0,str(REPO/'window-integration-qa'))
spec=importlib.util.spec_from_file_location('watch_qa',QA);qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa);qa.REPO=REPO
class FixedProtocolWatchAdmission(unittest.TestCase):
 def test_exact_literal_mode(self):self.assertTrue(qa.window_watch_protocol_mode(REPO/qa.WINDOW_WATCH_PROTOCOL_RUNNER,['protocol','--manifest-sha256','a'*64],'a'*64))
 def test_other_runner_and_modes_refuse(self):
  for runner,args in [(REPO/'tools/other.py',['protocol','--manifest-sha256','a'*64]),(REPO/qa.WINDOW_WATCH_PROTOCOL_RUNNER,['elm','--manifest-sha256','a'*64]),(REPO/qa.WINDOW_WATCH_PROTOCOL_RUNNER,['protocol','--manifest-sha256','a'*64,'--inside-private','/tmp']), (REPO/qa.WINDOW_WATCH_PROTOCOL_RUNNER,['protocol','--manifest-sha256','b'*64])]:self.assertFalse(qa.window_watch_protocol_mode(runner,args,'a'*64))
 def test_fixed_record_and_both_targets_in_source(self):
  text=RUNNER.read_text();self.assertIn('warlock-protocol:test:window-watch-boundary-controls',text);self.assertIn('warlock-runtime:lib:warlock-runtime',text);self.assertIn("choices=('protocol',)",text)
 def test_no_old_mode_functions_changed(self):
  self.assertEqual(qa.menu_tab_dom_mode(REPO/'tools/check_elm_cpu.py',['--menu-tab-dom','--arm64']),True);self.assertFalse(qa.menu_tab_dom_mode(REPO/'tools/check_elm_cpu.py',['--protocol']))
 def test_protocol_body_retains_exact_case_inventory_and_pass_sentinel(self):
  text=RUNNER.read_text();self.assertIn("[name for name, _ in cases] != data['haskellNames']",text);self.assertIn('window-watch-protocol:29-controls:PASS',text);self.assertIn('code != 0 or not all_pass',text)
 def test_current_cache_and_normal_custody_still_used(self):
  text=RUNNER.read_text();self.assertIn('build.verify_inputs(data)',text);self.assertIn('build.require_group_absent(child)',text);self.assertIn('core.current_selection(record, state',text);self.assertIn("timeout=302 if window_watch_protocol",QA.read_text());self.assertIn("p.resolve()!=p",QA.read_text())
if __name__=='__main__':unittest.main()
