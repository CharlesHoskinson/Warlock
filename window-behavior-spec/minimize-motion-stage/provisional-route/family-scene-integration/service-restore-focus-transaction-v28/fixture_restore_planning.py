"""Real owned helper/readonly kernel boundaries; no native GUI or PNG claim."""
from copy import deepcopy
import json
import os
from pathlib import Path
import threading
import time

from helper_supervisor import Keeper
from native_desktop import NativeDesktop
from owned_commands import OwnedCommands
from scene_controller import SceneController
from test_readonly_ipc import ReadonlyKernelTests
from test_scene_controller import Desktop, Transport


class CpuDesktop(NativeDesktop):
    # Explicit legacy CPU route retains six real jobs and three refreshes.
    apply_destinations=None
    refresh_destinations=None
    retire_gestures=None
    finish_capture_previews=None
    family_evidence=None
    def plan_destination(self,window):
        # Exact inherited planner executes. These barriers only prescribe CPU
        # completion order; no result/material/query assertion is substituted.
        result=super().plan_destination(window)
        if self.owner.ordered:
            index=next(i for i,w in enumerate(self.fixture.windows) if w['address']==window['address'])
            if index<2:
                if not self.owner.order_permits[index].wait(2):raise TimeoutError('CPU planner order permit')
            self.owner.completed.append(index)
            if index: self.owner.order_permits[index-1].set()
        return result
    def family(self,window,windows,single=False):
        return self.production.native_family_plan(window,windows,self.fixture.native)
    def reduced(self):return False
    def capture_source(self,window,token,index):return self.fixture.capture_source(window,token,index)
    def release_sources(self,sources):self.fixture.release_sources(sources)
    def commit(self,operation,window,preview=True):self.fixture.commit(operation,window,preview)


class KernelFixture:
    def __init__(self):
        self.ipc=ReadonlyKernelTests();self.ipc.setUp()
        self.registry=[];self.requests=[];self.completed=[]
        self.order_permits=[threading.Event(),threading.Event()]
        self.ordered=False;self.gate=None;self.native_gate=None
        self.first_three=threading.Event();self.monitor_started=0
        self.active_monitors=0;self.max_monitors=0
        self.monitor_lock=threading.Lock();self.monitor_delay=0
        self.dispatch_delay=0;self.dispatch_error=False;self.malformed=False
        self.current=True;self.errors=[]
        self.fixture=Desktop()
        for w in self.fixture.windows:w['workspace']['name']='special:win-minimized'
        for w in self.fixture.native:w['workspace']['name']='special:win-minimized'
        self.original_env={k:os.environ.get(k) for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','HOME')}
        home=self.ipc.runtime/'home';home.mkdir(mode=0o700)
        self.env=dict(self.ipc.env,HOME=str(home));os.environ.update({k:self.env[k] for k in self.original_env})
        controls=self.ipc.runtime/'hypr-windowctl';controls.mkdir(mode=0o700);self.controls=controls
        for w in self.fixture.windows:self.install_state(w)
        self.monitors=[{'id':0,'name':'CPU-1','focused':True,'x':0,'y':0,'width':1600,'height':1000,'scale':1}]
        self.ipc.handler=self.handle
        bins=home/'bin';bins.mkdir(mode=0o700)
        shell=bins/'omarchy-shell'
        shell.write_text('#!/usr/bin/python3\nimport os,socket\ns=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)\ns.connect(os.environ["XDG_RUNTIME_DIR"]+"/hypr/"+os.environ["HYPRLAND_INSTANCE_SIGNATURE"]+"/.socket.sock")\ns.sendall(b"CPU_REFRESH")\na=b""\nwhile True:\n b=s.recv(4096)\n if not b:break\n a+=b\nprint(a.decode())\n')
        shell.chmod(0o500);self.env['PATH']=str(bins)+':/usr/bin'
        self.keeper=Keeper(self.ipc.root,self.env,lambda row:self.registry.append(deepcopy(row)))
        self.commands=OwnedCommands(self.keeper,self.env,17,readonly=self.ipc.reader)
        root=self.ipc.runtime/'hypr-window-motion'/'actor-17';root.parent.mkdir(mode=0o700)
        self.desktop=CpuDesktop(root,core=self.ipc.runtime/'never-executed-core',commands=self.commands)
        self.desktop.fixture=self.fixture;self.desktop.owner=self
        self.transport=Transport();self.controller=SceneController(self.desktop,self.transport);self.controller.lock=self.ipc.lock
    def install_state(self,w):
        (self.controls/w['address']).write_text('1 0 '+w['stableId']+'\n')
        (self.controls/(w['address']+'.monitor.json')).write_text(json.dumps({'pid':w['pid'],'stableId':w['stableId'],'homeWorkspace':1,'monitorName':'CPU-1'}))
    def handle(self,connection,data):
        wire=data.decode();start=time.monotonic_ns()
        if wire=='j/monitors':
            with self.monitor_lock:
                self.monitor_started+=1;self.active_monitors+=1
                self.max_monitors=max(self.max_monitors,self.active_monitors)
                if self.monitor_started>=3:self.first_three.set()
            try:
                if self.gate and not self.gate.wait(3):raise TimeoutError('CPU monitor permit missing')
                if self.monitor_delay:time.sleep(self.monitor_delay)
                reply=b'[{' if self.malformed else json.dumps(self.monitors).encode()
            finally:
                with self.monitor_lock:self.active_monitors-=1
        elif wire=='j/workspaces':reply=b'[{"name":"1","monitorID":0,"monitor":"CPU-1"}]'
        elif wire=='j/clients':reply=json.dumps(self.fixture.windows).encode()
        elif 'dispatch ' in wire:
            if self.native_gate and not self.native_gate.wait(3):raise TimeoutError('CPU dispatch permit missing')
            if self.dispatch_delay:time.sleep(self.dispatch_delay)
            reply=b'error: CPU exact monitor refused' if self.dispatch_error else b'ok'
        elif wire=='CPU_REFRESH':reply=b'true'
        else:raise AssertionError(wire)
        try:connection.sendall(reply)
        except (BrokenPipeError,ConnectionResetError) as error:self.errors.append(type(error).__name__)
        self.requests.append({'wire':wire,'startNs':start,'replyNs':time.monotonic_ns()})
    def request(self,*,defer=False,context=1):
        w=self.fixture.windows[0]
        self.controller.request('restore',w['address'],w['stableId'],w['pid'],context=context,defer_prepare=defer)
        return self.controller.current
    def plans(self,members=None,deadline_ns=None,current=None):
        return self.desktop.plan_destinations(members or self.fixture.windows,
            current=current or (lambda:self.current),reservation_lock=self.ipc.lock,
            deadline_ns=deadline_ns if deadline_ns is not None else time.monotonic_ns()+2_000_000_000)
    def wait_worker(self):self.controller.workers.shutdown(wait=True)
    def focus(self):return [r for r in self.requests if 'dispatch ' in r['wire']]
    def assert_drained(self):
        assert not self.keeper.jobs
        history=self.ipc.reader.snapshot()['history']
        assert all(r['closed'] and r['published'] and r['outcome'] in ('complete','refused') for r in history)
        assert self.active_monitors==0
        assert not any(t.name.startswith('destination-observation') and t.is_alive() for t in threading.enumerate())
    def close(self):
        for event in [self.gate,self.native_gate,*self.order_permits]:
            if event:event.set()
        self.wait_worker()
        if self.keeper.jobs:
            # A test's unknown native completion remains uncertain; abort is
            # exact CPU cleanup, explicitly not normal acceptance.
            self.terminal=self.keeper.abort()
            assert self.terminal['normalStop'] is False
        else:
            self.keeper.stop();self.terminal=self.keeper.ownership['terminal']
            assert self.terminal['normalStop'] is True
        self.ipc.reader.assert_closed();self.ipc.tearDown()
        for k,v in self.original_env.items():
            if v is None:os.environ.pop(k,None)
            else:os.environ[k]=v
