"""Per-adapter subprocess facade with sealed helper source and durable jobs."""
import fcntl
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
from recovery_resources import SEALS,material_fd

class SealedFile:
    def __init__(self,path):
        self.original=str(Path(path).absolute());self.fd=None
        source=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
        try:
            before=os.fstat(source)
            if not stat.S_ISREG(before.st_mode) or before.st_uid not in (0,os.getuid()) or before.st_mode&0o022 or not before.st_mode&0o111 or before.st_size>128*1024*1024:raise ValueError('selected helper executable material unsafe')
            self.fd=os.memfd_create('motion-selected-helper',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING|getattr(os,'MFD_EXEC',0))
            offset=0
            while data:=os.pread(source,1048576,offset):
                offset+=len(data);written=0
                while written<len(data):written+=os.write(self.fd,data[written:])
            after=os.fstat(source)
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) or offset!=before.st_size:raise ValueError('helper source changed while sealing')
            os.fchmod(self.fd,0o500);fcntl.fcntl(self.fd,fcntl.F_ADD_SEALS,SEALS);self.material=material_fd(self.fd,sealed=True)
        except BaseException:self.close();raise
        finally:os.close(source)
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class OwnedCommands:
    PIPE=subprocess.PIPE;DEVNULL=subprocess.DEVNULL;STDOUT=subprocess.STDOUT
    SubprocessError=subprocess.SubprocessError;CalledProcessError=subprocess.CalledProcessError;TimeoutExpired=subprocess.TimeoutExpired
    def __init__(self,keeper,env,actor=None):self.keeper=keeper;self.env=dict(env);self.actor=actor
    def classify(self,argv):
        # IPC effects/exports require the service's durable returned completion;
        # group closure alone cannot authorize replay of an unfinished native call.
        if len(argv)>2 and argv[1]=='repl' and any(value in argv[2] for value in ('window_atlas(', 'window_snapshot(')):return 'native-export'
        if len(argv)>1 and (argv[1] in ('minimize','restore','dispatch') or argv[1]=='repl' and 'retire_gesture_current' in argv[2]):return 'native-effect'
        return 'helper'
    def run(self,args,*,input=None,capture_output=False,timeout=None,check=False,**options):
        from owned_launch import OwnedLaunch
        if not isinstance(args,(list,tuple)) or not args or any(type(v) is not str for v in args):raise ValueError('exact helper argv required')
        argv=list(args);env=options.pop('env',self.env)
        if any(env.get(k)!=self.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')):raise ValueError('helper selected session environment differs')
        selected=shutil.which(argv[0],path=env.get('PATH')) if '/' not in argv[0] else argv[0]
        if selected is None:raise FileNotFoundError(argv[0])
        # Python/Bash adaptation retains the original full source path as argv0.
        argv[0]=str(Path(selected).absolute())
        if input is not None:
            if 'stdin' in options:raise ValueError('input and stdin conflict')
            options['stdin']=subprocess.PIPE
        if capture_output:
            if 'stdout' in options or 'stderr' in options:raise ValueError('capture output conflicts')
            options.update(stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        from timeout_adapter import prepare
        env,adapter=prepare(env)
        with SealedFile(selected) as executable:
            launch=OwnedLaunch(argv,env=env,keeper=self.keeper,kind=self.classify(argv),actor=self.actor,executable_fd=executable.fd,timeout_adapter=adapter,**options)
        try:
            stdout,stderr=launch.process.communicate(input,timeout=timeout)
        except BaseException:
            # A timed-out native call has no completion proof and stays in the
            # durable job registry even after its direct leader is reaped.
            launch.process.kill();launch.process.communicate();raise
        finally:
            if launch.process.poll() is not None:
                for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):
                    if stream:stream.close()
        if launch.process.returncode!=0 and self.classify(argv) in ('native-export','native-effect'):
            # Returned failure can follow partial native work. Keep uncertain
            # callback provenance so restart cannot waive that boundary.
            result=subprocess.CompletedProcess(args,launch.process.returncode,stdout,stderr)
            if check:result.check_returncode()
            return result
        launch.complete()
        result=subprocess.CompletedProcess(args,launch.process.returncode,stdout,stderr)
        if check:result.check_returncode()
        return result
    def check_output(self,args,**options):
        if 'stdout' in options:raise ValueError('check_output controls stdout')
        return self.run(args,stdout=subprocess.PIPE,check=True,**options).stdout
