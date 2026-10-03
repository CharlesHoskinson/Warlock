"""Exact actual launcher and frozen BasicDesktop queries in owned nongraphical processes."""
import ast,json,os,select,shutil,socket,subprocess,sys,threading,unittest
from pathlib import Path
import helper_observer as h
import helper_setup as setup
import private_shell
sys.path.insert(0,str(Path(__file__).resolve().parent.parent));import qa_launch
B=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v12')
MEMBERS=[dict(address='0x'+str(i+1),stableId=str(i+1),pid=1234) for i in range(3)]

class ServiceQueryTests(unittest.TestCase):
    def test_strict_exact_service_payloads_methods_identity_and_source(self):
        root=dict(source=str(__file__),sourceSHA256=h.digest(__file__),sources={})
        config=dict(queryRoots=dict(service=root),serviceMembers=MEMBERS,serviceTargetLimitPerMember=2,serviceRefreshLimit=3)
        for member in MEMBERS:
            self.assertEqual(h.service_operation(['hoskinson.windows','motionTarget',json.dumps(member)],config),('service-motionTarget:'+h.service_member(member),2))
        self.assertEqual(h.service_operation(['hoskinson.windows','motionRefresh','{}'],config),('service-motionRefresh',3))
        for payload in ['{}',json.dumps({**MEMBERS[0],'pid':True}),json.dumps({**MEMBERS[0],'pid':1.0}),json.dumps({**MEMBERS[0],'extra':1}),json.dumps({**MEMBERS[0],'address':'0x4'}),' {"address": "0x1", "stableId": "1", "pid": 1234}', '{"address":"0x1","address":"0x1","stableId":"1","pid":1234}', '{"address":"0x1","stableId":"1","pid":NaN}']:
            with self.assertRaises(RuntimeError,msg=payload):h.service_operation(['hoskinson.windows','motionTarget',payload],config)
        for args in [['hoskinson.windows','motionRefresh','{"extra": 1}'],['hoskinson.windows','motionCancel','{}'],['hoskinson.windows','motionTarget',json.dumps(MEMBERS[0]),'extra']]:
            with self.assertRaises(RuntimeError):h.service_operation(args,config)
        root['sourceSHA256']='0'*64
        with self.assertRaisesRegex(RuntimeError,'source changed'):h.service_operation(['hoskinson.windows','motionTarget',json.dumps(MEMBERS[0])],config)

    def test_actual_gated_service_queries_full_eof_unchanged_launcher_and_refusals(self):
        try:qa_launch.require_qa_scope()
        except RuntimeError:self.skipTest('actual QA scope required for unchanged wrapper processes')
        with qa_launch.owned_runtime() as folder:
            runtime=Path(folder);home=runtime/'taskbar-home';shutil.copytree(B/'payload/home',home);private_shell.normalize_home_directories(home);binary=home/'.local/bin'
            env=dict(os.environ);env.update(HOME=str(home),XDG_RUNTIME_DIR=folder,HYPRLAND_INSTANCE_SIGNATURE='owned_fixture',PATH=str(binary)+':/usr/bin',OMARCHY_PATH=str(B/'payload/omarchy'),WINDOW_QA_HELPER_CONFIG=str(home/'helper-config.json'))
            helpers={}
            for kind,name,source in [('snap','hypr-snap-groups',setup.FRESH_HELPER),('shell','omarchy-shell',B/'payload/omarchy/bin/omarchy-shell')]:
                wrapper=binary/name;actual=wrapper.with_name(name+'.actual');shutil.copyfile(source,actual);actual.chmod(0o700);shutil.copyfile(B/'helper_observer.py',wrapper);wrapper.chmod(0o700)
                helpers[kind]=dict(wrapper=str(wrapper),actual=str(actual),wrapperSHA256=h.digest(wrapper),actualSHA256=h.digest(actual))
            # The unchanged packaged launcher execs this nongraphical QS argv
            # recorder. No actual Quickshell/compositor/client is started.
            qs=binary/'qs';qs.write_text('#!/usr/bin/python3\nimport json,os,sys\nfrom pathlib import Path\nwith (Path(os.environ["HOME"])/"qs-argv.jsonl").open("a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\nprint(json.dumps({"fixture":"unchanged backend output","argv":sys.argv[1:]}))\n');qs.chmod(0o700)
            script=home/'service-fixture.py'
            script.write_text('''import ast,json,os,subprocess,sys
from pathlib import Path
source=Path(sys.argv[1]);tree=ast.parse(source.read_text());original=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='BasicDesktop');methods=[n for n in original.body if isinstance(n,ast.FunctionDef) and n.name in ('ipc','target')];node=ast.ClassDef(name='BasicDesktop',bases=[],keywords=[],body=methods,decorator_list=[]);ast.fix_missing_locations(node)
scope=dict(json=json,subprocess=subprocess,key=lambda w:(w['address'],str(w['stableId']),w['pid']));exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),scope);desktop=scope['BasicDesktop']()
print(json.dumps({'ready':True,'pid':os.getpid()}),flush=True)
for line in sys.stdin:
 request=json.loads(line)
 if request.get('operation')=='quit':break
 try:
  if request['operation']=='target':result=desktop.target(request['window'])
  elif request['operation']=='refresh':result=desktop.ipc('motionRefresh',{})
  else:result=json.loads(subprocess.check_output([str(Path.home()/'.local/bin/omarchy-shell'),*request['args']],text=True))
  print(json.dumps({'pass':True,'result':result}),flush=True)
 except Exception as error:print(json.dumps({'pass':False,'error':str(error)}),flush=True)
''');script.chmod(0o600)
            copied=home/'service-source';copied.mkdir(mode=0o700)
            for name in ('native_desktop.py','production_motion_6d9.py','scene_controller.py','native_runtime.py','context_provider.py','service_runtime.py'):shutil.copyfile(SERVICE/name,copied/name)
            log=home/'helper-events.jsonl';log.touch(mode=0o600)
            server=socket.socket(socket.AF_UNIX);endpoint=runtime/'fixture-ipc';server.bind(str(endpoint));server.listen();server.settimeout(.1);reply=b'{"serviceTest":"owned local IPC; no compositor"}';info=endpoint.stat();stop=threading.Event();requests=[]
            def serve():
                while not stop.is_set():
                    try:connection,_=server.accept()
                    except socket.timeout:continue
                    with connection:requests.append(connection.recv(1024));connection.sendall(reply)
            thread=threading.Thread(target=serve);thread.start()
            config=dict(instance='owned_fixture',compositor=h.process(os.getpid()),socket=str(endpoint),socketIdentity=[info.st_dev,info.st_ino,info.st_uid],versionSHA256=h.digest_bytes(reply),helpers=helpers,log=str(log),allowed=[],queryRoots={},queryEnvironment={key:env[key] for key in ('HOME','PATH','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','OMARCHY_PATH','WINDOW_QA_HELPER_CONFIG')})
            command=['/usr/bin/python3',str(script),str(copied/'production_motion_6d9.py')];read_fd,write_fd=os.pipe2(os.O_CLOEXEC)
            stderr=(home/'fixture-stderr').open('w')
            p=subprocess.Popen(['/usr/bin/python3',str(B/'exec_gate.py'),str(read_fd),'--',*command],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,pass_fds=(read_fd,),start_new_session=True);os.close(read_fd)
            def respond(request):
                p.stdin.write(json.dumps(request)+'\n');p.stdin.flush();ready,_,_=select.select([p.stdout],[],[],4);self.assertTrue(ready,'owned helper reply timeout');return json.loads(p.stdout.readline())
            try:
                identity=h.process(p.pid);self.assertEqual(select.select([p.stdout],[],[],0)[0],[])
                setup.register_service_root(env,config,identity,command,MEMBERS,copied);os.write(write_fd,b'1');os.close(write_fd);write_fd=-1
                ready,_,_=select.select([p.stdout],[],[],3);self.assertTrue(ready);self.assertEqual(json.loads(p.stdout.readline())['pid'],identity['pid']);self.assertEqual(h.process(p.pid)['start'],identity['start'])
                for _ in range(2):
                    for member in MEMBERS:
                        row=respond(dict(operation='target',window=member));self.assertTrue(row['pass'],row);self.assertEqual(row['result']['argv'],['ipc','-n','-p',env['OMARCHY_PATH']+'/shell','call','--','hoskinson.windows','motionTarget',json.dumps(member)])
                for _ in range(3):self.assertTrue(respond(dict(operation='refresh'))['pass'])
                events=[json.loads(line) for line in log.read_text().splitlines()];expected={'service-motionTarget:'+h.service_member(row):2 for row in MEMBERS};expected['service-motionRefresh']=3
                summary=h.summarize(events,[],expected_service=expected);self.assertEqual(summary['serviceQueries'],9);self.assertTrue(summary['allExactProcessesGone']);self.assertEqual(len(requests),9)
                # Authorized exact service caller must leave durable refusal.
                self.assertFalse(respond(dict(operation='target',window=MEMBERS[0]))['pass'])
                self.assertFalse(respond(dict(operation='args',args=['hoskinson.windows','motionCancel','{}']))['pass'])
                (copied/'native_desktop.py').write_text('changed owned source')
                self.assertFalse(respond(dict(operation='refresh'))['pass'])
                events=[json.loads(line) for line in log.read_text().splitlines()];self.assertEqual(len([e for e in events if e['event']=='refused']),3)
                self.assertEqual(len((home/'qs-argv.jsonl').read_text().splitlines()),9);self.assertEqual(len(requests),12)
                with self.assertRaises(RuntimeError):h.summarize(events,[],expected_service=expected)
                self.assertEqual(Path(helpers['shell']['actual']).read_bytes(),(B/'payload/omarchy/bin/omarchy-shell').read_bytes())
            finally:
                if write_fd!=-1:os.close(write_fd)
                if p.poll() is None:p.stdin.write('{"operation":"quit"}\n');p.stdin.flush()
                p.wait(timeout=5);p.stdin.close();p.stdout.close();stderr.close();stop.set();thread.join(timeout=2);server.close()
            self.assertEqual(p.returncode,0);self.assertFalse(h.still_live(identity))
            refusals=[e for e in events if e['event']=='refused']
            self.assertTrue(all(e['exitCode']==125 and e['delegateExecuted'] is False for e in refusals))
            self.assertEqual((home/'fixture-stderr').read_text(),''.join(e['stderr'] for e in refusals))

if __name__=='__main__':unittest.main()
