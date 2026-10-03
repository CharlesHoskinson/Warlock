import sys,time,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from atspi_qa import assistive_session,find,invoke
H=Path.home()
def run(*args):return subprocess.check_output([str(x) for x in args],text=True).strip()
def clients():return json.loads(run('hyprctl','clients','-j'))
initial=json.loads(run('hyprctl','activewindow','-j'))
p=subprocess.Popen(['foot','--app-id=org.omarchy.readerdiag','--title=Reader action diagnostic','sleep','90'])
def w():return next((x for x in clients() if x['pid']==p.pid),None)
try:
 for i in range(40):
  if w():break
  time.sleep(.1)
 target=w();addr=target['address'];sid=target['stableId']
 with assistive_session():
  node=None
  for i in range(40):
   snapshot=json.loads(run(H/'.local/bin/hypr-taskbar','snapshot'))
   group=next((g for g in snapshot['groups'] if any(x['address']==addr for x in g['windows'])),None)
   if group:
    node=find(accessible_id='taskbar-app:'+group['key'])
    if node:break
   time.sleep(.1)
  print('snapshot exact',next(x for x in group['windows'] if x['address']==addr),flush=True)
  print('focus native',json.loads(run('hyprctl','activewindow','-j')).get('address'),'snapshot',snapshot['focusedAddress'],flush=True)
  invoke(node)
  print('after AX',w()['workspace'],json.loads(run('hyprctl','activewindow','-j')).get('address'),flush=True)
  print('direct expected helper',run(H/'.local/bin/hypr-windowctl','minimize',addr,sid,str(p.pid)),flush=True)
  print('after direct',w()['workspace'],flush=True)
  run(H/'.local/bin/hypr-windowctl','restore',addr,sid,str(p.pid))
  print('after restore exact',json.loads(run('hyprctl','activewindow','-j')).get('address'),addr,flush=True)
finally:
 p.terminate();p.wait()
 if initial.get('address'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
