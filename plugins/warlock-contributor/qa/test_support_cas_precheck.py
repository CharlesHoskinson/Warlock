"""Pure support-metadata pre-CAS controls. No broker, Git or source effects."""
import argparse
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

class SupportCasPrecheckTests(unittest.TestCase):
    def setUp(self):
        self.module=MODULE; self.actor='root-nextloop-20261106'; self.run='warlock-20261105-completion'
        self.env={'AGENTBUS_RUN':self.run,'AGENTBUS_AGENT':self.actor}
        self.paths=['plugins/warlock-contributor/scripts/warlock.py','plugins/warlock-contributor/qa/test_delivery.py']
        self.prefix='.warlock-contributor/evidence/support-custody/test/'
        self.entries=[{'path':name,'recordSnapshot':self.prefix+'record.json','currentSnapshot':self.prefix+str(i)+'.py','claimProof':self.prefix+'claims.json','reviewFile':self.prefix+str(i)+'-review.json','reason':'Reviewed exact support transition'}for i,name in enumerate(self.paths)]
        self.proofs={self.prefix+'claims.json':{'schema':1,'owner':'root-agentbus','claimOwner':self.actor,'run':self.run}}
    def check(self):
        return self.module.validate_plan('.warlock-contributor/transition.json',self.entries,self.proofs,self.paths,self.run,self.actor,self.env)
    def test_correct_scope_and_assigned_environment_accept_without_mutation(self):
        before=copy.deepcopy((self.entries,self.proofs,self.env));result=self.check()
        self.assertTrue(result['scopePrecheckPassed']);self.assertFalse(result['effectsPerformed'])
        self.assertEqual(before,(self.entries,self.proofs,self.env))
    def test_actual_installer_wrong_evidence_namespace_refuses_before_cas(self):
        for key in ('recordSnapshot','currentSnapshot','claimProof','reviewFile'):
            saved=self.entries[0][key];self.entries[0][key]='.warlock-contributor/evidence/nextloop-20261106/qualified-install/'+key
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.entries[0][key]=saved
    def test_transition_outside_ignored_root_and_traversal_refuse(self):
        for value in ('docs/transition.json','/tmp/transition.json','.warlock-contributor/../transition.json'):
            with self.subTest(value=value),self.assertRaises(ValueError):self.module.validate_plan(value,self.entries,self.proofs,self.paths,self.run,self.actor,self.env)
    def test_evidence_traversal_and_noncanonical_path_refuse(self):
        for value in (self.prefix+'../outside.json',self.prefix+'a//b.json',self.prefix+'a/./b.json'):
            self.entries[0]['recordSnapshot']=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.check()
    def test_missing_or_wrong_assigned_run_and_agent_refuse(self):
        for key in ('AGENTBUS_RUN','AGENTBUS_AGENT'):
            saved=self.env.pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.env[key]='other'
            with self.assertRaises(ValueError):self.check()
            self.env[key]=saved
    def test_proof_actor_or_run_mismatch_refuses(self):
        for key in ('claimOwner','run'):
            proof=self.proofs[self.prefix+'claims.json'];saved=proof[key];proof[key]='root-agentbus'
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            proof[key]=saved
    def test_partial_duplicate_or_unexpected_destination_batch_refuses(self):
        saved=copy.deepcopy(self.entries)
        for value in ([saved[0]], [saved[0],saved[0]], [dict(saved[0],path='docs/HANDOFF.md'),saved[1]]):
            self.entries=value
            with self.assertRaises(ValueError):self.check()
    def test_missing_proof_or_inexact_transition_fields_refuse(self):
        saved=self.proofs;self.proofs={}
        with self.assertRaises(ValueError):self.check()
        self.proofs=saved;self.entries[0]['extra']='not-a-core-transition-field'
        with self.assertRaises(ValueError):self.check()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--module',type=Path,required=True);args,rest=parser.parse_known_args()
    spec=importlib.util.spec_from_file_location('support_cas_precheck_under_test',args.module);MODULE=importlib.util.module_from_spec(spec);spec.loader.exec_module(MODULE)
    unittest.main(argv=[sys.argv[0],*rest])
else:
    spec=importlib.util.spec_from_file_location('support_cas_precheck_under_test',Path(__file__).resolve().parents[1]/'scripts/support_cas_precheck.py');MODULE=importlib.util.module_from_spec(spec);spec.loader.exec_module(MODULE)
