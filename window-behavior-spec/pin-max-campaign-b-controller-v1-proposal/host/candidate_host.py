"""Exact V2 owning host; B adds separate observational producer classification."""
from pathlib import Path
import importlib.util,sys
B=Path(__file__).resolve().parent.parent
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
sys.path.insert(0,str(V2/'proposed'))
try:
 spec=importlib.util.spec_from_file_location('_b_exact_v2_candidate_host',V2/'proposed/candidate_host.py')
 accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
finally:sys.path.pop(0)
from b_closure import BClosureMixin
original=accepted.original;CORE=accepted.CORE;AQ=accepted.AQ

class ReviewedWestonHost(BClosureMixin,accepted.ReviewedWestonHost):
 def launch(self,name,command,env=None):
  if name=='hyprland':
   import pair_binding
   pair_binding.read_pair(B/'PAIR_READY.json')
  # Inherited exact V2 core/env selectors and original stop/wait stay unchanged.
  return super().launch(name,command,env)

class PrivateHyprSession(accepted.PrivateHyprSession):
 def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
  super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
  self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
  self.evidence=self.host.evidence
