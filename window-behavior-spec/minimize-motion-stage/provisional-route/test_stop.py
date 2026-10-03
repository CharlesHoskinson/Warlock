#!/usr/bin/env python3
import fcntl,json,os,socket,time,unittest
import test_motion_service as base
class StopTests(unittest.TestCase):
 setUp=base.ServiceTests.setUp
 tearDown=base.ServiceTests.tearDown
 run_client=base.ServiceTests.run_client
 save=base.ServiceTests.save
 read=base.ServiceTests.read
 def test_absent_service_stop_is_idempotent_and_never_starts(self):
  for _ in range(3):
   r=self.run_client('stop');self.assertEqual(r.returncode,0,r.stderr)
  self.assertFalse(self.service_root.exists());self.assertFalse(self.read()['calls'])
 def test_empty_idle_journal_stop_is_idempotent(self):
  self.service_root.mkdir(parents=True);journal=self.service_root/'pending.json';journal.write_text('[]')
  for _ in range(3):self.assertEqual(self.run_client('stop').returncode,0)
  self.assertEqual(journal.read_text(),'[]');self.assertFalse((self.service_root/'daemon.pid').exists())
 def test_stale_socket_and_stale_dead_pid_stop_without_start(self):
  self.service_root.mkdir(parents=True)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stale:stale.bind(str(self.service_root/'control.sock'))
  (self.service_root/'pending.json').write_text('[]');(self.service_root/'daemon.pid').write_text('99999999')
  self.assertEqual(self.run_client('stop').returncode,0);self.assertEqual(self.read()['calls'],[])
  (self.service_root/'control.sock').unlink();(self.service_root/'daemon.pid').unlink()
 def test_pending_accepted_journal_is_preserved_and_not_reported_idle(self):
  self.service_root.mkdir(parents=True);p=self.service_root/'pending.json';p.write_text('[{"token":"accepted"}]')
  r=self.run_client('stop');self.assertEqual(r.returncode,3);self.assertIn('pending recovery',r.stderr)
  self.assertEqual(json.loads(p.read_text()),[{'token':'accepted'}]);self.assertFalse((self.service_root/'daemon.pid').exists())
 def test_startup_daemon_lock_prevents_false_idle(self):
  self.service_root.mkdir(parents=True)
  with (self.service_root/'daemon.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);r=self.run_client('stop');self.assertEqual(r.returncode,3)
  self.assertFalse((self.service_root/'daemon.pid').exists())
 def test_live_pid_without_listener_is_not_reported_idle_or_killed(self):
  self.service_root.mkdir(parents=True);(self.service_root/'daemon.pid').write_text(str(os.getpid()))
  r=self.run_client('stop');self.assertEqual(r.returncode,3);self.assertIn('daemon exists',r.stderr)
  (self.service_root/'daemon.pid').unlink()
 def test_existing_listener_shutdown_ack_then_idle_repeat(self):
  r=self.run_client('request','minimize','0x10','stable10','100');self.assertEqual(r.returncode,0,r.stderr)
  self.assertEqual(self.run_client('stop').returncode,0)
  deadline=time.monotonic()+3
  while (self.service_root/'daemon.pid').exists() and time.monotonic()<deadline:time.sleep(.03)
  self.assertFalse((self.service_root/'daemon.pid').exists());self.assertEqual(self.run_client('stop').returncode,0)
if __name__=='__main__':unittest.main()
