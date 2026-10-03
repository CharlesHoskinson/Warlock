import hashlib
from pathlib import Path
import struct
import tempfile
import threading
import time
import unittest
import zlib
from test_scene_controller import Desktop,Transport
from scene_controller import SceneController

def png(width,height):
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    pixels=(b'\0'+bytes((180,50,25,255))*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b'')

class FileDesktop(Desktop):
    def __init__(self,path):super().__init__();self.path=path;self.fail_member=None;self.created=[];self.removed=[]
    def capture_source(self,w,token,index):
        if index==self.fail_member:raise RuntimeError('injected member capture failure')
        source=super().capture_source(w,token,index)
        path=self.path/(token+'-'+str(index)+'.png');path.write_bytes(png(*w['size']));path.chmod(0o600)
        source['path']=str(path);source['digest']=hashlib.sha256(path.read_bytes()).hexdigest();self.created.append(path)
        return source
    def release_sources(self,sources):
        super().release_sources(sources)
        for source in sources:
            path=Path(source['path']);path.unlink(missing_ok=True);self.removed.append(path)

class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.d=FileDesktop(Path(self.temp.name));self.t=Transport();self.c=SceneController(self.d,self.t)
    def tearDown(self):self.c.workers.shutdown(wait=True,cancel_futures=True);self.temp.cleanup()
    def request(self,op='minimize'):
        w=self.d.windows[0];return self.c.request(op,w['address'],w['stableId'],w['pid'],context=1)
    def wait(self,p):
        end=time.monotonic()+3
        while time.monotonic()<end:
            if p():return
            time.sleep(.002)
        self.fail('capture lease boundary timeout')
    def assert_released(self,count):
        self.wait(lambda:len(self.d.removed)==count)
        self.assertEqual(len(self.d.created),count);self.assertFalse(any(path.exists() for path in self.d.created))
    def test_member_two_capture_failure_releases_first_actual_png(self):
        self.d.fail_member=1;self.request();self.assert_released(1)
        self.assertFalse(any(m['command']=='seed' for m in self.t.sent))
    def test_ensure_outputs_failure_releases_all_completed_actual_pngs(self):
        def fail(force=False):raise RuntimeError('injected output preparation failure')
        self.t.ensure_outputs=fail;self.request();self.assert_released(3)
        self.assertFalse(any(m['command']=='seed' for m in self.t.sent))
    def test_post_capture_geometry_rejection_releases_entire_local_lease(self):
        original=self.t.ensure_outputs
        def mutate(force=False):self.d.windows[1]['at'][0]+=20;return original(force)
        self.t.ensure_outputs=mutate;self.request();self.assert_released(3)
        self.assertFalse(any(m['command']=='seed' for m in self.t.sent))
    def test_superseded_completed_lease_cannot_delete_new_scene_pngs(self):
        original=self.t.ensure_outputs;observed=threading.Event();release=threading.Event();calls=0
        def blocked(force=False):
            nonlocal calls
            calls+=1
            if calls==1:observed.set();release.wait(3)
            return original(force)
        self.t.ensure_outputs=blocked;first=self.request();self.assertTrue(observed.wait(1));second=self.request('minimize')
        self.wait(lambda:any(m['command']=='seed' and m['token']==second['token'] for m in self.t.sent))
        release.set();self.wait(lambda:len(self.d.removed)==3)
        old=[p for p in self.d.created if p.name.startswith(first['token']+'-')];new=[p for p in self.d.created if p.name.startswith(second['token']+'-')]
        self.assertEqual(len(old),3);self.assertEqual(len(new),3);self.assertFalse(any(p.exists() for p in old));self.assertTrue(all(p.exists() for p in new))
        self.assertFalse(any(m['command']=='seed' and m['token']==first['token'] for m in self.t.sent))

if __name__=='__main__':unittest.main()
