"""Fresh cancel-ACK scenes retain lifetime expectations without old authority."""
import copy,unittest
import test_reduced_validation as base
from scene_controller import key

class Tests(unittest.TestCase):
 setUp=base.Tests.setUp
 tearDown=base.Tests.tearDown
 wait=base.Tests.wait
 request=base.Tests.request
 reserve=base.Tests.reserve
 event=base.Tests.event
 moving=base.Tests.moving
 cancel_count=base.Tests.cancel_count
 ack=base.Tests.ack
 def rejected_changed_scope(self,change):
  old,receipt=self.moving();original=copy.deepcopy(old.members);commits=list(self.d.commits);captures=self.d.captures;destinations=list(self.d.destinations)
  change()
  self.assertTrue(self.ack(old));fresh=self.c.current
  self.assertIsNot(fresh,old);self.assertEqual([key(w)for w in fresh.members],[key(w)for w in original])
  self.assertFalse(fresh.validated);self.assertIsNone(fresh.accepted_operation);self.assertEqual(fresh.sources,[]);self.assertIsNone(fresh.previous)
  self.d.block.set();self.wait(lambda:self.c.current is None)
  self.assertIn('failure',fresh.profile);self.assertFalse(fresh.validated);self.assertEqual(fresh.profile['managerReceipt'],receipt['receipt'])
  self.assertEqual(self.d.commits,commits);self.assertEqual(self.d.captures,captures);self.assertEqual(self.d.destinations,destinations)
  self.assertFalse(any(m.get('token')==fresh.token and m['command']in ('seed','validate','start','commit')for m in self.t.sent))
 def test_closed_noncaptured_member_refuses_after_exact_ack(self):
  def change():
   closed=self.d.windows.pop();self.d.native=[m for m in self.d.native if key(m)!=key(closed)]
  self.rejected_changed_scope(change)
 def test_same_count_member_pid_reuse_refuses_after_exact_ack(self):
  def change():
   self.d.windows[-1]['pid']+=100;self.d.native[-1]['pid']+=100
  self.rejected_changed_scope(change)
 def test_new_descendant_cannot_expand_original_ack_scope(self):
  def change():
   new=copy.deepcopy(self.d.windows[-1]);new.update(address='0xdd04',stableId='dd04',pid=44);self.d.windows.append(new)
   self.d.native.append(dict(new,parent=self.d.windows[-2]['address'],parentStableId=self.d.windows[-2]['stableId'],modal=True))
  self.rejected_changed_scope(change)
 def test_unmapped_member_cannot_truncate_original_ack_scope(self):
  def change():
   self.d.windows[-1]['mapped']=False;self.d.native[-1]['mapped']=False
  self.rejected_changed_scope(change)
 def test_complete_current_family_reobserves_geometry_and_old_order(self):
  old,receipt=self.moving();expected=[key(m)for m in old.members];received=old.profile['receivedNs']
  for members in (self.d.windows,self.d.native):
   for m in members:m['at']=[m['at'][0]+17,m['at'][1]+23]
  self.assertTrue(self.ack(old));fresh=self.c.current
  self.assertEqual([key(m)for m in fresh.members],expected);self.assertEqual(fresh.profile['receivedNs'],received);self.assertFalse(fresh.validated);self.assertEqual(fresh.sources,[])
  self.d.block.set();self.wait(lambda:self.c.current is None)
  self.assertNotIn('failure',fresh.profile);self.assertEqual([key(m)for m in fresh.members],expected);self.assertEqual([m['at']for m in fresh.members],[m['at']for m in self.d.windows])
  self.assertEqual([op for op,*_ in self.d.commits],['minimize']*3+['restore']*3);self.assertEqual(fresh.profile['managerReceipt'],receipt['receipt'])

if __name__=='__main__':unittest.main(verbosity=2)
