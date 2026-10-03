"""Actual kernel stat disappearance, strict registration and exact gate regressions."""
import ast,copy,errno,hashlib,os,select,subprocess
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import helper_observer as observer
from proc_disappearance_fixture import observe
B=Path(__file__).resolve().parent
class Disappearance(unittest.TestCase):
 def test_actual_open_proc_stat_read_after_normal_exit_is_selected_gone(self):
  row=observe(observer);self.assertIsNone(row['error']);self.assertIs(row['result'],False);self.assertEqual(row['actualChildExit'],0);self.assertTrue(row['pidfdExitObserved']);self.assertTrue(row['procPathGone']);self.assertEqual(row['ownedUID'],os.getuid())
 def test_actual_same_kernel_esrch_stays_strict_for_fresh_registration(self):
  row=observe(observer,'process');self.assertEqual(row['error']['type'],'ProcessLookupError');self.assertEqual(row['error']['errno'],errno.ESRCH);self.assertIsNone(row['result']);self.assertEqual(row['actualChildExit'],0);self.assertTrue(row['pidfdExitObserved'])
 def test_actual_path_enoent_selected_gone_but_registration_refused(self):
  child=subprocess.Popen(['/usr/bin/python3','-IS','-c','import os;os.read(0,1);os._exit(0)'],stdin=subprocess.PIPE)
  try:
   identity=observer.process(child.pid);child.stdin.write(b'G');child.stdin.flush();child.wait(timeout=3);self.assertFalse(observer.still_live(identity))
   with self.assertRaises(FileNotFoundError) as error:observer.process(identity['pid'])
   self.assertEqual(error.exception.errno,errno.ENOENT)
  finally:child.stdin.close();child.wait(timeout=3)
 def test_exact_live_and_wrong_start_or_pgid_remain_distinct(self):
  row=observer.process(os.getpid());self.assertTrue(observer.still_live(row));self.assertFalse(observer.still_live(dict(row,start='0')));self.assertFalse(observer.still_live(dict(row,pgid=row['pgid']+1)))
 def test_actual_exact_zombie_stays_live_until_normal_reap(self):
  child=subprocess.Popen(['/usr/bin/python3','-IS','-c','import os;os.read(0,1);os._exit(0)'],stdin=subprocess.PIPE);fd=None
  try:
   row=observer.process(child.pid);fd=os.pidfd_open(child.pid);child.stdin.write(b'G');child.stdin.flush();poll=select.poll();poll.register(fd,select.POLLIN);self.assertTrue(poll.poll(2000));self.assertEqual(Path('/proc',str(child.pid),'stat').read_text().rsplit(') ',1)[1].split()[0],'Z');self.assertTrue(observer.still_live(row));child.wait(timeout=3);self.assertFalse(observer.still_live(row))
  finally:child.stdin.close();child.wait(timeout=3);os.close(fd) if fd is not None else None
 def test_only_exact_two_errno_classes_are_selected_gone(self):
  row=dict(pid=1,start='1',pgid=1)
  for error in (FileNotFoundError(errno.ENOENT,'actual'),ProcessLookupError(errno.ESRCH,'actual')):
   with patch.object(observer,'process',side_effect=error):self.assertFalse(observer.still_live(row))
 def test_unknown_errors_errnos_owner_and_malformed_data_propagate(self):
  row=dict(pid=1,start='1',pgid=1)
  failures=[PermissionError(errno.EPERM,'no'),OSError(errno.EIO,'io'),OSError(errno.EINVAL,'invalid'),ProcessLookupError(errno.EIO,'wrong subclass'),FileNotFoundError(errno.EACCES,'wrong subclass'),ProcessLookupError(),FileNotFoundError(),RuntimeError('Foreign helper process'),IndexError('malformed stat'),KeyError('missing identity')]
  for failure in failures:
   with self.subTest(failure=repr(failure)),patch.object(observer,'process',side_effect=failure),self.assertRaises(type(failure)):observer.still_live(row)
 def test_gone_cannot_supply_missing_duplicate_or_nonzero_terminal(self):
  identity=dict(pid=1,start='1',pgid=1);start=dict(event='started',operation='exact',wrapper=identity,delegate=identity);end=dict(start,event='terminal',exitCode=0)
  with patch.object(observer,'still_live',return_value=False):
   self.assertIsNone(observer.summarize([start],['exact']));self.assertIsNone(observer.summarize([start,end,end],['exact']))
   for code in (120,125,-15):
    with self.subTest(code=code),self.assertRaises(RuntimeError):observer.summarize([start,dict(end,exitCode=code)],['exact'])
   self.assertTrue(observer.summarize([start,end],['exact'])['allNormal'])
 def test_live_process_still_prevents_normal_completion(self):
  identity=dict(pid=1,start='1',pgid=1);start=dict(event='started',operation='exact',wrapper=identity,delegate=identity);end=dict(start,event='terminal',exitCode=0)
  with patch.object(observer,'still_live',return_value=True):self.assertIsNone(observer.summarize([start,end],['exact']))
 def test_entire_v11_module_reconstructed_and_registration_body_exact(self):
  source=(B/'helper_observer.py').read_bytes();old=(B.parent/'toolkit-held-matrix-v11/helper_observer.py').read_bytes();fresh=b'    except (FileNotFoundError, ProcessLookupError) as error:\n        if error.errno not in (errno.ENOENT, errno.ESRCH):raise\n        return False\n';before=b'    except FileNotFoundError:\n        return False\n'
  self.assertEqual(source.replace(b'import errno\n',b'',1).replace(fresh,before,1),old)
  def method(raw,name):return ast.get_source_segment(raw.decode(),next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name==name))
  self.assertEqual(method(source,'process'),method(old,'process'));self.assertEqual(method(source,'summarize'),method(old,'summarize'))
  for name in ('helper_setup.py','evaluation_setup.py','run_native.py','held_route.py','held_controller.py','observations.py','qs_lifecycle.py','delegate_diagnostics.py','scroll_route.py','frontend_route.py','input_control.py','private_shell.py','service_observer.py'):
   self.assertEqual(__import__('source_conservation').reconstructed_runner() if name=='run_native.py' else (B/name).read_bytes(),(B.parent/'toolkit-held-matrix-v11'/name).read_bytes(),name)
 def test_qs_cpu_fixture_only_adds_source_backed_literal_body_receipt(self):
  current=(B/'test_qs_lifecycle.py').read_text();old=(B.parent/'toolkit-held-matrix-v11/test_qs_lifecycle.py').read_text()
  marker='print("owned CPU fixture ready",flush=True)\\n'
  added="  # Test fixture body receipt only; actual QS lifecycle/deadlines are unchanged.\n  import select\n  ready,_,_=select.select([process.stdout],[],[],3)\n  if not ready or process.stdout.readline()!='owned CPU fixture ready\\n':\n   self.dispose(process);raise AssertionError('Actual nongraphical fixture ready receipt missing')\n"
  self.assertEqual(current.replace(marker,'',1).replace(added,'',1),old)
  self.assertEqual((B/'qs_lifecycle.py').read_bytes(),(B.parent/'toolkit-held-matrix-v11/qs_lifecycle.py').read_bytes())
if __name__=='__main__':unittest.main(verbosity=2)
