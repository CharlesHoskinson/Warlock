import copy
import fcntl
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from scene_manager import SceneManager
from scene_controller import key,ids
from native_desktop import NativeDesktop
from native_runtime import complete_live_identities,NativeFactory
from snapshot_cache import SnapshotCache
from service_runtime import RuntimeService,JournalStore
from test_scene_controller import Desktop,Transport,rectangle
from test_capture_lease import png
import production_motion_6d9 as production


class Factory:
    def __init__(self):
        self.desktop=Desktop();self.rows=[];self.bound=[];self.retired_ids=[]
        self.close_gate=None;self.close_started=threading.Event();self.fail_close=False
    def __call__(self,number):
        t=Transport();row={'number':number,'closed':False,'disposed':False}
        self.rows.append(row)
        factory=self
        class ActorDesktop:
            def __getattr__(self,name):return getattr(factory.desktop,name)
            def dispose(self):row['disposed']=True
        def close():
            self.close_started.set()
            if self.close_gate:self.close_gate.wait(3)
            if self.fail_close:raise RuntimeError('normal child exit unavailable')
            row['closed']=True
        t.close=close
        t.bind_controller=lambda c:self.bound.append((number,c))
        return ActorDesktop(),t
    def retired(self,number,desktop):self.retired_ids.append(number)


class ActorLifecycle(unittest.TestCase):
    def setUp(self):
        self.f=Factory();self.persisted=[]
        self.m=SceneManager(self.f,max_actors=2,persist=lambda:self.persisted.append(
            ([a.number for a in self.m.actors],[a.number for a in self.m.retiring],copy.deepcopy(self.m.resource_errors))))
    def tearDown(self):
        if self.f.close_gate:self.f.close_gate.set()
        try:self.m.close()
        except RuntimeError:pass
    def reserve(self,index=0):
        w=self.f.desktop.windows[index]
        return self.m.reserve('minimize',w['address'],w['stableId'],w['pid'])
    def idle(self,index=0):
        r=self.reserve(index);self.m.fail_ingress(r['receipt'],'fixture context refusal');return r
    def test_capacity_refuses_before_factory_or_durable_receipt(self):
        self.reserve(0);self.reserve(1);before=(self.m.serial,len(self.f.rows),len(self.persisted))
        self.assertRaisesRegex(RuntimeError,'capacity',self.reserve,2)
        self.assertEqual((self.m.serial,len(self.f.rows),len(self.persisted)),before)
    def test_same_exact_pending_family_can_reverse_at_capacity(self):
        self.reserve(0);self.reserve(1);reply=self.reserve(0)
        self.assertEqual(reply['actor'],1);self.assertEqual(len(self.f.rows),2)
    def test_pending_and_cancel_ack_protect_actor(self):
        self.reserve();self.assertEqual(self.m.reap_idle(),[])
        self.m.fail_ingress(1,'failed');c=self.m.actors[0].controller
        c.retired['diagnostic-pending-cancel']=object()
        self.assertEqual(self.m.reap_idle(),[]);self.assertFalse(self.f.close_started.is_set())
        c.retired.clear();self.assertEqual(self.m.reap_idle(),[1])
    def test_normal_retirement_persists_completion_and_old_receipt_gc(self):
        self.idle();self.assertEqual(self.m.reap_idle(),[1])
        self.assertEqual(self.persisted[-1],([],[],[]));self.assertFalse(self.m.owners)
        self.assertFalse(self.m.receipts);self.assertEqual(self.f.retired_ids,[1])
        self.assertTrue(self.f.rows[0]['closed'] and self.f.rows[0]['disposed'])
        self.assertEqual(self.reserve()['actor'],2)
    def test_blocked_teardown_does_not_hold_unrelated_receipt_lock(self):
        self.idle();self.f.close_gate=threading.Event()
        thread=threading.Thread(target=self.m.reap_idle);thread.start()
        try:
            self.assertTrue(self.f.close_started.wait(1))
            reply=self.reserve(1);self.assertEqual(reply['actor'],2)
            self.assertEqual(len(self.m.retiring),1)
            self.assertRaisesRegex(RuntimeError,'capacity',self.reserve,2)
        finally:self.f.close_gate.set();thread.join(2)
        self.assertFalse(thread.is_alive())
    def test_new_same_identity_receipt_survives_old_actor_disposal(self):
        self.idle();self.f.close_gate=threading.Event()
        thread=threading.Thread(target=self.m.reap_idle);thread.start()
        try:
            self.assertTrue(self.f.close_started.wait(1));reply=self.reserve(0)
        finally:self.f.close_gate.set();thread.join(2)
        captured=key(self.f.desktop.windows[0])
        self.assertEqual(self.m.receipts[captured],reply['receipt'])
        self.assertEqual(self.m.owners[captured],self.m.actors[0].controller)
    def test_failed_normal_exit_keeps_quarantine_capacity_and_material(self):
        self.idle();self.f.fail_close=True
        self.assertEqual(self.m.reap_idle(),[]);self.assertEqual(len(self.m.retiring),1)
        self.assertFalse(self.f.rows[0]['disposed']);self.assertFalse(self.f.retired_ids)
        self.assertEqual(self.persisted[-1][1],[1]);self.assertTrue(self.persisted[-1][2])
    def test_shutdown_revokes_pending_before_blocked_renderer_then_disposes_and_persists(self):
        reserved=self.reserve();self.f.close_gate=threading.Event();errors=[]
        def finish():
            try:self.m.close()
            except Exception as error:errors.append(str(error))
        thread=threading.Thread(target=finish);thread.start()
        try:
            self.assertTrue(self.f.close_started.wait(1))
            self.assertTrue(self.m.closed);self.assertFalse(self.m.pending)
            self.assertEqual(self.persisted[-1][1],[1]);self.assertFalse(self.f.rows[0]['disposed'])
            self.assertRaisesRegex(RuntimeError,'closed',self.reserve,1)
            result=self.m.activate(reserved['receipt'],context='late context')
            self.assertTrue(result['superseded']);self.assertFalse(self.f.desktop.commits)
        finally:self.f.close_gate.set();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertFalse(errors)
        self.assertEqual(self.persisted[-1],([],[],[]));self.assertFalse(self.m.receipts)
        self.assertEqual(self.f.retired_ids,[1]);self.assertTrue(self.f.rows[0]['disposed'])
        self.m.close();self.assertEqual(self.f.retired_ids,[1])
    def test_shutdown_renderer_failure_durably_quarantines_and_preserves_files(self):
        self.reserve();self.f.fail_close=True
        self.assertRaisesRegex(RuntimeError,'normal child exit',self.m.close)
        self.assertFalse(self.m.actors);self.assertEqual(self.persisted[-1][1],[1])
        self.assertTrue(self.persisted[-1][2]);self.assertFalse(self.f.rows[0]['disposed'])
        self.assertFalse(self.f.retired_ids)
    def test_shutdown_still_closes_renderer_after_controller_settlement_failure(self):
        self.reserve();c=self.m.actors[0].controller
        c.close=lambda:(_ for _ in ()).throw(ValueError('fresh native settlement failed'))
        self.assertRaisesRegex(RuntimeError,'native settlement',self.m.close)
        self.assertTrue(self.f.rows[0]['closed']);self.assertFalse(self.f.rows[0]['disposed'])
        self.assertEqual(self.persisted[-1][1],[1]);self.assertFalse(self.f.retired_ids)
    def test_external_bound_observer_retains_actual_controller_after_registry_gc(self):
        self.idle();observed=self.f.bound[0]
        self.m.reap_idle();self.assertFalse(self.m.actors)
        self.assertEqual(observed[0],1);self.assertIsNone(observed[1].current)
        self.assertTrue(self.f.rows[0]['closed']);self.assertEqual(self.f.retired_ids,[1])


class NativeOwnedDisposal(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ar-');self.root=Path(self.tmp.name)
        self.parent=self.root/'hypr-window-motion'/'actors';self.parent.mkdir(parents=True,mode=0o700)
        self.env=patch.dict(os.environ,{'XDG_RUNTIME_DIR':str(self.root)});self.env.start()
        self.actor=NativeDesktop(self.parent/'actor-1',core=self.root/'unused-core')
    def tearDown(self):self.env.stop();self.tmp.cleanup()
    def material(self,name='abcdef123456-1.png',data=b'generated-owned'):
        p=self.actor.root/name;p.write_bytes(data);p.chmod(0o600);return p
    def test_only_owned_namespace_removed_shared_cache_and_public_preview_survive(self):
        self.material();self.material('full-aa01-41.json');self.material('frame-abcdef123456-2.png')
        cache=self.parent.parent/'snapshot-cache';cache.mkdir(mode=0o700);outside=cache/'keep.png';outside.write_bytes(b'keep')
        self.actor.dispose();self.assertFalse(self.actor.root.exists());self.assertEqual(outside.read_bytes(),b'keep')
    def test_unexpected_file_refuses_before_deleting_any_material(self):
        good=self.material();other=self.material('foreign.txt')
        self.assertRaisesRegex(ValueError,'unexpected',self.actor.dispose)
        self.assertTrue(good.exists() and other.exists())
    def test_symlink_and_public_material_refuse(self):
        good=self.material();good.unlink();foreign=self.root/'foreign';foreign.write_bytes(b'keep');good.symlink_to(foreign)
        self.assertRaises(ValueError,self.actor.dispose);self.assertEqual(foreign.read_bytes(),b'keep')
        good.unlink();good=self.material();good.chmod(0o644)
        self.assertRaises(ValueError,self.actor.dispose);self.assertTrue(good.exists())
    def test_replaced_actor_name_never_deletes_new_directory(self):
        original=self.material();archived=self.parent/'old';self.actor.root.rename(archived)
        self.actor.root.mkdir(mode=0o700);replacement=self.material(data=b'replacement')
        self.assertRaisesRegex(ValueError,'identity',self.actor.dispose)
        self.assertEqual(replacement.read_bytes(),b'replacement');self.assertTrue((archived/original.name).exists())
    def test_partial_or_changing_native_cache_coverage_refuses_pruning(self):
        clients=Desktop().clients();native=copy.deepcopy(clients)
        self.assertEqual(complete_live_identities(clients,native,clients),{key(w) for w in clients})
        self.assertRaises(ValueError,complete_live_identities,clients,native[:-1],clients)
        changed=copy.deepcopy(clients);changed[0]['pid']+=1
        self.assertRaises(ValueError,complete_live_identities,clients,native,changed)
    def test_last_actor_retirement_still_prunes_closed_cache_and_retains_exact_live_pair(self):
        windows=Desktop().windows[:2];cache=SnapshotCache(self.root/'factory-cache',production.Desktop.validate_snapshot)
        for w in windows:
            metadata={'whole':True,'canonical':True,'identity':list(key(w)),'clientSize':w['size'],'rect':rectangle(w),'insets':dict(left=0,top=0,right=0,bottom=0),'pixels':w['size']}
            cache.publish(w,metadata,png(*w['size']))
        factory=NativeFactory.__new__(NativeFactory);factory.desktops=[];factory.shared_cache=cache
        calls=[]
        class Guard:
            env={'SELECTED_PRIVATE':'yes'}
            def verify(self):calls.append('guard')
        factory.guard=Guard();factory.housekeeping_commands=__import__('subprocess')
        def observation(command,**options):
            self.assertEqual(options['env'],factory.guard.env)
            return __import__('json').dumps([windows[0]])
        with patch('native_runtime.subprocess.check_output',side_effect=observation) as queries:
            factory.housekeep();self.assertEqual(queries.call_count,3)
        self.assertEqual(calls,['guard','guard'])
        self.assertIsNotNone(cache.restore(windows[0]));self.assertRaises(FileNotFoundError,cache.restore,windows[1])
        self.assertFalse(factory.desktops)
    def test_incomplete_idle_factory_native_observation_preserves_every_cache_byte(self):
        cache=SnapshotCache(self.root/'factory-cache',production.Desktop.validate_snapshot)
        w=Desktop().windows[0];metadata={'whole':True,'canonical':True,'identity':list(key(w)),'clientSize':w['size'],'rect':rectangle(w),'insets':dict(left=0,top=0,right=0,bottom=0),'pixels':w['size']}
        cache.publish(w,metadata,png(*w['size']));before={p.name:p.read_bytes() for p in cache.root.iterdir()}
        factory=NativeFactory.__new__(NativeFactory);factory.desktops=[];factory.shared_cache=cache
        class Guard:
            env={}
            def verify(self):pass
        factory.guard=Guard();factory.housekeeping_commands=__import__('subprocess')
        with patch('native_runtime.subprocess.check_output',side_effect=[__import__('json').dumps([w]),'[]',__import__('json').dumps([w])]):
            self.assertRaisesRegex(ValueError,'coverage',factory.housekeep)
        self.assertEqual({p.name:p.read_bytes() for p in cache.root.iterdir()},before)
    def test_nonblocking_global_cache_lock_preserves_live_minimized_pair(self):
        w=Desktop().windows[0];data=png(*w['size']);cache=SnapshotCache(self.root/'cache',production.Desktop.validate_snapshot)
        metadata={'whole':True,'canonical':True,'identity':list(key(w)),'clientSize':w['size'],'rect':rectangle(w),'insets':dict(left=0,top=0,right=0,bottom=0),'pixels':w['size']}
        cache.publish(w,metadata,data);before={p.name:p.read_bytes() for p in cache.root.iterdir()}
        with cache.pair('publisher'):
            self.assertRaises(BlockingIOError,cache.prune,set(),complete=True,nonblocking=True)
            self.assertEqual({p.name:p.read_bytes() for p in cache.root.iterdir()},before)
        cache.prune({key(w)},complete=True,nonblocking=True)
        minimized=copy.deepcopy(w);minimized['workspace']['name']='special:win-minimized'
        self.assertEqual(cache.restore(minimized)[1],data)


class HousekeepingSeparation(unittest.TestCase):
    def test_runtime_shutdown_drains_context_before_actor_file_disposal_and_releases_lease(self):
        with tempfile.TemporaryDirectory(prefix='sd-') as temp:
            root=Path(temp)/'r';root.mkdir(mode=0o700)
            factory=Factory();entered=threading.Event();gate=threading.Event();errors=[]
            def context(request):entered.set();gate.wait(3);return 'late context'
            service=RuntimeService(root,'fixture',factory,context)
            try:
                service.start();w=factory.desktop.windows[0]
                reserved=service.frontend.dispatch({'command':'request','operation':'minimize',
                    'address':w['address'],'stableId':w['stableId'],'pid':w['pid']})
                self.assertTrue(entered.wait(1))
                def finish():
                    try:service.close()
                    except Exception as error:errors.append(str(error))
                thread=threading.Thread(target=finish);thread.start()
                deadline=time.monotonic()+1
                while time.monotonic()<deadline and not service.manager.closed:time.sleep(.002)
                self.assertTrue(service.manager.closed);self.assertFalse(factory.rows[0]['disposed'])
                self.assertFalse(service.manager.pending);self.assertTrue(thread.is_alive())
                gate.set();thread.join(3);self.assertFalse(thread.is_alive());self.assertFalse(errors)
                self.assertFalse(factory.desktop.commits);self.assertTrue(factory.rows[0]['disposed'])
                self.assertEqual(factory.retired_ids,[reserved['actor']]);self.assertIsNone(service.lease.fd)
                body=JournalStore(root,'fixture').read()
                self.assertFalse(body['pending'] or body['scenes'] or body['retiringActors'] or body['liveActors'])
                self.assertTrue(body['managerClosed']);self.assertFalse((root/'api.sock').exists())
            finally:gate.set();service.close()
    def test_runtime_stop_removes_exact_owned_actor_png_but_retains_shared_minimized_cache(self):
        with tempfile.TemporaryDirectory(prefix='sf-') as temp,patch.dict(os.environ,{'XDG_RUNTIME_DIR':temp}):
            root=Path(temp)/'r';root.mkdir(mode=0o700);parent=Path(temp)/'hypr-window-motion'/'actors';parent.mkdir(parents=True,mode=0o700)
            factory=Factory();original=factory.__class__.__call__;owned=[]
            class FileFactory(Factory):
                def __call__(self,number):
                    d,t=original(self,number)
                    native=NativeDesktop(parent/f'actor-{number}',core=root/'unused')
                    path=native.root/'abcdef123456-1.png';path.write_bytes(b'actor-owned');path.chmod(0o600)
                    d.dispose=native.dispose;owned.append(native.root)
                    return d,t
            factory=FileFactory();cache=root/'snapshot-cache';cache.mkdir(mode=0o700)
            cached=cache/'live-minimized.png';cached.write_bytes(b'cached-live');cached.chmod(0o600)
            service=RuntimeService(root,'fixture',factory,lambda request:'context')
            try:
                w=factory.desktop.windows[0];service.manager.reserve('minimize',w['address'],w['stableId'],w['pid'])
            finally:service.close()
            self.assertTrue(owned);self.assertFalse(owned[0].exists())
            self.assertEqual(cached.read_bytes(),b'cached-live');self.assertEqual(factory.retired_ids,[1])
    def test_bad_cache_observation_does_not_prevent_idle_actor_normal_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='hk-') as temp:
            root=Path(temp)/'r';root.mkdir(mode=0o700)
            factory=Factory();factory.housekeep=lambda:(_ for _ in ()).throw(ValueError('incomplete native cache snapshot'))
            service=RuntimeService(root,'fixture',factory,lambda request:'context')
            try:
                w=factory.desktop.windows[0];r=service.manager.reserve('minimize',w['address'],w['stableId'],w['pid'])
                service.manager.fail_ingress(r['receipt'],'fixture context refusal');service.start()
                def durable_retirement():
                    return factory.retired_ids==[1] and not JournalStore(root,'fixture').read()['retiringActors']
                deadline=time.monotonic()+3
                while time.monotonic()<deadline and not durable_retirement():time.sleep(.01)
                self.assertFalse(service.manager.actors);self.assertEqual(factory.retired_ids,[1])
                self.assertTrue(service.housekeeping_errors)
                body=JournalStore(root,'fixture').read();self.assertFalse(body['retiringActors'])
                self.assertTrue(body['housekeepingErrors']);self.assertFalse(body['pending'])
            finally:service.close()


if __name__=='__main__':unittest.main()
