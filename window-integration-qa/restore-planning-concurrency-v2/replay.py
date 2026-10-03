"""Frozen controller/planner/owned launch, genuine private Unix peer; CPU only."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time

OUT = Path(__file__).resolve().parent
QA = OUT.parent
SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26')
CORE = Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback/inverses/core')
sys.path[:0] = [str(SERVICE), str(QA)]
from qa_launch import require_qa_scope
from helper_supervisor import Keeper
from native_desktop import NativeDesktop
from owned_commands import OwnedCommands
from scene_controller import SceneController
from test_readonly_ipc import ReadonlyKernelTests
from test_scene_controller import Desktop, Transport


def stamp(p):
    return {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'mode': stat.S_IMODE(p.stat().st_mode)}


def save(name, row):
    with os.fdopen(os.open(OUT / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        json.dump(row, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())


class CpuDesktop(NativeDesktop):
    # The exact inherited plan/apply/refresh methods perform genuine queries
    # and sealed native-effect subprocess launches. CPU-only boundaries below
    # replace GPU pixels/native settlement and do not claim native acceptance.
    retire_gestures = None
    finish_capture_previews = None
    family_evidence = None
    def family(self, window, windows, single=False):
        return self.production.native_family_plan(window, windows, self.fixture.native)
    def reduced(self): return False
    def capture_source(self, window, token, index):
        return self.fixture.capture_source(window, token, index)
    def release_sources(self, sources): self.fixture.release_sources(sources)
    def commit(self, operation, window, preview=True): self.fixture.commit(operation, window, preview)


def main():
    scope = require_qa_scope()
    names = ('native_desktop.py','scene_controller.py','owned_commands.py','owned_launch.py',
             'helper_supervisor.py','readonly_ipc.py','native_runtime.py','service_runtime.py',
             'production_motion_6d9.py','test_readonly_ipc.py','test_scene_controller.py')
    paths = [Path(__file__), SERVICE/'manifest-housekeeping-admission-v26.json']
    paths += [SERVICE/n for n in names]
    paths += [CORE/'src/debug/HyprCtl.cpp', CORE/'hyprctl/src/main.cpp', Path('/usr/bin/hyprctl')]
    inputs = {str(p): stamp(p) for p in paths}
    frozen = json.loads(paths[1].read_text())
    for p in paths[2:2+len(names)]:
        assert inputs[str(p)]['sha256'] == frozen['inputs'][str(p)]
        assert inputs[str(p)]['mode'] == frozen['inputModes'][str(p)]
    assert stamp(CORE/'src/debug/HyprCtl.cpp')['sha256'] == stamp(QA/'qt-modal-private-v9/primary-cursor/HyprCtl.cpp')['sha256']
    ipc = ReadonlyKernelTests(); ipc.setUp()
    keeper = controller = None
    original_env = {k: os.environ.get(k) for k in ipc.env if k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','HOME')}
    result = {'result':'fail', 'GUI':False, 'nativeAcceptance':False}
    observations = []; registry = []
    try:
        home = ipc.runtime/'home'; home.mkdir(mode=0o700)
        env = dict(ipc.env, HOME=str(home)); os.environ.update({k:env[k] for k in original_env})
        fixture = Desktop()
        for w in fixture.windows: w['workspace']['name'] = 'special:win-minimized'
        for w in fixture.native: w['workspace']['name'] = 'special:win-minimized'
        controls = ipc.runtime/'hypr-windowctl'; controls.mkdir(mode=0o700)
        for w in fixture.windows:
            (controls/w['address']).write_text('1 0 '+w['stableId']+'\n')
            (controls/(w['address']+'.monitor.json')).write_text(json.dumps({'pid':w['pid'],'stableId':w['stableId'],'homeWorkspace':1,'monitorName':'CPU-1'}))
        monitors = [{'id':0,'name':'CPU-1','focused':True,'x':0,'y':0,'width':1600,'height':1000,'scale':1}]
        def handle(connection, data):
            start = time.monotonic_ns()
            wire = data.decode()
            if wire in ('j/monitors','j/workspaces'): time.sleep(.35)
            if wire == 'j/clients': reply = json.dumps(fixture.windows).encode()
            elif wire == 'j/monitors': reply = json.dumps(monitors).encode()
            elif wire == 'j/workspaces': reply = b'[{"name":"1","monitorID":0,"monitor":"CPU-1"}]'
            elif wire.startswith('[[BATCH]]'): reply = b'ok\n\n\nerror: CPU middle operation refused\n\n\nok'
            elif 'dispatch ' in wire: reply = b'ok'
            elif wire == 'CPU_REFRESH': reply = b'true'
            else: raise AssertionError(wire)
            connection.sendall(reply)
            observations.append({'wire':wire,'startNs':start,'replyNs':time.monotonic_ns(),'reply':reply.decode()})
        ipc.handler = handle
        bins = home/'bin'; bins.mkdir(mode=0o700)
        shell = bins/'omarchy-shell'
        shell.write_text('#!/usr/bin/python3\nimport os,socket\ns=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)\ns.connect(os.environ["XDG_RUNTIME_DIR"]+"/hypr/"+os.environ["HYPRLAND_INSTANCE_SIGNATURE"]+"/.socket.sock")\ns.sendall(b"CPU_REFRESH")\na=b""\nwhile True:\n b=s.recv(4096)\n if not b:break\n a+=b\nprint(a.decode())\n')
        shell.chmod(0o500); env['PATH']=str(bins)+':/usr/bin'
        keeper = Keeper(ipc.root, env, lambda row: registry.append(deepcopy(row)))
        commands = OwnedCommands(keeper, env, 17, readonly=ipc.reader)
        root = ipc.runtime/'hypr-window-motion'/'actor-17'
        root.parent.mkdir(mode=0o700)
        desktop = CpuDesktop(root, core=ipc.runtime/'never-executed-core', commands=commands)
        desktop.fixture = fixture
        transport = Transport()
        controller = SceneController(desktop, transport); controller.lock = ipc.lock
        request = controller.request('restore', fixture.windows[0]['address'], fixture.windows[0]['stableId'], fixture.windows[0]['pid'],context=1)
        record = controller.current
        controller.workers.shutdown(wait=True)
        assert record.profile['failure'] == 'original scene receipt deadline before seed', record.profile
        assert not any(m['command']=='seed' for m in transport.sent)
        focus = [r for r in observations if 'dispatch ' in r['wire']]
        assert len(focus)==6
        expected = ['monitor','workspace']*3
        assert all('hl.dsp.focus({ '+role+' =' in row['wire'] for role,row in zip(expected,focus,strict=True))
        assert len([r for r in observations if r['wire']=='CPU_REFRESH'])==3
        assert record.profile['metadataValidatedNs']-record.profile['receivedNs'] >= 2_000_000_000
        assert len(fixture.commits)==3 and all(op=='restore' for op,*_ in fixture.commits)
        assert not keeper.jobs
        # The real selected CLI's --batch drops request's nonzero return, so a
        # zero exit cannot substitute for per-operation completion evidence.
        result.update(actualProfile=deepcopy(record.profile), actualFallbackResults=deepcopy(record.results))
        batch = commands.run(['/usr/bin/hyprctl','--batch','dispatch one;dispatch two;dispatch three'],capture_output=True,text=True,timeout=2)
        result['batchObservedBeforeDecision'] = {'returncode':batch.returncode,'stdout':batch.stdout,'stderr':batch.stderr}
        assert batch.returncode==0 and 'error:' in batch.stdout
        result.update(result='pass', scope=scope, request=request, actualProfile=deepcopy(record.profile),
            actualFallbackResults=deepcopy(record.results), focusOperations=focus,
            actualReadonlyRows=ipc.reader.snapshot()['history'], ownedRegistrySnapshots=registry,
            actualBatchClient={'returncode':batch.returncode,'stdout':batch.stdout,'stderr':batch.stderr,
                               'currentClassifier':commands.classify(['/usr/bin/hyprctl','--batch','dispatch one'])},
            limits=['Frozen actual NativeDesktop planner/apply/refresh, SceneController and OwnedCommands/OwnedLaunch/Keeper executed.',
                    'Genuine selected hyprctl and authenticated ReadonlyIPC with kernel peer/EOF and durable JournalStore.',
                    'Each plan monitor/workspace CPU reply has explicit 350ms delay, within each unchanged2s query deadline.',
                    'CPU family/pixels/native settlement and shell refresh are explicit fixture boundaries; no native PNG acceptance.',
                    'Reachable original2s preparation exhaustion, not historical live-call latency attribution.',
                    'No grouped native effects or candidate runtime correction executed; batch ACK counterexample is diagnostic.'])
    finally:
        if controller: controller.workers.shutdown(wait=True,cancel_futures=True)
        if keeper:
            assert not keeper.jobs; keeper.stop()
            result['keeperNormalTerminal']=deepcopy(keeper.ownership['terminal'])
        ipc.reader.assert_closed(); ipc.tearDown()
        for k,v in original_env.items():
            if v is None: os.environ.pop(k,None)
            else: os.environ[k]=v
        assert inputs == {str(p):stamp(p) for p in paths}
        result.update(inputs=inputs,sourceUnchanged=True,observations=observations)
        save('report.json',result)
    print(json.dumps({'result':result['result'],'report':str(OUT/'report.json')}))
    return int(result['result']!='pass')


if __name__=='__main__': raise SystemExit(main())
