"""Actual recorded byte/link aliases; temporary files only, no native launch."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import collector_v9_closure as closure

class ClosureAliasKernelTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.backing=self.root/'backing';self.backing.write_bytes(b'exact source\n');self.backing.chmod(0o600)
        self.alternate=self.root/'alternate';self.alternate.write_bytes(self.backing.read_bytes());self.alternate.chmod(0o600)
        self.alias=self.root/'alias';self.alias.symlink_to('backing')
        self.digest=closure.sha(self.backing)
    def tearDown(self):self.temp.cleanup()
    def packet(self):
        return {'inputs':{str(self.alias):self.digest,str(self.backing):self.digest},'inputModes':{str(self.alias):0o600,str(self.backing):0o600},'links':{str(self.alias):'backing'}}
    def retain(self,packet,*,inputs=None,modes=None,links=None):
        path=self.root/'packet.json';path.write_text(json.dumps(packet));path.chmod(0o600)
        inputs={}if inputs is None else inputs;modes={}if modes is None else modes;links={}if links is None else links
        with patch.object(closure,'PACKETS',((path,closure.sha(path),'links'),)):
            closure.retain(inputs,modes,links)
        return inputs,modes,links
    def test_exact_dual_byte_mode_link_and_captured_backing_accept(self):
        inputs,modes,links=self.retain(self.packet())
        self.assertEqual(inputs[str(self.alias)],self.digest);self.assertEqual(modes[str(self.alias)],0o600)
        self.assertEqual(links[str(self.alias)],'backing');self.assertEqual(inputs[str(self.backing)],self.digest)
    def test_already_pinned_exact_link_accepts_same_alias_byte(self):
        packet=self.packet();packet['links']={}
        inputs,modes,links=self.retain(packet,links={str(self.alias):'backing'})
        self.assertEqual(inputs[str(self.alias)],self.digest);self.assertEqual(links[str(self.alias)],'backing')
    def test_unknown_alias_same_matching_bytes_without_declaration_refuses(self):
        packet=self.packet();packet['links']={}
        with self.assertRaisesRegex(ValueError,'exact selected target'):self.retain(packet)
    def test_missing_backing_byte_mode_declaration_refuses(self):
        packet=self.packet();packet['inputs'].pop(str(self.backing));packet['inputModes'].pop(str(self.backing))
        with self.assertRaisesRegex(ValueError,'backing lacks'):self.retain(packet)
    def test_declared_wrong_target_with_identical_bytes_refuses(self):
        packet=self.packet();packet['links'][str(self.alias)]='alternate'
        packet['inputs'][str(self.alternate)]=self.digest;packet['inputModes'][str(self.alternate)]=0o600
        self.assertEqual(closure.sha(self.backing),closure.sha(self.alternate))
        with self.assertRaisesRegex(ValueError,'link changed'):self.retain(packet)
    def test_wrong_observed_backing_bytes_and_mode_refuse(self):
        packet=self.packet();self.backing.write_bytes(b'foreign material\n')
        with self.assertRaisesRegex(ValueError,'bytes/mode changed'):self.retain(packet)
        self.backing.write_bytes(b'exact source\n');self.backing.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'bytes/mode changed'):self.retain(packet)
    def test_prior_digest_mode_and_target_conflicts_refuse(self):
        for changed in ('digest','mode','target'):
            with self.subTest(changed=changed):
                inputs={str(self.alias):'0'*64 if changed=='digest'else self.digest}
                modes={str(self.alias):0o644 if changed=='mode'else 0o600}
                links={str(self.alias):'alternate'if changed=='target'else'backing'}
                with self.assertRaisesRegex(ValueError,'conflict'):self.retain(self.packet(),inputs=inputs,modes=modes,links=links)
    def test_alias_changes_to_same_byte_target_during_hash_refuses(self):
        packet=self.packet();packet['inputs'][str(self.alternate)]=self.digest;packet['inputModes'][str(self.alternate)]=0o600
        original=closure.sha
        def change(path):
            result=original(path)
            if Path(path)==self.alias:self.alias.unlink();self.alias.symlink_to('alternate')
            return result
        with patch.object(closure,'sha',side_effect=change),self.assertRaisesRegex(ValueError,'alias changed'):self.retain(packet)
    def test_every_selected_link_rechecked_after_byte_resolution(self):
        sibling=self.root/'selected-link';sibling.symlink_to('backing')
        packet=self.packet();packet['links'][str(sibling)]='backing';original=closure.sha
        def change(path):
            result=original(path)
            if Path(path)==self.alias:sibling.unlink();sibling.symlink_to('alternate')
            return result
        with patch.object(closure,'sha',side_effect=change),self.assertRaisesRegex(ValueError,'link changed'):self.retain(packet)
    def test_missing_or_nonregular_backing_refuses(self):
        packet=self.packet();self.backing.unlink()
        with self.assertRaises(FileNotFoundError):self.retain(packet)
        self.backing.mkdir(mode=0o700)
        with self.assertRaisesRegex(ValueError,'not regular'):self.retain(packet)

if __name__=='__main__':unittest.main()
