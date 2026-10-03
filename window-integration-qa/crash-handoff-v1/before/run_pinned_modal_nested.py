#!/usr/bin/env python3
"""Use an already-running dedicated nested compositor, never stale env files."""
import json,os,subprocess,sys
from pathlib import Path
runtime='/run/user/1000/pinned-qa'
instance=json.loads(subprocess.check_output(['hyprctl','instances','-j'],
    env=dict(os.environ,XDG_RUNTIME_DIR=runtime),text=True))[0]
assert b'window-integration-qa/nested_pinned.lua' in Path(f'/proc/{instance["pid"]}/cmdline').read_bytes()
env=dict(os.environ,XDG_RUNTIME_DIR=runtime,XDG_CONFIG_HOME='/run/user/1000/pinned-qa-config',
    HYPRLAND_INSTANCE_SIGNATURE=instance['instance'],WAYLAND_DISPLAY=instance['wl_socket'])
env['PINNED_MODAL_DESKTOP_REPORT']=sys.argv[2]
if len(sys.argv)>3:env['GDK_BACKEND']=sys.argv[3]
def ctl(*a):return subprocess.check_output(['hyprctl',*a],env=env,text=True).strip()
if json.loads(ctl('plugin','list','-j')):
    paths={line.split(None,5)[5].strip() for line in Path(f'/proc/{instance["pid"]}/maps').read_text().splitlines() if len(line.split(None,5))==6}
    for path in paths:
        if path.startswith(str(Path.home())+'/') and ('hyprbars-' in Path(path).name or 'libhyprbars-' in Path(path).name) and path.endswith('.so'):
            ctl('plugin','unload',path)
    assert not json.loads(ctl('plugin','list','-j')),'nested plugin could not be unloaded'
assert ctl('plugin','load',str(Path(sys.argv[1]).resolve()))=='ok'
assert ctl('reload')=='ok'
assert not ctl('configerrors'),ctl('configerrors')
env['PINNED_QA_LIBRARY']=str(Path(sys.argv[1]).resolve())
if len(sys.argv)>3 and sys.argv[3]=='x11':
    env['DISPLAY']=ctl('repl','print(os.getenv("DISPLAY"))')
    assert env['DISPLAY'].startswith(':'),env['DISPLAY']
print('Nested monitor:',ctl('monitors','-j'),flush=True)
result=subprocess.run(['python3',str(Path(__file__).with_name('live_pinned_modal_desktops.py'))],env=env)
sys.exit(result.returncode)
