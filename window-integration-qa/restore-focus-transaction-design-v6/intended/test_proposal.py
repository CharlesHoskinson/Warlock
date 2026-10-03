"""CPU-only proposal execution: pure framing and real owned CLI/Keeper jobs.

The Unix peer supplies fixture receipts; it never executes Lua/native effects.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest

HERE=Path(__file__).resolve().parent
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
sys.path.insert(0,str(BASE))

def load(name):
    module=SimpleNamespace()
    import types
    module=types.ModuleType(name);module.__file__=str(BASE/(name+'.py'))
    sys.modules[name]=module
    exec(compile((HERE/(name+'.py.proposed')).read_text(),module.__file__,'exec'),module.__dict__)
    return module

owned=load('owned_commands');native=load('native_desktop')
from helper_supervisor import Keeper
from recovery_resources import process_start

OBSERVATIONS=[]
NONCE='0123456789abcdef0123456789abcdef'
EXPRESSION='local n=0; print("an echoed JSON receipt is not authority")'
def receipt(count=2,nonce=NONCE,**changes):
    row={'nonce':nonce,'expected':6,'completed':count,'ok':True};row.update(changes)
    return json.dumps(row,separators=(',',':')).encode()+b'\n'
def framed(expression=EXPRESSION,result=None,clear=False):
    return (b'> \x1b[H\x1b[2J> ' if clear else b'> ')+expression.encode()+b'\n'+(receipt() if result is None else result)+b'> '

class ParserTests(unittest.TestCase):
    def parse(self,data,expression=EXPRESSION):return owned.OwnedCommands._focus_reply(data,expression,NONCE,6,2)
    def test_plain_and_observed_readline_clear(self):
        for clear in (False,True):self.assertEqual(self.parse(framed(clear=clear))[0]['completed'],2)
    def test_partial_frames_are_never_usable(self):
        data=framed(clear=True)
        for index in range(len(data)):self.assertIsNone(self.parse(data[:index]))
    def test_echoed_receipt_never_authorizes(self):
        expression='local s='+json.dumps(receipt().decode().strip())+'; print(s)'
        echo=b'> '+expression.encode()+b'\n'
        self.assertIsNone(self.parse(echo,expression))
        self.assertIsNone(self.parse(echo+b'> ',expression))
    def test_unexpected_ansi_refuses(self):
        for data in (b'\x1b[31m'+framed(),framed().replace(b'> ',b'> \x1b[0m',1),framed().replace(b'\n{',b'\n\x1b[H{')):
            with self.assertRaises(ValueError):self.parse(data)
    def test_duplicate_or_extra_receipt_refuses(self):
        for data in (framed(result=receipt()+receipt()),framed()+receipt()):
            with self.assertRaises(ValueError):self.parse(data)
    def test_wrong_prior_nonce_refuses(self):
        with self.assertRaises(ValueError):self.parse(framed(result=receipt(nonce='f'*32)))
    def test_out_of_order_duplicate_prefix_refuses(self):
        for count in (0,4,6):
            with self.assertRaises(ValueError):self.parse(framed(result=receipt(count)))
    def test_duplicate_keys_and_bool_numeric_alias_refuse(self):
        for data in (receipt().replace(b'"expected":6',b'"expected":6,"expected":6'),receipt(expected=True),receipt(completed=2.0),receipt(ok=1)):
            with self.assertRaises(ValueError):self.parse(framed(result=data))
    def test_semantic_error_and_non_json_refuse(self):
        for data in (receipt(ok=False),b'error: failed\n',b'{"nonce": NaN}\n'):
            with self.assertRaises(ValueError):self.parse(framed(result=data))
    def test_changed_echo_and_extra_prompt_refuse(self):
        for data in (framed(expression=EXPRESSION+';'),framed()+b'> '):
            with self.assertRaises(ValueError):self.parse(data)
    def test_actual_retained_cli_stream(self):
        root=HERE.parent.parent/'restore-focus-interactive-cli-cpu-v1'
        report=json.loads((root/'report.json').read_text());buffer=(root/'stdout.bin').read_bytes()
        for index,request in enumerate(report['requests']):
            expression=request[len('/repl '):]
            # Parse one exact conversation, leaving its prompt for the next.
            boundary=report['boundaries'][index]['stdoutBytes']
            start=report['boundaries'][index-1]['stdoutBytes']-2 if index else 0
            portion=buffer[start:boundary]
            row,consumed=owned.OwnedCommands._focus_reply(portion,expression,NONCE,6,(index+1)*2)
            self.assertEqual(row['completed'],(index+1)*2);self.assertEqual(portion[consumed:],b'> ')

class KernelConversationTests(unittest.TestCase):
    def run_case(self,mode):
        with tempfile.TemporaryDirectory(prefix='focus-owned-cpu-',dir='/run/user/1000') as raw:
            runtime=Path(raw);runtime.chmod(0o700);session='owned-fixture';peer_dir=runtime/'hypr'/session;peer_dir.mkdir(parents=True,mode=0o700)
            actor_root=runtime/'actor';actor_root.mkdir(mode=0o700)
            state_dir=runtime/'hypr-windowctl';state_dir.mkdir(mode=0o700)
            windows=[{'address':'0x'+str(index+1),'stableId':str(index+1),'pid':os.getpid(),'mapped':True} for index in range(3)]
            monitor={'id':0,'name':'CPU-fixture-output','x':0,'y':0,'width':1600,'height':1000,'scale':1.0,'transform':0}
            plans=[]
            for window in windows:
                state=state_dir/window['address'];state.write_text('1 unused '+window['stableId']);metadata={'pid':window['pid'],'stableId':window['stableId'],'homeWorkspace':1};state.with_name(state.name+'.monitor.json').write_text(json.dumps(metadata))
                plans.append((copy.deepcopy(window),{'identity':list(native.key(window)),'destination':'1','monitor':dict(monitor),'storedFields':state.read_text().split(),'storedMetadata':metadata}))
            env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime),HYPRLAND_INSTANCE_SIGNATURE=session,WAYLAND_DISPLAY='cpu-only-never-connect')
            journal=[];keeper=Keeper(actor_root,env,lambda row:journal.append(copy.deepcopy(row)))
            commands=owned.OwnedCommands(keeper,env,17)
            owner=native.NativeDesktop.__new__(native.NativeDesktop);owner.commands=commands;owner.production=SimpleNamespace(RUNTIME=runtime)
            observation_times={}
            def final_monitors():
                if mode=='final-observation-expiry':
                    observation_times['startNs']=time.monotonic_ns();deadline=record.profile['receivedNs']+2000000000;gate=threading.Event()
                    timer=threading.Timer(max(0,(deadline-time.monotonic_ns())/1000000000)+.015,gate.set);timer.start()
                    try:self.assertTrue(gate.wait(timeout=2.5))
                    finally:timer.join(timeout=3)
                    observation_times['endNs']=time.monotonic_ns();self.assertGreaterEqual(observation_times['endNs'],deadline)
                return [dict(monitor)]
            owner.base=SimpleNamespace(clients=lambda:copy.deepcopy(windows),monitors=final_monitors)
            record=SimpleNamespace(profile={'receivedNs':time.monotonic_ns()})
            socket_owner=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);socket_owner.bind(str(peer_dir/'.socket.sock'));socket_owner.listen(4);socket_owner.settimeout(.1)
            stopped=threading.Event();requests=[];peer_errors=[]
            def peer():
                while not stopped.is_set():
                    try:connection,_=socket_owner.accept()
                    except socket.timeout:continue
                    try:
                        data=connection.recv(65536);requests.append(data)
                        packet=record.profile['ownedDestinationTransaction'];count=2*len(requests)
                        reply={'nonce':packet['nonce'],'expected':6,'completed':count,'ok':True}
                        if mode=='partial' and count==4:reply['ok']=False;reply['completed']=3
                        if mode=='wrong-prefix' and count==2:reply['completed']=4
                        if mode=='stale-material' and count==2:(state_dir/windows[1]['address']).write_text('2 unused '+windows[1]['stableId'])
                        if mode=='reused-lifetime' and count==2:windows[1]['pid']+=1
                        if mode=='output-post-receipt' and count==6:monitor['scale']=2.0
                        if mode=='EOF':connection.close();continue
                        connection.sendall(json.dumps(reply,separators=(',',':')).encode());connection.close()
                    except BaseException as error:peer_errors.append(repr(error));break
            thread=threading.Thread(target=peer);thread.start();failure=None
            try:
                if mode=='foreign-guard':owner._guard_destination=lambda window,plan:None
                try:owner.apply_destinations(plans,current=lambda:True,reservation_lock=threading.RLock(),deadline_ns=record.profile['receivedNs']+2000000000,record=record)
                except (ValueError,TimeoutError,EOFError) as error:failure=str(error)
                packet=record.profile.get('ownedDestinationTransaction',{})
                if mode=='normal':
                    self.assertIsNone(failure);self.assertEqual(len(requests),3);self.assertEqual(packet['completed'],6);self.assertTrue(packet['normalComplete']);self.assertFalse(keeper.jobs)
                    released=[r['jobs'][0] for r in journal if r['jobs'] and r['jobs'][0]['phase']=='released']
                    self.assertEqual(len({row['job'] for row in released}),1);self.assertEqual({row['kind'] for row in released},{'native-effect'})
                    self.assertEqual(released[0]['ownership']['targetArgv'],['/usr/bin/hyprctl','repl'])
                    self.assertEqual(len(packet['expressions']),3)
                else:
                    self.assertIsNotNone(failure)
                    if mode=='foreign-guard':self.assertFalse(keeper.jobs);self.assertFalse(requests)
                    else:self.assertEqual(len(keeper.jobs),1);self.assertFalse(packet['normalComplete'])
                    maximum={'partial':2,'wrong-prefix':1,'stale-material':1,'reused-lifetime':1,'EOF':1,'foreign-guard':0,'output-post-receipt':3,'final-observation-expiry':3}[mode]
                    self.assertEqual(len(requests),maximum)
                self.assertFalse(peer_errors)
                OBSERVATIONS.append({'mode':mode,'failure':failure,'requests':[data.decode() for data in requests],
                    'packet':copy.deepcopy(packet),'observationTimes':observation_times,'liveSnapshotBeforeCleanup':keeper.snapshot(),'journal':copy.deepcopy(journal)})
                return {'mode':mode,'failure':failure,'requests':len(requests),'jobsRemaining':len(keeper.jobs),'normalComplete':packet.get('normalComplete')}
            finally:
                stopped.set();thread.join(timeout=2);socket_owner.close()
                if keeper.jobs:keeper.abort()
                else:keeper.stop()
                self.assertTrue(keeper.closed);self.assertEqual(keeper.process.returncode,0)
                OBSERVATIONS[-1]['terminalAfterCleanup']=copy.deepcopy(keeper.ownership['terminal'])
    def test_actual_owned_positive_three_prefixes_one_job(self):self.run_case('normal')
    def test_partial_receipt_keeps_native_uncertainty(self):self.run_case('partial')
    def test_wrong_prefix_never_sends_second_pair(self):self.run_case('wrong-prefix')
    def test_original_stored_material_guard_blocks_next_pair(self):self.run_case('stale-material')
    def test_original_fresh_lifetime_guard_blocks_next_pair(self):self.run_case('reused-lifetime')
    def test_process_EOF_without_receipt_not_native_completion(self):self.run_case('EOF')
    def test_foreign_guard_refuses_before_launch(self):self.run_case('foreign-guard')
    def test_final_observation_expiry_retains_native_uncertainty(self):self.run_case('final-observation-expiry')
    def test_changed_output_after_last_receipt_cannot_complete(self):self.run_case('output-post-receipt')

if __name__=='__main__':
    sys.path.insert(0,'/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    scope=require_qa_scope();result=unittest.main(verbosity=2,exit=False).result
    report={'result':'pass' if result.wasSuccessful() else 'fail','tests':result.testsRun,'failures':[(str(t),e) for t,e in result.failures+result.errors],
        'scope':scope,'CPUProtocolOnly':True,'nativeLuaExecuted':False,'runtimeApplied':False,'observations':OBSERVATIONS}
    with os.fdopen(os.open(HERE/'focused-observations.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:json.dump(report,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    raise SystemExit(not result.wasSuccessful())
