"""Byte inverses for the source-only QML additions; no Qt execution claim."""
import ast,unittest
from pathlib import Path
from selection import B,COMPOSITION
class Inverse(unittest.TestCase):
 def test_entire_pin_menu_except_exact_diagnostics(self):
  tree=ast.parse((B/'observe_frontend.py').read_text());constants=[]
  for node in ast.walk(tree):
   if isinstance(node,ast.Assign)and any(isinstance(x,ast.Name)and x.id in ('added','extra')for x in node.targets)and isinstance(node.value,ast.Constant)and isinstance(node.value.value,str):constants.append(node.value.value)
  actual=(B/'frontend-observation/PinWindowMenu.qml').read_text();actual=actual.replace('    property var retirementObservations: []\n    property bool retirementObservationLost: false\n','',1)
  for text in constants:
   if text in actual:actual=actual.replace(text,'',1)
  self.assertEqual(actual,(COMPOSITION/'frontend/PinWindowMenu.qml').read_text())
 def test_entire_windows_except_fixed_negative_ipc(self):
  actual=(B/'frontend-observation/Windows.qml').read_text();addition='    function pinTypedRetirementRefusal(kind:string):string { return JSON.stringify(pinMenu.observeTypedRetirementRefusal(kind)) }\n';self.assertEqual(actual.count(addition),1);self.assertEqual(actual.replace(addition,'',1),(COMPOSITION/'frontend/Windows.qml').read_text())
 def test_selected_probe_byte_inverse(self):
  self.assertEqual((B/'native-probe/probe.cpp').read_bytes(),(COMPOSITION/'native-probe/probe.cpp').read_bytes())
if __name__=='__main__':unittest.main()
