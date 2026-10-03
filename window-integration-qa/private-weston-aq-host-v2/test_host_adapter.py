import unittest
from unittest.mock import patch
from pathlib import Path
import weston_host as h

class ChildOnly(unittest.TestCase):
    def make(self):return h.ReviewedWestonHost(Path('/unused'),{},320,240)
    def test_only_child_gets_private_library(self):
        host=self.make();host.evidence['privateAquamarine']={}
        env={'LD_LIBRARY_PATH':'/original','AQ_BACKENDS':'wayland'}
        with patch.object(h,'verify_inputs'),patch.object(h.original.PrivateWestonHost,'launch',return_value='child') as launch:
            self.assertEqual(host.launch('hyprland',['/usr/bin/Hyprland','--config','/private.lua'],env),'child')
        self.assertEqual(env['LD_LIBRARY_PATH'],'/original')
        self.assertEqual(launch.call_args.args[2]['LD_LIBRARY_PATH'],str(h.AQ/'prefix/lib')+':/original')
        self.assertEqual(launch.call_args.args[2]['AQ_BACKENDS'],'wayland')
    def test_weston_and_bus_keep_original_env(self):
        host=self.make();env={'LD_LIBRARY_PATH':'/weston'}
        for name in ('weston','privateBus'):
            with patch.object(h,'verify_inputs',side_effect=AssertionError('child-only')),patch.object(h.original.PrivateWestonHost,'launch') as launch:
                host.launch(name,['unchanged'],env)
            self.assertIs(launch.call_args.args[2],env)
    def test_changed_manifest_refuses_before_process(self):
        host=self.make()
        with patch.object(h,'verify_inputs',side_effect=RuntimeError('changed')),patch.object(h.original.PrivateWestonHost,'launch',side_effect=AssertionError('must not launch')):
            with self.assertRaises(RuntimeError):host.launch('hyprland',['/usr/bin/Hyprland'],{})
    def test_nonreviewed_child_refused(self):
        host=self.make()
        with patch.object(h,'verify_inputs'),patch.object(h.original.PrivateWestonHost,'launch',side_effect=AssertionError('must not launch')):
            with self.assertRaises(RuntimeError):host.launch('hyprland',['/other/Hyprland'],{})
    def test_constructor_has_no_side_effects(self):
        with patch.object(h.original.subprocess,'Popen',side_effect=AssertionError('no launch')):
            session=h.PrivateHyprSession(Path('/unused'),{},320,240,b'-- config')
        self.assertIsInstance(session.host,h.ReviewedWestonHost)
    def test_settings_isolation_leaves_caller_environment_unchanged(self):
        original={'GSETTINGS_BACKEND':'dconf','HOME':'/main'}
        host=h.ReviewedWestonHost(Path('/unused'),original,320,240)
        self.assertEqual(original,{'GSETTINGS_BACKEND':'dconf','HOME':'/main'})
        self.assertEqual(host.main_env['GSETTINGS_BACKEND'],'memory')
        self.assertEqual(host.evidence['privateSettingsBackend'],'memory')

if __name__=='__main__':unittest.main()
