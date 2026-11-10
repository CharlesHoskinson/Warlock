#!/usr/bin/env python3
"""Fixed real admitted RSI event/evidence binding controls; no metadata preparation."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,sys,unittest
p=argparse.ArgumentParser();p.add_argument('--module',type=Path,required=True);args,rest=p.parse_known_args()
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('native9_rsi_binding_helper',args.module);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
fixture_path=Path(__file__).resolve().parent/'actual-event-evidence.json'
assert hashlib.sha256(fixture_path.read_bytes()).hexdigest()=='f5f8d3fe0b490a3c7fd4ba2bef614c946c3c17b7169a36f20cb00894bff2f5ec'
fixture=json.loads(fixture_path.read_bytes())
core=m.load('native9_binding_actual_core',m.ROOT/m.CORE,m.CORE_SHA)
class Controls(unittest.TestCase):
 def setUp(self):
  self.expected=copy.deepcopy(fixture['expectedEvent'])
  self.record={'workflowPolicy':2,'delivery':{'authorizationExpiresUTC':fixture['actualInitialAuthorizationExpiresUTC'],'events':[copy.deepcopy(fixture['admittedEvent'])]}}
  self.history={'candidateSha256':self.expected['candidateSha256'],'integrated':{'revision':self.expected['integrationRevision']},'rsi':copy.deepcopy(fixture['validatedEvidence'])}
 def check_binding(self):return m.validate_admitted_rsi(core,self.record,self.history,self.expected)
 def test_real_admitted_event_and_resolved_validated_evidence(self):
  self.assertEqual(json.loads(core.delivery_ref(m.ROOT,self.expected['evidence'])),fixture['validatedEvidence'])
  self.assertEqual(self.check_binding(),fixture['validatedEvidence'])
 def test_mismatched_replay_evidence_refused(self):
  self.history['rsi']['reason']='changed replay evidence'
  with self.assertRaises(ValueError):self.check_binding()
 def test_missing_admitted_event_refused(self):
  self.record['delivery']['events']=[]
  with self.assertRaises(ValueError):self.check_binding()
 def test_wrong_disposition_even_in_matching_event_refused(self):
  self.expected['disposition']='no-change';self.record['delivery']['events'][0]['disposition']='no-change'
  with self.assertRaises(ValueError):self.check_binding()
 def test_duplicate_matching_admitted_event_refused(self):
  self.record['delivery']['events'].append(copy.deepcopy(self.record['delivery']['events'][0]))
  with self.assertRaises(ValueError):self.check_binding()
if __name__=='__main__':unittest.main(argv=[sys.argv[0],*rest])
