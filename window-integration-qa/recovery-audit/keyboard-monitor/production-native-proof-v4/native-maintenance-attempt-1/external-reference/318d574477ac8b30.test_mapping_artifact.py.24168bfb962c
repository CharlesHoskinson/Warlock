"""Real mmap/FD/bytes tests; SO data is never loaded or executed."""
from pathlib import Path
import hashlib,json,mmap,os,tempfile,types,unittest
from unittest.mock import patch
import mapping_artifact as m
import control

FROZEN=Path('/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/production-native-proof-v2/native-maintenance-attempt-1/payload/native/libomarchy-a11y-prod-v2.so')
SO_SHA='913cbc06c6f16a001a3726b24ee8009af24629051822a3344f97ee0a7b181b43'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class MappingTests(unittest.TestCase):
    def file(self,folder,name='artifact'):
        path=Path(folder)/name;path.write_bytes(b'owned mapping bytes\n'*1000);path.chmod(0o644);return path

    def test_actual_ordinary_file_self_map_buffer_backing_and_two_segments(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td)
            with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as first,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as second:
                with m.calibrated_artifact(path,sha(path)) as row:
                    self.assertEqual(row['inode'],path.stat().st_ino);self.assertTrue(row['selfMapping']['first']<=row['bufferAddress']<row['selfMapping']['last']);self.assertNotIn('x',row['selfMapping']['permissions']);self.assertFalse(row['nativeCodeExecuted'])
                    self.assertGreaterEqual(len(m.exact_remote_maps(Path('/proc/self/maps').read_text(),path,row)),3)

    def test_exact_frozen_btrfs_so_backing_device_is_calibrated_without_execute(self):
        self.assertEqual(sha(FROZEN),SO_SHA)
        before=m.witness(FROZEN.stat())
        with FROZEN.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as remote:
            with m.calibrated_artifact(FROZEN,SO_SHA) as row:
                self.assertEqual(row['statDevice'],before[0]);self.assertEqual(row['inode'],before[1]);self.assertNotEqual(row['device'],row['statDevice'])
                self.assertGreaterEqual(len(m.exact_remote_maps(Path('/proc/self/maps').read_text(),FROZEN,row)),2)
        self.assertEqual(before,m.witness(FROZEN.stat()));self.assertEqual(sha(FROZEN),SO_SHA)

    def test_wrong_device_same_inode_and_wrong_inode_same_device_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td)
            with m.calibrated_artifact(path,sha(path)) as row:
                line=next(line for line in Path('/proc/self/maps').read_text().splitlines() if line.split(maxsplit=5)[-1]==str(path))
                parts=line.split(maxsplit=5)
                wrong=list(parts);wrong[3]='00:ffff'
                with self.assertRaisesRegex(m.MappingRefused,'identity differs'):m.exact_remote_maps(' '.join(wrong),path,row)
                wrong=list(parts);wrong[4]=str(row['inode']+1)
                with self.assertRaisesRegex(m.MappingRefused,'identity differs'):m.exact_remote_maps(' '.join(wrong),path,row)
                wrong=list(parts);wrong[3]=f'{os.major(row["statDevice"]):x}:{os.minor(row["statDevice"]):x}'
                if row['device']!=row['statDevice']:
                    with self.assertRaises(m.MappingRefused):m.exact_remote_maps(' '.join(wrong),path,row)

    def test_missing_deleted_and_one_bad_segment_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td)
            with m.calibrated_artifact(path,sha(path)) as row:
                line=next(line for line in Path('/proc/self/maps').read_text().splitlines() if line.split(maxsplit=5)[-1]==str(path))
                for text in ['',line+' (deleted)',line+'\n'+line+' (deleted)']:
                    with self.assertRaises(m.MappingRefused):m.exact_remote_maps(text,path,row)

    def test_post_remote_read_path_replace_bytes_and_permissions_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            for change in ['replace','bytes','mode']:
                path=self.file(td,change)
                with self.assertRaises(m.MappingRefused,msg=change):
                    with m.calibrated_artifact(path,sha(path)):
                        if change=='replace':
                            replacement=self.file(td,'replacement');replacement.replace(path)
                        elif change=='bytes':
                            with path.open('r+b') as stream:stream.write(b'changed')
                        else:path.chmod(0o600)

    def test_actual_descriptor_swap_refuses_even_if_named_original_restored(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td);other=self.file(td,'other');saved=Path(td)/'saved';actual_open=os.open
            def swapped(name,*args):
                path.rename(saved);other.rename(path)
                try:return actual_open(name,*args)
                finally:path.rename(other);saved.rename(path)
            with patch.object(m.os,'open',side_effect=swapped):
                with self.assertRaisesRegex(m.MappingRefused,'descriptor/path identity'):
                    with m.calibrated_artifact(path,sha(path)):self.fail('wrong descriptor accepted')

    def test_symlink_mode_and_wrong_hash_reject(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td);link=Path(td)/'link';link.symlink_to(path)
            with self.assertRaises(m.MappingRefused):
                with m.calibrated_artifact(link,sha(path)):self.fail('link accepted')
            with self.assertRaises(m.MappingRefused):
                with m.calibrated_artifact(path,'0'*64):self.fail('wrong bytes accepted')
            path.chmod(0o666)
            with self.assertRaises(m.MappingRefused):
                with m.calibrated_artifact(path,sha(path)):self.fail('unsafe mode accepted')

    def test_actual_control_mapped_accepts_btrfs_and_retains_both_device_inode_guards(self):
        obj=control.Control.__new__(control.Control);obj.base=FROZEN.parent;obj.approved=False
        obj.manifest=dict(library=FROZEN.name,sha256=SO_SHA,packageID='omarchy-a11y-prod-v2',pluginName='omarchy-a11y-monitor',pluginVersion='0.8-production-v2')
        obj.identity=types.SimpleNamespace(pid=os.getpid(),start=control.start_time(os.getpid()))
        calls=[];obj._guard=lambda:calls.append('exact-session-guard');obj.plugin_rows=lambda:[dict(name=obj.manifest['pluginName'],version=obj.manifest['pluginVersion'])]
        with FROZEN.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ):obj._mapped()
        self.assertEqual(calls,['exact-session-guard','exact-session-guard']);self.assertNotEqual(obj.mapping_observation['device'],obj.mapping_observation['statDevice']);self.assertFalse(obj.mapping_observation['nativeCodeExecuted'])

    def test_control_path_mutation_during_plugin_verification_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.file(td);obj=control.Control.__new__(control.Control);obj.base=Path(td);obj.approved=False
            obj.manifest=dict(library=path.name,sha256=sha(path),packageID='test',pluginName='test',pluginVersion='1');obj.identity=types.SimpleNamespace(pid=os.getpid(),start=control.start_time(os.getpid()));obj._guard=lambda:None
            def rows():self.file(td,'replacement').replace(path);return [dict(name='test',version='1')]
            obj.plugin_rows=rows
            with self.assertRaises(control.Refused):obj._mapped()

if __name__=='__main__':unittest.main()
