#!/usr/bin/env python3
"""Raw native retained-interface dispatch and QML callback probes, offscreen only."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
B=Path(__file__).resolve().parent
root=B/'home';shutil.copytree(B.parent/'isolated-home',root,dirs_exist_ok=True)
(root/'fixture/beta.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',HOME=str(root),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'))
env.pop('DISPLAY',None);env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+str(B/'no-shared-session-bus');env.pop('WAYLAND_DISPLAY',None)
report={'scope':'Fresh guarded candidate QML/V5 dispatch in copied offscreen Qt; no Orca or compositor input. Media metadata injected only to probe logical rebinding.','observations':[]}
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
 before=state()['mode'];ipc('act','prompt','');time.sleep(.15)
 dispatch=json.loads(ipc('dispatch','Press'));raw=ipc('rawAttached')
 observe('prompt rejects retained background native and raw attached press',dispatch=dispatch,rawReturned=raw,modeBefore=before,modeAfter=state()['mode'],refused=state()['mode']==before)

 before=ipc('locus');ipc('key',76,0x04000000);time.sleep(.15)
 ipc('key',66,0x04000000);time.sleep(.1)
 observe('prompt Ctrl B routing',sidebarRequested=ui()['sidebarRequested'],focus=ipc('locus'),refused=not ui()['sidebarRequested'])
 observe('prompt Ctrl L routing',before=before,after=ipc('locus'),promptStillVisible=ui()['prompt']['visible'],pathEditing=ui()['path']['editing'])
 ipc('key',16777216,0);time.sleep(.2)
 ipc('scenario','home');wait(lambda:state()['view']=='home');time.sleep(.5)
 ipc('media',root/'fixture/image.svg');time.sleep(.2)
 iid=ipc('retain','Dashboard.mt');assert int(iid)>0
 first=json.loads(ipc('dispatch','setFocus'))
 ipc('media',root/'fixture/beta.svg');time.sleep(.2)
 second=json.loads(ipc('dispatch','Press'));time.sleep(.25)
 observe('static media logical-path rebind through retained native peer',interfaceId=iid,before=first,after=second,selected=state()['sel'],samePeerAlive=second.get('objectAlive'),capturedOldIdentityRefused=not second.get('interfaceFound'))
 iidNew=ipc('retain','Dashboard.mt');newDispatch=json.loads(ipc('dispatch','Press'));time.sleep(.25)
 observe('new media logical peer remains actionable',newInterfaceId=iidNew,oldInterfaceId=iid,dispatch=newDispatch,selected=state()['sel'],newPeer=int(iidNew)!=int(iid))
 ipc('open',root/'fixture');wait(lambda:state()['entries']==5)
 ipc('act','view','list');time.sleep(.25);ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.25)
 iid=ipc('retain','FileArea.row');assert int(iid)>0
 first=json.loads(ipc('dispatch','setFocus'));ipc('open','home');wait(lambda:state()['view']=='home');time.sleep(.25)
 second=json.loads(ipc('dispatch','Press'))
 observe('destroyed file delegate retained native peer',interfaceId=iid,before=first,after=second,refused=not second.get('interfaceFound'))
 ipc('open',root/'fixture');wait(lambda:state()['entries']==5);ipc('act','view','list');time.sleep(.2)
 ipc('retain','FileArea.row');before=state();ipc('mappedSet','false');time.sleep(.1);dispatch=json.loads(ipc('dispatch','Press'));raw=ipc('rawAttached');after=state()
 observe('hidden file row native and raw attached callback authority',dispatch=dispatch,rawReturned=raw,refused=before==after)
 ipc('mappedSet','true');time.sleep(.1);ipc('focus' ,'Explorer.keys');ipc('key',16777237,0);time.sleep(.25)
 before=ipc('locus');exported=ui().get('focusIdentity');debugBefore=json.loads(ipc("focusDebug"));samepid=p.pid
 # Actual watched-file reload of copied QML; never edit source evidence or original.
 host=B/'app/shell.qml';host.write_text(host.read_text()+'\n// offscreen focus reload probe\n');time.sleep(2.0)
 wait(lambda:json.loads(ipc('migrationStatus'))['ready'])
 observe('actual same PID focused file reload',before=before,after=ipc('locus'),exportedFocus=exported,debugBefore=debugBefore,debugAfter=json.loads(ipc('focusDebug')),loaded=json.loads(ipc('migrationStatus'))['initialization'],samePid=p.pid==samepid and p.poll() is None,requiredFocusPreserved=ipc('locus')==before)
 ipc('mappedSet','false');time.sleep(.2);before=ui();host.write_text(host.read_text()+'\n// hidden reload preservation probe\n');time.sleep(2.0)
 after=ui();loaded=json.loads(ipc('migrationStatus'))['initialization']
 observe('actual hidden same PID reload preserves logical focus token without mapping',beforeIdentity=before.get('focusIdentity'),afterIdentity=after.get('focusIdentity'),visible=after['visible'],backing=json.loads(ipc('focusDebug'))['backing'],loaded=loaded,refusedMapping=not after['visible'] and not loaded['backingVisible'],identityPreserved=before.get('focusIdentity')==after.get('focusIdentity'))
 ipc('mappedSet','true');ipc('open',root/'fixture');wait(lambda:state()['count']==5);ipc('act','view','list');ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.2)
 saved=ui().get('focusIdentity');ipc('deferFiles');host.write_text(host.read_text()+'\n// deferred-model newer-focus probe\n')
 wait(lambda:state()['count']==0 and json.loads(ipc('migrationStatus'))['initialization'].get('restoredFocus')==saved)
 ipc('focus','Sort');newer=ipc('locus');newerIdentity=ui().get('focusIdentity');ipc('releaseFiles');wait(lambda:state()['count']==5);time.sleep(.5)
 observe('deferred file restoration cannot override newer toolbar focus',savedIdentity=saved,newerLocus=newer,newerIdentity=newerIdentity,after=ipc('locus'),afterIdentity=ui().get('focusIdentity'),newerFocusPreserved=ipc('locus')==newer and ui().get('focusIdentity')==newerIdentity)
 ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.2);saved=ui().get('focusIdentity');ipc('deferFiles');host.write_text(host.read_text()+'\n// deferred-model newer-Tab-input probe\n')
 wait(lambda:state()['count']==0 and json.loads(ipc('migrationStatus'))['initialization'].get('restoredFocus')==saved)
 ipc('key',16777217,0);newer=ipc('locus');newerIdentity=ui().get('focusIdentity');ipc('releaseFiles');wait(lambda:state()['count']==5);time.sleep(.5)
 observe('deferred file restoration cannot override newer Tab input',savedIdentity=saved,newerLocus=newer,newerIdentity=newerIdentity,after=ipc('locus'),afterIdentity=ui().get('focusIdentity'),newerFocusPreserved=ipc('locus')==newer and ui().get('focusIdentity')==newerIdentity)
 ipc('focus','Explorer.keys');ipc('key',16777237,0);time.sleep(.2);saved=ui().get('focusIdentity');ipc('deferFiles');host.write_text(host.read_text()+'\n// deferred-model newer-modal probe\n')
 wait(lambda:state()['count']==0 and json.loads(ipc('migrationStatus'))['initialization'].get('restoredFocus')==saved)
 ipc('act','prompt','');newer=ipc('locus');ipc('releaseFiles');wait(lambda:state()['count']==5);time.sleep(.5)
 observe('deferred background restoration cannot override newer modal prompt',after=ipc('locus'),promptVisible=ui()['prompt']['visible'],newerFocusPreserved=ipc('locus')==newer and ui()['prompt']['visible'])
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
