#!/usr/bin/env python3
"""Observer-contract tests; no native desktop/window mutation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('trial',Path(__file__).with_name('native_motion_trial.py'))
trial=importlib.util.module_from_spec(spec);spec.loader.exec_module(trial)

class Observer(unittest.TestCase):
 def sample(self,progress=.35,operation='minimize',token='a'):
  start={'x':200,'y':300,'width':1000,'height':700};end={'x':10,'y':20,'width':19,'height':19}
  return {'observed':1,'finished':1.01,'imageDigest':'pixels','visual':{'identity':['0x1','a',10],'token':token,'operation':operation,'from':start,'to':end,'routeProgress':progress}}
 def reversed(self,before,progress=.4):
  after=self.sample(token='b',operation='restore');old=before['visual'];after['finished']=1.03
  after['visual']['from']={k:old['from'][k]+(old['to'][k]-old['from'][k])*progress for k in old['from']}
  return after
 def test_continuous_active_reversal(self):
  before=self.sample();result=trial.assert_reversal(before,self.reversed(before),'restore')
  self.assertTrue(result['samePixels']);self.assertAlmostEqual(result['reversalProgress'],.4)
 def test_full_window_reset_is_rejected(self):
  before=self.sample()
  with self.assertRaisesRegex(AssertionError,'reset/jumped'):trial.assert_reversal(before,self.reversed(before,0),'restore')
 def test_endpoint_arrival_is_rejected(self):
  before=self.sample();after=self.reversed(before,1);after['finished']=2
  with self.assertRaisesRegex(AssertionError,'endpoint'):trial.assert_reversal(before,after,'restore')
 def test_saturated_observer_bound_cannot_accept_either_endpoint(self):
  before=self.sample(progress=.001)
  for progress in (0,.0005,.9995,1):
   after=self.reversed(before,progress);after['finished']=2
   with self.subTest(progress=progress),self.assertRaisesRegex(AssertionError,'reset/jumped'):
    trial.assert_reversal(before,after,'restore')
 def test_saturated_bound_records_actual_interior_distances(self):
  before=self.sample(progress=.001);after=self.reversed(before,.995);after['finished']=1.285
  result=trial.assert_reversal(before,after,'restore')
  self.assertEqual(result['maximumProgress'],1);self.assertTrue(result['strictlyInterior'])
  self.assertGreater(result['distanceFromStartPx'],.5);self.assertGreater(result['distanceFromEndPx'],.5)
 def test_failure_retains_samples_and_computed_diagnostics(self):
  before=self.sample(progress=.001);after=self.reversed(before,1);after['finished']=2
  report={'samples':[before,after],'attempts':[],'continuity':[]}
  with self.assertRaises(trial.ReversalError):trial.record_reversal(report,before,after,'restore')
  self.assertEqual(len(report['samples']),2);self.assertFalse(report['attempts'][0]['passed'])
  self.assertEqual(report['attempts'][0]['diagnostics']['reversalProgress'],1)
  self.assertEqual(report['attempts'][0]['diagnostics']['distanceFromEndPx'],0)
 def test_changed_pixels_and_identity_are_rejected(self):
  before=self.sample();after=self.reversed(before);after['imageDigest']='other'
  with self.assertRaisesRegex(AssertionError,'pixels'):trial.assert_reversal(before,after,'restore')
  after=self.reversed(before);after['visual']['identity'][1]='reused'
  with self.assertRaisesRegex(AssertionError,'identity'):trial.assert_reversal(before,after,'restore')
 def test_off_route_start_is_rejected(self):
  before=self.sample();after=self.reversed(before);after['visual']['from']['width']+=100
  with self.assertRaisesRegex(AssertionError,'route'):trial.assert_reversal(before,after,'restore')
 def test_gate_ignores_loading_and_pending_readiness(self):
  original=[{'address':'0x1','stableId':'a','pid':10}]
  frame={'identity':['0x1','a',10],'token':'new','visible':True,'imageReady':True,'routeProgress':.2}
  with tempfile.TemporaryDirectory() as directory:
   image=Path(directory)/'image.png';image.write_bytes(b'captured')
   loading={'token':'new','identity':frame['identity'],'phase':'loading','image':str(image)}
   running={**loading,'phase':'running'}
   with patch.object(trial,'checked_current'),patch.object(trial,'visual',side_effect=[[frame],[frame]]),patch.object(trial,'records',side_effect=[[loading],[running]]):
    accepted=trial.active_sample(original,original[0])
   self.assertEqual(accepted['phase'],'running')
   self.assertEqual(accepted['imageDigest'],trial.hashlib.sha256(b'captured').hexdigest())
 def freeze_pair(self):
  before=self.sample();after=self.reversed(before);after['requestIssued']=1.001
  after['serviceProfile']={'received':1.002,'freezeSent':1.003,'freezeAck':1.004,'clientsStart':1.005,'clientsDone':1.006,'familyStart':1.007,'familyDone':1.008,'beginSent':1.009,
    'frozen':{'accepted':True,'rect':after['visual']['from'].copy(),'previousToken':'a','token':'b','routeProgress':.4}}
  return before,after
 def test_frozen_rect_and_query_order_are_proven(self):
  before,after=self.freeze_pair();result=trial.assert_freeze_profile(before,after)
  self.assertTrue(result['capturedRectanglePreserved']);self.assertAlmostEqual(result['receiptToFreezeMs'],2)
 def test_delayed_freeze_or_rectangle_reset_is_rejected_and_retained(self):
  for corrupt in ('order','rect','token'):
   before,after=self.freeze_pair()
   if corrupt=='order':after['serviceProfile']['freezeAck']=1.02
   elif corrupt=='rect':after['serviceProfile']['frozen']['rect']['width']+=10
   else:after['serviceProfile']['frozen']['previousToken']='other'
   report={'attempts':[],'continuity':[]}
   with self.subTest(corrupt=corrupt),self.assertRaises(trial.ReversalError):trial.record_reversal(report,before,after,'restore',True)
   self.assertFalse(report['attempts'][0]['passed']);self.assertIn('serviceProfile',report['attempts'][0]['diagnostics'])

if __name__=='__main__':unittest.main()
