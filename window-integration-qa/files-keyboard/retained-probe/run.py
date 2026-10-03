#!/usr/bin/env python3
"""Raw native retained-interface dispatch and QML callback probes, offscreen only."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
B=Path(__file__).resolve().parent
root=B/'home';shutil.copytree(B.parent/'isolated-home',root,dirs_exist_ok=True)
(root/'fixture/beta.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',HOME=str(root),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'))
env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None)
report={'scope':'Actual frozen candidate QML/V4 dispatch in copied offscreen Qt; no Orca or compositor input. Media metadata injected only to probe logical rebinding.','observations':[]}
log=(B/'run.log').open('w');p=subprocess.Popen(['qs','-p',str(B/'app')],env=env,stdout=log,stderr=log)
def ipc(name,*args):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-retained-qa',name,*map(str,args)],text=True,timeout=5).strip()
def wait(fn):
 end=time.monotonic()+6
 while time.monotonic()<end:
  try:
   if fn():return
  except (subprocess.CalledProcessError,json.JSONDecodeError):pass
  time.sleep(.08)
 raise AssertionError('fixture readiness')
def state():return json.loads(ipc('state'))
def ui():return json.loads(ipc('uiState'))
def observe(name,**kw):report['observations'].append(dict(name=name,**kw))
try:
 wait(lambda:state()['view']=='home')
 ipc('open',root/'fixture');wait(lambda:state()['entries']==5)
 ipc('act','view','grid');time.sleep(.2)
 iid=ipc('retain','Show list');assert int(iid)>0
 before=state()['mode'];dispatch=json.loads(ipc('dispatch','Press'));after=state()['mode']
 observe('visible native press sanity',interfaceId=iid,dispatch=dispatch,before=before,after=after,callbackExecuted=before!=after)
 ipc('mappedSet','false');time.sleep(.2)
 before=state()['mode'];dispatch=json.loads(ipc('dispatch','Press'));after=state()['mode']
 observe('hidden window retained native press',dispatch=dispatch,before=before,after=after,callbackExecuted=before!=after,requiredRefusal=before==after)
 before=state()['mode'];raw=ipc('callback');after=state()['mode']
 observe('hidden window raw retained QML activate',returned=raw,before=before,after=after,callbackExecuted=before!=after,requiredRefusal=before==after)
 ipc('mappedSet','true');time.sleep(.2)
 ipc('act','prompt','');time.sleep(.15)
 before=ipc('locus');ipc('key',76,0x04000000);time.sleep(.15)
 observe('prompt Ctrl L routing',before=before,after=ipc('locus'),promptStillVisible=ui()['prompt']['visible'],pathEditing=ui()['path']['editing'])
 ipc('key',16777216,0);time.sleep(.2)
 ipc('scenario','home');wait(lambda:state()['view']=='home');time.sleep(.5)
 ipc('media',root/'fixture/image.svg');time.sleep(.2)
 iid=ipc('retain','Dashboard.mt');assert int(iid)>0
 first=json.loads(ipc('dispatch','setFocus'))
 ipc('media',root/'fixture/beta.svg');time.sleep(.2)
 second=json.loads(ipc('dispatch','Press'));time.sleep(.25)
 observe('static media logical-path rebind through retained native peer',interfaceId=iid,before=first,after=second,selected=state()['sel'],samePeerAlive=second.get('objectAlive'),capturedOldIdentityRefused=second.get('name')==first.get('name'))
 ipc('act','view','list');time.sleep(.25);ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.25)
 iid=ipc('retain','FileArea.row');assert int(iid)>0
 first=json.loads(ipc('dispatch','setFocus'));ipc('open','home');wait(lambda:state()['view']=='home');time.sleep(.25)
 second=json.loads(ipc('dispatch','Press'))
 observe('destroyed file delegate retained native peer',interfaceId=iid,before=first,after=second,refused=not second.get('interfaceFound'))
 ipc('open',root/'fixture');wait(lambda:state()['entries']==5);ipc('act','view','list');ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.25)
 before=ipc('locus');exported=ui()['focus'];samepid=p.pid
 # Actual watched-file reload of copied QML; never edit source evidence or original.
 host=B/'app/shell.qml';host.write_text(host.read_text()+'\n// offscreen focus reload probe\n');time.sleep(.8)
 wait(lambda:json.loads(ipc('migrationStatus'))['ready'])
 observe('actual same PID focused file reload',before=before,after=ipc('locus'),exportedFocus=exported,samePid=p.pid==samepid and p.poll() is None,requiredFocusPreserved=ipc('locus')==before)
except Exception as e:report['error']=repr(e)
finally:
 if p.poll() is None:
  try:ipc('mappedSet','false');time.sleep(.1)
  except Exception:pass
  p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:report['cleanupError']='normal termination timed out'
 log.close();report['exitCode']=p.poll()
 report['result']='observed' if not report.get('error') else 'fixture-error'
 (B/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
