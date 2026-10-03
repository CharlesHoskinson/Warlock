"""Archive exact helper bytes before host disposal even after IPC/cleanup failure."""
from pathlib import Path
import json,os,tempfile,unittest
from unittest.mock import patch
import helper_setup as setup
import helper_observer as h
from test_v6_helpers import sandbox

class ArchiveTests(unittest.TestCase):
    def test_archive_before_host_disposal_after_cleanup_exception_without_ipc(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);log=Path(config['log'])
            event=dict(event='started',operation='hydrate',wrapper=h.process(os.getpid()),delegate=dict(pid=2147483646,start='1',pgid=1))
            raw=(json.dumps(event)+'\n').encode();log.write_bytes(raw);report={};order=[]
            class Host:
                def __enter__(self):return self
                def __exit__(self,*args):
                    order.append('host-disposal');self.outer.assertTrue((root/'archive/helper-events.jsonl').exists());self.outer.assertIn('helperArchive',report)
            host=Host();host.outer=self
            with patch.object(h,'verify_runtime',return_value=root),patch.object(h,'ipc_proof',side_effect=AssertionError('archive must not need live IPC')):
                with self.assertRaisesRegex(RuntimeError,'dead compositor'):
                    with host,setup.retain_before_runtime_delete(lambda:config,root/'archive',report):raise RuntimeError('dead compositor')
            self.assertEqual(order,['host-disposal']);self.assertEqual((root/'archive/helper-events.jsonl').read_bytes(),raw);self.assertEqual((root/'archive/helper-config.json').read_bytes(),path.read_bytes())
            row=report['helperArchive'];self.assertTrue(row['completeEOF']);self.assertFalse(row['normalLifecycleAccepted']);self.assertFalse(row['compositorIPCRequired']);self.assertEqual(len(row['processes']),2)
            self.assertEqual(row['processes'][0]['identity'],event['wrapper']);self.assertTrue(row['processes'][0]['liveAtArchive']);self.assertFalse(row['processes'][1]['liveAtArchive'])

    def test_truncated_crash_log_preserved_but_acceptance_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);raw=b'{"event":"started"}\n{"event":"term';Path(config['log']).write_bytes(raw)
            with patch.object(h,'verify_runtime',return_value=root):
                with self.assertRaisesRegex(RuntimeError,'Malformed helper evidence retained'):
                    setup.archive_helpers(config,root/'archive')
            self.assertEqual((root/'archive/helper-events.jsonl').read_bytes(),raw);self.assertTrue(json.loads((root/'archive/archive.json').read_text())['parseErrors'])

    def test_unsafe_config_or_log_symlink_refuses_before_archive(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);home,path,config=sandbox(root);target=home/'other';target.write_text('{}');target.chmod(0o600);path.unlink();path.symlink_to(target)
            with patch.object(h,'verify_runtime',return_value=root):
                with self.assertRaises(OSError):setup.archive_helpers(config,root/'archive')
            self.assertFalse((root/'archive').exists())

    def test_actual_runner_places_archive_context_before_host_exit(self):
        source=(Path(__file__).parent/'native_integration.py').read_text()
        self.assertIn('with host as session, helper_setup.retain_before_runtime_delete(',source)
        self.assertIn("lambda:helper_config,output/'terminal-helpers',report",source)

if __name__=='__main__':unittest.main()
