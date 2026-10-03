from pathlib import Path
import unittest,xml.etree.ElementTree as ET
from unittest.mock import patch
from private_bus_host import BUS_TEMPLATE,bus_command
class PrivateBus(unittest.TestCase):
 def test_no_activation_paths(self):
  root=ET.fromstring(BUS_TEMPLATE.replace('@PRIVATE_BUS_ADDRESS@','unix:path=/owned/bus'))
  self.assertEqual(root.findtext('type'),'session');self.assertEqual(root.findtext('auth'),'EXTERNAL')
  self.assertFalse(any(x.tag in {'include','includedir','servicedir','standard_session_servicedirs','standard_system_servicedirs','servicehelper'} for x in root.iter()))
 def test_exact_owned_command(self):
  root=Path('/owned');address='unix:path=/owned/bus'
  with patch('private_bus_host.original.qa.verify_runtime',return_value=root):
   self.assertEqual(bus_command(['/usr/bin/dbus-daemon','--session','--nofork','--address='+address],root,address,root/'browser-session-bus.conf'),['/usr/bin/dbus-daemon','--config-file=/owned/browser-session-bus.conf','--nofork','--address='+address])
 def test_foreign_command_refused(self):
  with self.assertRaises(RuntimeError):bus_command(['/usr/bin/dbus-daemon','--system'],Path('/owned'),'unix:path=/owned/bus',Path('/owned/browser-session-bus.conf'))
 def test_foreign_socket_refused(self):
  root=Path('/owned');address='unix:path=/main/bus'
  with patch('private_bus_host.original.qa.verify_runtime',return_value=root):
   with self.assertRaises(RuntimeError):bus_command(['/usr/bin/dbus-daemon','--session','--nofork','--address='+address],root,address,root/'browser-session-bus.conf')
 def test_foreign_config_refused(self):
  root=Path('/owned');address='unix:path=/owned/bus'
  with patch('private_bus_host.original.qa.verify_runtime',return_value=root):
   with self.assertRaises(RuntimeError):bus_command(['/usr/bin/dbus-daemon','--session','--nofork','--address='+address],root,address,Path('/foreign/browser-session-bus.conf'))
if __name__=='__main__':unittest.main(verbosity=2)
