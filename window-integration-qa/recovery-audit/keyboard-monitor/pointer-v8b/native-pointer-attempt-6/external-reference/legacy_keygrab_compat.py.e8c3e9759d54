"""Optional Orca50/AT-SPI2.60 Legacy keysym registration interoperability fix.

Reader commands, callbacks and event processing remain Orca's implementation.
No events, focus or command actions are synthesized by this module.
"""
from gi.repository import Gdk
from orca import ax_device_manager, keybindings, debug

_original = keybindings.KeyBinding._create_key_definitions

def _definitions(keyval, modifiers, orca_modifiers):
    definitions = _original(keyval, modifiers, orca_modifiers)
    device = ax_device_manager.get_manager().get_device()
    if device is not None and device.__gtype__.name == 'AtspiDeviceLegacy':
        for definition in definitions:
            if not definition.keycode and definition.keysym:
                symbol = Gdk.keyval_name(definition.keysym)
                _, code = keybindings.get_keycodes(symbol)
                if code:
                    definition.keycode = code
    return definitions

keybindings.KeyBinding._create_key_definitions = staticmethod(_definitions)
debug.print_message(debug.LEVEL_INFO, 'QA LEGACY KEYGRAB COMPAT: resolves command keysyms to actual GDK hardware keycodes for DeviceLegacy only', True)

# Tested strict Wayland mode: map virtual Orca modifiers through the same
# actual GDK keycodes as the Qt events. With DISPLAY unset this avoids stock
# Legacy's XKeysymToKeycode dependency and Orca's XKB server writes.
import os
from orca import input_event_manager
_original_map = input_event_manager.InputEventManager.map_keysym_to_modifier

def _map_keysym(self, keysym):
    device = self._device
    if device is not None and device.__gtype__.name == 'AtspiDeviceLegacy':
        _, code = keybindings.get_keycodes(Gdk.keyval_name(keysym))
        if code:
            self._mapped_keycodes.append(code)
            return device.map_modifier(code)
    return _original_map(self, keysym)

if os.environ.get('ORCA_QA_NATIVE_WAYLAND_MODIFIERS') == '1':
    input_event_manager.InputEventManager.map_keysym_to_modifier = _map_keysym
