"""Preserve the exact previous case intervention and original strict oracle."""
from pathlib import Path
import unittest
B=Path(__file__).resolve().parent;OLD=B.parent/'toolkit-held-matrix-v5'
class OriginalPolicy(unittest.TestCase):
 def test_original_oracle_is_byte_identical(self):
  self.assertEqual((B/'observations.py').read_bytes(),(OLD/'observations.py').read_bytes())
 def test_controller_only_adds_retained_evidence_before_unchanged_assertion(self):
  current=(B/'held_controller.py').read_text()
  current=current.replace('import json\n','').replace('import os\n','')
  start=current.index('def retain_retirement(');end=current.index('class HeldController:',start);current=current[:start]+current[end:]
  current=current.replace("before=self.sample('before actual nonrelease interruption');before_public=copy.deepcopy(route.report['trace'][-1]['public']);current_geometry", "before=self.sample('before actual nonrelease interruption');current_geometry")
  current=current.replace('        retain_retirement(route,before,before_public,after,peer,target,ack)\n','')
  self.assertEqual(current,(OLD/'held_controller.py').read_text())
if __name__=='__main__':unittest.main()
