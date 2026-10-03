"""Actual private Browser+Files input flow. No imports launch anything."""
from pathlib import Path
import hashlib,json,os,secrets,signal,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime
from private_desktop import PrivateDesktop
from logical_geometry import logical_output
from cursor_readiness import native_arrived,native_delta
from cdp_readonly import ReadOnlyPipe,TargetNotReady,DOMNotReady
from browser_exec import BINARY
from process_evidence import snapshot as process_snapshot,renderer as process_renderer
from runtime_inputs import mapping_authority,exact_files_instance
B=Path(__file__).resolve().parent
APP=B/'files-app';POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run_session(private_env,output,main_env,host_evidence,target_guard):
 require_qa_scope();runtime=verify_runtime(Path(private_env['XDG_RUNTIME_DIR']));target_guard()
 out=Path(output);out.mkdir(mode=0o700);obs=PrivateDesktop(private_env,target_guard)
 screen=logical_output(obs.data('monitors'));assert screen['logicalWidth']==1600 and screen['logicalHeight']==1000
 report={'result':'pending','checks':[],'commandAcknowledgements':[],'preservation':{},'inputSource':'Wayland virtual-pointer and virtual-keyboard protocols','physicalHardwareProved':False,'mainGUIWrites':False,'mainRestorationWrites':False,'copiedHostTimingPerturbation':True}
 browser=files=pointer=None;cdp=None;session_id=None;identities={};registered={};log=(out/'clients.log').open('w');owned_roots={};pointer_held=False
 def start(pid):return obs.start(pid)
 def row(pid):
  raw=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
  return {'pid':pid,'start':raw[19],'ppid':int(raw[1]),'pgid':int(raw[2])}
 def same(r):
  try:return start(r['pid'])==r['start']
  except OSError:return False
 def register_tree():
  target_guard();allrows={}
  for path in Path('/proc').glob('[0-9]*'):
   try:
    if path.stat().st_uid==os.getuid():allrows[int(path.name)]=row(int(path.name))
   except OSError:pass
  known={r['pid'] for r in [*owned_roots.values(),*registered.values()] if same(r)}
  for _ in range(len(allrows)+1):
   extra={p for p,r in allrows.items() if r['ppid'] in known}-known
   if not extra:break
   known.update(extra)
  for pid in known:
   if pid in allrows:registered[(pid,allrows[pid]['start'])]=allrows[pid]
  return [r for r in registered.values() if same(r)]
 def track(name,p):owned_roots[name]=row(p.pid);register_tree();report.setdefault('processRoots',{})[name]=owned_roots[name]
 def wait(fn,label,seconds=10):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   register_tree()
   try:
    value=fn()
    if value:return value
   except (ValueError,FileNotFoundError,subprocess.CalledProcessError,TargetNotReady,DOMNotReady):pass
   time.sleep(.08)
  raise RuntimeError('Bounded actual observation timed out:'+label)
 def check(name,value,**details):report['checks'].append({'name':name,'passed':bool(value),**details});assert value,name
 def native():return json.loads(obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.state())'))
 def own(name):
  process=browser if name=='browser' else files
  if not process:return None
  found=[r for r in obs.data('clients') if r['pid']==process.pid]
  if not found:return None
  assert len(found)==1,'One exact owned app window required:'+name
  value=found[0];identity={k:value[k] for k in ('address','stableId','pid')}
  if name in identities:assert identity==identities[name],'Owned window lifetime changed unexpectedly'
  else:identities[name]=identity
  assert same(owned_roots[name]);return value
 def surface(name):
  w=own(name);assert w
  matched=[r for r in native()['windows'] if r and all(r.get(k)==w[k] for k in ('address','stableId','pid'))]
  assert len(matched)==1 and matched[0]['surfaceBox'];return matched[0]
 def active(name):
  target=own(name);return bool(target) and all(obs.data('activewindow').get(k)==target[k] for k in ('address','stableId','pid'))
 def arrange(name,rect):
  x,y,width,height=rect;assert 0<=x and 0<=y and x+width<=1600 and y+height<=1000
  w=own(name);assert w
  if not w['floating']:obs.run('hyprctl','dispatch',f'hl.dsp.window.float({{action="set",window="address:{w["address"]}"}})')
  obs.run('hyprctl','dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{w["address"]}"}})')
  obs.run('hyprctl','dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
  wait(lambda:own(name)['at']==[x,y] and own(name)['size']==[width,height],name+' exact private placement')
 def ipc(method):
  target_guard();assert files and same(owned_roots['files'])
  instances=json.loads(subprocess.check_output(['/usr/bin/qs','list','-a','-j'],env=env,text=True,timeout=5))
  instance=exact_files_instance(instances,files.pid,APP)
  prior=report.setdefault('actualFilesInstance',instance);assert instance['id']==prior['id'],'Captured Files instance changed'
  return json.loads(subprocess.check_output(['/usr/bin/qs','ipc','--pid',str(files.pid),'call','files',method],env=env,text=True,timeout=8))
 def actual_app_bus(process,name):
  identity=owned_roots[name];assert same(identity)
  raw=Path(f'/proc/{process.pid}/environ').read_bytes();values=dict(x.split(b'=',1) for x in raw.split(b'\0') if b'=' in x)
  expected=('unix:path='+str(runtime/'bus')).encode()
  assert values.get(b'DBUS_SESSION_BUS_ADDRESS')==expected and values.get(b'DBUS_SYSTEM_BUS_ADDRESS')==expected and values.get(b'GIO_USE_VFS')==b'local','Actual app bus/VFS environment authority mismatch'
  assert same(identity)
  report.setdefault('actualAppBusAuthority',{})[name]={'identity':identity,'sessionBus':expected.decode(),'systemBus':expected.decode(),'gioVfs':'local','source':'Read actual owned root /proc/environ before input'}
 def dom():
  value=cdp.dom(session_id);assert value['url']==(B/'compose.html').as_uri() and value['title']=='Private local draft QA';return value
 def capture_processes(label):
  # Capture all owned processes before filtering, so a failed role/sandbox gate
  # retains the exact kernel bytes/status and every permission/race error.
  roots=register_tree();batch={'phase':label,'monotonicNs':time.monotonic_ns(),'processes':[process_snapshot(r,same) for r in roots]}
  report.setdefault('ownedProcessEvidence',[]).append(batch)
  evidence_path=out/'owned-process-evidence.json'
  PrivateDesktop.private_json(evidence_path,report['ownedProcessEvidence'])
  report['ownedProcessEvidencePath']=str(evidence_path)
  return batch['processes']
 def sandbox_state():
  samples=capture_processes('renderer enumeration before role filter');rows=[]
  for sample in samples:
   value=process_renderer(sample,os.getuid(),launch['network']['parentNetNamespace'])
   if value:rows.append(value)
  return rows
 def mapped_inputs(label):
  frozen=json.loads((B/'frozen-inputs.json').read_text());expected={str(Path(r['path']).resolve()):r for r in frozen['files']}
  evidence={'phase':label,'processes':[]};roots=register_tree()+[{'pid':host_evidence['compositorPID'],'start':host_evidence['compositorStart'],'classification':'Read-only owned compositor mapping observation; not an app cleanup target'}]
  for identity in roots:
   if not same(identity):continue
   try:
    raw=Path(f'/proc/{identity["pid"]}/maps').read_text()
    authority=mapping_authority(raw,expected,runtime,[profile,temporary,Path(private_env['XDG_CACHE_HOME']),Path(private_env['XDG_DATA_HOME'])/'quickshell'])
    assert same(identity),'Owned mapping process lifetime changed'
   except FileNotFoundError:
    if same(identity):raise
    evidence['processes'].append({'identity':identity,'exitedDuringObservation':True});continue
   evidence['processes'].append({'identity':identity,'maps':raw,**authority})
  report.setdefault('actualMappedInputs',[]).append(evidence)
 def clear_input(s):
  return not any(s[k] for k in ('sessionLocked','exclusiveLayers','constrained','heldButtons','seatGrab','captured','dnd','dragTarget')) and s['clickMode']==0
 def click(name,point):
  nonlocal pointer_held
  target_guard();assert own(name);assert clear_input(native()),'Existing private capture/grab refuses click'
  assert 0<=point[0]<1600 and 0<=point[1]<1000
  trace={'target':name,'requestedLogical':point,'observations':[]};report.setdefault('pointerCoordinateTrace',[]).append(trace)
  pointer.stdin.write(f'move {point[0]} {point[1]}\n');pointer.stdin.flush()
  def arrived():
   s=native();trace['observations'].append({'float':s['cursor'],'delta':native_delta(s,point),'integerIPC':obs.data('cursorpos')})
   return s if native_arrived(s,point) else None
  before=wait(arrived,'real native float cursor before buttons',3);assert clear_input(before)
  if name=='files':assert not active('files'),'Pointer motion must not pre-focus exposed Files before real press'
  expected=own(name);assert before['hitOwner'] and all(before['hitOwner'][k]==expected[k] for k in ('address','stableId','pid')),'Actual exposed hit must be exact intended app'
  pointer_held=True;pointer.stdin.write('button 272 1\nsleep 100\nbutton 272 0\nsleep 150\n');pointer.stdin.flush();time.sleep(.4);pointer_held=False
  wait(lambda:active(name),'actual app native focus after click');after=native();assert clear_input(after),'No stuck capture/held gesture after genuine release'
  trace.update(before=before,after=after)
 def type_text(text):
  target_guard();assert active('browser'),'Typing authority is actual owned focused browser'
  result=subprocess.run(['/usr/bin/wtype','-d','20','--',text],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)
  report['commandAcknowledgements'].append({'virtualKeyboardReturncode':result.returncode,'stderr':result.stderr,'textSHA256':hashlib.sha256(text.encode()).hexdigest()});assert result.returncode==0
 def browser_rect():
  previous=None;trace=[];report.setdefault('browserLayoutPairs',[]).append(trace)
  def paired():
   nonlocal previous
   d=dom();s=surface('browser')['surfaceBox'];key=(tuple(s),tuple(d['inner']),tuple(d['outer']),tuple(d['rect']),d['ratio']);valid=d['ratio']==1 and d['outer']==s[2:] and 0<d['inner'][1]<=s[3] and d['inner'][0]==s[2]
   trace.append({'dom':d,'surfaceBox':s,'ready':valid})
   stable=valid and key==previous;previous=key if valid else None
   if stable:
    r=d['rect'];return [s[0]+r[0]+10,s[1]+s[3]-d['inner'][1]+r[1]+10]
  return wait(paired,'browser actual stable viewport/native layout pairing')
 def files_point():
  previous=None;trace=[];report.setdefault('filesLayoutPairs',[]).append(trace)
  def paired():
   nonlocal previous
   info=ipc('qaButtons');s=surface('files')['surfaceBox'];name='Show list' if info['viewMode']=='grid' else 'Show grid'
   peers=[r for r in info['buttons'] if r['name']==name and r['visible'] and r['enabled'] and r['enabled2']]
   key=(tuple(s),tuple(info['client']),json.dumps(peers,sort_keys=True));valid=len(peers)==1 and info['client']==s[2:] and info['pid']==files.pid and info['visible'] and info['backingVisible']
   trace.append({'qml':info,'surfaceBox':s,'ready':valid});stable=valid and key==previous;previous=key if valid else None
   if stable:
    r=peers[0]['rect'];point=[s[0]+r[0]+r[2]/2,s[1]+r[1]+r[3]/2];b=surface('browser')['surfaceBox']
    assert not (b[0]<=point[0]<b[0]+b[2] and b[1]<=point[1]<b[1]+b[3]),'Files actual button must be exposed outside browser'
    return point,info,peers[0]
  return wait(paired,'real Files callback button coherent/exposed/native allocation')
 try:
  profile=runtime/'browser-profile';profile.mkdir(mode=0o700)
  temporary=runtime/'browser-tmp';temporary.mkdir(mode=0o700)
  env=dict(private_env,TMPDIR=str(temporary),DBUS_SYSTEM_BUS_ADDRESS=private_env['DBUS_SESSION_BUS_ADDRESS'],GIO_USE_VFS='local',QT_NO_XDG_DESKTOP_PORTAL='1',QT_QPA_PLATFORM='wayland',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion');env.pop('DISPLAY',None)
  assert env['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus') and env['DBUS_SYSTEM_BUS_ADDRESS']==env['DBUS_SESSION_BUS_ADDRESS']
  report['privateAppBusSelectors']={k:env[k] for k in ('DBUS_SESSION_BUS_ADDRESS','DBUS_SYSTEM_BUS_ADDRESS','GIO_USE_VFS')}
  reader_fd,parent_write=os.pipe();parent_read,writer_fd=os.pipe()
  cmd=['/usr/bin/unshare','--user','--map-current-user','--net','--',sys.executable,str(B/'browser_exec.py'),'--runtime',str(runtime),'--profile',str(profile),'--evidence',str(out/'browser-exec.json'),'--parent-netns',os.readlink('/proc/self/ns/net'),'--uid',str(os.getuid()),'--read-fd',str(reader_fd),'--write-fd',str(writer_fd),'--binary-sha',sha(BINARY),'--compositor-pid',str(host_evidence['compositorPID']),'--compositor-start',str(host_evidence['compositorStart']),'--signature',private_env['HYPRLAND_INSTANCE_SIGNATURE']]
  browser=subprocess.Popen(cmd,env=env,pass_fds=(reader_fd,writer_fd),stdout=log,stderr=log,start_new_session=True);os.close(reader_fd);os.close(writer_fd);track('browser',browser);cdp=ReadOnlyPipe(parent_write,parent_read)
  launch=wait(lambda:json.loads((out/'browser-exec.json').read_text()),'actual user+netns browser pre-exec guard')
  check('browser exact owned namespace/profile and sandboxed launch',launch['pid']==browser.pid and launch['start']==start(browser.pid) and launch['network']['parentNetNamespace']!=launch['network']['netNamespace'] and launch['network']['interfaces']==['lo'] and launch['sandboxEnabled'],evidence=launch)
  capture_processes('browser pre-exec guard accepted, before CDP version')
  report['actualBrowserVersion']=cdp.request('Browser.getVersion')
  actual_app_bus(browser,'browser')
  target,session_id=wait(lambda:cdp.attach((B/'compose.html').as_uri()),'one exact local browser page');report['actualPageTarget']=target
  sandboxes=wait(lambda:sandbox_state(),'actual owned renderer sandbox process')
  check('actual owned renderer seccomp and network isolation',all(r['seccomp']=='2' and r['noNewPrivileges']=='1' and r['netNamespace']!=launch['network']['parentNetNamespace'] for r in sandboxes),renderers=sandboxes,scope='Actual owned renderer filter/no-new-privileges; not full Chromium security certification')
  wait(lambda:own('browser'),'actual private Brave Wayland window');check('real private browser native identity and local DOM',not own('browser')['xwayland'] and dom()['value']=='',nativeIdentity=identities['browser'])
  files_state=runtime/'files-state';files_state.mkdir(mode=0o700);fixture=runtime/'files-fixture';fixture.mkdir(mode=0o700);(fixture/'owned.txt').write_text('Private fixture only\n')
  fenv=dict(env,FILES_WIDGET='0',FILES_STATE=str(files_state),FILES_OPEN=str(fixture),FILES_DRYRUN='0')
  files=subprocess.Popen(['/usr/bin/qs','-p',str(APP)],env=fenv,stdout=log,stderr=log,start_new_session=True);track('files',files)
  wait(lambda:own('files'),'actual copied Files native client');actual_app_bus(files,'files');wait(lambda:ipc('migrationStatus')['ready'],'copied real Files initialized')
  check('real copied Files exact process and sandbox cwd',ipc('state')['cwd']==str(fixture) and not own('files')['xwayland'],nativeIdentity=identities['files'],state=ipc('state'))
  arrange('browser',[140,100,930,700]);arrange('files',[760,220,700,550]);mapped_inputs('both actual clients initialized')
  pointer=subprocess.Popen([str(POINTER),'1600','1000'],env=env,stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL,stderr=log,start_new_session=True);track('pointer',pointer)
  textarea_point=browser_rect();click('browser',textarea_point);wait(lambda:dom()['active']=='draft','actual textarea focus from virtual pointer')
  text='private-draft-'+out.parent.name+'-'+secrets.token_hex(4);type_text(text);first=wait(lambda:dom() if dom()['value']==text else None,'actual trusted draft bytes')
  assert first['active']=='draft' and first['selection']==[len(text)]*2
  target_guard();assert active('browser')
  caret_command=subprocess.run(['/usr/bin/wtype','-d','20','-k','Left','-k','Left','-k','Left'],env=env,capture_output=True,text=True,timeout=8)
  report['commandAcknowledgements'].append({'nativeCaretKeysReturncode':caret_command.returncode,'stderr':caret_command.stderr});assert caret_command.returncode==0
  interior=wait(lambda:dom() if dom()['selection']==[len(text)-3]*2 else None,'actual interior retained textarea caret')
  check('actual trusted browser edit and interior caret native focus',interior['active']=='draft' and interior['value']==text and any(r['type']=='input' and r['trusted'] and r['target']=='draft' for r in interior['events']) and sum(r['type']=='keydown' and r['trusted'] and r['target']=='draft' for r in interior['events'])>=3,initialDom=first,interiorDom=interior)
  for iteration in range(2):
   if iteration:
    before=dom();target_guard();reload_reply=obs.run('hyprctl','reload');assert reload_reply=='ok';report['commandAcknowledgements'].append({'privateReloadReply':reload_reply,'semantics':'Official reloadRequest synchronously calls Config::mgr()->reload() before replying ok; native input/focus guard remains separately observed.'})
    wait(lambda:not obs.run('hyprctl','configerrors').strip(),'private reload config readiness');mapped_inputs('after genuine private reload')
    check('genuine private reload retains exact app identities/draft',own('browser') and own('files') and dom()['value']==before['value'] and dom()['selection']==before['selection'] and clear_input(native()),before=before,after=dom())
   point,info,peer=files_point();prior=dom();click('files',point)
   changed=wait(lambda:ipc('qaButtons') if ipc('qaButtons')['viewMode']!=info['viewMode'] else None,'actual Files view callback')
   check('actual exposed Files click raises and invokes original callback '+str(iteration),active('files') and len(changed['clicks'])==len(info['clicks'])+1 and changed['clicks'][-1]['identity']==peer['identity'] and changed['clicks'][-1]['button']==1 and changed['clicks'][-1]['modifiers']==0,before=info,after=changed,actualPoint=point,native=own('files'))
   after=dom();check('browser draft and caret unchanged under Files focus '+str(iteration),after['value']==prior['value'] and after['selection']==prior['selection'],before=prior,after=after)
   bw=own('browser');caption=[bw['at'][0]+90,bw['at'][1]-12];click('browser',caption)
   returned=dom();check('actual browser caption focus retains draft caret '+str(iteration),returned['value']==prior['value'] and returned['selection']==prior['selection'] and returned['active']=='draft',dom=returned)
   more='-continued'+str(iteration);old_inputs=len([r for r in returned['events'] if r['type']=='input' and r['trusted']]);type_text(more)
   expected=prior['value'][:prior['selection'][0]]+more+prior['value'][prior['selection'][1]:]
   final=wait(lambda:dom() if dom()['value']==expected else None,'actual continuation at retained caret')
   check('real trusted continuation at retained caret '+str(iteration),len([r for r in final['events'] if r['type']=='input' and r['trusted']])>old_inputs and final['selection']==[prior['selection'][0]+len(more)]*2,dom=final)
  mapped_inputs('after all actual editing/callback tests')
  check('no form submission or external page targets',all(r['url']==(B/'compose.html').as_uri() for r in cdp.request('Target.getTargets')['targetInfos'] if r['type']=='page') and dom()['clicks']==0,targets=cdp.request('Target.getTargets'))
 except Exception as error:report['error']=repr(error)
 finally:
  try:capture_processes('before normal client close')
  except Exception as error:report['finalProcessEvidenceError']=repr(error)
  # EOF is the producer's genuine release path, before app/plugin teardown.
  if pointer:
   try:
    pointer.stdin.close();pointer.wait(timeout=5);report['preservation']['pointerNormalExit']=pointer.returncode==0
   except Exception as error:report['pointerCloseError']=repr(error);report['preservation']['pointerNormalExit']=False
  if files:
   try:
    if files.poll() is None:
     target_guard();assert same(owned_roots['files']);instances=json.loads(subprocess.check_output(['/usr/bin/qs','list','-a','-j'],env=env,text=True,timeout=5));exact_files_instance(instances,files.pid,APP)
     reply=subprocess.run(['/usr/bin/qs','kill','--pid',str(files.pid)],env=env,capture_output=True,text=True,timeout=8);assert reply.returncode==0,reply.stderr
    files.wait(timeout=8);report['preservation']['filesNormalExit']=files.returncode==0
   except Exception as error:report['filesCloseError']=repr(error);report['preservation']['filesNormalExit']=False
  if browser:
   try:
    if browser.poll() is None:
     assert same(owned_roots['browser']);register_tree();cdp.request('Browser.close')
    browser.wait(timeout=10);report['preservation']['browserNormalExit']=browser.returncode==0
   except Exception as error:report['browserCloseError']=repr(error);report['preservation']['browserNormalExit']=False
  if cdp:report['commandAcknowledgements']+=cdp.acks;cdp.close_fds()
  try:wait(lambda:not register_tree(),'all captured owned app descendants exit normally',4);report['preservation']['allRegisteredDescendantsGoneNormally']=True
  except Exception as error:report['descendantCloseError']=repr(error);report['preservation']['allRegisteredDescendantsGoneNormally']=False
  surviving=register_tree();report['survivorsBeforeFallback']=surviving
  # Force cleanup only exact registered PID/start; failure evidence remains failed.
  for r in reversed(surviving):
   if same(r):
    try:os.kill(r['pid'],signal.SIGTERM)
    except ProcessLookupError:pass
  time.sleep(.1)
  for r in reversed(surviving):
   if same(r):
    try:os.kill(r['pid'],signal.SIGKILL)
    except ProcessLookupError:pass
  for p in (pointer,files,browser):
   if p:
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:pass
  try:capture_processes('after client cleanup')
  except Exception as error:report['cleanupProcessEvidenceError']=repr(error)
  report['registeredDescendants']=list(registered.values());report['remainingOwnedDescendants']=register_tree();report['preservation']['allOwnedFixturesGone']=not report['remainingOwnedDescendants']
  report['preservation']['noForcedCleanup']=not surviving
  report['preservation']['processEvidenceNormallyRecorded']=not report.get('finalProcessEvidenceError') and not report.get('cleanupProcessEvidenceError') and bool(report.get('ownedProcessEvidencePath'))
  try:report['preservation']['noPrivateCaptureAfterClients']=clear_input(native()) and not obs.data('clients')
  except Exception as error:report['postClientNativeError']=repr(error);report['preservation']['noPrivateCaptureAfterClients']=False
  log.close();log_path=out/'clients.log';log_path.chmod(0o600)
  report['result']='pass' if not report.get('error') and len(report['checks'])==15 and all(r['passed'] for r in report['checks']) and all(report['preservation'].values()) else 'fail'
  PrivateDesktop.private_json(out/'report.json',report)
 return report
