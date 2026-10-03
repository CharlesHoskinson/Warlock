#!/usr/bin/env python3
"""Run only against the dedicated nested observer compositor."""
import json, os, subprocess, sys, time
from pathlib import Path
runtime = '/run/user/1000/motion-qa'
instance = json.loads(subprocess.check_output(['hyprctl', 'instances', '-j'],
    env=dict(os.environ, XDG_RUNTIME_DIR=runtime), text=True))[0]
assert b'motion-probe/nested.lua' in Path(f'/proc/{instance["pid"]}/cmdline').read_bytes()
env = dict(os.environ, XDG_RUNTIME_DIR=runtime, WAYLAND_DISPLAY=instance['wl_socket'],
           HYPRLAND_INSTANCE_SIGNATURE=instance['instance'])
library = str(Path(sys.argv[1]).resolve())
def ctl(*args):
    return subprocess.check_output(['hyprctl', *args], env=env, text=True).strip()
process = None
loaded = False
try:
    result = ctl('plugin', 'load', library)
    assert result == 'ok', result
    loaded = True
    process = subprocess.Popen(['foot', '--app-id=motion-probe-smoke', 'sleep', '120'],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    window = None
    for _ in range(50):
        window = next((w for w in json.loads(ctl('clients', '-j')) if w['pid'] == process.pid), None)
        if window: break
        time.sleep(.1)
    assert window
    assert json.loads(ctl('motionprobe', 'start', window['address'], str(process.pid)))['active']
    ctl('dispatch', f'hl.dsp.window.move({{x=100,y=100,window="address:{window["address"]}"}})')
    time.sleep(.7)
    result = json.loads(ctl('motionprobe', 'stop'))
    assert result['frames'] and result['presentations'] and not result['overflow'], result
    assert json.loads(ctl('motionprobe', 'start', window['address'], str(process.pid + 1)))['error']
    print('PASS: nested load/capture/stale-PID rejection/unload', len(result['frames']),
          'frames', len(result['presentations']), 'presentations')
    (Path.home()/'.cache/window-motion-probe-smoke.json').write_text(json.dumps(result, indent=2))
finally:
    if process:
        process.terminate(); process.wait(timeout=3)
    if loaded: assert ctl('plugin', 'unload', library) == 'ok'
