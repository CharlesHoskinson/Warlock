"""Explicit Omarchy Orca compat startup. Never run by bridge installation/load."""
from pathlib import Path
import argparse,os,runpy,sys
from control import Control,Refused,reader_intent

def verify_status(value,owner):
    return (value.get('managerOwner')==owner and value.get('retiring') is False
            and all(value.get(key) is True for key in ('quiescent','unloadQuiescent','registered','callerPreReplay')))

def main():
    parser=argparse.ArgumentParser(description='Start Omarchy Orca compat only when existing ScreenReaderEnabled intent is true')
    parser.add_argument('--manifest',required=True);parser.add_argument('--instance');parser.add_argument('orca_args',nargs=argparse.REMAINDER)
    args=parser.parse_args();env=dict(os.environ)
    # Construct no Orca objects or subscriptions when disabled. Keep the actual
    # session read explicit; arbitrary DISPLAY/bus/runtime fallbacks are refused.
    control=Control(args.manifest,args.instance,env)
    if reader_intent(control.env) is not True:raise Refused('ScreenReaderEnabled is false; reader remains disabled')
    if os.environ.get('GDK_BACKEND')!='wayland' or os.environ.get('DISPLAY'):raise Refused('strict native Wayland launcher required')
    from gi.repository import Gio,GLib
    import gi
    gi.require_version('Atspi','2.0')
    gi.require_version('Gdk','3.0')
    from gi.repository import Atspi
    from orca import ax_device_manager
    from capability_adapter import CapabilityAdapter,PublicTransport
    session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    def pre_replay(connection,owner):
        # This public fresh-device connection must match the currently loaded
        # bridge epoch. No D-Bus maintenance interface is consulted or exposed.
        unique=connection.get_unique_name()
        if not unique:return False
        try:return verify_status(control.capability_status(unique),owner)
        except (Refused,OSError,ValueError):return False
    capability=CapabilityAdapter(Atspi,ax_device_manager.get_manager(),PublicTransport(session,GLib,Gio),pre_replay).install()
    # The accepted process-only Legacy modifier map has no global library or
    # X-server changes. It is inert for the official A11yManager device.
    os.environ['ORCA_QA_NATIVE_WAYLAND_MODIFIERS']='1'
    import legacy_keygrab_compat
    from reader_reconnect_v7 import install
    reconnect=install()
    # Preserve real user profile, preferences, speech backend and public CLI.
    # The package launcher supplies code/lib paths only, never QA profile data.
    prefix=Path(__file__).resolve().parent/'reader-prefix'
    script=prefix/'usr/bin/orca'
    from orca import mouse_review
    expected=Path(__file__).resolve().parent/'orca-compat/orca/mouse_review.py'
    if Path(mouse_review.__file__).resolve()!=expected.resolve():raise Refused('reviewed signed-coordinate compat not imported')
    if reader_intent(control.env) is not True:raise Refused('enabled intent revoked before reader construction')
    sys.argv=[str(script),*(args.orca_args[1:] if args.orca_args[:1]==['--'] else args.orca_args)]
    try:runpy.run_path(str(script),run_name='__main__')
    finally:reconnect.close();capability.close()
if __name__=='__main__':main()
