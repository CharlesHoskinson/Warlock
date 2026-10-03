from pathlib import Path
import json,os,subprocess,time
B=Path(__file__).resolve().parent;home=Path.home()/'window-integration-qa/files-keyboard/editable-stage-v6/isolated-home';env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',DBUS_SESSION_BUS_ADDRESS='unix:path='+str(B/'no-session-bus'),HOME=str(home),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'));env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None)
r={'scope':'Actual raw Qt attached toggleAction signal on copied gallery Cell; offscreen/private D-Bus, no reader proof','observations':[]};log=(B/'run.log').open('w');p=subprocess.Popen(['qs','-p',str(B/'app')],env=env,stdout=log,stderr=log)
def ipc(n,*a):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-retained-qa',n,*map(str,a)],text=True,timeout=5).strip()
try:
 time.sleep(.5);ipc('open',home/'fixture');time.sleep(.3);ipc('act','view','grid');ipc('retain','FileArea.cl')
 for context in ['visible','hidden','disabled','modalBackground']:
  ipc('mappedSet','true');ipc('controlProperty','enabled','true');ipc('key',16777216,0);time.sleep(.1);ipc('retain','FileArea.cl')
  if context=='hidden':ipc('mappedSet','false')
  if context=='disabled':ipc('controlProperty','enabled','false')
  if context=='modalBackground':ipc('act','prompt','')
  time.sleep(.05);peer=json.loads(ipc('dispatch','setFocus'));before=json.loads(ipc('state'));accepted=ipc('rawToggle');after=json.loads(ipc('state'))
  r['observations'].append({'context':context,'peer':peer,'signalInvoked':accepted,'selectionBefore':before['sel'],'selectionAfter':after['sel'],'changed':before['sel']!=after['sel']})
except Exception as e:r['error']=repr(e)
finally:
 if p.poll() is None:ipc('mappedSet','false');p.terminate();p.wait(timeout=8)
 log.close();r['exitCode']=p.poll();(B/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
