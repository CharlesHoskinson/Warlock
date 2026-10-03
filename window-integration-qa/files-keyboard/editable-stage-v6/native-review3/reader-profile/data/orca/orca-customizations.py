"""Register output adapter and observation-only QA getter; reader logic is untouched."""
import json
from orca import dbus_service, focus_manager, object_navigator, speech_manager, gsettings_registry, ax_device_manager
speech_manager.SPEECH_FACTORY_MODULES[:] = ['silent_factory']
registry = gsettings_registry.get_registry()
registry.set_runtime_value('braille', 'enabled', False)
registry.set_runtime_value('sound', 'enabled', False)


def describe(obj):
    if obj is None:
        return None
    try:
        return dict(name=obj.get_name() or "", role=obj.get_role_name() or "", identity=obj.get_accessible_id() or "",
                    app=obj.get_application().get_name(), text=obj.get_text_iface().get_text(0,-1) if obj.get_role_name()=="text" else None, object_path=getattr(obj,"path",None), app_bus=getattr(obj.app,"bus_name",None))
    except Exception as error:
        return dict(error=repr(error))


class QAObservation:
    @dbus_service.getter
    def get_state(self):
        manager = focus_manager.get_manager()
        navigator = object_navigator.get_navigator()
        device = ax_device_manager.get_manager().get_device()
        return json.dumps(dict(device_type=device.__gtype__.name if device else None, focus=describe(manager.get_locus_of_focus()),
            active_window=describe(manager.get_active_window()),
            navigator=describe(navigator._navigator_focus)))

observer = QAObservation()
dbus_service.get_remote_controller().register_decorated_module('QAObservation', observer)

# Explicit per-reader opt-in: absent by default, no global package patch.
import os
if os.environ.get('ORCA_QA_LEGACY_GRAB_FIX') == '1':
    import legacy_keygrab_compat
