#!/usr/bin/env python3
"""Root-only actual-chain/refusal controls; no loader, GUI, or native execution."""
import argparse, ast, copy, hashlib, importlib.util, json, os, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
parser=argparse.ArgumentParser()
for name in ('module','collector','proof','proof-sha256','boot','boot-sha256'):parser.add_argument('--'+name,required=True)
args,rest=parser.parse_known_args()
spec=importlib.util.spec_from_file_location('cursor_contract',args.module);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def pinned(ref,cap):
 p=Path(ref['path']);body=p.read_bytes()
 if not p.is_file() or p.is_symlink() or len(body)>cap or hashlib.sha256(body).hexdigest()!=ref['sha256']:raise ValueError('fixed test input hash or identity differs')
 return body
PROOF={'path':args.proof,'sha256':args.proof_sha256};BOOT={'path':args.boot,'sha256':args.boot_sha256}
class CursorCorrespondence(unittest.TestCase):
 def setUp(self):
  self.proof=json.loads(pinned(PROOF,4*1024*1024));self.report=json.loads(pinned(self.proof['qualification'],4*1024*1024));self.nested=copy.deepcopy(self.proof['historicalNested']);self.original=copy.deepcopy(self.nested);self.current=m.CurrentBoot(BOOT,pinned)
 def run_case(self):
  actual=self.current.pinned
  def changed(ref,cap):
   body=actual(ref,cap)
   if ref==PROOF:return json.dumps(self.proof).encode()
   if ref==self.proof['qualification']:return json.dumps(self.report).encode()
   return body
  with patch.object(self.current,'pinned',side_effect=changed):return m.cursor_inputs(self.current,self.nested,PROOF)
 def refused(self):
  with self.assertRaises((ValueError,KeyError,TypeError)):self.run_case()
 def test_actual_qualified_chain_one_delta_and_no_basis_mutation(self):
  live=self.run_case();expected=dict(self.original['inputs']);del expected[m.CURSOR_OLD['path']];expected[m.CURSOR_NEW['path']]=m.CURSOR_NEW['sha256'];self.assertEqual(live,expected);self.assertEqual(len(live),205);self.assertEqual(self.nested,self.original)
 def test_absent_proof_preserves_legacy_map_without_reads(self):
  with patch.object(self.current,'pinned',side_effect=AssertionError('unexpected read')):self.assertIs(m.cursor_inputs(self.current,self.nested,None),self.nested['inputs'])
 def test_missing_or_malformed_proof_refused(self):
  with self.assertRaises((ValueError,FileNotFoundError)):m.cursor_inputs(self.current,self.nested,{'path':args.proof,'sha256':'0'*64})
  self.proof['extra']=True;self.refused()
 def test_wrong_foundation_readiness_or_basis_refused(self):
  for name in ('foundationPacket','foundationReport','providerReadiness'):
   self.setUp();self.proof[name]['sha256']='0'*64;self.refused()
  self.setUp();self.proof['basisSha256']='0'*64;self.refused()
 def test_wrong_reviewer_or_missing_actual_success_refused(self):
  self.proof['reviewer']='root';self.refused();self.setUp();self.report['passed']=False;self.refused()
 def test_wrong_boot_refused(self):self.report['currentBootId']='other';self.refused()
 def test_changed_body_refused(self):
  actual=self.current.pinned
  def corrupt(ref,cap):
   body=actual(ref,cap)
   return body+b'changed' if ref==m.CURSOR_NEW else body
  with patch.object(self.current,'pinned',side_effect=corrupt),self.assertRaises(ValueError):m.cursor_inputs(self.current,self.nested,PROOF)
 def test_changed_alias_refused(self):
  with patch.object(m.os,'readlink',return_value='foreign.so'),self.assertRaises(ValueError):self.run_case()
 def test_old_map_wrong_hash_missing_old_or_extra_new_refused(self):
  for action in ('hash','missing','already-current'):
   self.setUp()
   if action=='hash':self.nested['inputs'][m.CURSOR_OLD['path']]='0'*64
   elif action=='missing':del self.nested['inputs'][m.CURSOR_OLD['path']]
   else:self.nested['inputs'][m.CURSOR_NEW['path']]=m.CURSOR_NEW['sha256']
   self.refused()
 def test_other_basis_delta_refused(self):self.nested['inputs']['/unqualified']='0'*64;self.refused()
 def test_loader_old_cursor_missing_new_or_extra_path_refused(self):
  for action in ('old','missing','extra'):
   self.setUp()
   if action=='old':self.report['resolvedFiles'][m.CURSOR_OLD['path']]=m.CURSOR_OLD['sha256']
   elif action=='missing':self.report['resolvedFiles'].pop(m.CURSOR_NEW['path'])
   else:self.report['resolvedFiles']['/unqualified']='0'*64
   self.refused()
 def test_loader_command_or_exit_refused(self):
  self.report['commands'][-1]['argv'][-1]='/usr/bin/false';self.refused();self.setUp();self.report['commands'][0]['exit']=1;self.refused()
 def test_package_member_symbols_or_owning_image_refused(self):
  self.report['package']['member']='usr/lib/other';self.refused();self.setUp();self.report['requiredSymbols']=self.report['requiredSymbols'][:-1];self.refused();self.setUp();self.report['hyprland']['sha256']='0'*64;self.refused()
 def test_all_three_provider_routes_carry_proof(self):
  helper=Path(args.module).read_text();collector=Path(args.collector).read_text()
  self.assertIn("cursor_inputs(current, nested, cursor_correspondence).items()",helper)
  self.assertIn("verify_private_provider(current, collector, base, packet['nested'], source_correspondence, cursor_correspondence)",helper)
  self.assertIn("required = list(required) + [CURSOR_NEW['path']]",helper)
  self.assertIn("foundation['nested'],packet['reuse']['providerSourceCorrespondence'],cursor_reference",collector)
  self.assertIn("nested,self.provider_source_correspondence,self.cursor_correspondence",collector)
  self.assertIn("self.clock,self.p,self.provider_source_correspondence,self.cursor_correspondence",collector)
 def test_nested_map_must_contain_required_actual_cursor(self):
  current=SimpleNamespace(devices=lambda graphics:{})
  base=SimpleNamespace(left=lambda clock:None)
  with self.assertRaisesRegex(ValueError,'required pinned provider not mapped'):m.strict_snapshot_files(current,base,{},[],{m.CURSOR_NEW['path']:m.CURSOR_NEW['sha256']},[m.CURSOR_NEW['path']],None,{})
 def test_32_literal_refusal_samples(self):
  for seed in range(32):
   self.setUp()
   if seed%4==0:self.report['resolvedFiles'][m.CURSOR_NEW['path']]='0'*64
   elif seed%4==1:self.proof['historicalNested']['libraryDir']='/unqualified/'+str(seed)
   elif seed%4==2:self.report['aliasChain'][0]['target']='other'+str(seed)
   else:self.report['sourceChanged']=True
   with self.subTest(seed=seed):self.refused()
if __name__=='__main__':unittest.main(argv=[__file__]+rest)
