"""Inherited Linux x86_64 process-group confinement for owned CPU helper jobs.

Install after creating the private session, before acknowledging the launch gate.
Unsupported architectures or kernel errors refuse execution.
"""
import ctypes
import errno
import os
import platform

class Filter(ctypes.Structure):
    _fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint)]
class Program(ctypes.Structure):
    _fields_=[('length',ctypes.c_ushort),('filters',ctypes.POINTER(Filter))]

POLICY='linux-x86_64-group-confinement-v1'
DENIED=(109,112,272,308,101,311) # setpgid, setsid, unshare, setns, ptrace, process_vm_writev
NAMESPACE_FLAGS=0x7e020080

def install():
    if platform.machine()!='x86_64' or ctypes.sizeof(ctypes.c_void_p)!=8:raise RuntimeError('unsupported helper confinement ABI')
    rows=[(0x20,0,0,4),(0x15,1,0,0xc000003e),(0x06,0,0,0x80000000),(0x20,0,0,0)]
    # Reject alternate x32 syscall ABI; its numbering cannot bypass this filter.
    rows.extend([(0x45,0,1,0x40000000),(0x06,0,0,0x80000000)])
    for number in DENIED:rows.extend([(0x15,0,1,number),(0x06,0,0,0x00050000|errno.EPERM)])
    rows.extend([(0x15,0,1,435),(0x06,0,0,0x00050000|errno.ENOSYS)])
    # clone is allowed for threads/fork, with every namespace flag refused.
    rows.extend([(0x15,0,3,56),(0x20,0,0,16),(0x45,0,1,NAMESPACE_FLAGS),(0x06,0,0,0x00050000|errno.EPERM),(0x06,0,0,0x7fff0000)])
    filters=(Filter*len(rows))(*(Filter(*row) for row in rows));program=Program(len(rows),filters)
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(38,1,0,0,0)!=0:raise OSError(ctypes.get_errno(),'PR_SET_NO_NEW_PRIVS')
    if libc.prctl(22,2,ctypes.byref(program),0,0)!=0:raise OSError(ctypes.get_errno(),'PR_SET_SECCOMP')
    if os.getsid(0)!=os.getpid() or os.getpgrp()!=os.getpid():raise RuntimeError('private helper session/group required before confinement')
