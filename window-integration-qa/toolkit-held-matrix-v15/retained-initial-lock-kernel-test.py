"""Actual private flock contention and deadline regressions. CPU/kernel only."""
from pathlib import Path
import fcntl,os,subprocess,tempfile,time,unittest
from unittest.mock import patch
import helper_observer as observer
from arm_lock_candidate_fixture import locked_until,remaining

class BoundedArmLock(unittest.TestCase):
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory();self.path=Path(self.temporary.name)/'journal';self.path.touch(mode=0o600);self.children=[]
 def tearDown(self):
  for child in self.children:
   if child.poll()is None:child.stdin.close()
   child.wait(timeout=2)
   for stream in (child.stdin,child.stdout,child.stderr):
    if stream and not stream.closed:stream.close()
  self.temporary.cleanup()
 def holder(self):
  script='import fcntl,sys;f=open(sys.argv[1],"r+");fcntl.flock(f,fcntl.LOCK_EX);print("exact-flock-ready",flush=True);sys.stdin.read()'
  child=subprocess.Popen(['/usr/bin/python3','-IS','-c',script,str(self.path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  self.children.append(child);self.assertEqual(child.stdout.readline().strip(),'exact-flock-ready');self.identity=observer.process(child.pid);return child
 def test_actual_held_lock_expires_without_acquisition(self):
  child=self.holder();begin=time.monotonic();deadline=begin+.09;busy=[]
  with self.assertRaisesRegex(TimeoutError,'Original evaluation arm deadline expired'):
   with locked_until(self.path,deadline,lambda:busy.append(time.monotonic())):self.fail('Held lock acquired')
  elapsed=time.monotonic()-begin;self.assertGreaterEqual(elapsed,.09);self.assertLess(elapsed,.4);self.assertTrue(busy);self.assertTrue(observer.still_live(self.identity));self.assertIsNone(child.poll())
  child.stdin.close();self.assertEqual(child.wait(timeout=2),0)
  with locked_until(self.path,time.monotonic()+.5):pass
 def test_actual_release_allows_acquire_with_same_deadline(self):
  child=self.holder();deadline=time.monotonic()+.5;busy=[]
  def release():
   busy.append(time.monotonic())
   if not child.stdin.closed:child.stdin.close()
  with locked_until(self.path,deadline,release)as stream:
   self.assertLess(time.monotonic(),deadline);stream.write('actual owned lock acquisition\n')
  self.assertTrue(busy);self.assertEqual(child.wait(timeout=2),0)
 def test_original_blocking_flock_can_overrun_budget(self):
  child=self.holder();script='import fcntl,sys;print("before-blocking",flush=True);f=open(sys.argv[1],"r+");fcntl.flock(f,fcntl.LOCK_EX);print("after-blocking",flush=True)'
  waiter=subprocess.Popen(['/usr/bin/python3','-IS','-c',script,str(self.path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);self.children.append(waiter)
  self.assertEqual(waiter.stdout.readline().strip(),'before-blocking');begin=time.monotonic();time.sleep(.09);self.assertIsNone(waiter.poll());child.stdin.close();self.assertEqual(waiter.stdout.readline().strip(),'after-blocking');self.assertEqual(waiter.wait(timeout=2),0);self.assertGreaterEqual(time.monotonic()-begin,.09);self.assertEqual(child.wait(timeout=2),0)
 def test_expiry_inside_lock_refuses_publication_and_releases(self):
  deadline=time.monotonic()+.04
  with self.assertRaises(TimeoutError):
   with locked_until(self.path,deadline):time.sleep(.05);remaining(deadline);self.fail('No late publication')
  with locked_until(self.path,time.monotonic()+.5):pass
  self.assertEqual(self.path.read_bytes(),b'')
 def test_expired_before_open_is_refused(self):
  with patch('arm_lock_candidate_fixture.os.open',side_effect=AssertionError('Must not open')):
   with self.assertRaises(TimeoutError):
    with locked_until(self.path,time.monotonic()):pass
 def test_wrong_mode_is_hard_refusal(self):
  self.path.chmod(0o644)
  with self.assertRaisesRegex(RuntimeError,'exact-mode'):
   with locked_until(self.path,time.monotonic()+.5):pass
 def test_unknown_flock_error_is_hard_refusal(self):
  import errno
  with patch('arm_lock_candidate_fixture.fcntl.flock',side_effect=OSError(errno.EINVAL,'test actual unknown')):
   with self.assertRaises(OSError)as error:
    with locked_until(self.path,time.monotonic()+.5):pass
   self.assertEqual(error.exception.errno,errno.EINVAL)
 def test_inode_replacement_before_lock_is_refused(self):
  real_open=os.open
  def replace(*args,**kwargs):
   fd=real_open(*args,**kwargs);other=self.path.with_name('replacement');other.touch(mode=0o600);other.replace(self.path);return fd
  with patch('arm_lock_candidate_fixture.os.open',side_effect=replace):
   with self.assertRaisesRegex(RuntimeError,'replaced'):
    with locked_until(self.path,time.monotonic()+.5):pass
