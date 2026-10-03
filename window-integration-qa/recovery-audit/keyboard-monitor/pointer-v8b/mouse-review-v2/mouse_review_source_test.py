"""Offline source-method tests, not a native Orca/AT-SPI claim.

Extracts the actual changed MouseReviewer methods. Controlled collaborators
make lifecycle consequences observable without importing or enabling a reader.
"""
from __future__ import annotations
import ast
from collections import deque
from pathlib import Path
from types import SimpleNamespace as NS
import time
import unittest

SOURCE = Path(__file__).parent / 'orca-compat/orca/mouse_review.py'

class Item:
    def __init__(self, *args, obj=None, **kwargs):
        self.obj, self.when = obj, time.time()
    def get_object(self): return self.obj
    def get_time(self): return self.when

class Device:
    def __init__(self, capable=True, error=False):
        self.capable, self.error = capable, error
        self.handlers, self.next_id, self.calls = {}, 1, []
    def get_capabilities(self): return 0
    def set_capabilities(self, caps):
        self.calls.append(caps)
        if self.error: raise RuntimeError('controlled capability failure')
        return caps if self.capable else 0
    def connect(self, signal, callback):
        key=self.next_id; self.next_id+=1
        self.handlers[key]=callback; return key
    def disconnect(self, key): del self.handlers[key]
    def emit(self, obj):
        for callback in list(self.handlers.values()): callback(self, obj, 1.5, 2.75)

def reviewer(device):
    cls = next(n for n in ast.parse(SOURCE.read_text()).body
               if isinstance(n, ast.ClassDef) and n.name=='MouseReviewer')
    names={'__init__','_get_setting','_register_dbus_commands','refresh_device',
           'activate','deactivate','get_current_item','get_is_enabled',
           'set_is_enabled','toggle','_on_pointer_moved','_process_event'}
    cls.decorator_list=[]
    cls.body=[n for n in cls.body if not isinstance(n, (ast.FunctionDef,ast.AsyncFunctionDef))
              or n.name in names]
    for n in cls.body:
        if isinstance(n,ast.FunctionDef): n.decorator_list=[]
    registry=NS(enabled=False)
    registry.layered_lookup=lambda *a,**k: registry.enabled
    registry.set_runtime_value=lambda schema,key,value: setattr(registry,'enabled',value)
    controller=NS(registrations=[])
    controller.register_decorated_module=lambda name,obj: controller.registrations.append((name,obj))
    scheduled=[]
    debug=NS(LEVEL_WARNING=1,LEVEL_INFO=2,print_exception=lambda *a:None,
             print_message=lambda *a:None,print_tokens=lambda *a:None)
    ns={'deque':deque,'time':time,'_ItemContext':Item,'debug':debug,
        'Atspi':NS(Device=Device,DeviceCapability=NS(POINTER_MONITOR=1),get_version=lambda:(2,60,6),
                   EventListener=NS(new=lambda callback:NS())),
        'ax_device_manager':NS(get_manager=lambda:NS(activate=lambda:None,get_device=lambda:device)),
        'gsettings_registry':NS(get_registry=lambda:registry),
        'dbus_service':NS(get_remote_controller=lambda:controller),
        'focus_manager':NS(get_manager=lambda:NS(get_locus_of_focus=lambda:None)),
        'GLib':NS(timeout_add=lambda delay,fn,*args: scheduled.append((fn,args))),
        'messages':NS(MOUSE_REVIEW_ENABLED='on',MOUSE_REVIEW_DISABLED='off'),
        'presentation_manager':NS(get_manager=lambda:NS(present_message=lambda msg:None))}
    cls.body=[n for n in cls.body if not isinstance(n, ast.Assign)
              or all(not isinstance(t,ast.Name) or t.id not in {'_SCHEMA','KEY_PRESENT_TOOLTIPS','KEY_ENABLED'} for t in n.targets)] + [
        ast.parse("_SCHEMA='mouse-review'\nKEY_ENABLED='enabled'").body[0],
        ast.parse("KEY_ENABLED='enabled'").body[0]]
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),cls],type_ignores=[])
    exec(compile(ast.fix_missing_locations(module),str(SOURCE),'exec'),ns)
    # The unrelated deprecated listener is required only as an event-listener
    # constructor callback. It is never used in this AT-SPI lifecycle trial.
    ns['MouseReviewer']._listener=lambda *a:None
    r=ns['MouseReviewer']()
    r._on_mouse_moved=lambda obj,x,y:setattr(r,'_current_mouse_over',Item(obj=obj))
    return r,registry,controller,scheduled

class SourceTests(unittest.TestCase):
    def test_default_and_true_false(self):
        d=Device();r,s,c,q=reviewer(d)
        self.assertFalse(r.get_is_enabled());self.assertIsNone(r.get_current_item())
        self.assertTrue(r.set_is_enabled(True));self.assertTrue(r._active)
        self.assertEqual(len(d.handlers),1)
        d.emit('actual-test-item');q.pop(0)[0](r._device_epoch)
        self.assertEqual(r.get_current_item(),'actual-test-item')
        self.assertTrue(r.set_is_enabled(False));self.assertFalse(r._active)
        self.assertEqual(len(d.handlers),0);self.assertIsNone(r.get_current_item())
    def test_toggle_and_activation_idempotence(self):
        d=Device();r,s,c,q=reviewer(d)
        r.toggle(None,notify_user=False);r.activate();r.activate()
        self.assertEqual(len(d.handlers),1);self.assertTrue(r.get_is_enabled())
        r.toggle(None,notify_user=False)
        self.assertFalse(r.get_is_enabled());self.assertEqual(len(d.handlers),0)
    def test_enabled_replacement_uses_same_actual_argument(self):
        old=Device();r,s,c,q=reviewer(old);r.set_is_enabled(True)
        new=Device();self.assertTrue(r.refresh_device(new))
        self.assertEqual(len(old.handlers),0);self.assertEqual(len(new.handlers),1)
        self.assertEqual(new.calls,[1]);self.assertIs(r._device,new)
        self.assertTrue(r.get_is_enabled());self.assertEqual(len(c.registrations),1)
    def test_disabled_replacement_passive(self):
        r,s,c,q=reviewer(Device());new=Device();r.refresh_device(new)
        self.assertEqual(len(new.handlers),0);self.assertFalse(r._active)
    def test_backend_loss_and_return_preserve_request(self):
        r,s,c,q=reviewer(Device());r.set_is_enabled(True)
        self.assertFalse(r.refresh_device(None));self.assertTrue(r.get_is_enabled())
        self.assertFalse(r._active);self.assertIsNone(r.get_current_item())
        new=Device();r.refresh_device(new)
        self.assertTrue(r._active);self.assertEqual(len(new.handlers),1)
    def test_initial_unsupported_backend_registers_on_recovery(self):
        r,s,c,q=reviewer(Device(False));self.assertEqual(c.registrations,[])
        self.assertTrue(r.refresh_device(Device()))
        self.assertEqual(len(c.registrations),1);self.assertIs(c.registrations[0][1],r)
        r.refresh_device(Device());self.assertEqual(len(c.registrations),1)
    def test_old_device_and_timeout_cannot_consume_new_queue(self):
        old=Device();r,s,c,q=reviewer(old);r.set_is_enabled(True);old.emit('old')
        fn,args=q.pop(0);new=Device();r.refresh_device(new);new.emit('new')
        r._on_pointer_moved(old,'late-old',0,0);self.assertEqual(len(r._event_queue),1)
        fn(*args);self.assertEqual(len(r._event_queue),1);self.assertIsNone(r.get_current_item())
        fn,args=q.pop(0);fn(*args);self.assertEqual(r.get_current_item(),'new')
    def test_capability_exception_is_inactive_and_preserves_request(self):
        r,s,c,q=reviewer(Device());r.set_is_enabled(True)
        self.assertFalse(r.refresh_device(Device(error=True)))
        self.assertTrue(r.get_is_enabled());self.assertFalse(r._active)
    def test_disabling_invalidates_pending_item(self):
        d=Device();r,s,c,q=reviewer(d);r.set_is_enabled(True);d.emit('pending')
        fn,args=q.pop(0);r.set_is_enabled(False);fn(*args)
        self.assertEqual(len(r._event_queue),0);self.assertIsNone(r.get_current_item())

    def test_disable_during_outage_does_not_reenable_on_return(self):
        r,s,c,q=reviewer(Device());r.set_is_enabled(True);r.refresh_device(None)
        self.assertTrue(r.set_is_enabled(False));self.assertFalse(r.get_is_enabled())
        new=Device();r.refresh_device(new)
        self.assertFalse(r._active);self.assertEqual(len(new.handlers),0)
    def test_disable_temporarily_inactive_clears_request(self):
        r,s,c,q=reviewer(Device());r.set_is_enabled(True);r.deactivate()
        self.assertTrue(r.get_is_enabled());self.assertFalse(r._active)
        self.assertTrue(r.set_is_enabled(False));self.assertFalse(r.get_is_enabled())
        r.refresh_device(Device());self.assertFalse(r._active)
    def test_outage_toggle_cancels_requested_enable(self):
        r,s,c,q=reviewer(Device());r.set_is_enabled(True);r.refresh_device(None)
        self.assertTrue(r.toggle(None,notify_user=False));self.assertFalse(r.get_is_enabled())
        r.refresh_device(Device());self.assertFalse(r._active)
    def test_enable_during_outage_replays_only_explicit_request(self):
        r,s,c,q=reviewer(Device(False));self.assertTrue(r.set_is_enabled(True))
        self.assertTrue(r.get_is_enabled());self.assertFalse(r._active)
        r.refresh_device(Device());self.assertTrue(r._active)
    def test_direct_activate_respects_disabled_intent(self):
        d=Device();r,s,c,q=reviewer(d);r.activate()
        self.assertFalse(r._active);self.assertEqual(len(d.handlers),0)

if __name__=='__main__': unittest.main(verbosity=2)
