"""Actual independent editable/selection native API calls on retained Qt peers."""
from pathlib import Path
import json,os,shutil,subprocess,time
B=Path(__file__).resolve().parent
root=B/'home';shutil.copytree('/home/hoskinson/window-integration-qa/files-installed-qa-v2/home-template',root)
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',HOME=str(root),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'),DBUS_SESSION_BUS_ADDRESS='unix:path='+str(B/'no-session-bus'))
env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None)
r={'scope':'Actual native Qt6.11.2 editable/selection interfaces on copied Files PathBar TextInput and diagnostic native TextEdit; isolated offscreen session bus, no Orca/compositor claim','cases':[]};log=(B/'run.log').open('w');p=subprocess.Popen(['qs','-p',str(B/'app')],env=env,stdout=log,stderr=log)
def ipc(n,*a):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-keyboard-qa',n,*map(str,a)],text=True,timeout=5).strip()
def wait(fn):
 end=time.monotonic()+5
 while time.monotonic()<end:
  try:
   if fn():return
  except subprocess.CalledProcessError:pass
  time.sleep(.08)
 raise AssertionError('fixture readiness')
operations=['delete','insert','replace','selection','addSelection','removeSelection','cursor','setValue']
try:
 wait(lambda:json.loads(ipc('migrationStatus'))['ready']);ipc('open',root/'fixture');time.sleep(.4)
 for name in ['PathBar.input','QA.TextEdit']:
  for context in ['visible','hidden','disabled','modalBackground','readOnly']:
   for op in operations:
    ipc('mappedSet','true');ipc('key',16777216,0);ipc('scenario','path');time.sleep(.05)
    assert int(ipc('retain',name))>0
    ipc('controlProperty','enabled','true');ipc('controlProperty','readOnly','false');ipc('prepareText','ABCDEF')
    if context=='hidden':ipc('mappedSet','false')
    if context=='disabled':ipc('controlProperty','enabled','false')
    if context=='modalBackground':ipc('act','prompt','')
    if context=='readOnly':ipc('controlProperty','readOnly','true')
    time.sleep(.05);result=json.loads(ipc('mutate',op));r['cases'].append(dict(item=name,context=context,operation=op,**result))
   ipc('mappedSet','true');ipc('controlProperty','enabled','true');ipc('controlProperty','readOnly','false');ipc('key',16777216,0)
 # Own prompt text remains editable through native interfaces.
 ipc('act','prompt','');assert int(ipc('retain','Prompt.input'))>0
 for op in operations:ipc('prepareText','ABCDEF');r['cases'].append(dict(item='Prompt.input',context='modalOwner',operation=op,**json.loads(ipc('mutate',op))))
 ipc('key',16777216,0);ipc('retain','QA.TextEdit');ipc('editorLifetime','false');time.sleep(.1)
 r['destroyedPeer']=json.loads(ipc('mutate','insert'))
except Exception as error:r['error']=repr(error)
finally:
 if p.poll() is None:
  try:ipc('mappedSet','false')
  except Exception:pass
  p.terminate();p.wait(timeout=8)
 log.close();r['exitCode']=p.poll();(B/'report.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({'error':r.get('error'),'cases':len(r['cases']),'unauthorizedChanges':[{'item':c['item'],'context':c['context'],'operation':c['operation']} for c in r['cases'] if c['context'] in ['hidden','disabled','modalBackground'] and c['changed']],'destroyedPeer':r.get('destroyedPeer')},indent=2))
