from pathlib import Path
import json,os,subprocess,time
B=Path(__file__).resolve().parent;env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',DBUS_SESSION_BUS_ADDRESS='unix:path='+str(B/'no-session-bus'),HOME=str(Path('/home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/isolated-home')),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'));env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None)
r={'scope':'Actual Qt key events on copied fresh routing list/grid focus, selection and prompt payload; private session bus; no new reader/compositor test','trace':[]};log=(B/'run.log').open('w');p=subprocess.Popen(['qs','-p',str(B/'app')],env=env,stdout=log,stderr=log)
def ipc(n,*a):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-keyboard-qa',n,*map(str,a)],text=True,timeout=5).strip()
def snapshot(event):
 s=json.loads(ipc('state'));u=json.loads(ipc('uiState'));r['trace'].append({'event':event,'cur':s['cur'],'sel':s['sel'],'focus':ipc('locus'),'focusIdentity':u.get('focusIdentity'),'prompt':u['prompt']})
try:
 time.sleep(.5);ipc('resize',330,320);time.sleep(.2)
 for mode in ['list','grid']:
  ipc('open','home');time.sleep(.1);ipc('open',Path('/home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/isolated-home/fixture'));time.sleep(.3);ipc('act','view',mode);ipc('focus','Explorer.keys');ipc('key',16777232,0);time.sleep(.15);snapshot(mode+' Home')
  for i in range(2):ipc('key',16777237,0);time.sleep(.15);snapshot(mode+' Down '+str(i+1))
  ipc('key',16777265,0);time.sleep(.15);snapshot(mode+' F2');assert r['trace'][-1]['prompt']['visible']
  assert r['trace'][-1]['prompt']['text']==r['trace'][-2]['sel'][0]
  ipc('key',16777216,0);ipc('focus','Explorer.keys');ipc('key',16777232,0);ipc('key',16777237,0x02000000);time.sleep(.15);snapshot(mode+' Shift Down');assert len(r['trace'][-1]['sel'])>=2
except Exception as e:r['error']=repr(e)
finally:
 if p.poll() is None:ipc('toggle');p.terminate();p.wait(timeout=8)
 log.close();r['exitCode']=p.poll();(B/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
