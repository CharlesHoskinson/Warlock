import unittest
from normal_frame_control import settle_frames
class Control(unittest.TestCase):
 def run_gate(self,values):
  now=[0];calls=[]
  def read(n):calls.append(n);return values[min(n,len(values)-1)]
  result=settle_frames(read,lambda:now[0],lambda d:now.__setitem__(0,now[0]+d),timeout=.7)
  return result,calls
 def test_three_complete_matching_frames_required(self):
  ok,calls=self.run_gate([b'a',b'b',b'b',b'b']);self.assertTrue(ok);self.assertEqual(len(calls),4)
 def test_no_masked_warning_or_dynamic_pixels(self):
  now=[0];calls=[]
  def read(n):calls.append(n);return bytes([n%2])
  self.assertFalse(settle_frames(read,lambda:now[0],lambda d:now.__setitem__(0,now[0]+d),timeout=.7));self.assertGreater(len(calls),3)
 def test_instability_resets_count(self):
  ok,calls=self.run_gate([b'a',b'a',b'b',b'b',b'b']);self.assertTrue(ok);self.assertEqual(len(calls),5)
 def test_empty_frame_rejected(self):
  with self.assertRaises(ValueError):self.run_gate([b''])
if __name__=='__main__':unittest.main()
