"""Guard every actual owned input write, preserve transitions and normal EOF."""
import hashlib
import math
import os
from pathlib import Path
import select
import time
import helper_observer as process_api

class PinnedInput:
    def __init__(self,process,command,environment,session_guard,kind):
        self.process=process;self.command=list(map(str,command));self.environment=environment;self.session_guard=session_guard;self.kind=kind
        self.identity=process_api.process(process.pid);self.executable=Path(command[0]).resolve();self.sha256=process_api.digest(self.executable);self.down=set();self.trace=[];self.closed=False
        self.sync()
    def guard(self):
        self.session_guard()
        if self.closed or self.process.poll() is not None or not process_api.still_live(self.identity):raise RuntimeError('Exact owned input producer lifetime gone')
        proc=Path('/proc')/str(self.identity['pid'])
        if (proc/'exe').resolve()!=self.executable or process_api.digest(self.executable)!=self.sha256 or process_api.cmdline(self.identity['pid'])!=self.command:raise RuntimeError('Exact input producer executable/argv/source changed')
        values=dict(part.split(b'=',1) for part in (proc/'environ').read_bytes().split(b'\0') if b'=' in part)
        for name in ('HOME','XDG_RUNTIME_DIR','WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','POINTER_QA_COMPOSITOR_PID','POINTER_QA_COMPOSITOR_START','HYPR_A11Y_BRIDGE_PRIVATE'):
            if values.get(name.encode())!=self.environment[name].encode():raise RuntimeError('Actual input producer private environment changed')
        if (proc/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise RuntimeError('Actual input producer QA scope changed')
    def send(self,command):
        self.guard();self.process.stdin.write(command+'\n');self.process.stdin.flush();self.trace.append(dict(command=command,pid=self.identity['pid'],start=self.identity['start'],sentNs=time.monotonic_ns(),nativeOutcomeNotInferred=True))
    def sync(self):
        self.send('sync');ready,_,_=select.select([self.process.stdout],[],[],6)
        if not ready or self.process.stdout.readline()!='ready\n':raise RuntimeError('Actual producer Wayland roundtrip failed')
    def button(self,code,pressed):
        if self.kind!='pointer' or code not in (272,273) or type(pressed) is not bool or (code in self.down)==pressed:raise ValueError('Exact genuine pointer transition required')
        self.send('button '+str(code)+' '+str(int(pressed)))
        if pressed:self.down.add(code)
        else:self.down.remove(code)
        self.sync()
    def key(self,code,pressed):
        if self.kind!='keyboard' or type(code) is not int or not 0<=code<256 or type(pressed) is not bool or (code in self.down)==pressed:raise ValueError('Exact genuine key transition required')
        self.send('key '+str(code)+' '+str(int(pressed)))
        if pressed:self.down.add(code)
        else:self.down.remove(code)
        self.sync()
    def absolute(self,point,extents):
        if self.kind!='pointer' or len(point)!=2 or len(extents)!=2 or not all(type(v) in (int,float) and math.isfinite(v) for v in [*point,*extents]) or any(not 0<=p<bound<=400000 for p,bound in zip(point,extents)):raise ValueError('Exact bounded private logical point required')
        self.send('absolute '+' '.join(format(v,'.12g') for v in [*point,*extents]));self.sync()
    def wheel(self,direction):
        if self.kind!='pointer' or type(direction) is not int or direction not in (-1,1) or self.down:raise ValueError('One typed genuine released wheel detent required')
        self.send('wheel '+str(direction));self.sync()
    def close(self):
        for code in sorted(self.down):
            if self.kind=='pointer':self.button(code,False)
            else:self.key(code,False)
        self.guard();self.process.stdin.close();self.process.wait(timeout=8);self.closed=True
        if self.process.returncode!=0 or process_api.still_live(self.identity):raise RuntimeError('Actual owned producer normal EOF/exit failed')
        return dict(identity=self.identity,exitCode=0,normalEOF=True,knownDownTransitionsReleased=True,trace=self.trace)
