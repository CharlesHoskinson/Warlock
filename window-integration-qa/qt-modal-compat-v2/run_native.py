#!/usr/bin/env python3
"""Root reviewed native slot only. Actual same-Qt-process WindowModal compatibility."""
from pathlib import Path
from logical_geometry import logical_output
import argparse,hashlib,json,os,shutil,signal,subprocess,time
import sys
QA=Path('/home/hoskinson/window-integration-qa/files-keyboard/routing-stage-v7/durable-reload-review2');sys.path.insert(0,str(QA));import observations as obs
B=Path(__file__).resolve().parent;HOME=Path.home();parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=Path,required=True);args=parser.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((B/'frozen-inputs.json').read_text())
 for row in manifest['files']:assert sha(Path(row['path']))==row['sha256'],row['path']
verify();frozen=(B/'frozen-inputs.json').read_bytes();O=args.attempt.resolve();assert O.parent==B and O.name.startswith('attempt-');os.umask(0o077);O.mkdir(mode=0o700)
report={'scope':'QtWidgets6.11.2 QDialog.open WindowModal, same QApplication independent peer, real native virtual-pointer callback delivery and installed family helper integration','checks':[],'preservation':{},'physicalHardwareProved':False,'inputSource':'Wayland virtual-pointer protocol','sourceManifestSHA256':sha(B/'frozen-inputs.json'),'result':'pending'}
process=pointer=None;before=None;identity={};epoch=0;held=False;log=(O/'fixture.log').open('w')
def check(name,value,**details):report['checks'].append({'name':name,'passed':bool(value),**details});assert value,name

def wait(fn,label,seconds=8):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  try:
   value=fn()
   if value:return value
  except (subprocess.CalledProcessError,ValueError,FileNotFoundError):pass
  time.sleep(.08)
 raise AssertionError(label)
def blocked():return [r for m in obs.data('layers').values() for level in m.get('levels',{}).values() for r in level if r.get('alpha',1)>0 and ('sudo-askpass' in r.get('namespace','') or 'hyprlock' in r.get('namespace',''))]
def state():return json.loads((O/'state.json').read_text())
def command(name):
 global epoch
 epoch+=1;temp=O/'command.new';temp.write_text(json.dumps({'epoch':epoch,'command':name}));os.replace(temp,O/'command.json');wait(lambda:state().get('commandEpoch')==epoch,'actual fixture command '+name)
 report.setdefault('commandAcknowledgements',[]).append({'command':name,'epoch':epoch})
def own(name):
 values=[r for r in obs.data('clients') if process and r['pid']==process.pid and r['title']=='Qt WindowModal QA '+name]
 if not values:return None
 assert len(values)==1;w=values[0];key=(w['address'],w['stableId'],w['pid'])
 if name not in identity:identity[name]=key
 else:assert key==identity[name],'captured native fixture identity reused'
 assert obs.start(process.pid)==report['fixtureStart'];return w

def families():return json.loads(obs.run('hyprctl','repl','print(hl.plugin.hyprbars.window_families())'))
def metadata(name):
 row=own(name);return next((r for r in families() if row and r['address']==row['address'] and r['stableId']==row['stableId'] and r['pid']==row['pid']),None)
def focus(name):
 w=own(name);assert w;obs.run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
def active(name):return obs.data('activewindow').get('stableId')==(own(name) or {}).get('stableId')
def arrange(name,x,y,width,height):
 assert x>=0 and y>=0 and x+width<=screen['logicalWidth'] and y+height<=screen['logicalHeight'],'Fixture rectangle must fit logical output'
 w=own(name);assert w
 if not w['floating']:obs.run('hyprctl','dispatch',f'hl.dsp.window.float({{action="set",window="address:{w["address"]}"}})')
 obs.run('hyprctl','dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{w["address"]}"}})');obs.run('hyprctl','dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
 wait(lambda:own(name)['at']==[x,y] and own(name)['size']==[width,height],name+' exact fixture geometry');time.sleep(.2)
def count(name):return state()['windows'].get(name,{}).get('clicks',0)
def click(name,point=None):
 global held
 assert not blocked(),'foreign input grab';w=own(name);assert w
 x,y=point or (w['at'][0]+w['size'][0]//2,w['at'][1]+w['size'][1]//2)
 assert 0<=x<screen['logicalWidth'] and 0<=y<screen['logicalHeight']
 trace={'target':name,'requestedLogical':[x,y],'logicalExtents':[screen['logicalWidth'],screen['logicalHeight']],'observationsBeforeButtons':[]}
 report.setdefault('pointerCoordinateTrace',[]).append(trace)
 # Motion is dispatched and independently observed before any button is sent.
 pointer.stdin.write(f'move {x} {y}\n');pointer.stdin.flush()
 def arrived():
  position=obs.data('cursorpos')
  if not trace['observationsBeforeButtons'] or trace['observationsBeforeButtons'][-1]!=position:trace['observationsBeforeButtons'].append(position)
  return position if abs(position['x']-x)<=.5 and abs(position['y']-y)<=.5 else None
 actual=wait(arrived,'actual logical IPC cursor arrives before '+name+' click',seconds=3)
 trace['actualIPCBeforeButtons']=actual;trace['deltaLogical']=[actual['x']-x,actual['y']-y]
 assert not blocked(),'foreign grab after cursor motion';assert own(name),'owned target lifetime remains mapped before click'
 pointer.stdin.write('button 272 1\nsleep 100\nbutton 272 0\nsleep 180\n');pointer.stdin.flush();held=True;time.sleep(.5);held=False
 report.setdefault('actualQtNativeSnapshots',[]).append({'target':name,'point':[x,y],'qtState':state(),'nativeActive':{k:obs.data('activewindow').get(k) for k in ('address','stableId','pid')},'families':families()})
def helper(operation,name):
 w=own(name);assert w;assert not blocked();obs.run(HOME/'.local/bin/hypr-windowctl',operation,w['address'],w['stableId'],str(w['pid']))
try:
 assert not blocked(),'foreign input grab';before=obs.capture(O/'before-main');screen=logical_output(obs.data('monitors'));report['monitorCoordinateContract']=screen
 env=dict(os.environ,QT_QPA_PLATFORM='wayland',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',HOME=str(O/'home'),XDG_CONFIG_HOME=str(O/'config'),XDG_CACHE_HOME=str(O/'cache'));env.pop('DISPLAY',None)
 for name in ('home','config','cache'):(O/name).mkdir()
 process=subprocess.Popen([str(B/'build/qt-window-modal-fixture'),str(O)],env=env,stdout=log,stderr=log,start_new_session=True);report['fixtureStart']=obs.start(process.pid)
 wait(lambda:own('owner') and own('peer'),'native Qt owner and same-app peer');wait(state,'public Qt fixture state')
 check('real public Qt6.11.2 native Wayland same-process owner/peer',state()['qtVersion']=='6.11.2' and state()['platform']=='wayland' and own('owner')['pid']==own('peer')['pid']==process.pid and not own('owner')['xwayland'] and not own('peer')['xwayland'])
 arrange('owner',100,250,460,300);arrange('peer',1000,300,460,300)
 pointer=subprocess.Popen([str(HOME/'.local/share/hypr-window-controls/qa/virtual-pointer'),str(screen['logicalWidth']),str(screen['logicalHeight'])],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL,stderr=log,start_new_session=True)
 command('open');wait(lambda:own('child'),'native QDialog child');arrange('child',260,310,320,180)
 child=metadata('child');parent=own('owner');check('Qt WindowModal agrees with actual native owner/modal metadata',state()['windows']['child']['modality']==1 and state()['windows']['child']['transientParentTitle']=='Qt WindowModal QA owner' and child is not None and child['modal'] and child['parent']==parent['address'] and child['parentStableId']==parent['stableId'],qt=state(),native=child)
 start=count('peer');click('peer');check('same QApplication independent peer stays actionable',count('peer')==start+1 and active('peer'))
 start=count('owner');click('owner',(own('owner')['at'][0]+25,own('owner')['at'][1]+own('owner')['size'][1]-25));check('window-modal owner body refuses callback and routes to child',count('owner')==start and active('child'))
 rect=own('owner')['at']+own('owner')['size'];focus('peer');wait(lambda:active('peer'),'independent peer before caption');click('owner',(own('owner')['at'][0]+80,own('owner')['at'][1]-12));check('window-modal owner caption routes child without geometry change',active('child') and own('owner')['at']+own('owner')['size']==rect and count('owner')==start)
 start=count('child');click('child');check('actual Qt dialog button receives native click',count('child')==start+1 and active('child'))
 command('nested');wait(lambda:own('nested'),'native nested QDialog');arrange('nested',330,350,240,140);nested=metadata('nested');child=own('child')
 check('nested Qt/native modal parent chain agrees',state()['windows']['nested']['modality']==1 and state()['windows']['nested']['transientParentTitle']=='Qt WindowModal QA child' and nested is not None and nested['modal'] and nested['parent']==child['address'] and nested['parentStableId']==child['stableId'],native=nested)
 focus('peer');wait(lambda:active('peer'),'independent peer before deepest owner route');start=count('owner');click('owner',(own('owner')['at'][0]+25,own('owner')['at'][1]+own('owner')['size'][1]-25));check('owner input routes deepest Qt modal',count('owner')==start and active('nested'))
 focus('peer');wait(lambda:active('peer'),'independent peer before intermediate route');start=count('child');click('child',(own('child')['at'][0]+15,own('child')['at'][1]+own('child')['size'][1]-20));check('intermediate dialog input refuses callback and routes deepest',count('child')==start and active('nested'))
 start=count('nested');click('nested');check('deepest Qt modal receives its real native callback',count('nested')==start+1 and active('nested'))
 start=count('peer');click('peer');check('same QApplication peer remains usable with nested WindowModal',count('peer')==start+1 and active('peer'))
 peer_before={k:own('peer').get(k) for k in ('address','stableId','pid','at','size','workspace','pinned','fullscreen','fullscreenClient')};helper('minimize','owner');wait(lambda:all(own(n)['workspace']['name']=='special:win-minimized' for n in ('owner','child','nested')),'Qt family minimizes')
 check('Qt family minimize excludes independent same-process peer',{k:own('peer').get(k) for k in peer_before}==peer_before)
 helper('restore','owner');wait(lambda:active('nested') and len({own(n)['workspace']['name'] for n in ('owner','child','nested')})==1,'Qt family deepest restore');check('Qt family restore retains deepest native modal focus',active('nested'))
 start=count('nested');click('nested');check('restored nested Qt dialog stays actionable',count('nested')==start+1 and active('nested'))
 command('closeNested');wait(lambda:not own('nested'),'nested dialog closes');focus('owner');start=count('child');click('child');check('normal nested destruction restores surviving dialog action/focus',count('child')==start+1 and active('child'))
 command('closeChild');wait(lambda:not own('child'),'child dialog closes');start=count('owner');click('owner');check('closing modal restores actual owner button action',count('owner')==start+1 and active('owner'))
 # A new QObject/native lifetime gets a new captured identity only after the
 # first lifetime is observed absent. Retain the old identity as evidence.
 report.setdefault('retiredIdentityLifetimes',[]).append({'role':'child','identity':identity.pop('child')})
 command('open');wait(lambda:own('child'),'fresh modal reopens');child=metadata('child');parent=own('owner')
 check('fresh Qt modal lifetime has valid captured parent',child is not None and child['modal'] and child['parent']==parent['address'] and child['parentStableId']==parent['stableId'])
 captured_destroyed={n:identity[n] for n in ('owner','child')};command('destroyOwner');wait(lambda:not own('owner') and not own('child'),'normal owner/dialog destruction')
 rows=families();check('destroying Qt owner destroys its own modal and removes native family metadata',not any((r['address'],r['stableId'],r['pid']) in captured_destroyed.values() for r in rows) and 'owner' not in state()['windows'] and 'child' not in state()['windows'],destroyedIdentities=captured_destroyed)
 start=count('peer');click('peer');check('independent same-process peer survives owner hierarchy destruction',count('peer')==start+1 and active('peer'))
except Exception as error:report['error']=repr(error)
finally:
 if pointer:
  try:
   if pointer.poll() is None:pointer.stdin.write('button 272 0\n');pointer.stdin.flush();pointer.stdin.close();pointer.wait(timeout=3)
  except (BrokenPipeError,subprocess.TimeoutExpired,OSError):
   if pointer.poll() is None:
    os.killpg(pointer.pid,signal.SIGTERM)
    try:pointer.wait(timeout=8)
    except subprocess.TimeoutExpired:report['forcedPointerKill']=True;os.killpg(pointer.pid,signal.SIGKILL);pointer.wait(timeout=4)
  report['pointerCleanup']={'pid':pointer.pid,'exitCode':pointer.poll(),'gone':not Path(f'/proc/{pointer.pid}').exists()}
 if process:
  report['fixtureIdentityLifetimes']=identity
  try:report['finalQtState']=state();report['qtEvents']=[json.loads(row) for row in (O/'events.jsonl').read_text().splitlines()]
  except Exception as error:report['finalStateError']=repr(error)
  if process.poll() is None:
   os.killpg(process.pid,signal.SIGTERM)
   try:process.wait(timeout=8)
   except subprocess.TimeoutExpired:report['forcedKill']=True;os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=4)
  report['fixtureCleanup']={'pid':process.pid,'exitCode':process.poll(),'gone':not Path(f'/proc/{process.pid}').exists()}
 if before:
  original=next((r for r in obs.data('clients') if r['address']==before['focus']['address'] and r['stableId']==before['focus']['stableId'] and r['pid']==before['focus']['pid']),None)
  if original:obs.run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{original["address"]}"}})')
  obs.run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={before["cursor"]["x"]},y={before["cursor"]["y"]}}})');time.sleep(.2)
  try:checks,details=obs.compare(before,O/'after-main');report['preservation'].update(checks);report['preservationDetails']=details
  except Exception as error:report['preservationError']=repr(error)
 report['preservation']['allOwnedNativeWindowsGone']=not any(process and r['pid']==process.pid for r in obs.data('clients'))
 report['preservation']['normalFixtureShutdown']=bool(process and process.poll() in (0,-signal.SIGTERM) and not report.get('forcedKill') and not report.get('forcedPointerKill'))
 report['preservation']['exactOwnedProcessesGone']=bool(process and report['fixtureCleanup']['gone'] and (not pointer or report['pointerCleanup']['gone']))
 report['preservation']['frozenManifestBytes']=(B/'frozen-inputs.json').read_bytes()==frozen
 try:verify();report['preservation']['allFrozenInputsExact']=True
 except Exception as error:report['preservation']['allFrozenInputsExact']=False;report['sourceError']=repr(error)
 log.close();report['result']='pass' if not report.get('error') and not report.get('preservationError') and all(c['passed'] for c in report['checks']) and all(report['preservation'].values()) else 'fail';obs.private_json(O/'report.json',report)
 print(json.dumps({'result':report['result'],'featureGates':len(report['checks']),'commandAcknowledgements':len(report.get('commandAcknowledgements',[])),'preservation':report['preservation'],'reportSHA256':sha(O/'report.json'),'error':report.get('error')}))
raise SystemExit(report['result']!='pass')
