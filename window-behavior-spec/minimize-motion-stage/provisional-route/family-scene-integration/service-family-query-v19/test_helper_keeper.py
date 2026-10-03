import array
import json
import os
from pathlib import Path
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
from helper_keeper import send,receive,private_terminal

ROOT=Path(__file__).parent

class KeeperTests(unittest.TestCase):
    def sockets(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);b.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.addCleanup(a.close);self.addCleanup(b.close);return a,b
    def test_actual_sender_credentials_and_descriptor(self):
        a,b=self.sockets();fd=os.open('/dev/null',os.O_RDONLY)
        try:send(a,{'command':'test'},fd)
        finally:os.close(fd)
        packet,owned=receive(b,os.getpid(),os.getuid())
        try:self.assertEqual(packet,{'command':'test'});self.assertFalse(os.get_inheritable(owned));self.assertTrue(os.path.samefile('/dev/null',f'/proc/self/fd/{owned}'))
        finally:os.close(owned)
    def test_wrong_exact_peer_refused(self):
        a,b=self.sockets();send(a,{'ok':True})
        with self.assertRaisesRegex(ValueError,'exact kernel peer'):receive(b,os.getpid()+1,os.getuid())
    def test_forked_inherited_socket_cannot_claim_parent_credentials(self):
        a,b=self.sockets();pid=os.fork()
        if pid==0:
            send(a,{'ok':True});os._exit(0)
        try:
            with self.assertRaisesRegex(ValueError,'exact kernel peer'):receive(b,os.getpid(),os.getuid())
        finally:os.waitpid(pid,0)
    def test_truncated_extra_descriptors_refused_without_leak(self):
        a,b=self.sockets();fd=os.open('/dev/null',os.O_RDONLY)
        before=set(os.listdir('/proc/self/fd'))
        try:a.sendmsg([b'{}'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]*8))])
        finally:os.close(fd)
        with self.assertRaisesRegex(ValueError,'truncated'):receive(b,os.getpid(),os.getuid())
        self.assertLessEqual(len(os.listdir('/proc/self/fd')),len(before))
    def test_terminal_requires_exact_private_directory(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);info=root.stat();identity=[info.st_dev,info.st_ino]
            private_terminal(root,identity,'proof.json',{'allGroupsEmpty':True})
            self.assertEqual(json.loads((root/'proof.json').read_text()),{'allGroupsEmpty':True})
            with self.assertRaises(ValueError):private_terminal(root,[identity[0],identity[1]+1],'bad.json',{})
            root.chmod(0o755)
            with self.assertRaises(ValueError):private_terminal(root,identity,'bad.json',{})
    def test_group_descriptor_still_addresses_children_after_leader_reaped(self):
        # Isolated CPU-only subreaper owns and reaps both test lifetimes.
        script='''
import ctypes,json,os,signal,time
from helper_keeper import group_empty
libc=ctypes.CDLL(None,use_errno=True)
assert libc.prctl(36,1,0,0,0)==0
r,w=os.pipe();release_r,release_w=os.pipe()
pid=os.fork()
if pid==0:
 os.close(r);os.close(release_w);os.setsid()
 child=os.fork()
 if child==0:
  os.close(w);os.close(release_r)
  while True:signal.pause()
 os.write(w,str(child).encode());os.close(w)
 os.read(release_r,1);os._exit(0)
os.close(w);os.close(release_r);child=int(os.read(r,100));os.close(r)
fd=os.pidfd_open(pid,0);os.write(release_w,b'G');os.close(release_w);os.waitpid(pid,0)
assert not group_empty(fd)
signal.pidfd_send_signal(fd,signal.SIGKILL,None,4)
assert os.waitpid(child,0)[1]==signal.SIGKILL
assert group_empty(fd)
os.close(fd);print(json.dumps({'leaderReaped':True,'childKilled':True,'exactGroupEmpty':True}))
'''
        result=subprocess.run([sys.executable,'-c',script],cwd=ROOT,text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(result.stdout)['exactGroupEmpty'])

if __name__=='__main__':unittest.main()
