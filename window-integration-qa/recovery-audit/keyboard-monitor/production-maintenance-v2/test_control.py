import ast,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import control
from reader_bootstrap import verify_status
from launch_reader import environment

class Managed(control.Control):
    def __init__(self):
        self.identity=control.Identity('a'*40+'_1_2',1,2,3,4)
        self.manifest={'packageID':'pkg','pluginName':'monitor'};self.library=Path('/immutable/library.so')
        self.nonce='a'*64;self.owner=':1.5';self.quiet=True;self.retired=False;self.loaded=True;self.calls=[];self.swap=False
    def _mapped(self):pass
    def ipc(self,*args):
        self.calls.append(args)
        if args[0]=='repl':
            if '.identity()' in args[1]:return json.dumps(dict(instance=self.identity.signature,packageID='pkg',incarnation=self.nonce,managerOwner=self.owner))
            if '.prepare_unload(' in args[1]:
                old=self.nonce
                if self.swap:self.nonce='b'*64
                if old!=self.nonce:raise control.Refused('stale nonce')
                self.retired=self.quiet
                return json.dumps(dict(instance=self.identity.signature,packageID='pkg',incarnation=self.nonce,managerOwner=self.owner,ready=self.quiet))
        if args[0]=='plugin' and args[1]=='unload':self.loaded=False;return 'ok'
        if args==('-j','plugin','list'):return json.dumps([{'name':'monitor'}] if self.loaded else [])
        raise AssertionError(args)

class Tests(unittest.TestCase):
    def test_unknown_preferred_does_not_fallback(self):
        with self.assertRaises(control.Refused):control.select([{'instance':'a'*40+'_1_2'}],'missing')
    def test_ambiguous_absent_target(self):
        with self.assertRaises(control.Refused):control.select([{'instance':'a'*40+'_1_2'}]*2)
    def test_same_artifact_new_nonce_refuses_before_raw_unload(self):
        c=Managed();c.swap=True
        with self.assertRaises(control.Refused):c.unload()
        self.assertFalse(any(x[:2]==('plugin','unload') for x in c.calls));self.assertTrue(c.loaded);self.assertFalse(c.retired)
    def test_held_refusal_preserves_loaded_subscription(self):
        c=Managed();c.quiet=False
        with self.assertRaises(control.Refused):c.unload()
        self.assertTrue(c.loaded);self.assertFalse(c.retired);self.assertFalse(any(x[:2]==('plugin','unload') for x in c.calls))
    def test_true_retire_then_normal_path(self):
        c=Managed();self.assertTrue(c.unload()['ready']);self.assertTrue(c.retired);self.assertFalse(c.loaded)
    def test_replaced_after_prepare_refuses_raw_unload(self):
        c=Managed();original=c.native_identity;count=0
        def identity():
            nonlocal count
            count+=1
            if count==2:c.nonce='c'*64
            return original()
        c.native_identity=identity
        with self.assertRaises(control.Refused):c.unload()
        self.assertTrue(c.loaded);self.assertTrue(c.retired)
    def test_capability_requires_exact_owner_and_all_actual_flags(self):
        value=dict(managerOwner=':1.5',retiring=False,quiescent=True,unloadQuiescent=True,registered=True,callerPreReplay=True)
        self.assertTrue(verify_status(value,':1.5'))
        for key in ('quiescent','unloadQuiescent','registered','callerPreReplay'):
            with self.subTest(key=key):self.assertFalse(verify_status(dict(value,**{key:False}),':1.5'))
        self.assertFalse(verify_status(value,':1.6'));self.assertFalse(verify_status(dict(value,retiring=True),':1.5'))
    def test_unapproved_artifact_fails_before_session_access(self):
        with self.assertRaises(control.Refused):control.artifact({'productionAccepted':False},Path('/does-not-exist'))
    def test_profile_and_real_speech_environment_preserved(self):
        source=dict(HOME='/real/user',XDG_CONFIG_HOME='/real/config',XDG_DATA_HOME='/real/data',XDG_CACHE_HOME='/real/cache',XDG_STATE_HOME='/real/state',GSETTINGS_BACKEND='dconf',DISPLAY=':0',ORCA_QA_UTTERANCES='/qa/log')
        actual=environment(source,Path('/reviewed/package'))
        for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','GSETTINGS_BACKEND'):self.assertEqual(actual[key],source[key])
        self.assertNotIn('DISPLAY',actual);self.assertNotIn('ORCA_QA_UTTERANCES',actual);self.assertEqual(actual['GDK_BACKEND'],'wayland')
    def test_public_adapter_classes_exactly_match_accepted_source(self):
        original=ast.parse(Path('../pointer-private-host-v5/capability_adapter.py').read_text())
        fresh=ast.parse(Path('capability_adapter.py').read_text())
        for name in ('CapabilityAdapter','PublicTransport'):
            old=next(node for node in original.body if isinstance(node,ast.ClassDef) and node.name==name)
            new=next(node for node in fresh.body if isinstance(node,ast.ClassDef) and node.name==name)
            self.assertEqual(ast.dump(old,include_attributes=False),ast.dump(new,include_attributes=False))
        self.assertNotIn('org.omarchy.KeyboardMonitorProbe',Path('capability_adapter.py').read_text())
    def test_unaccepted_control_cannot_target_canonical_main(self):
        # The real constructor must refuse before any session/IPC observation.
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'artifact.so').write_bytes(b'fixture');(base/'artifact.so').chmod(0o644)
            manifest=dict(packageID='test',library='artifact.so',sha256=control.sha(base/'artifact.so'))
            (base/'package.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(control.Refused,'restricted to reviewed private proof'):
                control.Control(base/'package.json',env={'XDG_RUNTIME_DIR':f'/run/user/{os.getuid()}'},approved=False,transport=lambda *args:self.fail('IPC must not be reached'))
    def test_probe_absent_actual_binary(self):
        data=Path('native/libomarchy-a11y-prod-v2.so').read_bytes();self.assertNotIn(b'org.omarchy.KeyboardMonitorProbe',data)
        self.assertIn(b'omarchy_a11y',data)
if __name__=='__main__':unittest.main()
