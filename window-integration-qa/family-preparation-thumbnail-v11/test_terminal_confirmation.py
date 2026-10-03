"""Actual kernel and durable refusal evidence; no native GUI acceptance."""
from contextlib import contextmanager
import json,os,unittest
from unittest.mock import patch
import test_actual_binding as actual
import module_binding as binding

class TerminalConfirmationTests(unittest.TestCase):
 setUp=actual.OwnerKernelTests.setUp
 tearDown=actual.OwnerKernelTests.tearDown
 query=actual.OwnerKernelTests.query
 package=actual.OwnerKernelTests.package
 bound=actual.OwnerKernelTests.bound
 @contextmanager
 def terminal(self,refused=False):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest)
   if refused:
    self.handler=lambda c,d:c.sendall(b'[{')
    with self.assertRaises(ValueError):self.query()
   else:self.assertEqual(self.query(),b'[]')
   journal=self.store.read();journal['helperOwnership']={'keeper':{'servicePID':os.getpid(),'serviceStart':actual.service_runtime.process_start(os.getpid()),'rootIdentity':list(self.lease.root_identity)}};self.store.write(journal);self.lease.close()
   service=type('CpuTerminal',(),{'lease':self.lease,'store':self.store,'closed':True,'failure':None})()
   modules=binding._observe('terminal',previous=initial)
   yield factory,service,destination/'actual-terminal-binding.json',modules
 def evidence(self,path):
  return json.loads(path.read_text()),json.loads(path.with_name('actual-terminal-binding-confirmation.json').read_text())
 def test_genuine_refused_query_retains_primary_without_unbound_error(self):
  with self.terminal(refused=True) as args:
   with self.assertRaisesRegex(ValueError,'actual terminal binding refused'):binding.archive_final(*args)
   raw,confirm=self.evidence(args[2])
   self.assertEqual(raw['errors'],[{'type':'ValueError','message':'complete closed actual query proof required'}])
   self.assertEqual(confirm['errors'],[{'type':'ValueError','message':'terminal binding refused before post-disk acceptance'}])
   self.assertFalse(raw['usable']);self.assertIn('terminalBatchConfirmation',confirm)
   self.assertEqual(raw['ledger']['history'][-1]['outcome'],'refused')
 def test_missing_predisk_source_packet_gets_fresh_confirmation_and_stays_refused(self):
  with self.terminal() as args:
   packet=binding.source_packet()
   with patch.object(binding,'source_packet',side_effect=[ValueError('pre-disk source packet unavailable'),packet]) as source,self.assertRaisesRegex(ValueError,'actual terminal binding refused'):binding.archive_final(*args)
   raw,confirm=self.evidence(args[2]);self.assertEqual(source.call_count,2)
   self.assertEqual(raw['errors'],[{'type':'ValueError','message':'pre-disk source packet unavailable'}])
   self.assertEqual(confirm['errors'],[{'type':'ValueError','message':'terminal binding refused before post-disk acceptance'}]);self.assertFalse(raw['usable'])
 def test_missing_postdisk_source_packet_cannot_reuse_predisk_packet(self):
  with self.terminal() as args:
   packet=binding.source_packet()
   with patch.object(binding,'source_packet',side_effect=[packet,ValueError('post-disk source packet unavailable')]) as source,self.assertRaisesRegex(ValueError,'actual terminal binding refused'):binding.archive_final(*args)
   raw,confirm=self.evidence(args[2]);self.assertEqual(source.call_count,2)
   self.assertEqual(raw['errors'],[]);self.assertEqual(confirm['errors'],[{'type':'ValueError','message':'post-disk source packet unavailable'}]);self.assertFalse(raw['usable'])
 def test_normal_complete_query_acquires_two_independent_source_packets(self):
  with self.terminal() as args:
   real=binding.source_packet;packets=[]
   def fresh():
    p=real();packets.append(p);return p
   with patch.object(binding,'source_packet',side_effect=fresh) as source:accepted=binding.archive_final(*args)
   self.assertEqual(source.call_count,2);self.assertEqual(len(packets),2);self.assertIsNot(packets[0],packets[1]);self.assertEqual(packets[0],packets[1])
   self.assertTrue(accepted['usable']);raw,confirm=self.evidence(args[2]);self.assertEqual(raw['errors'],[]);self.assertEqual(confirm['errors'],[])

if __name__=='__main__':unittest.main()
