"""Staged process-only Orca 50.2/Atspi 2.60 reconnect adapter.

Import is passive. install() is an explicit reader-launcher action. Only public
Orca binding/device APIs rebuild explicitly active command definitions. No
bus-name ownership is interpreted as an interception request.
"""
from __future__ import annotations


class Reconnector:
    def __init__(self, ax, inputs, commands, modifiers, bus, glib, gio, report=None, mouse_refresh=None):
        self.mouse_refresh = mouse_refresh
        self.ax, self.inputs = ax, inputs
        self.commands, self.modifiers = commands, modifiers
        self.bus, self.glib, self.gio = bus, glib, gio
        self.report = report or (lambda event, **fields: None)
        self.owner = ""
        self.epoch = 0
        self.watch_requested = False
        self.full_requested = False
        self.pause_requested = False
        self.switching = False
        self.closed = False
        self.applied_epoch = -1
        self.originals = {}
        self.watch_id = 0

    def _wrap(self, name, update):
        original = getattr(self.inputs, name)
        self.originals[name] = original

        def requested(*args, **kwargs):
            result = original(*args, **kwargs)
            if not self.switching:
                update(*args, **kwargs)
            return result

        setattr(self.inputs, name, requested)

    def start(self):
        self._wrap("start_key_watcher", lambda: self._watch(True))
        self._wrap("stop_key_watcher", lambda: self._watch(False))
        self._wrap("grab_keyboard", lambda *a, **k: setattr(self, "full_requested", True))
        self._wrap("ungrab_keyboard", lambda *a, **k: setattr(self, "full_requested", False))
        self._wrap("pause_key_watcher", self._pause)
        self.watch_id = self.gio.bus_watch_name_on_connection(
            self.bus, "org.freedesktop.a11y.Manager", self.gio.BusNameWatcherFlags.NONE,
            self._appeared, self._vanished)
        return self

    def _pause(self, pause=True, reason=""):
        self.pause_requested = pause

    def _watch(self, requested):
        self.watch_requested = requested
        if requested:
            self._schedule()

    def _appeared(self, connection, name, owner):
        self._changed(owner)

    def _vanished(self, connection, name):
        self._changed("")

    def _changed(self, owner):
        if self.closed or owner == self.owner:
            return
        self.owner = owner
        self.epoch += 1
        self._schedule()

    def _schedule(self):
        if not self.closed and self.watch_requested:
            self.glib.idle_add(self._reconnect, self.epoch, self.owner)

    def _current_owner(self):
        try:
            value = self.bus.call_sync(
                "org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                "GetNameOwner", self.glib.Variant("(s)", ("org.freedesktop.a11y.Manager",)),
                None, self.gio.DBusCallFlags.NONE, 500, None)
            return value.unpack()[0]
        except self.glib.Error:
            return ""

    def _reconnect(self, epoch, owner):
        if (self.closed or self.switching or not self.watch_requested
                or epoch != self.epoch or owner != self.owner or epoch == self.applied_epoch):
            return False
        if not self.ax.is_active() or self._current_owner() != owner:
            return False
        # No key release is synthesized. Restart requires compositor quiescence.
        # All manager methods below run synchronously in the reader GLib thread.
        commands = self.commands.get_keyboard_commands()
        bindings = {id(binding): binding for command in commands.values()
                    if (binding := command.get_keybinding()) is not None}
        self.switching = True
        try:
            self.originals["pause_key_watcher"](True, "manager epoch replacement")
            if self.full_requested:
                self.originals["ungrab_keyboard"]("manager epoch replacement")
            for binding in bindings.values():
                binding.remove_grabs()  # clears the binding's cached IDs too
            self.modifiers.remove_grabs_for_orca_modifiers()
            self.inputs.unmap_all_modifiers()
            self.originals["stop_key_watcher"]()
            self.ax.deactivate()
            self.ax.activate()  # real public Atspi.Device factory, never a fake
            if self.mouse_refresh is not None:
                # Capability negotiation completes on this same fresh device
                # before any selected/full interception definitions are replayed.
                self.mouse_refresh(self.ax.get_device())
            self.originals["start_key_watcher"]()  # replaces retained input _device
            if self._current_owner() != owner or epoch != self.epoch:
                self.report("owner-raced", epoch=epoch, owner=owner)
                self.glib.idle_add(self._retry_owner)
                return False
            device = self.ax.get_device()
            backend = device.__gtype__.name
            expected = "AtspiDeviceA11yManager" if owner else "AtspiDeviceLegacy"
            if backend != expected:
                raise RuntimeError(f"public factory returned {backend}, expected {expected}")
            self.modifiers.refresh_orca_modifiers("manager epoch replacement")
            # Uses the unchanged current command dictionary. The official diff
            # honors suspended commands and NumLock-specific keypad exclusions.
            self.commands.set_active_commands(commands, "manager epoch replacement")
            self.originals["pause_key_watcher"](self.pause_requested, "restore requested pause")
            if self.full_requested:
                self.originals["grab_keyboard"]("restore explicitly requested full grab")
            self.applied_epoch = epoch
            self.report("reconnected", epoch=epoch, owner=owner, backend=backend,
                        full=self.full_requested, paused=self.pause_requested,
                        commands=len(commands))
        finally:
            self.switching = False
        return False

    def _retry_owner(self):
        if not self.closed:
            current = self._current_owner()
            if current != self.owner:
                self._changed(current)
            else:
                self._schedule()
        return False

    def close(self):
        self.closed = True
        self.epoch += 1
        if self.watch_id:
            self.gio.bus_unwatch_name(self.watch_id)
            self.watch_id = 0
        for name, original in self.originals.items():
            setattr(self.inputs, name, original)
        self.originals.clear()


def install(report=None):
    """Call once in an explicitly launched reader before it starts watching."""
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Gio, GLib
    from orca import ax_device_manager, input_event_manager, command_manager, orca_modifier_manager
    import os
    if os.environ.get("DISPLAY"):
        raise RuntimeError("staged reconnect requires the strict native Wayland reader launcher")
    def refresh_mouse(device):
        from orca import mouse_review
        reviewer = mouse_review.get_reviewer()
        if not hasattr(reviewer, "refresh_device"):
            raise RuntimeError("pointer reconnect requires the reviewed Omarchy Orca compat package")
        return reviewer.refresh_device(device)
    return Reconnector(ax_device_manager.get_manager(), input_event_manager.get_manager(),
                       command_manager.get_manager(), orca_modifier_manager.get_manager(),
                       Gio.bus_get_sync(Gio.BusType.SESSION, None), GLib, Gio, report, refresh_mouse).start()
