from pathlib import Path
import json,os,subprocess,time
B=Path(__file__).resolve().parent
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',HOME=str(B/'isolated-home'),FILES_STATE=str(B/'isolated-state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'isolated-cache'))
env.pop('WAYLAND_DISPLAY',None);env.pop('DISPLAY',None);env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+str(B/'no-shared-session-bus')
env['QT_QPA_PLATFORMTHEME']='';env['QT_STYLE_OVERRIDE']='Fusion'
with (B/'geometry.log').open('w') as log:
 p=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=log,stderr=log)
 try:
  time.sleep(.6)
  r=subprocess.run(['python3',str(B/'check_geometry.py')],timeout=150)
  assert r.returncode==0, r.returncode
 finally:
  subprocess.run(['qs','ipc','--pid',str(p.pid),'call','files-keyboard-qa','shutdown'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:
   p.terminate();p.wait(timeout=8)
 print(json.dumps({'fixtureExitCode':p.returncode}))
