"""Actual owned lifetimes and locks; fixtures grant no compositor authority."""
from pathlib import Path
import errno,fcntl,inspect,json,os,subprocess,tempfile,threading,time,unittest
from unittest.mock import patch
import helper_setup as setup
import helper_observer as observer
B=Path(__file__).resolve().parent
class HelperFailureDrainTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.log=self.root/'events.jsonl'
        fd=os.open(self.log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
        self.config={'log':str(self.log),'allowed':['hydrate']};self.child=None;self.gatefd=None
    def tearDown(self):
        if self.child is not None and self.child.poll()is None:
            os.write(self.gatefd,b'1');self.child.wait(timeout=3)
        if self.gatefd is not None:os.close(self.gatefd)
        self.temp.cleanup()
    def launch(self,code=0):
        gate=self.root/'delegate.fifo';os.mkfifo(gate,0o600);self.gatefd=os.open(gate,os.O_RDWR|os.O_CLOEXEC)
        ready=self.root/'ready.json';self.child=subprocess.Popen(['/usr/bin/python3','-B',str(B/'helper_drain_fixture.py'),'wrapper',str(self.log),str(ready),str(gate),str(code)])
        limit=time.monotonic()+3
        while not ready.exists()and time.monotonic()<limit:
            self.assertIsNone(self.child.poll());time.sleep(.002)
        self.row=json.loads(ready.read_text());self.assertTrue(all(observer.still_live(self.row[n])for n in ('wrapper','delegate')))
    def release(self):
        os.write(self.gatefd,b'1');code=self.child.wait(timeout=3)
        self.assertFalse(any(observer.still_live(self.row[n])for n in ('wrapper','delegate')))
        return code
    def events(self):
        with observer.locked_log(self.log)as f:return observer.rows(f)
    def rewrite(self,rows):
        with observer.locked_log(self.log)as f:
            f.seek(0);f.truncate()
            for row in rows:observer.append(f,row)
    def background(self,**kw):
        result={};done=threading.Event()
        def work():
            try:result['value']=setup.wait_and_archive(self.config,self.root/'archive.json',**kw)
            except BaseException as e:result['error']=e
            finally:done.set()
        t=threading.Thread(target=work);t.start();return result,done,t
    def test_actual_normal_drain_retains_original_missing_harness(self):
        self.launch();entered=threading.Event();canonical=setup.registered_helper_closure
        def observed(*a):entered.set();return canonical(*a)
        with patch.object(setup,'registered_helper_closure',observed):
            result,done,t=self.background(expect_harness=True);self.assertTrue(entered.wait(2));self.assertFalse(done.is_set())
            self.assertEqual(self.release(),0);t.join(3)
        self.assertFalse(t.is_alive());self.assertEqual(str(result['error']),'Exactly one harness query required')
        row=json.loads((self.root/'archive.json').read_text());self.assertEqual(row['result'],'fail');self.assertFalse(row['campaignAccepted']);self.assertTrue(row['cleanupProof']['registeredJobsNormal']);self.assertIsNone(row['cleanupError']);self.assertEqual(len(row['events']),2)
    def test_unchanged_complete_workload_success(self):
        self.launch();self.assertEqual(self.release(),0)
        result=setup.wait_and_archive(self.config,self.root/'archive.json')
        self.assertTrue(result['allNormal']);self.assertTrue(result['allExactProcessesGone']);self.assertEqual(result['operations'],['hydrate'])
        self.assertNotIn('campaignAccepted',json.loads((self.root/'archive.json').read_text()))
    def test_nonzero_terminal_retains_failure_without_normal_cleanup(self):
        self.launch(7);self.assertEqual(self.release(),7)
        with self.assertRaisesRegex(RuntimeError,'Exactly one harness query required'):setup.wait_and_archive(self.config,self.root/'archive.json',expect_harness=True)
        row=json.loads((self.root/'archive.json').read_text());self.assertIsNone(row['cleanupProof']);self.assertIn('Helper normal completion mismatch',row['cleanupError'])
    def test_wrong_lifetime_terminal_refuses(self):
        self.launch();self.release();rows=self.events();rows[1]['delegate']={**rows[1]['delegate'],'start':str(int(rows[1]['delegate']['start'])+1)};self.rewrite(rows)
        with self.assertRaisesRegex(RuntimeError,'Exactly one harness query required'):setup.wait_and_archive(self.config,self.root/'archive.json',expect_harness=True)
        row=json.loads((self.root/'archive.json').read_text());self.assertIsNone(row['cleanupProof']);self.assertIn('completion mismatch',row['cleanupError'])
    def test_actual_live_registered_helper_timeout_never_normal(self):
        self.launch()
        with self.assertRaisesRegex(RuntimeError,'Exactly one harness query required'):setup.wait_and_archive(self.config,self.root/'archive.json',expect_harness=True,seconds=.08)
        row=json.loads((self.root/'archive.json').read_text());self.assertIsNone(row['cleanupProof']);self.assertIn('deadline',row['cleanupError']);self.assertTrue(observer.still_live(self.row['delegate']));self.release()
    def test_held_actual_log_lock_expires_original_remaining_budget(self):
        with observer.locked_log(self.log):
            before=time.monotonic()
            with self.assertRaisesRegex(TimeoutError,'Original helper completion deadline'):setup.completion_snapshot(self.config,before+.08)
            elapsed=time.monotonic()-before
            self.assertGreaterEqual(elapsed,.08);self.assertLess(elapsed,.4)
    def test_held_lock_release_allows_exact_snapshot(self):
        locked=threading.Event();release=threading.Event()
        def holder():
            with observer.locked_log(self.log):locked.set();self.assertTrue(release.wait(2))
        t=threading.Thread(target=holder);t.start();self.assertTrue(locked.wait(2));threading.Timer(.05,release.set).start()
        self.assertEqual(setup.completion_snapshot(self.config,time.monotonic()+1),[]);t.join(2);self.assertFalse(t.is_alive())
    def test_unknown_flock_errno_is_not_pending(self):
        with patch.object(observer.fcntl,'flock',side_effect=BlockingIOError(errno.EIO,'unknown fixture errno')):
            with self.assertRaises(BlockingIOError)as error:setup.completion_snapshot(self.config,time.monotonic()+1)
        self.assertEqual(error.exception.errno,errno.EIO)
    def test_unknown_refused_event_never_normalized(self):
        self.rewrite([{'event':'refused','operation':'hydrate'}])
        with self.assertRaisesRegex(RuntimeError,'Unregistered/refused'):setup.wait_and_archive(self.config,self.root/'archive.json',expect_harness=True)
        row=json.loads((self.root/'archive.json').read_text());self.assertEqual(row['reason'],'unknown/refused operation');self.assertNotIn('cleanupProof',row)
    def service_row(self,prefix):
        return {'event':'started','operation':prefix+':1','class':'query','queryRoot':'service','serviceOperation':prefix}
    def test_unknown_service_prefix_refuses(self):
        self.config.update(queryRoots={'service':{}},serviceMembers=[{'address':'0x1','stableId':'a','pid':123}],serviceTargetLimitPerMember=1,serviceRefreshLimit=1)
        with self.assertRaisesRegex(RuntimeError,'Unregistered service operation'):setup.registered_helper_closure([self.service_row('service-motionTarget:0x2:b:124')],self.config)
    def test_extra_service_count_refuses(self):
        self.config.update(queryRoots={'service':{}},serviceMembers=[],serviceTargetLimitPerMember=1,serviceRefreshLimit=1)
        rows=[self.service_row('service-motionRefresh'),{**self.service_row('service-motionRefresh'),'operation':'service-motionRefresh:2'}]
        with self.assertRaisesRegex(RuntimeError,'Extra service helper query'):setup.registered_helper_closure(rows,self.config)
    def test_unknown_query_root_refuses(self):
        self.config['queryRoots']={}
        with self.assertRaisesRegex(RuntimeError,'Unregistered query root'):setup.registered_helper_closure([{'event':'started','class':'query','queryRoot':'qs'}],self.config)
    def test_archive_failure_cannot_replace_original_exception(self):
        self.launch();self.release()
        with patch.object(setup,'write_json',side_effect=OSError('explicit fixture archive failure')):
            with self.assertRaisesRegex(RuntimeError,'Exactly one harness query required')as error:setup.wait_and_archive(self.config,self.root/'archive.json',expect_harness=True)
        self.assertIsInstance(error.exception.__cause__,OSError);self.assertIn('archive error',error.exception.__notes__[0])
    def test_original_default_deadline_and_observer_guards_unchanged(self):
        self.assertEqual(inspect.signature(setup.wait_and_archive).parameters['seconds'].default,10)
        old=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v10/helper_observer.py');self.assertEqual(Path(observer.__file__).read_bytes(),old.read_bytes())
if __name__=='__main__':unittest.main()
