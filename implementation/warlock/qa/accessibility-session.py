"""Reviewed AT opt-in for the original private, nonactivating session host.

No user bus, default system bus, installed activation directories or desktop
services are admitted. The additional AT bus has an explicit owned listener.
"""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from isolation import directory, no_activation_xml, Refused
from session_bus import bus_xml
from system_isolation import supply, validate


def isolate_session_host(host):
    parent = host.ReviewedWestonHost

    class AccessiblePrivateHost(parent):
        def launch(self, name, command, env=None):
            env = supply(self.env if env is None else env, self.runtime)
            validate(env, self.runtime)
            env.update(GIO_USE_VFS='local', GSETTINGS_BACKEND='memory', GTK_USE_PORTAL='0')
            address = env.get('AT_SPI_BUS_ADDRESS')
            if address is None:
                env.update(GTK_A11Y='none', NO_AT_BRIDGE='1')
            else:
                if address != 'unix:path=' + str(directory(self.runtime) / 'a11y-bus'):
                    raise Refused('AT bus must be the exact owned private listener')
                env.pop('GTK_A11Y', None)
                env.pop('NO_AT_BRIDGE', None)
            if name in ('privateBus', 'accessibility-bus'):
                runtime = directory(self.runtime)
                if name == 'privateBus':
                    address = self.env['DBUS_SESSION_BUS_ADDRESS']
                    xml = bus_xml(runtime, address)
                    filename = 'session-no-activation.conf'
                else:
                    root = ET.fromstring(no_activation_xml(os.getuid()))
                    ET.SubElement(root, 'listen').text = address
                    xml = ET.tostring(root, encoding='unicode')
                    filename = 'a11y-no-activation.conf'
                config = runtime / filename
                fd = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, 'w') as stream:
                    stream.write(xml)
                    stream.flush()
                    os.fsync(stream.fileno())
                command = ['/usr/bin/dbus-daemon', '--nofork', '--config-file=' + str(config), '--address=' + address]
                self.evidence.update(sessionActivationDisabled=True, sessionListenerOwned=True)
                if name == 'accessibility-bus':
                    self.evidence.update(accessibilityActivationDisabled=True, accessibilityListenerOwned=True)
            return super().launch(name, command, env)

    host.ReviewedWestonHost = AccessiblePrivateHost
