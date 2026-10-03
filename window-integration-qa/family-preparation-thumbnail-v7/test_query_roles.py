"""Query guards and gate regressions; no compositor, Quickshell or GUI starts."""
import json,multiprocessing,os,shutil,socket,subprocess,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
import helper_observer as h
import helper_setup as setup
import exec_gate
import private_shell
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import qa_launch

B=Path(__file__).resolve().parent

def gated_child(read_fd,write_fd,marker):
    os.close(write_fd)
    with patch.object(exec_gate,'require_qa_scope'),patch.object(exec_gate,'verify_runtime'):
        code=exec_gate.main([str(read_fd),'--','/usr/bin/python3','-c',
            'from pathlib import Path;import os;Path('+repr(str(marker))+').write_text(str(os.getpid()))'])
    os._exit(code)

class QueryRoles(unittest.TestCase):
    def test_real_gate_exec_keeps_registered_pid_start_and_eof_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            marker=Path(td)/'exec-marker'
            for release in (True,False):
                read_fd,write_fd=os.pipe();os.set_inheritable(read_fd,True)
                p=multiprocessing.get_context('fork').Process(target=gated_child,args=(read_fd,write_fd,marker));p.start();os.close(read_fd)
                identity=h.process(p.pid);self.assertFalse(marker.exists())
                if release:os.write(write_fd,b'1')
                os.close(write_fd);p.join(timeout=4);self.assertFalse(p.is_alive());self.assertFalse(h.still_live(identity))
                if release:
                    self.assertEqual(p.exitcode,0);self.assertEqual(marker.read_text(),str(identity['pid']));marker.unlink()
                else:self.assertEqual(p.exitcode,125);self.assertFalse(marker.exists())

    def test_query_summary_distinct_qs_lifetimes_and_one_harness(self):
        events=[]
        for key,role in [('hydrate',None),('inactive-fileDrag',None),('list-json:10:20','qs'),('list-json:11:21','qs'),('harness-list-json','harness')]:
            row=dict(event='started',operation=key,wrapper=dict(pid=2147483647,start='1',pgid=1),delegate=dict(pid=2147483646,start='1',pgid=1),queryRoot=role,**{'class':'query' if role else 'compositor'})
            events.extend([row,{**row,'event':'terminal','exitCode':0}])
        result=h.summarize(events,['hydrate','inactive-fileDrag'],expect_harness=True)
        self.assertEqual(result['harnessQueries'],1);self.assertEqual(len(result['queryOperations']),3)
        with self.assertRaises(RuntimeError):h.summarize(events+events[-2:],['hydrate','inactive-fileDrag'],expect_harness=True)
        with self.assertRaises(RuntimeError):h.summarize(events[:-2],['hydrate','inactive-fileDrag'],expect_harness=True)
        with self.assertRaises(RuntimeError):h.summarize(events[:-1]+[{**events[-1],'exitCode':7}],['hydrate','inactive-fileDrag'],expect_harness=True)

    def test_actual_taskbar_snapshot_delegates_unchanged_real_snap_query(self):
        try:qa_launch.require_qa_scope()
        except RuntimeError:self.skipTest('actual QA scope required for unmodified wrapper subprocess')
        with qa_launch.owned_runtime() as folder:
            runtime=Path(folder);home=runtime/'taskbar-home';shutil.copytree(B/'payload/home',home);private_shell.normalize_home_directories(home)
            env=dict(os.environ);env.update(HOME=str(home),XDG_RUNTIME_DIR=folder,HYPRLAND_INSTANCE_SIGNATURE='owned_fixture',PATH=str(home/'.local/bin')+':/usr/bin',OMARCHY_PATH=str(B/'payload/omarchy'),PYTHONDONTWRITEBYTECODE='1',XDG_DATA_DIRS=str(home/'empty'),XDG_DATA_HOME=str(home/'.local/share'),XDG_CONFIG_HOME=str(home/'.config'))
            # Exact production taskbar and Snap backend; only hyprctl is an owned
            # local JSON fixture. No real compositor IPC or session is contacted.
            ctl=home/'.local/bin/hyprctl';ctl.write_text('#!/usr/bin/python3\nimport sys\nprint("[]")\n');ctl.chmod(0o700)
            helpers={}
            for kind,name,source in [('snap','hypr-snap-groups',setup.FRESH_HELPER),('shell','omarchy-shell',B/'payload/omarchy/bin/omarchy-shell')]:
                wrapper=home/'.local/bin'/name;actual=wrapper.with_name(name+'.actual')
                shutil.copyfile(source,actual);actual.chmod(0o700);shutil.copyfile(B/'helper_observer.py',wrapper);wrapper.chmod(0o700)
                helpers[kind]=dict(wrapper=str(wrapper),actual=str(actual),wrapperSHA256=h.digest(wrapper),actualSHA256=h.digest(actual))
            log=home/'helper-events.jsonl';log.touch(mode=0o600)
            server=socket.socket(socket.AF_UNIX);endpoint=runtime/'fixture-ipc';server.bind(str(endpoint));server.listen();server.settimeout(.1)
            reply=b'{"queryTest":"owned local server; no compositor"}';info=endpoint.stat();stop=threading.Event();received=[]
            def serve():
                while not stop.is_set():
                    try:conn,_=server.accept()
                    except socket.timeout:continue
                    with conn:received.append(conn.recv(1024));conn.sendall(reply)
            thread=threading.Thread(target=serve);thread.start()
            config=dict(instance='owned_fixture',compositor=h.process(os.getpid()),socket=str(endpoint),socketIdentity=[info.st_dev,info.st_ino,info.st_uid],versionSHA256=h.digest_bytes(reply),helpers=helpers,log=str(log),allowed=[])
            path=home/'helper-config.json';env['WINDOW_QA_HELPER_CONFIG']=str(path)
            # QS metadata is registered but never launched by this test.
            setup.register_query_roots(env,config,dict(pid=2147483645,start='1',pgid=1),['/usr/bin/qs','-p',str(B/'payload/omarchy/shell')],h.process(os.getpid()),h.cmdline(os.getpid()))
            try:
                result=subprocess.run([str(home/'.local/bin/hypr-taskbar'),'snapshot'],env=env,text=True,capture_output=True,timeout=5,check=True)
                self.assertEqual(json.loads(result.stdout)['snapGroups'],[]);self.assertEqual(result.stderr,'')
                events=[json.loads(line) for line in log.read_text().splitlines()]
                result=h.summarize(events,[],expect_harness=True);self.assertTrue(result['allQueriesNormal']);self.assertEqual(result['queryOperations'],['harness-list-json'])
                self.assertEqual(events[0]['args'],['list','--json']);self.assertEqual(events[0]['ancestry'][1]['pid'],os.getpid());self.assertEqual(received,[b'j/version'])
                self.assertEqual(Path(helpers['snap']['actual']).read_bytes(),setup.FRESH_HELPER.read_bytes())
                # The production taskbar catches helper failure; the exact log
                # still refuses acceptance of a duplicate harness query.
                subprocess.run([str(home/'.local/bin/hypr-taskbar'),'snapshot'],env=env,text=True,capture_output=True,timeout=5,check=True)
                with self.assertRaises(RuntimeError):h.summarize([json.loads(line) for line in log.read_text().splitlines()],[],expect_harness=True)
            finally:stop.set();thread.join(timeout=2);server.close()

    def test_native_runner_registers_before_gate_and_checks_final_roles(self):
        source=(B/'native_integration.py').read_text()
        self.assertLess(source.index('register(helper_setup.observer.process(process.pid))'),source.index("os.write(write_fd,b'1')"))
        self.assertIn('expect_harness=True',source);self.assertIn("row['queryRoot']=='qs'",source)

if __name__=='__main__':unittest.main()
