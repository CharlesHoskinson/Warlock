"""Native private Qt session only; host orchestration and main read-only preservation wrap it.

No import-time commands. No default/main compositor environment is used.
"""
from pathlib import Path
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime
import hashlib,json,os,signal,subprocess,time
from logical_geometry import logical_output
from private_desktop import PrivateDesktop
from private_target import verify_socket
from button_geometry import button_point,contains,geometry_key,layout_ready
from cursor_readiness import native_arrived,native_delta
from xcb_loader import native_loader_gate
B=Path(__file__).resolve().parent
HOME=Path('/home/hoskinson')

def run_session(private_env,output,main_env,host_evidence,target_guard):
 require_qa_scope();verify_runtime(Path(private_env['XDG_RUNTIME_DIR']))
 target_guard();socket_evidence=verify_socket(main_env,private_env,allow_x11=True)
 O=Path(output);assert O.is_absolute() and not O.exists();os.umask(0o077);O.mkdir(mode=0o700)
 obs=PrivateDesktop(private_env,target_guard)
 host_pid=host_evidence['compositorPID'];assert obs.start(host_pid)==host_evidence['compositorStart']
 config=Path(host_evidence['compositorConfig']);assert config.resolve().is_relative_to(Path(private_env['XDG_RUNTIME_DIR']).resolve())
 assert str(config).encode() in Path(f'/proc/{host_pid}/cmdline').read_bytes()
 report={'scope':'QtWidgets6.11.2 QDialog.open WindowModal, same QApplication independent peer, real native virtual-pointer callback delivery and installed family helper integration','checks':[],'preservation':{},'physicalHardwareProved':False,'inputSource':'Wayland virtual-pointer protocol','result':'pending','mainGUIWrites':False,'mainRestorationWrites':False,'privateSocketAuthority':socket_evidence,'hostEvidence':host_evidence,'x11ProtocolGates':[]}
 process=pointer=motion=None;identity={};epoch=0;held=False;log=(O/'fixture.log').open('w')
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
  nonlocal epoch
  epoch+=1;temp=O/'command.new';temp.write_text(json.dumps({'epoch':epoch,'command':name}));os.replace(temp,O/'command.json')
  if name=='quit':
   process.wait(timeout=8)
   events=[json.loads(row) for row in (O/'events.jsonl').read_text().splitlines()]
   assert process.returncode==0 and any(row.get('event')=='commandHandled' and row.get('command')=='quit' and row.get('epoch')==epoch for row in events),'normal exit and exact synchronous quit record required'
  else:wait(lambda:state().get('commandEpoch')==epoch,'actual fixture command '+name)
  report.setdefault('commandAcknowledgements',[]).append({'command':name,'epoch':epoch})
 def own(name):
  values=[r for r in obs.data('clients') if process and r['pid']==process.pid and r['title']=='Qt WindowModal QA '+name]
  if not values:return None
  assert len(values)==1;w=values[0];key=(w['address'],w['stableId'],w['pid'])
  if name not in identity:identity[name]=key
  else:assert key==identity[name],'captured native fixture identity reused'
  assert obs.start(process.pid)==report['fixtureStart'];return w
 
 def families():return json.loads(obs.run('hyprctl','repl','print(hl.plugin.hyprbars.window_families())'))
 def native_row(name):
  expected=own(name);assert expected
  snapshot=json.loads(obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.state())'))
  rows=[row for row in snapshot['windows'] if row is not None and all(row[k]==expected[k] for k in ('address','stableId','pid'))]
  assert len(rows)==1 and rows[0]['surfaceBox'] is not None,'Exact actual native surface identity required'
  return rows[0]
 def capture_button(name):
  trace={'target':name,'observations':[],'requiredConsecutive':2,'timeoutSeconds':8}
  report.setdefault('pairedLayoutReadiness',[]).append(trace)
  previous=None
  def paired():
   nonlocal previous
   widget=state()['windows'].get(name,{});native=native_row(name)
   sample={'qtClient':widget.get('geometryGlobal'),'layoutGeometry':widget.get('layoutGeometry'),'buttonClient':widget.get('buttonClient'),'nativeSurface':native,'ready':layout_ready(widget,native)}
   sample['ordinal']=len(trace['observations'])+1;sample['observedMonotonic']=time.monotonic();trace['observations'].append(sample)
   if not sample['ready']:previous=None;return None
   key=geometry_key(widget,native)
   stable=previous==key;previous=key
   if stable:
    trace['accepted']={'qt':widget,'native':native,'geometryKey':key,'consecutive':2}
    return widget,native
   return None
  return wait(paired,name+' configured Qt/native client and completed layout readiness')
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
  wait(lambda:own(name)['at']==[x,y] and own(name)['size']==[width,height],name+' exact fixture geometry');return capture_button(name)
 def count(name):return state()['windows'].get(name,{}).get('clicks',0)
 def click(name,point=None):
  nonlocal held
  assert not blocked(),'foreign input grab';w=own(name);assert w
  x,y=point or (w['at'][0]+w['size'][0]//2,w['at'][1]+w['size'][1]//2)
  assert 0<=x<screen['logicalWidth'] and 0<=y<screen['logicalHeight']
  trace={'target':name,'requestedLogical':[x,y],'logicalExtents':[screen['logicalWidth'],screen['logicalHeight']],'observationsBeforeButtons':[]}
  report.setdefault('pointerCoordinateTrace',[]).append(trace)
  # Motion is dispatched and actual native float position is observed before any button.
  # Integer cursorpos floors the same position; retain it only as a diagnostic.
  pointer.stdin.write(f'move {x} {y}\n');pointer.stdin.flush()
  def arrived():
   native=json.loads(obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.state())'))
   integer_ipc=obs.data('cursorpos')
   sample={'nativeFloat':native['cursor'],'integerIPC':integer_ipc,'deltaLogical':native_delta(native,[x,y]),'ordinal':len(trace['observationsBeforeButtons'])+1}
   trace['observationsBeforeButtons'].append(sample)
   return native if native_arrived(native,[x,y]) else None
  actual=wait(arrived,'actual native float cursor arrives before '+name+' click',seconds=3)
  trace['actualIPCBeforeButtons']=trace['observationsBeforeButtons'][-1]['integerIPC']
  trace['actualNativeFloatBeforeButtons']=actual['cursor'];trace['deltaLogical']=native_delta(actual,[x,y])
  trace['nativeReadOnlyBeforeButtons']=actual
  assert not blocked(),'foreign grab after cursor motion';assert own(name),'owned target lifetime remains mapped before click'
  pointer.stdin.write('button 272 1\nsleep 100\nbutton 272 0\nsleep 180\n');pointer.stdin.flush();held=True;time.sleep(.5);held=False
  report.setdefault('actualQtNativeSnapshots',[]).append({'target':name,'point':[x,y],'qtState':state(),'nativeActive':{k:obs.data('activewindow').get(k) for k in ('address','stableId','pid')},'families':families(),'nativeReadOnlyAfterButtons':json.loads(obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.state())')),'nativeButtonObservation':json.loads(obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.events())'))})
 def helper(operation,name):
  w=own(name);assert w;assert not blocked();obs.run(HOME/'.local/bin/hypr-windowctl',operation,w['address'],w['stableId'],str(w['pid']))
 try:
  assert not blocked(),'foreign input grab';screen=logical_output(obs.data('monitors'));report['monitorCoordinateContract']=screen
  env=dict(private_env,QT_QPA_PLATFORM='xcb',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',QT_NO_XDG_DESKTOP_PORTAL='1');env.pop('WAYLAND_SOCKET',None)
  process=subprocess.Popen([str(B/'build-v7/qt-window-modal-fixture'),str(O)],env=env,stdout=log,stderr=log,start_new_session=True);report['fixtureStart']=obs.start(process.pid)
  wait(lambda:own('owner') and own('peer'),'native Qt owner and same-app peer');wait(state,'public Qt fixture state')
  loader=native_loader_gate(process.pid);report['x11ProtocolGates'].append({'name':'actual owned X11 Qt process loads exact XCB/Qt6XcbQpa modules',**loader})
  check('real public Qt6.11.2 native X11 same-process owner/peer',state()['qtVersion']=='6.11.2' and state()['platform']=='xcb' and own('owner')['pid']==own('peer')['pid']==process.pid and own('owner')['xwayland'] and own('peer')['xwayland'])
  arrange('owner',100,250,460,300);arrange('peer',1000,300,460,300)
  pointer=subprocess.Popen([str(HOME/'.local/share/hypr-window-controls/qa/virtual-pointer'),str(screen['logicalWidth']),str(screen['logicalHeight'])],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL,stderr=log,start_new_session=True,env=private_env);report['pointerStart']=obs.start(pointer.pid)
  owner_button,owner_surface=capture_button('owner');owner_point=button_point(owner_button,owner_surface)
  baseline=count('owner');click('owner',owner_point)
  report['checks'][0]['ownerBaselineCallback']={'point':owner_point,'buttonClient':owner_button['buttonClient'],'nativeSurface':owner_surface,'before':baseline,'after':count('owner'),'passed':count('owner')==baseline+1}
  assert report['checks'][0]['ownerBaselineCallback']['passed'],'Actual owner button baseline callback required'
  command('open');wait(lambda:own('child'),'native QDialog child');arrange('child',260,310,320,180)
  child=metadata('child');parent=own('owner');check('Qt WindowModal agrees with actual native owner/modal metadata',state()['windows']['child']['modality']==1 and state()['windows']['child']['transientParentTitle']=='Qt WindowModal QA owner' and child is not None and child['modal'] and child['parent']==parent['address'] and child['parentStableId']==parent['stableId'],qt=state(),native=child)
  start=count('peer');click('peer');check('same QApplication independent peer stays actionable',count('peer')==start+1 and active('peer'))
  assert owner_point==button_point(state()['windows']['owner'],native_row('owner')) and not contains(native_row('child')['surfaceBox'],owner_point),'Reuse same actual owner button outside child surface'
  start=count('owner');click('owner',owner_point);check('window-modal owner body refuses callback and routes to child',count('owner')==start and active('child'),actualButtonPoint=owner_point,baselineVerified=True)
  rect=own('owner')['at']+own('owner')['size'];focus('peer');wait(lambda:active('peer'),'independent peer before caption');click('owner',(own('owner')['at'][0]+80,own('owner')['at'][1]-12));check('window-modal owner caption routes child without geometry change',active('child') and own('owner')['at']+own('owner')['size']==rect and count('owner')==start)
  child_button,child_surface=capture_button('child');child_point=button_point(child_button,child_surface);start=count('child');click('child',child_point);check('actual Qt dialog button receives native click',count('child')==start+1 and active('child'),actualButtonPoint=child_point)
  command('nested');wait(lambda:own('nested'),'native nested QDialog');arrange('nested',330,350,240,140);nested=metadata('nested');child=own('child')
  check('nested Qt/native modal parent chain agrees',state()['windows']['nested']['modality']==1 and state()['windows']['nested']['transientParentTitle']=='Qt WindowModal QA child' and nested is not None and nested['modal'] and nested['parent']==child['address'] and nested['parentStableId']==child['stableId'],native=nested)
  assert owner_point==button_point(state()['windows']['owner'],native_row('owner')) and not contains(native_row('nested')['surfaceBox'],owner_point),'Same owner button outside nested surface'
  focus('peer');wait(lambda:active('peer'),'independent peer before deepest owner route');start=count('owner');click('owner',owner_point);check('owner input routes deepest Qt modal',count('owner')==start and active('nested'),actualButtonPoint=owner_point)
  assert child_point==button_point(state()['windows']['child'],native_row('child')) and not contains(native_row('nested')['surfaceBox'],child_point),'Same tested child button outside nested surface'
  focus('peer');wait(lambda:active('peer'),'independent peer before intermediate route');start=count('child');click('child',child_point);check('intermediate dialog input refuses callback and routes deepest',count('child')==start and active('nested'),actualButtonPoint=child_point,baselineVerified=True)
  start=count('nested');click('nested');check('deepest Qt modal receives its real native callback',count('nested')==start+1 and active('nested'))
  start=count('peer');click('peer');check('same QApplication peer remains usable with nested WindowModal',count('peer')==start+1 and active('peer'))
  motion_root=Path(private_env['XDG_RUNTIME_DIR'])/'hypr-window-motion'/hashlib.sha256(private_env['HYPRLAND_INSTANCE_SIGNATURE'].encode()).hexdigest()[:20]
  assert not (motion_root/'daemon.pid').exists() and not (motion_root/'control.sock').exists(),'Do not reuse a pre-existing daemon'
  motion=subprocess.Popen(['python3',str(HOME/'.local/bin/hypr-window-motion'),'daemon'],env=private_env,stdout=log,stderr=log,start_new_session=True);report['motionStart']=obs.start(motion.pid)
  wait(lambda:(motion_root/'daemon.pid').exists() and (motion_root/'daemon.pid').read_text().strip()==str(motion.pid) and (motion_root/'control.sock').exists(),'exact owned private motion daemon')
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
  def finish_owned(label,owned,captured_start,normal_stop):
   result={'pid':owned.pid,'start':captured_start,'normalStopAttempted':False}
   try:
    if owned.poll() is None:
     assert obs.start(owned.pid)==captured_start and os.getpgid(owned.pid)==owned.pid,'exact owned process group/start required'
     result['normalStopAttempted']=True;normal_stop();owned.wait(timeout=8)
   except Exception as error:
    result['normalStopError']=repr(error)
    if owned.poll() is None:
     try:
      assert obs.start(owned.pid)==captured_start and os.getpgid(owned.pid)==owned.pid,'fallback owned identity required'
      result['forcedTermination']=True;os.killpg(owned.pid,signal.SIGTERM)
      try:owned.wait(timeout=5)
      except subprocess.TimeoutExpired:
       assert obs.start(owned.pid)==captured_start and os.getpgid(owned.pid)==owned.pid
       result['forcedKill']=True;os.killpg(owned.pid,signal.SIGKILL);owned.wait(timeout=4)
     except Exception as cleanup_error:result['fallbackError']=repr(cleanup_error)
   result.update(exitCode=owned.poll(),gone=not Path(f'/proc/{owned.pid}').exists())
   report[label+'Cleanup']=result
  if pointer:
   def release_pointer():
    pointer.stdin.write('button 272 0\n');pointer.stdin.flush();pointer.stdin.close()
   finish_owned('pointer',pointer,report['pointerStart'],release_pointer)
  if motion:
   finish_owned('motion',motion,report['motionStart'],lambda:obs.run('python3',HOME/'.local/bin/hypr-window-motion','stop'))
  if process:
   report['fixtureIdentityLifetimes']=identity
   try:report['finalQtState']=state()
   except Exception as error:report['finalStateError']=repr(error)
   finish_owned('fixture',process,report['fixtureStart'],lambda:command('quit'))
   try:report['qtEvents']=[json.loads(row) for row in (O/'events.jsonl').read_text().splitlines()]
   except Exception as error:report['finalEventError']=repr(error)
  try:report['preservation']['allOwnedNativeWindowsGone']=not any(process and r['pid']==process.pid for r in obs.data('clients'))
  except Exception as error:report['privateCleanupObservationError']=repr(error);report['preservation']['allOwnedNativeWindowsGone']=False
  cleanups=[report[label+'Cleanup'] for label,obj in [('pointer',pointer),('motion',motion),('fixture',process)] if obj]
  report['preservation']['normalOwnedShutdown']=bool(process and all(row['exitCode']==0 and row['gone'] and not row.get('normalStopError') and not row.get('forcedTermination') for row in cleanups))
  report['preservation']['exactOwnedProcessesGone']=bool(process and all(row['gone'] for row in cleanups))
  log.close();report['result']='pass' if not report.get('error') and all(c['passed'] for c in report['checks']) and all(report['preservation'].values()) else 'fail';obs.private_json(O/'report.json',report)
 return report
