"""Actual Quickshell offscreen service/transport test; no compositor connection."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope, owned_runtime

BASE = Path(__file__).resolve().parents[1]
HELPER = '''#!/usr/bin/python3
import json,os,signal,sys
from pathlib import Path
state=Path(os.environ['PROBE_STATE'])
(state/'helper.pid').write_text(str(os.getpid()))
def stop(*args):
 (state/'helper-normal-stop').write_text('SIGTERM handled, exit0')
 raise SystemExit(0)
signal.signal(signal.SIGTERM,stop)
def row(epoch,sequence): return dict(protocolVersion=1,epoch=epoch,sequence=sequence,groups=[],snapGroups=[],monitors=[],settings={},focusedAddress='',reducedMotion=False)
for value in (row('fixture',1),row('fixture',1),row('foreign',2),{'bad':True}): print(json.dumps(value),flush=True)
for line in sys.stdin:
 if line != 'refresh\\n': raise SystemExit(2)
 print(json.dumps(row('fixture',2)),flush=True)
'''
QML = '''import QtQuick
import Quickshell
ShellRoot {
 id: root
 property string helperPath: Quickshell.env("PROBE_HELPER")
 property var currentService: service
 property int phase: 0
 property int ticks: 0
 property int seenA: 0
 property int seenB: 0
 Service { id: service; helper: root.helperPath }
 QtObject {
  id: registry
  property var services: ({"hoskinson.windows":root.currentService})
  function serviceFor(id) { return services[id] || null }
 }
 QtObject {
  id: facade
  property var lookup: function(id) { return registry.serviceFor(id) }
  function serviceFor(id) { return lookup(id) }
 }
 Item {
  id: a
  readonly property var observed: facade.serviceFor("hoskinson.windows")
  Connections { target:a.observed; function onSnapshotTextChanged() {root.seenA++} }
 }
 Item {
  id: b
  readonly property var observed: facade.serviceFor("hoskinson.windows")
  Connections { target:b.observed; function onSnapshotTextChanged() {root.seenB++} }
 }
 function fail(message) { console.error("QT_PROBE_FAIL:"+message); service.stop(); Qt.exit(1) }
 Timer {
  interval: 25; repeat:true; running:true
  onTriggered: {
   root.ticks++
   if(root.ticks>200) {root.fail("timeout phase "+root.phase);return}
   if(root.phase===0 && service.online) {
    if(service.acceptedSnapshots!==1 || service.rejectedSnapshots!==3) {root.fail("initial protocol checks");return}
    if(a.observed!==service || b.observed!==service) {root.fail("shared service lookup");return}
    root.phase=1; service.refresh()
   } else if(root.phase===1 && service.acceptedSnapshots===2) {
    if(service.streamState.sequence!==2 || service.rejectedSnapshots!==3 || root.seenA<2 || root.seenB<2) {root.fail("refresh and shared fanout");return}
    root.phase=2;root.currentService=null
   } else if(root.phase===2) {
    if(a.observed!==null || b.observed!==null) {root.fail("facade invalidation binding");return}
    root.phase=3;root.currentService=service
   } else if(root.phase===3) {
    if(a.observed!==service || b.observed!==service) {root.fail("facade replacement binding");return}
    root.phase=4;service.stop()
   } else if(root.phase===4 && !service.online && service.streamState.sequence===0) {
    console.log("QT_PROBE_PASS:actual Process/SplitParser refresh, three rejected packets, two consumers, facade replacement, normal stop")
    Qt.quit()
   }
  }
 }
}
'''

def main():
    require_qa_scope()
    failed_start = '--failed-start' in sys.argv
    cache = Path.home() / '.cache/windows-parity-research/runtime-probes'
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix='service-', dir=cache) as temp, owned_runtime() as selected_runtime:
        root = Path(temp)
        runtime = Path(selected_runtime)
        for name in ('Service.qml', 'SnapshotStream.js'):
            shutil.copy2(BASE / 'widget_v68' / name, root / name)
        helper = root / 'fixture'
        helper.write_text(HELPER)
        helper.chmod(0o700)
        qml = QML
        if failed_start:
            qml = qml.replace('property string helperPath: Quickshell.env("PROBE_HELPER")', 'property string helperPath: Quickshell.env("PROBE_MISSING_HELPER")')
            qml = qml.replace('root.ticks++', 'root.ticks++\n   if(root.helperPath!==Quickshell.env("PROBE_HELPER") && service.lastError.indexOf("failed to start")>=0) root.helperPath=Quickshell.env("PROBE_HELPER")')
        (root / 'shell.qml').write_text(qml)
        env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME='generic', QT_STYLE_OVERRIDE='Fusion', XDG_RUNTIME_DIR=str(runtime), PROBE_HELPER=str(helper), PROBE_MISSING_HELPER=str(root/'missing'), PROBE_STATE=str(root))
        for name in ('WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'DISPLAY', 'XAUTHORITY'):
            env.pop(name, None)
        result = subprocess.run(['/usr/bin/quickshell', '--no-color', '-p', str(root)], env=env, capture_output=True, text=True, timeout=12)
        normal = (root / 'helper-normal-stop').exists() and not Path('/proc', (root / 'helper.pid').read_text()).exists()
        success = result.returncode == 0 and 'QT_PROBE_PASS:' in result.stdout + result.stderr and normal
        report = dict(result='pass' if success else 'fail', returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                      noCompositorConnection=True, nativeWindowEffects=False, actualQuickshell=True, helperNormalStop=normal)
        target = BASE / 'tests' / (('qt-failed-start-report.json' if failed_start else 'qt-service-report.json') if success else 'qt-service-failure-'+str(time.time_ns())+'.json')
        target.write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(dict(result=report['result'], report=str(target))))
        if not success:
            print(result.stdout + result.stderr)
        return int(not success)

if __name__ == '__main__':
    raise SystemExit(main())
