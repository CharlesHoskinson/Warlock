"""Gate an isolated, confined helper after durable keeper registration."""
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import select
import subprocess
import sys
from recovery_resources import SEALS,material_fd,material_path,process_start
from helper_policy import POLICY


def handoff_source():
    policy=Path(__file__).with_name('helper_policy.py').read_bytes()
    return policy+b'''\nimport json,sys\ngate=int(sys.argv[1]);ready=int(sys.argv[2]);target=int(sys.argv[3]);argv=json.loads(sys.argv[4]);mode=sys.argv[5];interpreter=int(sys.argv[6])\ninstall()\nos.write(ready,b"R");os.close(ready)\npermit=os.read(gate,1);os.close(gate)\nif permit!=b"G":sys.exit(125)\nif mode=='python':
 code=os.pread(target,128*1024*1024,0);sys.argv=argv;sys.path[0]=os.path.dirname(os.path.abspath(argv[0]));os.close(target)
 scope={'__name__':'__main__','__file__':argv[0],'__package__':None,'__cached__':None,'__builtins__':__builtins__}
 exec(compile(code,argv[0],'exec'),scope,scope)
elif mode=='bash':
 code=os.pread(target,128*1024*1024,0).decode();os.close(target)
 os.execve('/proc/self/fd/'+str(interpreter),['bash','-c',code,argv[0],*argv[1:]],dict(os.environ))
else:os.execve('/proc/self/fd/'+str(target),argv,dict(os.environ))\n'''

class OwnedLaunch:
    def __init__(self,argv,*,env,keeper,kind,actor=None,executable_fd=None,record=None,timeout_adapter=None,**options):
        if not isinstance(argv,list) or not argv or any(type(v) is not str for v in argv):raise ValueError('exact argument vector required')
        self.keeper=keeper;self.job=None;self.process=None;self.closed=False
        if executable_fd is None:raise ValueError('owned launch requires selected sealed executable descriptor')
        target=executable_fd;producer=material_fd(target,sealed=True)
        first=os.pread(target,256,0);mode='elf';interpreter=None
        if first.startswith(b'#!'):
            shebang=first.split(b'\n',1)[0].decode('utf-8')
            if shebang in ('#!/usr/bin/env python3','#!/usr/bin/python3','#!/usr/bin/python','#!/usr/bin/env python'):mode='python'
            elif shebang in ('#!/usr/bin/env bash','#!/bin/bash','#!/usr/bin/bash'):
                mode='bash'
                if b'BASH_SOURCE' in os.pread(target,producer['size'],0):raise ValueError('bash source-path introspection requires explicit adapter')
                from owned_commands import SealedFile
                interpreter=SealedFile('/usr/bin/bash')
            else:raise ValueError('unsupported owned helper interpreter')
        elif not first.startswith(b'\x7fELF'):raise ValueError('selected helper must be supported ELF or script')
        script=os.memfd_create('motion-confined-launch',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
        read_gate,write_gate=os.pipe2(os.O_CLOEXEC);read_ready,write_ready=os.pipe2(os.O_CLOEXEC)
        try:
            policy=Path(__file__).with_name('helper_policy.py').read_bytes()
            code=handoff_source()
            os.write(script,code);os.fchmod(script,0o400);fcntl.fcntl(script,fcntl.F_ADD_SEALS,SEALS)
            launcher=str(Path(sys.executable).resolve())
            handoff=[launcher,f'/proc/self/fd/{script}',str(read_gate),str(write_ready),str(target),json.dumps(argv,separators=(',',':')),mode,str(interpreter.fd if interpreter else -1)]
            if options.get('start_new_session') is False:raise ValueError('owned launch requires private session')
            inherited=options.pop('pass_fds',())
            if any(type(v) is not int or v<0 for v in inherited):raise ValueError('typed inherited descriptor required')
            options['start_new_session']=True
            self.process=subprocess.Popen(handoff,env=env,pass_fds=tuple(set((*inherited,target,script,read_gate,write_ready,*((interpreter.fd,) if interpreter else ())))),**options)
            os.close(write_ready);write_ready=None
            poll=select.poll();poll.register(read_ready,select.POLLIN|select.POLLHUP)
            if not poll.poll(5000) or os.read(read_ready,1)!=b'R':raise RuntimeError('confined helper failed gate readiness')
            start=process_start(self.process.pid)
            self.ownership={'pid':self.process.pid,'start':start,'uid':os.getuid(),'producer':producer,'launcher':material_path(launcher),
                'script':material_fd(script,sealed=True),'argv':handoff,'scriptFD':script,'producerFD':target,'targetArgv':argv,
                'mode':mode,'interpreter':material_fd(interpreter.fd,sealed=True) if interpreter else None,'policy':POLICY,'policySHA256':__import__('hashlib').sha256(policy).hexdigest(),
                'environment':{k:env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}}
            if timeout_adapter is not None:self.ownership['timeoutAdapter']=timeout_adapter
            if process_start(self.process.pid)!=start:raise ValueError('confined helper lifetime changed')
            if material_path(f'/proc/{self.process.pid}/exe')!=self.ownership['launcher']:raise ValueError('confined launcher material differs')
            if material_path(f'/proc/{self.process.pid}/fd/{script}',sealed=True)!=self.ownership['script']:raise ValueError('confined handoff material differs')
            self.job=keeper.register(self.ownership,kind=kind,actor=actor,process=self.process)
            if record:record(deepcopy(self.ownership))
            # The durable phase covers release uncertainty. A crash after this
            # fsync, before G, still has the exact registered group to close.
            keeper.released(self.job)
            if os.write(write_gate,b'G')!=1:raise BrokenPipeError('owned execution gate failed')
        except BaseException:
            os.close(write_gate);write_gate=None
            if self.process is not None:
                try:self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=2)
                for stream in (self.process.stdin,self.process.stdout,self.process.stderr):
                    if stream:stream.close()
                if self.job is not None:
                    try:keeper.complete(self.job)
                    except Exception:pass # Registered uncertain job remains durable.
            raise
        finally:
            for fd in (script,read_gate,write_gate,read_ready,write_ready):
                if fd is not None:os.close(fd)
            if interpreter:interpreter.close()
    def complete(self):
        if self.closed:return
        if self.process.poll() is None:raise ValueError('direct helper has not exited')
        self.process.wait();self.keeper.complete(self.job);self.closed=True

def checked_owned(row,*,environment):
    import hashlib
    from recovery_resources import checked_material
    from recovery_intent import positive
    expected={'pid','start','uid','producer','launcher','script','argv','scriptFD','producerFD','targetArgv','mode','interpreter','policy','policySHA256','environment'}
    if isinstance(row,dict) and 'timeoutAdapter' in row:
        from timeout_adapter import check
        check(row['timeoutAdapter']);expected.add('timeoutAdapter')
    if not isinstance(row,dict) or set(row)!=expected:raise ValueError('complete typed owned helper source/lifetime required')
    positive(row['pid']);positive(row['start'])
    if type(row['uid']) is not int or row['uid']!=os.getuid():raise ValueError('exact helper UID required')
    if row['environment']!=environment or row['policy']!=POLICY or row['policySHA256']!=hashlib.sha256(Path(__file__).with_name('helper_policy.py').read_bytes()).hexdigest():raise ValueError('helper environment or reviewed policy differs')
    checked_material(row['producer'],sealed=True);checked_material(row['launcher'],sealed=False);checked_material(row['script'],sealed=True)
    if row['script']['sha256']!=hashlib.sha256(handoff_source()).hexdigest():raise ValueError('owned helper handoff is not reviewed source')
    if row['mode'] not in ('elf','python','bash') or any(type(row[field]) is not int or row[field]<0 for field in ('scriptFD','producerFD')):raise ValueError('typed helper execution mode/descriptors required')
    if row['mode']=='bash':checked_material(row['interpreter'],sealed=True)
    elif row['interpreter'] is not None:raise ValueError('unexpected helper interpreter')
    argv=row['argv'];target=row['targetArgv']
    if not isinstance(target,list) or not target or any(type(v) is not str for v in target) or not isinstance(argv,list) or len(argv)!=8 or any(type(v) is not str for v in argv):raise ValueError('exact helper argument vectors required')
    if argv[1]!=f"/proc/self/fd/{row['scriptFD']}" or not argv[2].isdigit() or not argv[3].isdigit() or argv[4]!=str(row['producerFD']) or json.loads(argv[5])!=target or argv[6]!=row['mode'] or row['mode']!='bash' and argv[7]!='-1' or row['mode']=='bash' and not argv[7].isdigit():raise ValueError('helper handoff descriptor/argv binding differs')
    return row
