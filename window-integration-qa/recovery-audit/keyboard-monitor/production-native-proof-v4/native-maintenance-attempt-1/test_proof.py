"""Offline actual-source regressions; never owns a bus or launches a compositor."""
import ast,hashlib,importlib.util,json,os,stat,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'native_probe_maintenance.py'

def function(path,name,scope):
    tree=ast.parse(Path(path).read_text());node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope);return scope[name]
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value
sys.path.insert(0,str(ROOT/'payload'))
control=module(ROOT/'payload/control.py','_proof_actual_control_offline')

class ProofTests(unittest.TestCase):
    def test_frozen_v4_payload_bytes_and_modes(self):
        prior=ROOT.parent/'production-maintenance-v4';manifest=json.loads((prior/'stage-manifest.json').read_text())
        for name,digest in manifest['local'].items():
            if not name.startswith('payload/'):continue
            path=ROOT/name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest,name)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode),manifest['localModes'][name],name)
    def test_approval_false_and_probe_absent_actual_binary(self):
        package=json.loads((ROOT/'payload/package.json').read_text())
        self.assertFalse(package['nativeAccepted']);self.assertFalse(package['productionAccepted'])
        self.assertNotIn(b'org.omarchy.KeyboardMonitorProbe',(ROOT/'payload'/package['library']).read_bytes())
    def test_calibrated_mapping_sources_and_all_inode_device_guards_are_packaged(self):
        source=(ROOT/'payload/control.py').read_text();mapping=(ROOT/'payload/mapping_artifact.py').read_text()
        self.assertIn('with calibrated_artifact(path',source);self.assertIn('exact_remote_maps(',source)
        self.assertIn("(row['device'],row['inode'])!=(calibration['device'],calibration['inode'])",mapping)
        self.assertIn('ctypes.addressof(buffer)',mapping);self.assertIn('access=mmap.ACCESS_COPY',mapping)
        self.assertNotIn('ctypes.CDLL',mapping);self.assertNotIn('PROT_EXEC',mapping)
        for name in ['control.py','mapping_artifact.py']:
            self.assertEqual((ROOT/'payload'/name).read_bytes(),(ROOT.parent/'production-maintenance-v4'/name).read_bytes())
    def test_native_guard_observation_archived_without_namespace_or_raw_unload_change(self):
        source=SOURCE.read_text()
        self.assertIn("report['actualCalibratedArtifactMapping']=control.mapping_observation",source)
        self.assertIn("report['cleanupCalibratedArtifactMapping']=control.mapping_observation",source)
        source=(ROOT/'proof_cases.py').read_text();prior=(ROOT.parent/'production-native-proof-v3/proof_cases.py').read_text()
        self.assertEqual(source[source.index('def run(c):'):source.index('    refusal=observe_native_refusal')],prior[prior.index('def run(c):'):prior.index("    stale='return hl.plugin")])
        anchor="    check('old nonce refusal preserves new capture policy'"
        self.assertEqual(source[source.index(anchor):],prior[prior.index(anchor):])
    def test_signed_prefix_executable_modes(self):
        manifest=json.loads((ROOT/'payload/payload-manifest.json').read_text())
        executables=[n for n,v in manifest.items() if v['mode']==0o755]
        self.assertEqual(len(executables),38)
        for name in executables:self.assertEqual(stat.S_IMODE((ROOT/'payload'/name).stat().st_mode),0o755,name)
    def test_scope_helpers_and_host_are_exact_pins(self):
        for name,expected in [('qa_launch.py','6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'),('qa_run.py','656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1')]:
            self.assertEqual(hashlib.sha256((Path('/home/hoskinson/window-integration-qa')/name).read_bytes()).hexdigest(),expected)
    def test_factory_only_injects_approved_false(self):
        for name in ('proof_reader_entry.py','proof_control_entry.py'):
            calls=[];scope={'actual':lambda *a,**k:calls.append((a,k)) or 'actual'}
            fn=function(ROOT/name,'private_factory',scope)
            self.assertEqual(fn('manifest',explicit='private',env={'owned':True}),'actual')
            self.assertEqual(calls,[ (('manifest',),dict(explicit='private',env={'owned':True},approved=False)) ])
            with self.assertRaises(RuntimeError):fn('manifest',approved=True)
    def test_canonical_main_rejected_before_transport(self):
        calls=[]
        with self.assertRaisesRegex(control.Refused,'restricted to reviewed private proof'):
            control.Control(ROOT/'payload/package.json',explicit='unavailable',env={'XDG_RUNTIME_DIR':'/run/user/'+str(os.getuid())},transport=lambda *x:calls.append(x),approved=False)
        self.assertFalse(calls)
    def test_rpc_void_reply(self):
        for unpacked,expected in [((),None),('tuple',None),((True,),True)]:
            if unpacked=='tuple':unpacked=({'one':1},);expected={'one':1}
            variant=types.SimpleNamespace(unpack=lambda:unpacked)
            scope={'GLib':types.SimpleNamespace(Variant=types.SimpleNamespace(parse=lambda *a:variant)),'command':lambda *a,**k:'actual parsed fixture'}
            self.assertEqual(function(SOURCE,'rpc',scope)({},'d','p','m'),expected)
    def test_owned_profile_detects_empty_directory_creation(self):
        fn=function(SOURCE,'profile_tree',dict(Path=Path,hashlib=hashlib))
        with tempfile.TemporaryDirectory() as td:
            env={k:str(Path(td)/k) for k in ('XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME')}
            for value in env.values():Path(value).mkdir()
            before=fn(env);(Path(env['XDG_DATA_HOME'])/'created').mkdir();self.assertNotEqual(before,fn(env))
    def test_owned_profile_tracks_symlink_and_mode(self):
        fn=function(SOURCE,'profile_tree',dict(Path=Path,hashlib=hashlib))
        with tempfile.TemporaryDirectory() as td:
            env={k:str(Path(td)/k) for k in ('XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME')}
            for value in env.values():Path(value).mkdir()
            path=Path(env['XDG_CONFIG_HOME'])/'preferences';path.write_text('a');path.chmod(0o600);before=fn(env);path.chmod(0o644)
            self.assertNotEqual(before,fn(env));link=path.parent/'link';link.symlink_to(path.name);self.assertEqual(fn(env)[str(link)]['kind'],'symlink')
    def test_manifest_rejects_mode_only_change(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=root/'helper';path.write_text('# executable');path.chmod(0o755)
            manifest=dict(dependencies={'helper':hashlib.sha256(path.read_bytes()).hexdigest()},dependencyModes={'helper':0o755},externalDependencies={})
            fn=function(SOURCE,'verify_manifest',dict(Path=Path,hashlib=hashlib,HERE=root));fn(manifest)
            path.chmod(0o644)
            with self.assertRaises(AssertionError):fn(manifest)
    def test_fresh_attempt_copy_preserves_modes(self):
        with tempfile.TemporaryDirectory() as td:
            stage=Path(td);src=stage/'exec-helper';src.write_text('#!/bin/sh\nexit 0\n');src.chmod(0o755)
            manifest=dict(dependencies={'exec-helper':hashlib.sha256(src.read_bytes()).hexdigest()},dependencyModes={'exec-helper':0o755},externalDependencies={},externalSymlinks={})
            (stage/'proof-frozen-stage-report.json').write_text(json.dumps(manifest))
            scope=dict(STAGE=stage,HERE=stage,Path=Path,os=os,hashlib=hashlib,json=json,QA_ROOT=Path('/home/hoskinson/window-integration-qa'))
            function(SOURCE,'verify_manifest',scope);fn=function(SOURCE,'freeze_attempt',scope);destination=stage/'native-maintenance-attempt-test';fn(destination)
            self.assertEqual(stat.S_IMODE((destination/'exec-helper').stat().st_mode),0o755)
            self.assertEqual((destination/'exec-helper').read_bytes(),src.read_bytes())
            with self.assertRaises(FileExistsError):fn(destination)
    def test_actual_attempt_materialization_preserves_declared_import_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            stage=Path(td)
            names=('import-preflight.json','native_probe_maintenance.py','native_refusal.py','proof_cases.py','proof_reader_entry.py','proof_control_entry.py','production_client.py','payload/control.py','payload/mapping_artifact.py','payload/reader_bootstrap.py')
            hashes={};modes={}
            for name in names:
                source=ROOT/name;target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());target.chmod(source.stat().st_mode&0o7777)
                hashes[name]=hashlib.sha256(target.read_bytes()).hexdigest();modes[name]=target.stat().st_mode&0o7777
            manifest=dict(dependencies=hashes,dependencyModes=modes,externalDependencies={},externalModes={},externalSymlinks={})
            (stage/'proof-frozen-stage-report.json').write_text(json.dumps(manifest))
            scope=dict(STAGE=stage,HERE=stage,Path=Path,os=os,hashlib=hashlib,json=json,QA_ROOT=Path('/home/hoskinson/window-integration-qa'),__file__=str(SOURCE),exact_module=lambda name,path:module(path,name))
            function(SOURCE,'verify_manifest',scope);copy=function(SOURCE,'freeze_attempt',scope)
            destination=stage/'native-maintenance-attempt-materialization';copy(destination)
            function(SOURCE,'import_preflight',scope);write=function(SOURCE,'write_runtime_preflight',scope)
            result=write();self.assertTrue(result['pass_']);self.assertFalse(result['GUI']);self.assertFalse(result['nativeCalled'])
            self.assertEqual((destination/'import-preflight.json').read_bytes(),(ROOT/'import-preflight.json').read_bytes())
            self.assertTrue((destination/'runtime-import-preflight.json').exists())
            self.assertEqual(stat.S_IMODE((destination/'runtime-import-preflight.json').stat().st_mode),0o600)
            scope['verify_manifest'](manifest,destination)
            with self.assertRaises(FileExistsError):write()
            manifest['dependencies']['runtime-import-preflight.json']='invalid'
            (stage/'proof-frozen-stage-report.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AssertionError,'cannot be a source input'):copy(stage/'native-maintenance-attempt-forbidden')
            self.assertFalse((stage/'native-maintenance-attempt-forbidden').exists())
    def test_disabled_actual_bootstrap_stops_before_orca_import(self):
        tree=ast.parse((ROOT/'payload/reader_bootstrap.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        calls=[]
        import argparse
        scope=dict(argparse=argparse,os=os,sys=sys,Control=lambda *args: calls.append(args) or types.SimpleNamespace(env={'owned':True}),reader_intent=lambda env:False,Refused=control.Refused)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'actual reader_bootstrap','exec'),scope)
        with patch.object(sys,'argv',['owned-entry','--manifest','owned-package','--instance','owned-sig']):
            with self.assertRaisesRegex(control.Refused,'ScreenReaderEnabled is false'):scope['main']()
        self.assertEqual(len(calls),1);self.assertFalse(any(n=='orca' or n.startswith('orca.') for n in sys.modules))
    def test_control_main_real_lock_and_false_intent(self):
        import contextlib
        events=[]
        class Fixture:
            env={'owned':True}
            @contextlib.contextmanager
            def locked(self):events.append('lock');yield;events.append('unlock')
            def load(self):events.append('load');return {'actual':'controlled boundary'}
        with patch.object(control,'Control',lambda *a:Fixture()),patch.object(control,'reader_intent',lambda env:events.append('read') or False),patch.object(sys,'argv',['entry','load','--manifest','private','--instance','private']),patch('builtins.print') as printed:
            control.main()
        self.assertEqual(events,['lock','read','load','read','unlock']);self.assertFalse(json.loads(printed.call_args[0][0])['readerEnabledAfter'])
    def test_control_main_rejects_external_intent_transition(self):
        import contextlib
        class Fixture:
            env={}
            @contextlib.contextmanager
            def locked(self):yield
            def load(self):return {}
        with patch.object(control,'Control',lambda *a:Fixture()),patch.object(control,'reader_intent',side_effect=[False,True]),patch.object(sys,'argv',['entry','load','--manifest','private']):
            with self.assertRaisesRegex(control.Refused,'changed externally'):control.main()
    def test_scenario_cleanup_eof_before_normal_unload(self):
        events=[]
        class Stream:
            closed=False
            def close(self):self.closed=True;events.append('paired EOF')
        p=types.SimpleNamespace(stdin=Stream(),poll=lambda:None,wait=lambda timeout:events.append('producer waited'))
        scope={'pid_stop':lambda process:events.append('process fallback')}
        function(SOURCE,'finish_fixture',scope)(p)
        self.assertEqual(events[:2],['paired EOF','producer waited'])
        production=types.SimpleNamespace(unload=lambda:events.append('actual normal unload') or {'ready':True})
        production.mapping_observation={'fixture':'read-only guard observation'}
        report={};function(SOURCE,'retire_private_plugin',{})(production,report)
        self.assertEqual(events[-1],'actual normal unload');self.assertEqual(report['cleanupNormalUnloadResult'],'ok')
    def test_stale_oracle_has_specific_native_error(self):
        source=(ROOT/'proof_cases.py').read_text();observer=(ROOT/'native_refusal.py').read_text()
        self.assertIn("MISMATCH='maintenance target/incarnation mismatch'",observer);self.assertIn('observe_native_refusal(control,first)',source)
        self.assertNotIn('except (ValueError',source)
        native=(ROOT/'payload/source/native/MaintenanceLua.hpp').read_text();self.assertIn('maintenance target/incarnation mismatch',native)
    def test_public_query_rejection_uses_real_interface(self):
        source=(ROOT/'production_client.py').read_text();compile(source,'production client','exec')
        self.assertIn("elif operation=='query':method='QueryPointer'",source)
        self.assertIn("'org.freedesktop.a11y.PointerLocator' if operation=='query'",source)
    def test_normal_orca_shutdown_exact_source(self):
        source=(ROOT/'payload/orca-compat/orca/orca.py').read_text();self.assertIn('signal.signal(signal.SIGINT, _shutdown_on_signal)',source);self.assertIn('Atspi.event_quit()',source)
        self.assertIn('return 0',source)
    def test_frozen_producer_handshakes_before_first_key(self):
        source=SOURCE.read_text();self.assertIn('producer_control.ready(p,report,stderr_path=log',source)
        accepted=ROOT.parent/'pointer-private-host-v5'
        for name in ('producer_control.py','private_runtime_guard.py','host_acceptance.py','startup_reporting.py'):
            self.assertEqual((ROOT/name).read_bytes(),(accepted/name).read_bytes(),name)
        for name in ('native-input','native-pointer'):
            self.assertEqual((ROOT/'native-fixture'/name).read_bytes(),(accepted/'native-fixture'/name).read_bytes(),name)
    def test_helper_import_preflight_is_offline(self):
        scope={'Path':Path,'__file__':str(SOURCE),'exact_module':lambda name,path:module(path,name)}
        result=function(SOURCE,'import_preflight',scope)(ROOT)
        self.assertTrue(result['pass_']);self.assertFalse(result['GUI']);self.assertFalse(result['nativeCalled'])

if __name__=='__main__':unittest.main(verbosity=2)
