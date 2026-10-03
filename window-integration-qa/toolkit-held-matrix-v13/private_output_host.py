"""Owned output budget only; exact selected reviewed host otherwise inherited."""
from pathlib import Path
import importlib.util,time
from types import SimpleNamespace
QA=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('_held_output_accepted_aq_v4',QA/'private-weston-aq-host-v4/weston_host.py')
accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
original=accepted.original

def adapt(selected):
 if selected.original.__file__!=original.__file__:raise RuntimeError('Exact reviewed common host API required')
 class OutputWestonHost(selected.ReviewedWestonHost):
  def launch(self,name,command,env=None):
   result=super().launch(name,command,env)
   if name=='hyprland':
    launch_returned=time.monotonic()
    self.evidence['browserStartupBudget']={'launchReturnedMonotonic':launch_returned,'deadlineMonotonic':launch_returned+15,'seconds':15,'origin':'same actual child launch return before inherited original15s instance discovery starts','pid':result.pid}
   return result
 class PrivateHyprSession(selected.PrivateHyprSession):
  def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
   super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
   self.host=OutputWestonHost(output,main_env,width,height,dri_prime,mesa_vendor);self.evidence=self.host.evidence
 return SimpleNamespace(PrivateHyprSession=PrivateHyprSession,ReviewedWestonHost=OutputWestonHost,original=selected.original)
