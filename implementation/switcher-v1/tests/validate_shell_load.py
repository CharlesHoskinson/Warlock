"""Load full staged controls shell offscreen with its overlay kept hidden."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,owned_runtime
BASE=Path(__file__).resolve().parents[1]
require_qa_scope()
with tempfile.TemporaryDirectory() as folder, owned_runtime() as runtime:
    path=Path(folder)
    for name in ('SwitcherController.qml','SwitcherState.js'):shutil.copy2(BASE/name,path/name)
    source=(BASE/'shell.qml').read_text();index=source.rfind('}')
    source=source[:index]+'''Timer { interval:50; running:true; onTriggered: {
        if(root.opened) {console.error("STAGED_SHELL_FAIL overlay opened");Qt.exit(1);return}
        console.log("STAGED_SHELL_PASS hidden full controls shell loaded");Qt.quit()
    }}\n'''+source[index:]
    (path/'shell.qml').write_text(source)
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='generic',QT_STYLE_OVERRIDE='Fusion',XDG_RUNTIME_DIR=str(runtime),HYPRLAND_INSTANCE_SIGNATURE='session')
    for name in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPR_WINDOW_MENU'):env.pop(name,None)
    result=subprocess.run(['qs','-p',str(path),'-d','-n'],env=env,capture_output=True,text=True,timeout=8)
    print(result.stdout+result.stderr)
    if result.returncode or 'STAGED_SHELL_PASS' not in result.stdout+result.stderr:raise SystemExit(1)
