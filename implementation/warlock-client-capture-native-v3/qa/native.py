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
private=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-client-capture-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Owning205/derived492/AQ155 isolated public MAIN client tree, source commits/stale contexts, three independent client PNG color samples under overlapping unrelated same-process peer, distinct FD kind and physical export/producer retirement. No WebKit, eligible production provider, family/color/output/minimized/resource/S09 or full release acceptance','checks':[],'pair':pre['pair']}
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
    value=request('preview-client-scope-request',subjectIncarnation=subject)
    assert value['kind']=='preview-client-scope' and value['scope']['binding']==attached['binding'] and value['previewEligible'] is False and value['scopeKind']=='isolated-root-client-unqualified'
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
    reply=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(scope['now'])+2000000000),context=context)
    check('nativeStaleContextRefuses_'+field,reply.get('reason')=='preview-client-context-stale',reply=reply,requested=context)
    absent=request('preview-client-state-request');check('staleContextNoPublishedProbe_'+field,absent.get('reason')=='preview-client-unavailable',reply=absent)
    stale.append(field)
   check('allSevenRequestedNativeContextFieldsChecked',len(stale)==7)
   clients=s.data('clients');source=next(w for w in clients if w['title']=='ELM-AUTHORITY-FIXTURE');sourceAddress=source['address']
   if not source['floating']:check('sourceFloatingForOverlap',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='address:"+sourceAddress+"'})").strip()=='ok')
   check('sourcePositionControlled',s.ctl('dispatch',"hl.dsp.window.move({x=80,y=80,window='address:"+sourceAddress+"'})").strip()=='ok')
   control({'op':'show-peer'});wait(lambda:len(s.data('clients'))==2)
   peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER');peerAddress=peer['address']
   if not peer['floating']:check('peerFloatingForOverlap',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='address:"+peerAddress+"'})").strip()=='ok')
   check('peerPositionControlled',s.ctl('dispatch',"hl.dsp.window.move({x=80,y=80,window='address:"+peerAddress+"'})").strip()=='ok')
   check('peerRaisedOverSource',s.ctl('dispatch',"hl.dsp.focus({window='address:"+peerAddress+"'})").strip()=='ok')
   clients=wait(lambda: (rows if all(w['at']==[80,80] for w in rows) else None) if len(rows:=s.data('clients'))==2 else None)
   check('actualUnrelatedSameProcessPeerOverlapsSource',len({w['pid'] for w in clients})==1 and all(w['at']==[80,80] for w in clients) and s.data('activewindow')['address']==peerAddress,clients=clients)
   baseline=[{'address':w['address'],'at':w['at'],'size':w['size'],'floating':w['floating']} for w in sorted(clients,key=lambda w:w['address'])]
   import array,fcntl,mmap,struct,subprocess
   magic=0x454c4d5046443031
   lifetime,session,frontend=[int(attached['binding'][k]) for k in ['lifetime','session','frontend']]
   def exchange(op,capture,transfer=0):
    query=[magic,1,op,lifetime,session,frontend,2000+op,int(capture),int(subject),int(transfer)]
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child)
     assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(26*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==26*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC)
     words=struct.unpack('!26Q',data);assert words[0]==magic and words[1]==1 and words[2]==0 and words[3:6]==(lifetime,session,frontend) and words[6]==2000+op and words[7]==int(capture) and words[8]==int(subject)
     assert len(rights)==(1 if op==1 else 0)
     return words,rights
   previousContext=None
   for color in ['red','blue','red']:
    if color!='red' or previousContext:
     oldScope=sourceScope();control({'op':'source-color','color':color});wait(lambda: (value if int(value['context']['content'])>int(oldScope['context']['content']) else None) if (value:=sourceScope()) else None)
    scope=sourceScope();check('clientScopeRetainsUnqualifiedKind_'+color,scope['binding']==attached['binding'])
    deadline=int(scope['now'])+2000000000
    captured=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check('actualIsolatedClientCapture_'+color,captured.get('kind')=='preview-client-owned' and captured.get('planeSpace')=='client-logical-unqualified' and captured['previewEligible'] is False,reply=captured)
    legacy=request('preview-capture-probe-state-request');check('legacyMonitorStateCannotAliasClient_'+color,legacy.get('reason')=='preview-probe-unavailable',reply=legacy)
    h,rights=exchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     check('exactClientSourceAndContextFD_'+color,h[22]==11 and h[18]==int(scope['context']['privacy']) and h[19]==int(scope['context']['rendering']) and h[20]==int(scope['context']['scene']) and h[21]==int(scope['context']['content']) and h[9]==int(scope['context']['output']) and h[23]==deadline and h[10]<deadline and h[11]>=h[10],header=list(h))
     size=next(w['size'] for w in s.data('clients') if w['address']==sourceAddress);check('clientDimensionsExcludeMonitor_'+color,list(h[12:14])==size and size!=[800,600],size=size)
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
     check('clientDescriptorImmutable_'+color,fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check('clientNativePNGChecksum_'+color,__import__('zlib').crc32(blob)==h[17])
     image=private/('client-'+str(len(r['checks']))+'.png');image.write_bytes(blob);image.chmod(0o600)
     name='pixels-'+str(len(r['checks']));decoder=s.host.launch(name,[pre['pixelOracle'],str(image)],env=env);decoder.wait(timeout=5);check('independentPixelDecoderNormalExit_'+color,decoder.returncode==0)
     pixels=json.loads((private/(name+'.log')).read_text());total=pixels['width']*pixels['height']
     check('independentClientPixelsExcludeOverlappingPeer_'+color,[pixels['width'],pixels['height']]==size and pixels[color]>total*.5 and pixels['green']==0,pixels=pixels)
     early=request('preview-client-retire-request');check('clientRetireRefusesOutstandingExport_'+color,early.get('reason')=='preview-client-import-outstanding')
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Closed FD unexpectedly remains live')
    except OSError as error:check('clientPhysicalMappingAndDescriptorGone_'+color,error.errno==9)
    released,_=exchange(2,captured['captureRequest'],h[16]);check('nativeClientExportReleased_'+color,released[16]==h[16]);retired=request('preview-client-retire-request');check('nativeClientProducerRetired_'+color,retired.get('kind')=='preview-client-retired' and retired['ownedBytes']=='0')
    previousContext=scope['context']
   after=[{'address':w['address'],'at':w['at'],'size':w['size'],'floating':w['floating']} for w in sorted(s.data('clients'),key=lambda w:w['address'])];check('capturePreservesNativeWindowGeometryAndFocus',after==baseline and s.data('activewindow')['address']==peerAddress,before=baseline,after=after)
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
