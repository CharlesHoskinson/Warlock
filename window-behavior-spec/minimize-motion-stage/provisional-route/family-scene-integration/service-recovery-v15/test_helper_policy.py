import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).parent

class PolicyTests(unittest.TestCase):
    def test_actual_inherited_policy_denies_escape_but_permits_threads_and_exec(self):
        script='''
import ctypes,errno,json,os,sys,threading
from helper_policy import install
install()
libc=ctypes.CDLL(None,use_errno=True)
results={}
for name,number,args in [('setsid',112,()),('setpgid',109,(0,0)),('unshare',272,(0,)),('setns',308,(-1,0)),('cloneNamespace',56,(0x10000000|17,0,0,0,0)),('clone3',435,(0,0))]:
    libc.syscall.restype=ctypes.c_long
    rc=libc.syscall(number,*args);results[name]=[rc,ctypes.get_errno()]
thread=threading.Thread(target=lambda:results.update(thread=True));thread.start();thread.join()
pid=os.fork()
if pid==0:
    try:os.setpgid(0,0)
    except OSError as e:os._exit(0 if e.errno==errno.EPERM else 2)
    os._exit(3)
results['forkChildInherited']=os.waitpid(pid,0)[1]==0
print(json.dumps(results),flush=True)
os.execve('/usr/bin/true',['true'],dict(os.environ))
'''
        result=subprocess.run([sys.executable,'-c',script],cwd=ROOT,start_new_session=True,text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        evidence=json.loads(result.stdout)
        for name in ('setsid','setpgid','unshare','setns','cloneNamespace'):self.assertEqual(evidence[name],[-1,1],name)
        self.assertEqual(evidence['clone3'],[-1,38])
        self.assertTrue(evidence['thread']);self.assertTrue(evidence['forkChildInherited'])

    def test_unisolated_policy_refuses(self):
        result=subprocess.run([sys.executable,'-c','from helper_policy import install; install()'],cwd=ROOT,capture_output=True,text=True,timeout=5)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('private helper session',result.stderr)

if __name__=='__main__':unittest.main()
