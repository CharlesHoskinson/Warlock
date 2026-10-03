#!/usr/bin/env python3
"""Actual daemon startup/Unix stream tests in isolated runtime with mocked hyprctl."""
import json,os,socket,subprocess,tempfile,time,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
HELPER=Path(os.environ.get('ATTENTION_SELECTION_HELPER',HERE/'hypr-taskbar-attention'))
LIVE=Path.home()/'.local/bin/hypr-taskbar-attention'

def wait(fn,label):
    deadline=time.monotonic()+4
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.02)
    raise AssertionError(label)

class Sandbox:
    def __init__(self,instances,explicit=''):
        self.directory=tempfile.TemporaryDirectory(prefix='attn-');self.root=Path(self.directory.name)
        self.sockets={}
        for index,name in enumerate(('main','nested')):
            path=self.root/'hypr'/name/'.socket2.sock';path.parent.mkdir(parents=True)
            server=socket.socket(socket.AF_UNIX);server.bind(str(path));server.listen();server.settimeout(2)
            os.utime(path,(1000+index,1000+index));self.sockets[name]=server
        (self.root/'instances.json').write_text(json.dumps(instances))
        (self.root/'hypr-taskbar-attention.json').write_text('{"original-cache":"preserved"}\n')
        self.original=(self.root/'hypr-taskbar-attention.json').read_bytes()
        binaries=self.root/'bin';binaries.mkdir();ctl=binaries/'hyprctl'
        ctl.write_text('''#!/usr/bin/env python3
import os,json,pathlib,sys
r=pathlib.Path(os.environ['XDG_RUNTIME_DIR'])
signature=os.environ.get('HYPRLAND_INSTANCE_SIGNATURE','')
with (r/'calls.jsonl').open('a') as out:out.write(json.dumps({'args':sys.argv[1:],'signature':signature})+'\\n')
if sys.argv[1]=='instances':print((r/'instances.json').read_text())
elif sys.argv[1]=='clients':print(json.dumps([{'address':'0x123','pid':99 if signature=='nested' else 42,'stableId':'nested-id' if signature=='nested' else 'main-id'}]))
else:print('{}')
''');ctl.chmod(0o755)
        self.env=dict(os.environ,XDG_RUNTIME_DIR=str(self.root),PATH=str(binaries)+':'+os.environ['PATH'])
        self.env.pop('HYPRLAND_INSTANCE_SIGNATURE',None)
        if explicit:self.env['HYPRLAND_INSTANCE_SIGNATURE']=explicit
        self.process=None;self.streams=[]
    def launch(self,helper=HELPER):
        self.process=subprocess.Popen([str(helper)],env=self.env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def accept(self,name):
        stream,_=self.sockets[name].accept();self.streams.append(stream);return stream
    def state(self):
        try:return json.loads((self.root/'hypr-taskbar-attention.json').read_text())
        except (OSError,ValueError):return None
    def calls(self):
        p=self.root/'calls.jsonl';return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
    def no_connections(self,test):
        for server in self.sockets.values():
            server.setblocking(False)
            with test.assertRaises(BlockingIOError):server.accept()
    def close(self):
        if self.process:
            if self.process.poll() is None:self.process.terminate()
            self.process.communicate(timeout=4)
        for stream in self.streams:stream.close()
        for server in self.sockets.values():server.close()
        self.directory.cleanup()
    def __enter__(self):return self
    def __exit__(self,*_args):self.close()

class Selection(unittest.TestCase):
    def test_unique_implicit_sets_same_query_and_stream_target(self):
        with Sandbox([{'instance':'main'}]) as box:
            box.launch();stream=box.accept('main');stream.sendall(b'urgent>>123\n')
            wait(lambda:box.state()=={'0x123':{'pid':42,'stableId':'main-id'}},'unique main urgency')
            calls=box.calls();self.assertEqual(calls[0]['args'],['instances','-j'])
            self.assertTrue(all(call['signature']=='main' for call in calls[1:]))
            box.sockets['nested'].setblocking(False)
            with self.assertRaises(BlockingIOError):box.sockets['nested'].accept()
    def test_ambiguous_implicit_fails_without_cache_or_lock_mutation(self):
        with Sandbox([{'instance':'main'},{'instance':'nested'}]) as box:
            box.launch();out,err=box.process.communicate(timeout=3)
            self.assertEqual(box.process.returncode,2);self.assertIn('unique',err)
            self.assertEqual((box.root/'hypr-taskbar-attention.json').read_bytes(),box.original)
            self.assertFalse((box.root/'.hypr-taskbar-attention.lock').exists());box.no_connections(self)
    def test_missing_implicit_fails_without_cache_mutation(self):
        with Sandbox([]) as box:
            box.launch();box.process.communicate(timeout=3)
            self.assertEqual(box.process.returncode,2)
            self.assertEqual((box.root/'hypr-taskbar-attention.json').read_bytes(),box.original);box.no_connections(self)
    def test_malformed_unique_instance_fails_without_cache_mutation(self):
        with Sandbox([{'instance':''}]) as box:
            box.launch();box.process.communicate(timeout=3)
            self.assertEqual(box.process.returncode,2)
            self.assertEqual((box.root/'hypr-taskbar-attention.json').read_bytes(),box.original);box.no_connections(self)
    def test_explicit_main_ignores_multiple_instances_and_newer_socket(self):
        with Sandbox([{'instance':'main'},{'instance':'nested'}],'main') as box:
            box.launch();stream=box.accept('main');stream.sendall(b'urgent>>123\n')
            wait(lambda:box.state()=={'0x123':{'pid':42,'stableId':'main-id'}},'explicit main urgency')
            self.assertTrue(all(c['signature']=='main' and c['args'][0]!='instances' for c in box.calls()))
            box.sockets['nested'].setblocking(False)
            with self.assertRaises(BlockingIOError):box.sockets['nested'].accept()
    def test_explicit_absent_never_falls_back(self):
        with Sandbox([{'instance':'main'}],'absent') as box:
            box.launch();wait(lambda:box.state()=={},'explicit absent startup cache cleared as existing behavior')
            box.no_connections(self);self.assertEqual(box.calls(),[])
            self.assertIsNone(box.process.poll())

def reproduce_live():
    with Sandbox([{'instance':'main'},{'instance':'nested'}]) as box:
        box.launch(LIVE);stream=box.accept('nested');stream.sendall(b'urgent>>123\n')
        wait(lambda:box.state()=={'0x123':{'pid':42,'stableId':'main-id'}},'live wrong-instance urgency reproduced')
        result={'reproduced':True,'selectedStream':'nested (newest socket)','queryDefaultTarget':'main','queryEnvironment':box.calls(),'resultingFalseMainUrgency':box.state(),'cachedStateChangedBeforeAmbiguityResolved':(box.root/'hypr-taskbar-attention.json').read_bytes()!=box.original}
        (HERE/'live-mismatch-reproduction.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':
    import sys
    if '--reproduce-live' in sys.argv:reproduce_live()
    else:unittest.main()
