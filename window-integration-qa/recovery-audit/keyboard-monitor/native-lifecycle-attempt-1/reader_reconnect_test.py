"""Adapter control-flow tests with doubles; not native or official-reader proof."""
import types
import unittest
from reader_reconnect import Reconnector


class Fixture:
    def __init__(self):
        self.log = []
        self.owner = ":1.9"
        self.queue = []
        self.device = types.SimpleNamespace(__gtype__=types.SimpleNamespace(name="AtspiDeviceLegacy"))
        self.ax = types.SimpleNamespace(is_active=lambda: True, get_device=lambda: self.device,
            deactivate=lambda: self.log.append("ax.deactivate"), activate=self.activate)
        self.inputs = types.SimpleNamespace(**{name:self.operation(name) for name in (
            "start_key_watcher", "stop_key_watcher", "grab_keyboard", "ungrab_keyboard",
            "pause_key_watcher", "unmap_all_modifiers")})
        self.bindings = [self.binding(i) for i in (10, 20)]
        self.command_dict = {str(i):types.SimpleNamespace(get_keybinding=lambda b=b: b,
            suspended=(i == 1)) for i,b in enumerate(self.bindings)}
        self.commands = types.SimpleNamespace(get_keyboard_commands=lambda:self.command_dict,
            set_active_commands=self.replay)
        self.modifiers = types.SimpleNamespace(remove_grabs_for_orca_modifiers=self.operation("modifier.remove"),
            refresh_orca_modifiers=self.operation("modifier.refresh"))
        self.glib = types.SimpleNamespace(idle_add=lambda fn,*a:self.queue.append((fn,a)))
        self.gio = types.SimpleNamespace(BusNameWatcherFlags=types.SimpleNamespace(NONE=0),
            bus_watch_name_on_connection=lambda *a: 7,
            bus_unwatch_name=lambda handle:self.log.append("unwatch"))
        self.adapter = Reconnector(self.ax,self.inputs,self.commands,self.modifiers,None,
                                   self.glib,self.gio).start()
        self.adapter._current_owner = lambda:self.owner

    def binding(self, grab_id):
        binding=types.SimpleNamespace(ids=[grab_id])
        def remove():
            self.log.append("binding.remove")
            binding.ids=[]
        binding.remove_grabs=remove
        return binding

    def operation(self,name):
        return lambda *a,**k:self.log.append(name)

    def activate(self):
        self.log.append("ax.activate")
        assert all(not b.ids for b in self.bindings)
        self.device.__gtype__.name="AtspiDeviceA11yManager" if self.owner else "AtspiDeviceLegacy"

    def replay(self, commands, reason):
        assert commands is self.command_dict
        self.log.append("commands.replay")

    def drain(self):
        for fn,args in list(self.queue):
            fn(*args)
        self.queue.clear()


class ReconnectTest(unittest.TestCase):
    def test_retire_ids_before_both_devices_replace(self):
        f=Fixture();f.inputs.start_key_watcher();f.adapter._changed(f.owner);f.drain()
        self.assertLess(f.log.index("binding.remove"),f.log.index("ax.activate"))
        self.assertLess(f.log.index("unmap_all_modifiers"),f.log.index("ax.activate"))
        self.assertLess(f.log.index("stop_key_watcher"),f.log.index("ax.deactivate"))
        self.assertLess(f.log.index("ax.activate"),f.log.index("modifier.refresh"))
        self.assertEqual(f.log.count("commands.replay"),1)
        self.assertTrue(f.command_dict["1"].suspended)

    def test_stale_owner_callback_does_nothing(self):
        f=Fixture();f.inputs.start_key_watcher();f.adapter._changed(":1.8")
        f.adapter._changed(f.owner);f.drain()
        self.assertEqual(f.log.count("ax.activate"),1)
        self.assertEqual(f.adapter.applied_epoch,2)

    def test_preserves_explicit_full_grab_pause_and_watcher(self):
        f=Fixture();f.inputs.start_key_watcher();f.inputs.grab_keyboard("learn")
        f.inputs.pause_key_watcher(True,"requested");f.adapter._changed(f.owner);f.drain()
        self.assertTrue(f.adapter.full_requested and f.adapter.pause_requested and f.adapter.watch_requested)
        self.assertEqual(f.log.count("grab_keyboard"),2)
        self.assertLess(f.log.index("ungrab_keyboard"),f.log.index("ax.activate"))

    def test_no_requested_watch_remains_passive(self):
        f=Fixture();f.adapter._changed(f.owner);f.drain()
        self.assertEqual(f.log,[])

    def test_duplicate_epoch_not_replayed(self):
        f=Fixture();f.inputs.start_key_watcher();f.adapter._changed(f.owner);f.drain()
        f.adapter._schedule();f.drain()
        self.assertEqual(f.log.count("ax.activate"),1)

    def test_close_invalidates_queued_callback(self):
        f=Fixture();f.inputs.start_key_watcher();f.adapter._changed(f.owner)
        f.adapter.close();f.drain()
        self.assertNotIn("ax.activate",f.log)
        self.assertEqual(f.log[-1],"unwatch")


if __name__=="__main__":
    unittest.main()
