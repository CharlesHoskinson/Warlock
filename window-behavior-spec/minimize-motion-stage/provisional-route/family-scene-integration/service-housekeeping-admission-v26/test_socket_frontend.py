import json
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from socket_frontend import SocketFrontend
from scene_manager import SceneManager
from test_scene_controller import Desktop,Transport

class FrontendTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='mf-');self.root=Path(self.temp.name)
        self.d=Desktop();self.transports=[];self.gate=threading.Event();self.entered=threading.Event()
        def factory(number):t=Transport();self.transports.append(t);return self.d,t
        self.m=SceneManager(factory)
        def provider(request):self.entered.set();self.gate.wait(2);return ('actual-provider',1)
        self.f=SocketFrontend(self.root/'api',self.m,provider);self.f.start()
    def tearDown(self):self.gate.set();self.f.close();self.temp.cleanup()
    def call(self,request):
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
            c.settimeout(2);c.connect(str(self.f.path));c.sendall(json.dumps(request).encode()+b'\n');data=b''
            while b'\n' not in data:data+=c.recv(8192)
            return json.loads(data)
    def request(self,index=0,op='minimize',**extra):
        w=self.d.windows[index]
        return self.call({'command':'request','operation':op,'address':w['address'],'stableId':w['stableId'],'pid':w['pid'],**extra})
    def wait(self,p):
        end=time.monotonic()+2
        while time.monotonic()<end:
            if p():return
            time.sleep(.002)
        self.fail('frontend context boundary timeout')
    def test_actual_socket_acceptance_precedes_blocked_context_and_state_stays_responsive(self):
        result=self.request();self.assertTrue(result['accepted']);self.assertFalse(result['completed']);self.assertTrue(self.entered.wait(1))
        state=self.call({'command':'state'});self.assertEqual(state['pendingReceipts'],[result['receipt']]);self.assertFalse(self.d.commits)
        self.assertEqual(self.f.path.stat().st_mode&0o777,0o600)
        self.gate.set();self.wait(lambda:any(e['command']=='seed' for t in self.transports for e in t.sent))
    def test_frontend_cannot_forge_context_or_trigger_native_operation(self):
        result=self.request(context='fake-current-workspace');self.assertFalse(result['accepted']);self.assertIn('service-owned',result['error'])
        self.assertFalse(self.m.actors);self.assertFalse(self.d.commits)
    def test_bounded_context_queue_refuses_before_second_receipt(self):
        self.f.max_pending=1;first=self.request();self.assertTrue(self.entered.wait(1))
        second=self.request();self.assertFalse(second['accepted']);self.assertIn('unavailable',second['error'])
        self.assertEqual(self.m.serial,first['receipt'])
    def latest_completed(self,receipt):
        with self.m.lock:
            return not self.m.pending and all(a.controller.current is None for a in self.m.actors) and any(h.profile.get('managerReceipt')==receipt and 'cleanupAckNs' in h.profile for a in self.m.actors for h in a.controller.history)
    def test_reversed_context_completion_never_changes_latest_scene(self):
        first=self.request();self.assertTrue(self.entered.wait(1));second=self.request(op='restore')
        self.gate.set();self.wait(lambda:self.latest_completed(second['receipt']))
        active=[a.controller.current for a in self.m.actors if a.controller.current]
        self.assertFalse(active);self.wait(lambda:len(self.d.commits)==3)
        done=self.m.actors[0].controller.history[-1]
        self.assertEqual(done.profile['managerReceipt'],second['receipt']);self.assertEqual(done.operation,'restore')
        self.assertTrue(done.profile['nativeEndpointAlreadySatisfied']);self.assertFalse(any(t.sent for t in self.transports))
        self.assertTrue(any(h.get('superseded') and h['receipt']==first['receipt'] for h in self.m.ingress_history))
    def test_shutdown_only_removes_own_socket_identity(self):
        self.f.path.unlink();replacement=self.f.path;replacement.write_text('other-owned-file')
        self.f.close();self.assertEqual(replacement.read_text(),'other-owned-file')

if __name__=='__main__':unittest.main()
