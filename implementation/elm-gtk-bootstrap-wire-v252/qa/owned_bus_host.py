"""Fresh private activation wrapper around byte-preserved owning compositor host."""
import time
from private_bus import Activations
from activation_import import identity

def derivative(host):
 class BusHost(host.ReviewedWestonHost):
  def launch(self,name,command,env=None):
   if name=='privateBus':
    if command!=['/usr/bin/dbus-daemon','--session','--nofork','--address='+self.env['DBUS_SESSION_BUS_ADDRESS']]:raise RuntimeError('original private bus invocation required')
    self.activations=Activations(self.runtime,self.output)
    config=self.activations.install()
    command=['/usr/bin/dbus-daemon','--config-file='+str(config),'--nofork','--address='+self.env['DBUS_SESSION_BUS_ADDRESS']]
    self.evidence['privateActivationOverlay']={'configuration':str(config),'installedServiceFilesChanged':False,'supervisedRealExec':True}
   return super().launch(name,command,env)
  def close(self):
   if not self.runtime:return
   activation_error=None
   try:
    if hasattr(self,'activations') and hasattr(self.activations,'busrow'):
     self.evidence['privateActivationCleanup']=self.activations.close(time.monotonic()+3)
     self.evidence['privateActivationCleanupPassed']=True
   except BaseException as error:
    activation_error=repr(error);self.evidence['privateActivationCleanupError']=activation_error;self.evidence['privateActivationCleanupPassed']=False
   # Keep inherited unexpected-descendant detection active, including every failure.
   super().close()
   if activation_error:raise RuntimeError('private activation cleanup failed: '+activation_error)
 class BusSession(host.PrivateHyprSession):
  def __init__(self,*args,**kwargs):
   super().__init__(*args,**kwargs);self.host=BusHost(*args[:4],**{k:v for k,v in kwargs.items() if k in ('dri_prime','mesa_vendor')});self.evidence=self.host.evidence
  def __enter__(self):
   result=super().__enter__()
   try:
    deadline=time.monotonic()+3
    row=next(row for _,row in self.host.processes if row['name']=='privateBus')
    self.host.activations.connect(identity(row['pid']),deadline)
    # Activation runs inside the nested child, never the outer parent display.
    selected={k:self.env[k] for k in ('WAYLAND_DISPLAY','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE','XDG_CONFIG_HOME','XDG_DATA_HOME','HOME')}
    self.host.activations.call('UpdateActivationEnvironment',(selected,),'(a{ss})',deadline)
    self.evidence['privateActivationEnvironment']=selected
    return result
   except BaseException:
    self.host.close();raise
 return BusSession
