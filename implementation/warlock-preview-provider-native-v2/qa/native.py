"""Protected serial native FD and actual WebKit pixels; not full S09."""
import hashlib,importlib.util,json,os,pathlib,resource,shutil,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((ROOT/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for p,h in pre['inputs'].items():assert sha(p)==h,p
runtime=REPO/'implementation/elm-preview-source-runtime-v506';spec=importlib.util.spec_from_file_location('exact_fd_private_host',runtime/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(ROOT/'qa'));from session_bus import isolate_session_host
from system_isolation import supply,validate
isolate_session_host(host)
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
private=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-preview-enrollment-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Typed provider-v5 own C bootstrap enrollment/scope against actual205/492/AQ155 plus retained504 probe campaign. Exact205/492 producer -> sealed descriptor -> native broker/GIO/421 callback -> actual470 compiled Elm picker, native WebKit snapshot source pixels and independent libpng, actual Elm acquire/release/receipt acknowledgements. Private popup view only, capture after actual frontend demand and exact native root commit context; no full production main-host integration or family/transform/color/S09 acceptance','checks':[],'pair':pre['pair']}
s=None;fixture=None;web=None;probe=None;loaded=False
def check(name,ok,**values):r['checks'].append({'name':name,'passed':bool(ok),**values});assert ok,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Original six-second fixture observation deadline')
def control(value):
 path=private/'fixture-control.json';temp=private/'fixture-control.tmp';temp.write_text(json.dumps(value));temp.chmod(0o600);temp.replace(path)
try:
 lua=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
 s=host.PrivateHyprSession(private,dict(os.environ),1600,1000,lua,mesa_vendor=True)
 with s:
  try:
   plugin=pre['pair']['plugin']['path'];check('exactFDProducerPluginLoaded',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory')
   fixture=s.host.launch('source',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(private/'fixture-control.json')],env=env);wait(lambda:len(s.data('clients'))==2);control({'op':'hide-peer'});wait(lambda:len(s.data('clients'))==1)
   # Native lifetime/incarnation must come from the owning authority. One hello
   # from this runner is insufficient for the distinct host PID: the actual C++
   # host independently authenticates/attaches its own grant before requesting FD.
   import socket,struct
   def observe(body):
    path=s.host.runtime/'hypr'/s.env['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
    before=host.original.socket_identity(path,s.host.runtime);child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert host.original.same_process(child)
    assert not path.parent.is_symlink() and not path.parent.parent.is_symlink()
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
     c.settimeout(3);c.connect(str(path));pid,uid,gid=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==child['pid'] and uid==os.getuid() and host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before;c.sendall(('elm_observe '+json.dumps(body)).encode());reply=bytearray()
     while True:
      chunk=c.recv(4096)
      if not chunk:break
      reply.extend(chunk);assert len(reply)<=65536
    assert host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before
    return json.loads(reply)
   attached=observe({'protocolVersion':3,'kind':'hello'});snapshot=observe({'protocolVersion':3,'kind':'scene-facts-request','binding':attached['binding'],'requestId':'1','minimumWatermark':'0'});subject=snapshot['facts']['windows'][0]['incarnation']
   requestId=1
   def request(kind,**fields):
    global requestId
    requestId+=1
    return observe({'protocolVersion':3,'kind':kind,'binding':attached['binding'],'requestId':str(requestId),**fields})
   def sourceScope():
    value=request('preview-capture-probe-scope-request',subjectIncarnation=subject)
    assert value['kind']=='preview-capture-probe-scope' and value['scope']['binding']==attached['binding'] and value['previewEligible'] is False
    return value['scope']
   check('sourceIncarnationNativeObserved',subject.isdecimal() and snapshot['facts']['windows'][0]['minimized'] is False)
   before=sourceScope();control({'op':'source-color','color':'blue'})
   blue=wait(lambda: (value if int(value['context']['content'])>int(before['context']['content']) else None) if (value:=sourceScope()) else None)
   control({'op':'source-color','color':'red'})
   red=wait(lambda: (value if int(value['context']['content'])>int(blue['context']['content']) else None) if (value:=sourceScope()) else None)
   check('actualRootSurfaceCommitsAdvanceWithoutCapture',int(before['context']['content'])<int(blue['context']['content'])<int(red['context']['content']),scopes=[before,blue,red])
   stale=[]
   for field in ['lifetime','incarnation','output','privacy','rendering','scene','content']:
    scope=sourceScope();context=dict(scope['context']);context[field]=str(int(context[field])+1)
    reply=request('preview-capture-probe-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(scope['now'])+2000000000),context=context)
    check('nativeStaleContextRefuses_'+field,reply.get('reason')=='preview-probe-context-stale',reply=reply,requested=context)
    absent=request('preview-capture-probe-state-request');check('staleContextNoPublishedProbe_'+field,absent.get('reason')=='preview-probe-unavailable',reply=absent)
    stale.append(field)
   check('allSevenRequestedNativeContextFieldsChecked',len(stale)==7)
   child=next(row for _,row in s.host.processes if row['name']=='hyprland');start=host.original.process(child['pid'])['start']
   enrollment=private/'provider-authority.json'
   enrollment.write_text(json.dumps({'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':child['pid'],'expected_start':int(start),'binary_sha256':pre['pair']['core']['sha256']}));enrollment.chmod(0o600)
   probe=s.host.launch('provider-enrollment',[pre['providerProbe'],str(enrollment),subject],env=env)
   probe.wait(timeout=8);check('providerOwnTypedNativeGrantNormalExit',probe.returncode==0)
   values=[json.loads(line) for line in (private/'provider-enrollment.log').read_text().splitlines() if line.startswith('{')]
   check('providerActualNativeEnrollmentAndScope',len(values)==1 and values[0]['passed'] and values[0]['checks']==5 and values[0]['previewEligible'] is False,result=values)
   check('providerGrantSeparateFromRunner',values[0]['binding']!=attached['binding'] and values[0]['providerPID']==probe.pid,providerBinding=values[0]['binding'],runnerBinding=attached['binding'])
   command=[pre['hostBinary'],str(child['pid']),start,str(s.host.runtime),s.env['HYPRLAND_INSTANCE_SIGNATURE'],pre['pair']['core']['sha256'],subject,pre['guiAssets']];web=s.host.launch('preview-host',command,env=env)
   # Host has original2s capture/read deadlines internally; bounded observation
   # allowance is8s for process startup, two actual loads and ordered local drain.
   web.wait(timeout=8);check('actualPreviewHostNormalExit',web.returncode==0)
   log=(private/'preview-host.log').read_text();rows=[json.loads(line) for line in log.splitlines() if line.startswith('{')];check('actualCompleteHostPixelReport',len(rows)==1 and rows[0]['passed'],output=rows)
   result=rows[0];check('actualElmAndNativeRenderedSourcePixels',result['captureAfterActualElmAcquire'] and result['nativeSourceContextMatched'] and result['libpngSourcePixels'] and result['webkitRenderedSourcePixels'] and result['actualElmPicker'] and result['renderedPixelChecks']==2 and result['actualAcquire']==1 and result['actualRelease']==1 and result['actualReceiptAcknowledgements']==2 and result['unregisteredViewDenied']==1 and result['ownedMappingDestroyed']==1 and result['productionFidelityAccepted'] is False,result=result)
   stopped=request('scene-facts-request',minimumWatermark='0');check('actualSourceStillMappedButMinimized',any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')) and any(w['incarnation']==subject and w['minimized'] is True for w in stopped['facts']['windows']))
   control({'op':'quit'});fixture.wait(timeout=5);check('sourceApplicationNormalExit',fixture.returncode==0);wait(lambda:not s.data('clients'))
   r['passed']=True
  finally:
   if probe and probe.poll() is None:s.host.stop(next(row for p,row in s.host.processes if p is probe),probe);probe.wait(timeout=5);check('providerProbeCleanupNormalExit',probe.returncode==0)
   if web and web.poll() is None:s.host.stop(next(row for p,row in s.host.processes if p is web),web);web.wait(timeout=5);check('previewHostCleanupNormalExit',web.returncode==0)
   if fixture and fixture.poll() is None:control({'op':'quit'});fixture.wait(timeout=5);check('sourceCleanupNormalExit',fixture.returncode==0)
   if loaded:wait(lambda:not s.data('clients'));check('clientsEmptyBeforeFDPluginUnload',not s.data('clients'));check('FDPluginUnloadsAfterConsumers',s.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
 r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes];check('allOwnedProcessesNormalExit',all(row['exitCode']==0 for row in r['ownedExitCodes']),exits=r['ownedExitCodes'])
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
 if s:r['privateHost']=s.host.evidence;r['cleanupPassed']=bool(s.host.evidence.get('runtimeGone') and not s.host.evidence.get('remainingDescendants') and not s.host.evidence.get('unexpectedInnerDescendants') and not s.host.evidence.get('cleanupErrors'))
 if private.exists():shutil.copytree(private,OUT/'private-evidence',symlinks=True)
 r['passed']=r['passed'] and r.get('cleanupPassed',False);r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not r['passed'])
