"""Approved scheduling with actual selected controller/owned kernel boundaries."""
from copy import deepcopy
import json
import subprocess
import threading
import time
import unittest

from fixture_restore_planning import KernelFixture


class RestorePlanningTests(unittest.TestCase):
    def setUp(self):self.k=KernelFixture()
    def tearDown(self):self.k.close()
    def threaded(self,fn):
        result={}
        def invoke():
            try:result['value']=fn()
            except BaseException as e:result['error']=e
        thread=threading.Thread(target=invoke);thread.start();return thread,result
    def finish(self,thread,result):
        thread.join(5);self.assertFalse(thread.is_alive());return result
    def assert_no_effect(self):
        self.assertEqual(self.k.focus(),[])
        self.assertFalse(any(r['wire']=='CPU_REFRESH' for r in self.k.requests))
        self.assertFalse(any(m['command'] in ('seed','validate') for m in self.k.transport.sent))
        self.k.assert_drained()
    def test_actual_ordered_three_plans_keep_six_focus_and_three_refresh(self):
        self.k.ordered=True;self.k.monitor_delay=.025
        record=self.k.request();self.k.wait_worker()
        self.assertNotIn('failure',record.profile)
        self.assertEqual(self.k.completed,[2,1,0])
        self.assertEqual(len(self.k.focus()),6)
        for role,row in zip(['monitor','workspace']*3,self.k.focus(),strict=True):
            self.assertIn('hl.dsp.focus({ '+role+' =',row['wire'])
        self.assertEqual(len([r for r in self.k.requests if r['wire']=='CPU_REFRESH']),3)
        self.assertEqual(len(record.sources),3)
        self.assertTrue(record.validated)
        self.assertLess(record.profile['seedQueuedNs']-record.profile['receivedNs'],2_000_000_000)
        jobs=[j for row in self.k.registry for j in row['jobs'] if j['kind']=='native-effect']
        self.assertEqual(len({j['job'] for j in jobs}),6)
        self.k.assert_drained()
    def test_actual_max_three_workers_for_sixty_four_slots_then_cancel_drain(self):
        self.k.gate=threading.Event()
        members=[]
        for i in range(64):
            w=deepcopy(self.k.fixture.windows[0]);w.update(address='0x'+format(i+100,'x'),stableId=format(i+100,'x'),pid=i+100)
            self.k.install_state(w);members.append(w)
        thread,result=self.threaded(lambda:self.k.plans(members))
        self.assertTrue(self.k.first_three.wait(2))
        self.assertEqual(self.k.max_monitors,3)
        self.k.current=False;self.k.gate.set();self.finish(thread,result)
        self.assertIsInstance(result['error'],ValueError)
        self.assertLessEqual(self.k.monitor_started,3)
        self.assert_no_effect()
    def test_sixty_five_refuses_before_actual_query(self):
        members=[]
        for i in range(65):
            w=deepcopy(self.k.fixture.windows[0]);w.update(address='0x'+format(i+100,'x'),stableId=format(i+100,'x'),pid=i+100);members.append(w)
        before=len(self.k.ipc.reader.rows)
        with self.assertRaisesRegex(ValueError,'bounded'):self.k.plans(members)
        self.assertEqual(len(self.k.ipc.reader.rows),before);self.assert_no_effect()
    def test_duplicate_identity_refuses_before_actual_query(self):
        with self.assertRaisesRegex(ValueError,'unique'):self.k.plans([self.k.fixture.windows[0]]*2)
        self.assert_no_effect()
    def test_actual_controller_successor_context_cancels_old_plans_then_drains(self):
        self.k.gate=threading.Event()
        old=self.k.request();self.assertTrue(self.k.first_three.wait(2))
        successor=self.k.request(defer=True,context=2)
        self.assertIsNot(old,successor);self.assertTrue(successor.profile['contextPending'])
        self.k.gate.set();self.k.wait_worker()
        self.assertIs(self.k.controller.current,successor)
        self.assertFalse(old.validated);self.assertEqual(old.sources,[]);self.assert_no_effect()
    def test_actual_malformed_query_error_drains_without_focus(self):
        self.k.gate=threading.Event();self.k.malformed=True
        thread,result=self.threaded(self.k.plans)
        self.assertTrue(self.k.first_three.wait(2));self.k.gate.set();self.finish(thread,result)
        self.assertIsInstance(result['error'],ValueError)
        self.assertTrue(any(r['outcome']=='refused' for r in self.k.ipc.reader.rows.values()))
        self.assert_no_effect()
    def test_expired_plan_admission_has_no_query_or_effect(self):
        with self.assertRaises(TimeoutError):self.k.plans(deadline_ns=time.monotonic_ns())
        self.assert_no_effect()
    def test_deadline_during_real_query_drains_normal_eof_then_refuses(self):
        self.k.gate=threading.Event()
        record=self.k.request(defer=True)
        deadline=record.profile['receivedNs']+2_000_000_000
        # Spend the first1.8s before starting observations. The unchanged2s
        # individual query timeout can still close normally after receipt expiry.
        while time.monotonic_ns()<deadline-200_000_000:time.sleep(.002)
        thread,result=self.threaded(lambda:self.k.plans(deadline_ns=deadline,
            current=lambda:self.k.controller.owns(record)))
        self.assertTrue(self.k.first_three.wait(2))
        while time.monotonic_ns()<deadline:time.sleep(.002)
        self.k.gate.set();self.finish(thread,result)
        error=result['error']
        self.assertIsInstance(error,(TimeoutError,ValueError))
        self.assertIn(str(error),('original scene receipt deadline during destination planning',
            'destination planning superseded or failed'))
        self.assertGreaterEqual(time.monotonic_ns(),deadline)
        self.assertIs(self.k.controller.current,record)
        self.assertTrue(all(r['outcome']=='complete' and r['evidence']['completeServerEOF'] for r in self.k.ipc.reader.rows.values()))
        self.assert_no_effect()
    def test_original_stored_material_apply_guard_before_focus(self):
        plans=self.k.plans();w,plan=plans[0]
        (self.k.controls/w['address']).write_text('2 0 '+w['stableId']+'\n')
        with self.assertRaisesRegex(ValueError,'stored destination changed'):self.k.desktop.apply_destination(w,plan)
        self.assert_no_effect()
    def test_original_live_lifetime_apply_guard_before_focus(self):
        plans=self.k.plans();w,plan=plans[0];w=deepcopy(w)
        self.k.fixture.windows[0]['pid']+=1000
        with self.assertRaisesRegex(ValueError,'identity changed before'):self.k.desktop.apply_destination(w,plan)
        self.assert_no_effect()
    def test_original_wrong_plan_identity_refused_before_focus(self):
        plans=self.k.plans();w,plan=plans[0];plan['identity'][2]+=1000
        with self.assertRaisesRegex(ValueError,'plan identity differs'):self.k.desktop.apply_destination(w,plan)
        self.assert_no_effect()
    def test_original_atomic_six_focus_can_cross_deadline_but_cannot_seed(self):
        self.k.dispatch_delay=.35
        record=self.k.request();self.k.wait_worker()
        self.assertEqual(len(self.k.focus()),6)
        self.assertEqual(record.profile['failure'],'original scene receipt deadline before seed')
        self.assertGreaterEqual(record.profile['metadataValidatedNs']-record.profile['receivedNs'],2_000_000_000)
        self.assertEqual(len([r for r in self.k.requests if r['wire']=='CPU_REFRESH']),3)
        self.assertEqual(len(self.k.fixture.commits),3)
        self.assertFalse(any(m['command']=='seed' for m in self.k.transport.sent));self.k.assert_drained()
    def test_original_nonzero_native_focus_keeps_exact_unknown_job(self):
        plans=self.k.plans();self.k.dispatch_error=True
        with self.assertRaises(subprocess.CalledProcessError):self.k.desktop.apply_destination(*plans[0])
        self.assertEqual(len(self.k.focus()),1)
        self.assertEqual(len(self.k.keeper.jobs),1)
        job=next(iter(self.k.keeper.jobs.values()))
        self.assertEqual(job['kind'],'native-effect');self.assertNotEqual(job['phase'],'closed')
        with self.assertRaisesRegex(ValueError,'outstanding'):self.k.keeper.stop()
    def test_original_native_focus_timeout_keeps_uncertain_job_and_exact_cleanup(self):
        plans=self.k.plans();self.k.native_gate=threading.Event()
        thread,result=self.threaded(lambda:self.k.desktop.apply_destination(*plans[0]))
        self.finish(thread,result)
        self.assertIsInstance(result['error'],subprocess.TimeoutExpired)
        self.assertEqual(len(self.k.keeper.jobs),1)
        self.assertEqual(next(iter(self.k.keeper.jobs.values()))['kind'],'native-effect')
        self.k.native_gate.set()
        with self.assertRaisesRegex(ValueError,'outstanding'):self.k.keeper.stop()


if __name__=='__main__':unittest.main()
