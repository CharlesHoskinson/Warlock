"""Controlled public adapter tests; actual GI/native ordering remains unproved."""
import unittest
from types import SimpleNamespace as NS
from capability_adapter import CapabilityAdapter,PublicTransport

class AdapterTests(unittest.TestCase):
    def make(self):
        events=[]
        state=NS(owner=':1.9',name_owner=':1.2',quiet=True,raise_cap=False,
                 replace_on_cap=False,unsupported=False,request_code=1,watched=False)
        connection=NS(get_unique_name=lambda:':1.2')
        class Device:
            __gtype__=NS(name='AtspiDeviceA11yManager')
            def __init__(self): self.caps=0
            def get_capabilities(self):return self.caps
            def get_property(self,key):
                assert key=='session-bus';return connection
            def get_app_id(self):return 'org.gnome.Orca'
            def set_capabilities(self,caps):
                events.append(('actual-capability',self,state.name_owner))
                if state.replace_on_cap:state.owner=':1.10'
                if state.raise_cap:raise ValueError('actual capability exception')
                self.caps=0 if state.unsupported else caps;return self.caps
        atspi=NS(Device=Device,DeviceCapability=NS(POINTER_MONITOR=1))
        ax=NS(current=None,get_device=lambda:ax.current)
        def activate():
            if ax.current is None:
                ax.current=Device();events.append(('constructor',ax.current));state.name_owner=':1.2'
        ax.activate=activate
        def release(conn,name):
            events.append(('release',name));state.name_owner='';return 1
        def request(conn,name,flags):
            events.append(('request',name,flags))
            if state.request_code in (1,4):state.name_owner=':1.2'
            return state.request_code
        def watch(conn):events.append(('watch',));state.watched=True
        transport=NS(manager_owner=lambda:state.owner,name_owner=lambda conn,name:state.name_owner,
                     release=release,request=request,watch=watch,arm=lambda conn:events.append(('authorized-query',)))
        adapter=CapabilityAdapter(atspi,ax,transport,lambda conn,owner:state.quiet).install()
        self.addCleanup(adapter.close)
        return adapter,ax,state,events
    def test_actual_same_device_ordering_and_do_not_queue(self):
        a,ax,s,e=self.make();ax.activate();d=ax.get_device();self.assertEqual(d.set_capabilities(1),1)
        self.assertEqual([x[0] for x in e],['constructor','release','actual-capability','request','watch','authorized-query'])
        self.assertIs(e[2][1],d);self.assertEqual(e[2][2],'');self.assertEqual(e[3][2],4)
    def test_unsupported_result_reclaims_and_watches_without_arming(self):
        a,ax,s,e=self.make();ax.activate();s.unsupported=True
        with self.assertRaisesRegex(RuntimeError,"did not enable POINTER_MONITOR"):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,":1.2");self.assertTrue(s.watched)
        self.assertNotIn("authorized-query",[x[0] for x in e])
    def test_held_or_dirty_refusal_preserves_registration(self):
        a,ax,s,e=self.make();ax.activate();s.quiet=False
        with self.assertRaisesRegex(RuntimeError,'refused'):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,':1.2');self.assertEqual([x[0] for x in e],['constructor'])
    def test_capability_exception_reclaims_without_watch(self):
        a,ax,s,e=self.make();ax.activate();s.raise_cap=True
        with self.assertRaisesRegex(ValueError,'actual capability'):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,':1.2');self.assertFalse(s.watched)
        self.assertEqual([x[0] for x in e],['constructor','release','actual-capability','request'])
    def test_owner_change_during_capability_reclaims_without_replay(self):
        a,ax,s,e=self.make();ax.activate();s.replace_on_cap=True
        with self.assertRaisesRegex(RuntimeError,'epoch changed'):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,':1.2');self.assertFalse(s.watched)
    def test_owner_change_before_probe_does_not_release(self):
        a,ax,s,e=self.make();ax.activate();s.owner=':1.10'
        with self.assertRaisesRegex(RuntimeError,'epoch changed'):ax.current.set_capabilities(1)
        self.assertEqual([x[0] for x in e],['constructor'])
    def test_wrong_actual_name_owner_not_released(self):
        a,ax,s,e=self.make();ax.activate();s.name_owner=':1.99'
        with self.assertRaisesRegex(RuntimeError,'does not own'):ax.current.set_capabilities(1)
        self.assertEqual([x[0] for x in e],['constructor'])
    def test_existing_capability_does_not_release_again(self):
        a,ax,s,e=self.make();ax.activate();ax.current.set_capabilities(1);e.clear()
        ax.current.set_capabilities(1)
        self.assertEqual([x[0] for x in e],['actual-capability'])
    def test_untracked_current_device_refused(self):
        a,ax,s,e=self.make();ax.activate();a.fresh.clear()
        with self.assertRaisesRegex(RuntimeError,'fresh pre-replay'):ax.current.set_capabilities(1)
        self.assertEqual([x[0] for x in e],['constructor'])
    def test_failed_do_not_queue_reclaim_does_not_watch(self):
        a,ax,s,e=self.make();ax.activate();s.request_code=3
        with self.assertRaisesRegex(RuntimeError,'could not reclaim'):ax.current.set_capabilities(1)
        self.assertFalse(s.watched)
    def test_owner_change_during_bootstrap_prevents_success_report(self):
        a,ax,s,e=self.make();ax.activate()
        a.transport.arm=lambda conn:setattr(s,'owner',':1.10')
        with self.assertRaisesRegex(RuntimeError,'after pointer bootstrap'):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,':1.2')
    def test_bootstrap_failure_preserves_name_and_propagates(self):
        a,ax,s,e=self.make();ax.activate()
        def fail(conn):raise RuntimeError('bootstrap AccessDenied')
        a.transport.arm=fail
        with self.assertRaisesRegex(RuntimeError,'bootstrap AccessDenied'):ax.current.set_capabilities(1)
        self.assertEqual(s.name_owner,':1.2')
    def test_transport_accepts_only_truthful_unknown_error(self):
        class Error(Exception):pass
        glib=NS(Error=Error);gio=NS(DBusError=NS(get_remote_error=lambda error:str(error)),DBusCallFlags=NS(NONE=0))
        transport=PublicTransport(None,glib,gio)
        def connection(name):
            def call(*args):raise Error(name)
            return NS(call_sync=call)
        transport.arm(connection('org.freedesktop.a11y.UnknownToplevel'))
        for name in ('org.freedesktop.DBus.Error.AccessDenied','org.freedesktop.a11y.ServiceRetired','transport timeout'):
            with self.assertRaises(Error):transport.arm(connection(name))

if __name__=='__main__':unittest.main(verbosity=2)
