"""Actual owned CPU/kernel tracer proof. No compositor, Wayland or native input."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import select
import sys
import tempfile
import unittest
from unittest.mock import patch
import delegate_diagnostics as diagnostic
import helper_observer
B=Path(__file__).resolve().parent
WRAPPER=r'''
import sys,os,json,hashlib
from pathlib import Path
sys.path.insert(0,sys.argv[1]);import delegate_diagnostics as d
path=Path(sys.argv[2]);script=sys.argv[3];shebang=len(sys.argv)>4
entry=path/'actual-backend'
if shebang:entry.write_text('#!/usr/bin/env python3\n'+script);entry.chmod(0o700)
gate,release=os.pipe()
child=os.fork()
if child==0:
 os.close(release)
 if os.read(gate,1)!=b'G':os._exit(125)
 os.close(gate);d.child_bootstrap()
 if shebang:os.execv(str(entry),[str(entry),'list','--json'])
 os.execve('/usr/bin/python3',['/usr/bin/python3','-IS','-c',script],dict(os.environ))
os.close(gate)
def identity(pid):
 fields=Path('/proc',str(pid),'stat').read_text().rsplit(') ',1)[1].split();return dict(pid=pid,start=fields[19])
parent=identity(os.getppid());delegate=identity(child);journal=d.Journal(path/'trace.jsonl')
chain=[dict(executable=str(Path('/usr/bin/python3').resolve()),executableSHA256=hashlib.sha256(Path('/usr/bin/python3').read_bytes()).hexdigest(),argv=['/usr/bin/python3','-IS','-c',script])]
if shebang:chain=[dict(executable=str(Path('/usr/bin/env').resolve()),executableSHA256=hashlib.sha256(Path('/usr/bin/env').read_bytes()).hexdigest(),argv=['/usr/bin/env','python3',str(entry),'list','--json']),dict(executable=str(Path('/usr/bin/python3').resolve()),executableSHA256=hashlib.sha256(Path('/usr/bin/python3').read_bytes()).hexdigest(),argv=['python3',str(entry),'list','--json'])]
try:
 observer=d.Observer(journal,delegate,parent,parent,chain,dict(cpuFixture=True,environmentSHA256=hashlib.sha256(Path('/proc/self/environ').read_bytes()).hexdigest()))
 os.write(release,b'G');os.close(release);status,summary=observer.run()
 with (path/'summary.json').open('x') as f:json.dump(dict(status=status,summary=summary,delegate=delegate,parent=parent,originalEnvironmentSHA256=hashlib.sha256(Path('/proc/self/environ').read_bytes()).hexdigest()),f)
finally:journal.close()
'''
class DiagnosticKernelTests(unittest.TestCase):
 def fixture(self,script,closed=False,shebang=False):
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup);path=Path(folder.name);path.chmod(0o700)
  process=subprocess.Popen(['/usr/bin/python3','-IS','-c',WRAPPER,str(B),str(path),script]+(['shebang'] if shebang else []),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if closed:process.stdout.close();stdout=None;stderr=process.stderr.read();process.wait(timeout=10);process.stderr.close()
  else:stdout,stderr=process.communicate(timeout=10)
  self.assertEqual(process.returncode,0,stderr.decode(errors='replace'));rows=[json.loads(x) for x in (path/'trace.jsonl').read_text().splitlines()];summary=json.loads((path/'summary.json').read_text())
  return stdout,stderr,rows,summary
 def test_exact_stdout_stderr_bytes_syscall_return_argv_env_and_fd_routing(self):
  script="import os;os.write(1,b'actual stdout\\x00bytes');os.write(2,b'actual stderr\\n')"
  stdout,stderr,rows,summary=self.fixture(script);self.assertEqual(stdout,b'actual stdout\x00bytes');self.assertEqual(stderr,b'actual stderr\n');self.assertTrue(summary['summary']['complete']);self.assertEqual(summary['summary']['exitCode'],0)
  entries=[r for r in rows if r['event']=='stdio-write-entry'];returns=[r for r in rows if r['event']=='stdio-write-return'];self.assertEqual([bytes.fromhex(r['offeredBytesHex']) for r in entries],[stdout,stderr]);self.assertEqual([r['kernelReturn'] for r in returns],[len(stdout),len(stderr)]);self.assertTrue(all(not r['kernelIsError'] for r in returns));self.assertTrue(all(r['parentObservation']['kind']=='exact' for r in entries));self.assertTrue(all(r['stdio']==rows[0]['stdio'] for r in rows if r['event']=='backend-exec'))
 def test_actual_env_shebang_exec_chain_argv_and_stdio(self):
  stdout,stderr,rows,summary=self.fixture("import os,sys;assert sys.argv[1:]==['list','--json'];os.write(1,b'actual query\\n')",shebang=True)
  self.assertEqual(stdout,b'actual query\n');self.assertEqual(stderr,b'');self.assertTrue(summary['summary']['complete']);self.assertEqual(summary['summary']['exitCode'],0);self.assertEqual([r['execOrdinal'] for r in rows if r['event']=='backend-exec'],[0,1])
 def test_actual_writev_complete_vectors_preserved(self):
  stdout,stderr,rows,summary=self.fixture("import os;os.writev(1,[b'alpha',b'\\x00beta',b'gamma'])")
  self.assertEqual(stdout,b'alpha\x00betagamma');self.assertEqual(stderr,b'');entry=next(r for r in rows if r['event']=='stdio-write-entry');self.assertEqual(entry['nr'],20);self.assertEqual(entry['vectorLengths'],[5,5,5]);self.assertEqual(bytes.fromhex(entry['offeredBytesHex']),stdout);self.assertTrue(summary['summary']['complete'])
 def test_closed_consumer_actual_epipe_and_stderr_remain_unchanged(self):
  script="import os;\ntry:os.write(1,b'actual offered JSON\\n')\nexcept OSError as e:os.write(2,('actual errno='+str(e.errno)+'\\n').encode());os._exit(120)"
  stdout,stderr,rows,summary=self.fixture(script,closed=True);self.assertEqual(stderr,b'actual errno=32\n');self.assertTrue(summary['summary']['complete']);self.assertEqual(summary['summary']['exitCode'],120);result=next(r for r in rows if r['event']=='stdio-write-return' and r['fd']==1);self.assertEqual((result['kernelReturn'],result['errno'],result['deliveredCount']),(-32,32,0));self.assertEqual(bytes.fromhex(next(r for r in rows if r['event']=='stdio-write-entry')['offeredBytesHex']),b'actual offered JSON\n')
 def test_genuine_sigterm_forward_and_actual_signal_wait_preserved(self):
  stdout,stderr,rows,summary=self.fixture("import os,signal;os.kill(os.getpid(),signal.SIGTERM)")
  self.assertEqual(summary['summary']['exitCode'],-15);self.assertTrue(summary['summary']['complete']);self.assertEqual([r['signal'] for r in rows if r['event']=='genuine-signal-forward'],[15])
 def test_genuine_handled_signal_is_forwarded_once(self):
  stdout,stderr,rows,summary=self.fixture("import os,signal;signal.signal(signal.SIGUSR1,lambda *a:os.write(1,b'handled once\\n'));os.kill(os.getpid(),signal.SIGUSR1)")
  self.assertEqual(stdout,b'handled once\n');self.assertTrue(summary['summary']['complete']);self.assertEqual([r['signal'] for r in rows if r['event']=='genuine-signal-forward'],[10])
 def test_unknown_trap_refuses_but_preserves_genuine_handler_and_wait(self):
  stdout,stderr,rows,summary=self.fixture("import os,signal;signal.signal(signal.SIGTRAP,lambda *a:os.write(1,b'original trap handler\\n'));os.kill(os.getpid(),signal.SIGTRAP)")
  self.assertEqual(stdout,b'original trap handler\n');self.assertEqual(summary['summary']['exitCode'],0);self.assertFalse(summary['summary']['complete']);self.assertTrue(any(r['event']=='observer-error' for r in rows))
 def test_only_own_exact_child_can_be_observed(self):
  with tempfile.TemporaryDirectory() as raw:
   p=Path(raw);p.chmod(0o700);j=diagnostic.Journal(p/'x.jsonl')
   try:
    identity=helper_observer.process(os.getpid())
    with self.assertRaisesRegex(RuntimeError,'Only own exact'):diagnostic.Observer(j,identity,identity,identity,[],{})
   finally:j.close()
 def test_actual_parent_pidfd_exit_and_raw_z_wait_status_are_observed(self):
  child=subprocess.Popen(['/usr/bin/python3','-IS','-c',"import os;os.read(0,1);os._exit(23)"],stdin=subprocess.PIPE)
  identity=helper_observer.process(child.pid);fd=os.pidfd_open(child.pid)
  try:
   observer=diagnostic.Observer.__new__(diagnostic.Observer);observer.parent=identity;observer.parent_fd=fd
   self.assertFalse(observer.parent_state()['pidfdExitObserved']);child.stdin.write(b'G');child.stdin.flush()
   p=select.poll();p.register(fd,select.POLLIN);self.assertTrue(p.poll(2000));actual=observer.parent_state()
   self.assertTrue(actual['pidfdExitObserved']);self.assertEqual(actual['state'],'Z');self.assertTrue(actual['exitCodeKnown']);self.assertEqual(actual['kernelWaitStatus'],23*256)
  finally:child.stdin.close();child.wait(timeout=3);os.close(fd)
 def test_partial_memory_and_oversized_write_refuse_without_routing_change(self):
  observer=diagnostic.Observer.__new__(diagnostic.Observer);observer.delegate=dict(pid=os.getpid());observer.c=diagnostic.libc()
  with self.assertRaises(RuntimeError):observer.memory(1,16)
  with self.assertRaises(RuntimeError):observer.memory(1,diagnostic.MAX_WRITE+1)
 def test_unsafe_log_symlink_nonfinite_and_record_bounds_refuse(self):
  with tempfile.TemporaryDirectory() as raw:
   p=Path(raw);p.chmod(0o700);(p/'x').symlink_to(p/'real')
   with self.assertRaises(FileExistsError):diagnostic.Journal(p/'x')
   j=diagnostic.Journal(p/'y')
   try:
    with self.assertRaises(ValueError):j.emit('invalid',dict(value=float('nan')))
    with patch.object(diagnostic,'MAX_RECORDS',0),self.assertRaises(RuntimeError):j.emit('invalid',{})
   finally:j.close()
if __name__=='__main__':unittest.main(verbosity=2)
