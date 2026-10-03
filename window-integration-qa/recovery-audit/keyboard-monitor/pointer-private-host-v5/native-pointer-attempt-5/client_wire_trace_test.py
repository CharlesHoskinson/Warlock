"""Controlled actual trace implementation tests; no application/bus connection."""
import importlib.util,json,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
spec=importlib.util.spec_from_file_location('client_wire_trace',Path(__file__).parent/'native-fixture/client_wire_trace.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class TraceTests(unittest.TestCase):
 def message(self,interface='org.freedesktop.a11y.PointerLocator',member='PointerPositionChanged'):
  body=NS(unpack=lambda:())
  return NS(get_body=lambda:body,get_message_type=lambda:4,get_serial=lambda:41,
     get_reply_serial=lambda:0,get_sender=lambda:':1.5',get_destination=lambda:':1.3',
     get_interface=lambda:interface,get_member=lambda:member)
 def test_filter_returns_exact_message_and_records_wire_metadata(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'trace';trace=module.WireTrace(p);message=self.message()
   self.assertIs(trace.filter(None,message,True,None),message);trace.close()
   row=json.loads(p.read_text());self.assertEqual(row['serial'],41);self.assertEqual(row['destination'],':1.3')
   self.assertEqual(row['body'],[]);self.assertEqual(len(trace.arrivals),1)
   self.assertEqual(p.stat().st_mode&0o777,0o600)
 def test_outgoing_pointer_packet_cannot_be_counted_as_incoming_signal(self):
  with tempfile.TemporaryDirectory() as d:
   trace=module.WireTrace(Path(d)/'trace');trace.filter(None,self.message(),False,None)
   self.assertEqual(trace.arrivals,[]);trace.close()
 def test_other_incoming_packet_is_logged_without_pointer_arrival(self):
  with tempfile.TemporaryDirectory() as d:
   trace=module.WireTrace(Path(d)/'trace');trace.filter(None,self.message('org.freedesktop.DBus','NameOwnerChanged'),True,None)
   self.assertEqual(trace.arrivals,[]);trace.close()
 def test_existing_trace_never_overwritten(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'trace';p.write_bytes(b'retained')
   with self.assertRaises(FileExistsError):module.WireTrace(p)
   self.assertEqual(p.read_bytes(),b'retained')
 def test_nonprivate_parent_refused(self):
  with tempfile.TemporaryDirectory() as d:
   os.chmod(d,0o755)
   with self.assertRaisesRegex(RuntimeError,'owned0700'):module.WireTrace(Path(d)/'trace')
   self.assertFalse((Path(d)/'trace').exists())
if __name__=='__main__':unittest.main(verbosity=2)
