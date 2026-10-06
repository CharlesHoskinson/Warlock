"""Fresh677 launch refinement of frozen669 policy: mandatory owned listener.
Only the private session bus launch changes; no installed service directories,
systemd broker, user-bus forwarding or main configuration is included.
"""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from isolation import directory,no_activation_xml,Refused

def bus_xml(runtime,address):
    runtime=directory(runtime)
    if type(address) is not str or address!='unix:path='+str(runtime/'bus'):raise Refused('exact original private session address')
    root=ET.fromstring(no_activation_xml(os.getuid()))
    ET.SubElement(root,'listen').text=address
    return ET.tostring(root,encoding='unicode')

def isolate_session_host(host):
    parent=host.ReviewedWestonHost
    class ActivationFreeHost(parent):
        def launch(self,name,command,env=None):
            from system_isolation import supply,validate
            env=supply(self.env if env is None else env,self.runtime);validate(env,self.runtime)
            env.update(GIO_USE_VFS='local',GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
            if name=='privateBus':
                runtime=directory(self.runtime);config=runtime/'session-no-activation.conf'
                xml=bus_xml(runtime,self.env['DBUS_SESSION_BUS_ADDRESS'])
                fd=os.open(config,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                with os.fdopen(fd,'w') as out:
                    os.fchmod(out.fileno(),0o600);out.write(xml);out.flush();os.fsync(out.fileno())
                command=['/usr/bin/dbus-daemon','--nofork','--config-file='+str(config),'--address='+self.env['DBUS_SESSION_BUS_ADDRESS']]
                self.evidence.update(sessionActivationDisabled=True,sessionListenerOwned=True)
            return super().launch(name,command,env)
    host.ReviewedWestonHost=ActivationFreeHost
