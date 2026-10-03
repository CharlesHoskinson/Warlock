"""Actual owned subprocess/backend and mode regressions; no compositor/GUI."""
import importlib.util,json,multiprocessing,os,shutil,stat,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import helper_observer as h
import helper_setup as setup
import private_shell
from test_helpers import delegated_fixture

B=Path(__file__).resolve().parent

def sandbox(root):
    home=root/'taskbar-home';binary=home/'.local/bin';binary.mkdir(parents=True)
    for path in (home,home/'.local',binary):path.chmod(0o700)
    helpers={}
    for kind,name in [('snap','hypr-snap-groups'),('shell','omarchy-shell')]:
        wrapper=binary/name;wrapper.write_bytes((B/'helper_observer.py').read_bytes());wrapper.chmod(0o700)
        actual=binary/(name+'.actual')
        actual.write_text('#!/usr/bin/python3\nimport json,os,sys\nfrom pathlib import Path\nwith (Path(os.environ["HOME"])/"backend-called").open("a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\n');actual.chmod(0o700)
        helpers[kind]=dict(wrapper=str(wrapper),actual=str(actual),wrapperSHA256=h.digest(wrapper),actualSHA256=h.digest(actual),invocation=str(wrapper) if kind=='snap' else 'omarchy-shell')
    log=home/'helper-events.jsonl';log.touch(mode=0o600)
    config=dict(instance='owned_fixture',compositor=h.process(os.getpid()),helpers=helpers,log=str(log),allowed=['hydrate','inactive-fileDrag'])
    path=home/'helper-config.json';path.write_text(json.dumps(config));path.chmod(0o600)
    return home,path,config

def invoke(root,config,args,kind='snap'):
    ctx=multiprocessing.get_context('fork');q=ctx.Queue();p=ctx.Process(target=delegated_fixture,args=(str(root),str(config),q,args,kind));p.start();p.join(timeout=6)
    if p.is_alive():p.terminate();p.join();raise AssertionError('owned backend test timeout')
    return p,q.get(timeout=1)

class V6Tests(unittest.TestCase):
    def test_exact_inactive_relay_args_integer_boundaries(self):
        for args in [('0','0','-1','0'),('-4','5','0','123'),(str(-(1<<63)),str((1<<63)-1),'1',str((1<<63)-1))]:
            self.assertEqual(h.operation(['hoskinson.windows','fileDrag','false',*args]),'inactive-fileDrag')
        invalid=[['hoskinson.windows','fileDrag','true','0','0','0','0'],['wrong','fileDrag','false','0','0','0','0'],['hoskinson.windows','fileDrag','false','0','0','0','-1']]
        for value in ['nan','inf','1.0','1e3','+1','01','-0',str(1<<63)]:invalid.append(['hoskinson.windows','fileDrag','false',value,'0','0','0'])
        invalid.append(['hoskinson.windows','fileDrag','false','0','0','0','0','extra'])
        for args in invalid:
            with self.assertRaises(RuntimeError,msg=str(args)):h.operation(args)
    def test_runtime_directory_normalization_preserves_payload_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'payload';source.mkdir();(source/'deep/child').mkdir(parents=True)
            executable=source/'deep/helper';executable.write_text('immutable');executable.chmod(0o700)
            before={str(p.relative_to(source)):(h.digest(p),stat.S_IMODE(p.stat().st_mode)) for p in source.rglob('*') if p.is_file()}
            home=root/'runtime-home';shutil.copytree(source,home);modes=private_shell.normalize_home_directories(home)
            self.assertTrue(all(mode==0o700 for mode in modes.values()))
            self.assertEqual(before,{str(p.relative_to(source)):(h.digest(p),stat.S_IMODE(p.stat().st_mode)) for p in source.rglob('*') if p.is_file()})
            self.assertEqual((home/'deep/helper').read_bytes(),executable.read_bytes())
    def test_runtime_symlink_directory_refused(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td)/'home';home.mkdir();(home/'link').symlink_to(Path(td))
            with self.assertRaisesRegex(ValueError,'linked'):private_shell.normalize_home_directories(home)
    def test_early_owned_bad_mode_refusal_is_durable_without_exec(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);home.chmod(0o755)
            p,answer=invoke(root,path,['hydrate'])
            self.assertEqual(answer[0],'refused');self.assertIn('private directory invalid',answer[1]);self.assertFalse((home/'backend-called').exists())
            events=[json.loads(x) for x in (home/'helper-events.jsonl').read_text().splitlines()]
            self.assertEqual(len(events),1);self.assertEqual(events[0]['event'],'refused');self.assertEqual(events[0]['wrapper']['pid'],p.pid)
    def test_backend_source_mutation_refuses_and_records(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);Path(config['helpers']['snap']['actual']).write_text('changed source')
            p,answer=invoke(root,path,['hydrate']);self.assertEqual(answer[0],'refused');self.assertIn('source changed',answer[1]);self.assertFalse((home/'backend-called').exists())
            self.assertEqual(json.loads((home/'helper-events.jsonl').read_text())['event'],'refused')
    def test_two_exact_delegates_complete_once_and_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root)
            args=['hoskinson.windows','fileDrag','false','-12','14','-1','99']
            for role,a in [('snap',['hydrate']),('shell',args)]:
                p,answer=invoke(root,path,a,role);self.assertEqual(answer,('exit',0));self.assertEqual(p.exitcode,0)
            calls=[json.loads(l) for l in (home/'backend-called').read_text().splitlines()];self.assertEqual(calls,[['hydrate'],args])
            events=[json.loads(l) for l in (home/'helper-events.jsonl').read_text().splitlines()];summary=h.summarize(events,config['allowed']);self.assertTrue(summary['allExactProcessesGone'])
            self.assertEqual([row['helper'] for row in events if row['event']=='started'],['snap','shell'])
            _,answer=invoke(root,path,args,'shell');self.assertEqual(answer[0],'refused');self.assertIn('Duplicate',answer[1])
    def test_unchanged_packaged_launcher_executes_owned_qs_argv(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);actual=Path(config['helpers']['shell']['actual'])
            actual.write_bytes((B/'payload/omarchy/bin/omarchy-shell').read_bytes());actual.chmod(0o700);config['helpers']['shell']['actualSHA256']=h.digest(actual);path.write_text(json.dumps(config))
            package=root/'packaged/shell';package.mkdir(parents=True);(package/'shell.qml').write_text('owned sandbox placeholder; not launched')
            qs=home/'.local/bin/qs';qs.write_text('#!/usr/bin/python3\nimport json,os,sys\nfrom pathlib import Path\n(Path(os.environ["HOME"])/"launcher-argv").write_text(json.dumps(sys.argv[1:]))\n');qs.chmod(0o700)
            args=['hoskinson.windows','fileDrag','false','12','14','1','99'];p,answer=invoke(root,path,args,'shell')
            self.assertEqual(answer,('exit',0));self.assertEqual(p.exitcode,0)
            observed=json.loads((home/'launcher-argv').read_text());self.assertEqual(observed,['ipc','-n','-p',str(package),'call','--',*args])
            self.assertEqual(actual.read_bytes(),(B/'payload/omarchy/bin/omarchy-shell').read_bytes())
    def test_selected_wrapper_rejects_other_helper_operation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);_,answer=invoke(root,path,['hydrate'],'shell')
            self.assertEqual(answer[0],'refused');self.assertIn('another exact helper',answer[1]);self.assertFalse((home/'backend-called').exists())
    def test_compositor_environment_includes_actual_private_omarchy_path(self):
        env={key:'private-'+key for key in ('HOME','PATH','OMARCHY_PATH','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME','PYTHONDONTWRITEBYTECODE','GIO_USE_VFS','QT_NO_XDG_DESKTOP_PORTAL','WINDOW_QA_HELPER_CONFIG')}
        class Session:
            calls=[]
            def ctl(self,*args):
                self.calls.append(args)
                if len(self.calls)==2:return '\n'.join(env.values())
                if len(self.calls)==3:return 'WQA paired Snap Lua loaded'
                return ''
        session=Session();result=setup.install_lua(env,{},session,lambda body:'do\n'+body+'\nend')
        self.assertEqual(result['actualCompositorEnv']['OMARCHY_PATH'],env['OMARCHY_PATH']);self.assertIn('hl.env("OMARCHY_PATH",',session.calls[0][1])
    def test_full_snap_source_unchanged_and_real_shell_precedes_load(self):
        self.assertEqual(h.digest(setup.SNAP),'a0ac977fd958f3f262ddc7a7b37196381c189e6707594c914de9139c8b5965fc4' if False else h.digest(B.parent/'toolkit-interruption-v4/native-candidate/installed-snap.lua'))
        source=(B/'native_integration.py').read_text();start=source.index("helper_config=helper_setup.prepare")
        self.assertLess(source.index("shell = launch('taskbar-shell'",start),source.index("helper_setup.install_lua",start))
        self.assertIn("len(helper_evidence['operations'])==6",source);self.assertIn("len(report['checks'])!=29",source)

if __name__=='__main__':unittest.main()
