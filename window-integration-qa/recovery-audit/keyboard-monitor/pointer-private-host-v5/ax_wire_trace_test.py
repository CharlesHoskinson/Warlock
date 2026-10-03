import tempfile,unittest
from pathlib import Path
from ax_wire_trace import signed_query_evidence
from private_helpers import unexpected,portal_activations
WIRE="""method call time=100.250000 sender=:1.3 -> destination=:1.6 serial=81 path=/frame; interface=org.a11y.atspi.Component; member=GetAccessibleAtPoint
   int32 180
   int32 -14
   uint32 1
method return time=100.260000 sender=:1.6 -> destination=:1.3 serial=90 reply_serial=81
   struct {
      string ":1.6"
      object path "/actual-popup-child"
   }
"""
class AXWire(unittest.TestCase):
 def run_wire(self,text,**kwargs):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'wire';p.write_text(text)
   return signed_query_evidence(p,**dict(after=100.2,reader_bus=':1.3',app_bus=':1.6',x=180,y=-14,item_path='/actual-popup-child',**kwargs))
 def test_actual_signed_reply_correlated(self):self.assertEqual(self.run_wire(WIRE)[0]['signedCoordinates'],[180,-14])
 def test_wrong_owner_refused(self):self.assertEqual(self.run_wire(WIRE.replace('sender=:1.3','sender=:1.4')),[])
 def test_old_query_refused(self):self.assertEqual(self.run_wire(WIRE.replace('100.250000','99.900000')),[])
 def test_mismatched_reply_refused(self):self.assertEqual(self.run_wire(WIRE.replace('reply_serial=81','reply_serial=82')),[])
 def test_unsigned_query_refused(self):self.assertEqual(self.run_wire(WIRE.replace('int32 -14','uint32 4294967282')),[])
 def test_screen_query_refused(self):self.assertEqual(self.run_wire(WIRE.replace('uint32 1','uint32 0')),[])
 def test_wrong_child_refused(self):self.assertEqual(self.run_wire(WIRE.replace('/actual-popup-child','/frame')),[])
 def test_absent_reply_refused(self):self.assertEqual(self.run_wire(WIRE.split('method return')[0]),[])
 def test_exact_infrastructure_allowed(self):self.assertEqual(unexpected([dict(pid=1,start='2')],[dict(pid=1,start='2')]),[])
 def test_pid_reuse_is_unexpected(self):self.assertEqual(unexpected([dict(pid=1,start='3')],[dict(pid=1,start='2')]),[dict(pid=1,start='3')])
 def test_activated_helper_is_unexpected(self):self.assertEqual(unexpected([dict(pid=2,start='2')],[dict(pid=1,start='2')]),[dict(pid=2,start='2')])
 def test_retained_real_portal_autoload_detected(self):
  p=Path(__file__).parent/'mouse-review-signed-v3/portal-analysis/retained-privateBus.log'
  names=portal_activations(p.read_text())
  self.assertIn('org.freedesktop.portal.Desktop',names);self.assertIn('org.gtk.vfs.Daemon',names)
 def test_nonportal_accessibility_startup_not_a_portal_claim(self):
  self.assertEqual(portal_activations("Activating service name='org.freedesktop.systemd1'"),[])
if __name__=='__main__':unittest.main()
