"""Actual staged controller/JS inside offscreen Quickshell, no native GUI."""
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
    for source,target in [(BASE/'SwitcherController.qml','SwitcherController.qml'),(BASE/'SwitcherState.js','SwitcherState.js'),(BASE/'tests/probe.qml','shell.qml')]:shutil.copy2(source,path/target)
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='generic',QT_STYLE_OVERRIDE='Fusion',XDG_RUNTIME_DIR=str(runtime),HYPRLAND_INSTANCE_SIGNATURE='session')
    for name in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY'):env.pop(name,None)
    result=subprocess.run(['qs','-p',str(path),'-d','-n'],env=env,capture_output=True,text=True,timeout=8)
    print(result.stdout+result.stderr)
    if result.returncode or 'SWITCHER_QML_PASS 10' not in result.stdout+result.stderr:raise SystemExit(1)
