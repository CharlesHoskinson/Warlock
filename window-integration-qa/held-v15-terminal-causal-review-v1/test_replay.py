"""Fault injection into copies of retained receipts; no native commands."""
from pathlib import Path
import copy,json,unittest
import replay_v3 as replay
class Faults(unittest.TestCase):
 def setUp(self):
  self.d=replay.js(replay.V/'qs-terminal-drain.json');self.answer=copy.deepcopy(self.d['samples'][-1]['answer']);self.nonce=self.d['nonce'];self.rows=copy.deepcopy(self.d['lastRawHelperRows'])
 def test_retained_actual_normal_receipts_close(self):self.assertTrue(replay.process_receipts(self.answer,self.nonce)[0]);self.assertEqual(len(replay.helpers(self.rows)),46)
 def test_exit120_cannot_be_normalized(self):
  next(r for r in self.answer['states'][0]['records']if r['event']=='exited')['code']=120
  with self.assertRaises(ValueError):replay.process_receipts(self.answer,self.nonce)
  next(r for r in self.rows if r['event']=='terminal')['exitCode']=120
  with self.assertRaises(ValueError):replay.helpers(self.rows)
 def test_missing_and_wrong_generation_cannot_close(self):
  records=self.answer['states'][0]['records'];index=next(i for i,r in enumerate(records)if r['event']=='exited');records.pop(index)
  with self.assertRaises(ValueError):replay.process_receipts(self.answer,self.nonce)
 def test_wrong_nonce_refuses(self):
  with self.assertRaises(ValueError):replay.process_receipts(self.answer,'0'*32)
 def test_record_prefix_reset_refuses(self):
  previous=copy.deepcopy(self.answer);previous['states'][0]['records'][0]['utcMs']+=1
  with self.assertRaises(ValueError):replay.process_receipts(self.answer,self.nonce,previous)
 def test_duplicate_terminal_and_refusal_fail(self):
  self.rows.append(copy.deepcopy(next(r for r in self.rows if r['event']=='terminal')))
  with self.assertRaises(ValueError):replay.helpers(self.rows)
  self.rows=copy.deepcopy(self.d['lastRawHelperRows']);self.rows.append({'event':'refused'})
  with self.assertRaises(ValueError):replay.helpers(self.rows)
 def test_fresh_post_quiesce_poll_cannot_borrow_prior_success(self):
  state=self.answer['states'][0];state['records'].append(dict(event='requested',utcMs=state['records'][-1]['utcMs']+1,kind='snapshot',generation=state['generations']['snapshot']+1,commandDeclaration=['owned']))
  with self.assertRaises(ValueError):replay.process_receipts(self.answer,self.nonce)
if __name__=='__main__':unittest.main()
