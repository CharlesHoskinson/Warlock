"""Real local socket/process/exec checks; fixtures never contact a compositor."""
from pathlib import Path
import json
import multiprocessing
import os
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch
import helper_observer as h


def delegated_fixture(runtime, config, result, args=None, kind='snap'):
    os.environ.update(HOME=str(Path(runtime)/'taskbar-home'), XDG_RUNTIME_DIR=runtime,
                      HYPRLAND_INSTANCE_SIGNATURE='owned_fixture', WINDOW_QA_HELPER_CONFIG=str(config),PATH=str(Path(runtime)/'taskbar-home/.local/bin')+':/usr/bin',WAYLAND_DISPLAY='sandbox-no-real-display',DBUS_SESSION_BUS_ADDRESS='unix:path='+str(Path(runtime)/'sandbox-bus'),OMARCHY_PATH=str(Path(runtime)/'packaged'))
    with patch.object(h, 'require_qa_scope', return_value={'cgroup': Path('/proc/self/cgroup').read_text().strip(), 'coreLimit': 1}), patch.object(h, 'verify_runtime', return_value=Path(runtime)), patch.object(h, 'ipc_proof', return_value={'fixtureOnly': True}):
        try:
            source=h.read_config(config);code=h.run(['hydrate'] if args is None else args,entry=source['helpers'][kind]['wrapper']); result.put(('exit', code))
        except Exception as error:
            result.put(('refused', str(error)))


class HelperTests(unittest.TestCase):
    def test_strict_exact_operation_identity(self):
        self.assertEqual(h.operation(['forget-closed','0xbeef','abc','12']), 'forget-closed:0xbeef:abc:12')
        for args in ([], ['unsnap','0xbeef'], ['hydrate','extra'], ['forget-closed','0xbeef','abc','-1'], ['forget-closed','../../x','abc','12']):
            with self.assertRaises(RuntimeError): h.operation(args)

    def test_real_unix_peer_full_eof_and_actual_reply(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sock'; server=socket.socket(socket.AF_UNIX);server.bind(str(path));server.listen()
            reply=b'{"fixture":"owned local server"}';received=[]
            def serve():
                with server.accept()[0] as conn:
                    received.append(conn.recv(4096));conn.sendall(reply)
            thread=threading.Thread(target=serve);thread.start();info=path.lstat()
            c={'socket':str(path),'socketIdentity':[info.st_dev,info.st_ino,info.st_uid], 'compositor':{'pid':os.getpid()},'versionSHA256':h.digest_bytes(reply)}
            row=h.ipc_proof(c);thread.join(timeout=3);server.close()
            self.assertFalse(thread.is_alive());self.assertEqual(received,[b'j/version']);self.assertTrue(row['completeServerEOF']);self.assertEqual(row['peer']['pid'],os.getpid())

    def test_wrong_actual_socket_peer_refuses_before_send(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sock';server=socket.socket(socket.AF_UNIX);server.bind(str(path));server.listen();info=path.lstat()
            c={'socket':str(path),'socketIdentity':[info.st_dev,info.st_ino,info.st_uid], 'compositor':{'pid':2147483647}}
            with self.assertRaisesRegex(RuntimeError,'peer mismatch'):h.ipc_proof(c)
            with server.accept()[0] as conn:self.assertEqual(conn.recv(100),b'')
            server.close()

    def test_symlink_config_refuses(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);(p/'source').write_text('{}');(p/'source').chmod(0o600);(p/'link').symlink_to(p/'source')
            with self.assertRaises(RuntimeError):h.read_config(p/'link')

    def test_actual_opened_descriptor_swap_refuses_even_if_path_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);config=p/'config';other=p/'other';saved=p/'saved'
            config.write_text('{"owned":"original"}');other.write_text('{"owned":"replacement"}')
            config.chmod(0o600);other.chmod(0o600);actual_open=os.open
            def swapped(path,flags,*args,**kwargs):
                config.rename(saved);other.rename(config)
                try:return actual_open(path,flags,*args,**kwargs)
                finally:config.rename(other);saved.rename(config)
            with patch.object(h.os,'open',side_effect=swapped):
                with self.assertRaisesRegex(RuntimeError,'Opened helper configuration identity differs'):h.read_config(config)
            self.assertEqual(h.read_config(config),{'owned':'original'})

    def test_real_gated_exec_once_argv_status_and_duplicate_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime=Path(folder);home=runtime/'taskbar-home';binary=home/'.local/bin';binary.mkdir(parents=True)
            for p in (home,home/'.local',binary):p.chmod(0o700)
            wrapper=binary/'hypr-snap-groups';wrapper.write_bytes(Path(h.__file__).read_bytes());wrapper.chmod(0o700)
            actual=binary/'hypr-snap-groups.actual';actual.write_text('#!/usr/bin/python3\nimport os,sys,json\nfrom pathlib import Path\np=Path(os.environ["HOME"])/"calls"\nwith p.open("a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\n');actual.chmod(0o700)
            log=home/'helper-events.jsonl';log.touch(mode=0o600)
            conf=home/'helper-config.json';c={'instance':'owned_fixture','compositor':h.process(os.getpid()),'wrapper':str(wrapper),'actual':str(actual),'wrapperSHA256':h.digest(wrapper),'actualSHA256':h.digest(actual),'log':str(log),'allowed':['hydrate']};conf.write_text(json.dumps(c));conf.chmod(0o600)
            shell=binary/'omarchy-shell';shell.write_bytes(Path(h.__file__).read_bytes());shell.chmod(0o700)
            shell_actual=binary/'omarchy-shell.actual';shell_actual.write_bytes(actual.read_bytes());shell_actual.chmod(0o700)
            c['helpers']={'snap':{key:c[key] for key in ('wrapper','actual','wrapperSHA256','actualSHA256')},'shell':{'wrapper':str(shell),'actual':str(shell_actual),'wrapperSHA256':h.digest(shell),'actualSHA256':h.digest(shell_actual),'invocation':'omarchy-shell'}}
            conf.write_text(json.dumps(c))
            context=multiprocessing.get_context('fork');queue=context.Queue()
            first=context.Process(target=delegated_fixture,args=(folder,conf,queue));first.start();first.join(timeout=5)
            self.assertFalse(first.is_alive());self.assertEqual(queue.get(timeout=1),('exit',0));self.assertEqual(first.exitcode,0)
            events=[json.loads(x) for x in log.read_text().splitlines()];summary=h.summarize(events,{'hydrate'});self.assertTrue(summary['allExactProcessesGone'])
            self.assertEqual((home/'calls').read_text(), '["hydrate"]\n')
            self.assertEqual(events[0]['ancestry'][0]['pid'],os.getpid());self.assertNotEqual(events[0]['wrapper']['pid'],events[0]['delegate']['pid'])
            second=context.Process(target=delegated_fixture,args=(folder,conf,queue));second.start();second.join(timeout=5)
            self.assertFalse(second.is_alive());answer=queue.get(timeout=1);self.assertEqual(answer[0],'refused');self.assertIn('Duplicate',answer[1]);self.assertEqual((home/'calls').read_text(),'["hydrate"]\n')

    def test_exact_terminal_identity_required(self):
        start={'event':'started','operation':'hydrate','wrapper':{'pid':1,'start':'1','pgid':1},'delegate':{'pid':2,'start':'2','pgid':1}}
        terminal={**start,'event':'terminal','exitCode':0};terminal['delegate']={**start['delegate'],'start':'new'}
        with self.assertRaisesRegex(RuntimeError,'completion mismatch'):h.summarize([start,terminal],{'hydrate'})

    def test_nonzero_and_unknown_events_never_accept(self):
        start={'event':'started','operation':'hydrate','wrapper':{},'delegate':{}}
        with self.assertRaises(RuntimeError):h.summarize([start,{**start,'event':'terminal','exitCode':1}],{'hydrate'})
        with self.assertRaises(RuntimeError):h.summarize([{'event':'refused','operation':'unexpected'}],{'hydrate'})


if __name__=='__main__':unittest.main()
