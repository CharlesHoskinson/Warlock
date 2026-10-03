#!/usr/bin/env python3
import argparse,json,subprocess,time
from pathlib import Path
H=Path.home()
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--pin',action='store_true');parser.add_argument('--capture',action='store_true');args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
def data(name):return json.loads(subprocess.check_output(['hyprctl',name,'-j'],text=True))
def dispatch(s):subprocess.check_call(['hyprctl','dispatch',s],stdout=subprocess.DEVNULL)
original=data('clients');focus=data('activewindow');cursor=data('cursorpos')
p=subprocess.Popen(['foot','--app-id=motion-native-qa','--title=Motion native QA','python3','-c','import time\nprint("\\033[46m Minimize / Restore Native QA \\033[0m\\n"*12,flush=True)\ntime.sleep(180)'],stdout=subprocess.DEVNULL,stderr=(out/'foot.log').open('w'))
try:
 w=None
 for _ in range(100):
  w=next((w for w in data('clients') if w['pid']==p.pid),None)
  if w:break
  time.sleep(.05)
 assert w,'foot map timeout'
 a=w['address']
 if not w['floating']:dispatch(f'hl.dsp.window.float({{action="set",window="address:{a}"}})')
 dispatch(f'hl.dsp.window.resize({{x=620,y=380,window="address:{a}"}})');dispatch(f'hl.dsp.window.move({{x=320,y=350,window="address:{a}"}})')
 if args.pin:dispatch(f'hl.dsp.window.pin({{window="address:{a}"}})')
 dispatch(f'hl.dsp.focus({{window="address:{a}"}})');time.sleep(1)
 command=['python3',str(H/'window-behavior-spec/minimize-motion-stage/native_motion_trial.py'),'--window',a,'--output',str(out),'--reduced-motion-trial']
 if args.capture:command.append('--capture-frames')
 subprocess.run(command,check=True)
finally:
 p.terminate()
 try:p.wait(timeout=4)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 current=data('clients');preserved={w['stableId'] for w in original}.issubset({w['stableId'] for w in current})
 if any(w['stableId']==focus.get('stableId') and w['pid']==focus.get('pid') for w in current):dispatch(f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
 dispatch(f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
 (out/'fixture-cleanup.json').write_text(json.dumps({'originalWindowsPreserved':preserved,'fixturePID':p.pid},indent=2));assert preserved
