"""Real native child-only commits and independent pixels on the exact owning tuple."""
import re,math,array,fcntl,hashlib,importlib.util,json,mmap,os,pathlib,resource,shutil,socket,struct,subprocess,sys,time,traceback,zlib
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((ROOT/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for path,digest in pre['inputs'].items():assert sha(path)==digest,path
runtime=ROOT;spec=importlib.util.spec_from_file_location('exact_child_private_host',runtime/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(ROOT/'qa'));from session_bus import isolate_session_host
from system_isolation import supply,validate
isolate_session_host(host)
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
private=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-client-child-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'pair':pre['pair'],'scope':'Retained original 1739 controls plus actual typed family FD3 capture through shared Elm policy and GTK/WebKit URI pixels, offscreen modal/popup and physical retirement/ACK. Production eligibility, complete style/source-stop/minimized fidelity, hardware and full release remain unqualified.','checks':[],'samples':[]}
s=None;fixture=None;peer=None;web=None;companion=None;locker=None;witness=None;witnessSource=None;lockControl=None;witnessControl=None;loaded=False;commandSequence=0;requestId=1;importWitness=None;importControl=None
reuseSource=None;reuseControl=None;reuseReaderControl=None
r['cacheTraceReplay']=[]
r['popupRevisionReplay']=[]
r['familyRevisionReplay']=[]
r['popupCaptureSamples']=[]
r['familyCaptureSamples']=[]
def check(name,ok,**values):r['checks'].append({'name':name,'passed':bool(ok),**values});assert ok,name
def logs():
 path=private/'child.log'
 rows=[json.loads(line) for line in path.read_text().splitlines() if line.startswith('{')] if path.exists() else []
 assert not any(row['event']=='refused' for row in rows),rows[-5:]
 return rows
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Original six-second fixture observation deadline')
def command(name):
 global commandSequence
 commandSequence+=1;temp=private/'child-control.tmp';temp.write_text(str(commandSequence)+' '+name+'\n');temp.chmod(0o600);temp.replace(private/'child-control')
 if name=='quit':return None
 return wait(lambda:next((row for row in logs() if row['event']=='server-barrier' and row['barrierControl']==commandSequence),None))
def peerQuit():
 temp=private/'peer-control.tmp';temp.write_text(json.dumps({'op':'quit'}));temp.chmod(0o600);temp.replace(private/'peer-control.json')
try:
 lua=b'hl.config({xwayland={enabled=false},animations={enabled=false},misc={disable_hyprland_logo=true,disable_splash_rendering=true}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
 s=host.PrivateHyprSession(private,dict(os.environ),1600,1000,lua,mesa_vendor=True)
 with s:
  try:
   plugin=pre['pair']['plugin']['path'];check('exactOwningPluginLoads',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory')
   peer=s.host.launch('peer',['/usr/bin/python3','-B',str(ROOT/'peer.py'),str(private/'peer-control.json')],env=env);wait(lambda:len(s.data('clients'))==1)
   childEnv=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(private/'child-control'));fixture=s.host.launch('child',[pre['fixtureClient']],env=childEnv);wait(lambda:any(row['event']=='ready' for row in logs()));wait(lambda:len(s.data('clients'))==2)
   source=next(w for w in s.data('clients') if w['title']=='WARLOCK-CHILD-PROBE');unrelated=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
   for name,window in [('source',source),('peer',unrelated)]:
    target='address:'+window['address']
    if not window['floating']:check(name+'Floating',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+target+"'})").strip()=='ok')
    check(name+'Sized',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+target+"'})").strip()=='ok')
    check(name+'Positioned',s.ctl('dispatch',"hl.dsp.window.move({x=80,y=80,window='"+target+"'})").strip()=='ok')
   check('unrelatedPeerRaised',s.ctl('dispatch',"hl.dsp.focus({window='address:"+unrelated['address']+"'})").strip()=='ok');wait(lambda:all(w['at']==[80,80] and w['size']==[320,240] for w in s.data('clients')))
   time.sleep(.15);s.guard()
   def observe(body):
    path=s.host.runtime/'hypr'/s.env['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock';before=host.original.socket_identity(path,s.host.runtime);child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert host.original.same_process(child)
    assert not path.parent.is_symlink() and not path.parent.parent.is_symlink()
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
     c.settimeout(3);c.connect(str(path));pid,uid,gid=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==child['pid'] and uid==os.getuid() and host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before;c.sendall(('elm_observe '+json.dumps(body)).encode());reply=bytearray()
     while True:
      chunk=c.recv(4096)
      if not chunk:break
      reply.extend(chunk);assert len(reply)<=65536
    assert host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before;return json.loads(reply)
   attached=observe({'protocolVersion':3,'kind':'hello'});snapshot=observe({'protocolVersion':3,'kind':'scene-facts-request','binding':attached['binding'],'requestId':'1','minimumWatermark':'0'});subject=next(w['incarnation'] for w in snapshot['facts']['windows'] if w['application']=='warlock-child-probe')
   def request(kind,**fields):
    global requestId
    requestId+=1;return observe({'protocolVersion':3,'kind':kind,'binding':attached['binding'],'requestId':str(requestId),**fields})
   def sourceScope():
    value=request('preview-client-scope-request',subjectIncarnation=subject);assert value['kind']=='preview-client-scope' and value['previewEligible'] is False and value['scope']['binding']==attached['binding'];return value['scope']
   magic=0x454c4d5046443031;lifetime,session,frontend=[int(attached['binding'][k]) for k in ['lifetime','session','frontend']]
   def exchange(op,capture,transfer=0,captureSubject=None):
    captureSubject=subject if captureSubject is None else captureSubject
    query=[magic,1,op,lifetime,session,frontend,2000+op,int(capture),int(captureSubject),int(transfer)]
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child);assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(25*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==25*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC);words=struct.unpack('!25Q',data);assert words[:3]==(magic,1,0) and words[3:6]==(lifetime,session,frontend) and words[6]==2000+op and words[7]==int(capture) and words[8]==int(captureSubject);assert len(rights)==(1 if op==1 else 0);return words,rights
   def capture(name,scope):
    deadline=int(scope['now'])+2000000000;captured=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context']);check(name+'Captured',captured.get('kind')=='preview-client-owned' and captured['previewEligible'] is False,reply=captured)
    h,rights=exchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     check(name+'ExactFDContext',h[22]==11 and h[21]==int(scope['context']['content']) and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[320,240],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'Sealed',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'PNGChecksum',zlib.crc32(blob)==h[17]);image=private/(name+'.png');image.write_bytes(blob);image.chmod(0o600)
     decoder=s.host.launch('pixels-'+name,[pre['pixelOracle'],str(image)],env=env);decoder.wait(timeout=5);check(name+'DecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text());r['samples'].append({'name':name,'scope':scope,'pixels':pixels,'fixture':logs()[-1]})
     check(name+'PeerExcluded',pixels['green']==0 and pixels['points']['root']==[255,0,0,255],pixels=pixels)
     refused=request('preview-client-retire-request');check(name+'HeldExportRefusesRetirement',refused.get('reason')=='preview-client-import-outstanding')
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Descriptor unexpectedly live')
    except OSError as error:check(name+'PhysicalFDGone',error.errno==9)
    released,_=exchange(2,captured['captureRequest'],h[16]);check(name+'ExportReleased',released[16]==h[16]);retired=request('preview-client-retire-request');check(name+'ProducerRetired',retired.get('kind')=='preview-client-retired' and retired['ownedBytes']=='0');return pixels
   def stale(name,old):
    value=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(sourceScope()['now'])+2000000000),context=old['context']);check(name+'PreviousContextRejected',value.get('reason')=='preview-client-context-stale',reply=value)
   command('child-create');base=sourceScope();pixels=capture('initial-child',base);check('initialChildBlue',pixels['points']['old']==[0,0,255,255] and pixels['blue']==64*48,pixels=pixels)
   counts=logs()[-1];changed=command('child-yellow');after=sourceScope();pixels=capture('desync-yellow',after)
   check('desyncChildOnlyNoRootCommit',changed['rootCommits']==counts['rootCommits'] and changed['childCommits']==counts['childCommits']+1,before=counts,after=changed)
   check('desyncChildContextAndPixelsAdvance',int(after['context']['content'])>int(base['context']['content']) and pixels['points']['old']==[255,255,0,255] and pixels['yellow']==64*48,before=base,after=after,pixels=pixels);stale('desyncChild',base)
   command('child-sync');synced=sourceScope();counts=logs()[-1];queued=command('child-blue');pending=sourceScope();pixels=capture('sync-pending-blue',pending)
   check('syncQueuedNoRootCommit',queued['rootCommits']==counts['rootCommits'],before=counts,after=queued)
   check('syncQueuedRetainsAppliedContextAndPixels',pending['context']==synced['context'] and pixels['points']['old']==[255,255,0,255] and pixels['yellow']==64*48,before=synced,after=pending,pixels=pixels)
   command('root-commit');applied=sourceScope();pixels=capture('sync-applied-blue',applied);check('syncParentAppliesBlue',int(applied['context']['content'])>int(synced['context']['content']) and pixels['points']['old']==[0,0,255,255],pixels=pixels);stale('syncApplied',synced)
   command('child-desync');command('child-move');moved=sourceScope();pixels=capture('moved-child',moved);check('appliedChildPosition',pixels['points']['old']==[255,0,0,255] and pixels['points']['moved']==[0,0,255,255],pixels=pixels)
   command('child-below');pixels=capture('below-root',sourceScope());check('childBelowRootExcluded',pixels['blue']==0 and pixels['points']['moved']==[255,0,0,255],pixels=pixels)
   command('child-above');command('grand-create');nested=sourceScope();pixels=capture('nested-child',nested);check('nestedAccumulatedOffset',pixels['points']['nested']==[0,255,255,255] and pixels['cyan']==16*12,pixels=pixels)
   command('child-detach');detached=sourceScope();pixels=capture('detached-child',detached);check('detachedPixelsAbsent',pixels['blue']==0 and pixels['cyan']==0,pixels=pixels);stale('detach',nested)
   command('child-reattach');pixels=capture('reattached-child',sourceScope());check('reattachedPixelsPresent',pixels['blue']>0,pixels=pixels)
   previous=sourceScope();command('child-destroy');destroyed=sourceScope();pixels=capture('destroyed-child',destroyed);check('destroyedPixelsAbsent',pixels['blue']==0 and pixels['cyan']==0,pixels=pixels);stale('destroy',previous)
   command('child-create');replacement=sourceScope();pixels=capture('replacement-child',replacement);check('replacementFreshContext',int(replacement['context']['content'])>int(destroyed['context']['content']) and pixels['points']['old']==[0,0,255,255],pixels=pixels);stale('replacement',destroyed)
   for tracePath,traceHash in sorted(pre['cacheTraces'].items()):
    check('cacheTraceHash'+pathlib.Path(tracePath).stem,sha(tracePath)==traceHash)
    trace=json.loads(pathlib.Path(tracePath).read_text());before=None;exists=True;steps=[]
    for index,state in enumerate(trace['states']):
     cmd=state['command'];number=lambda k:int(state[k]['#bigint'])
     priorCounts=logs()[-1]
     if cmd=='reset':
      if exists:command('child-destroy')
      exists=False
     elif cmd!='inspect':
      command(cmd)
      if cmd=='child-create-sync':exists=True
      elif cmd=='child-destroy':exists=False
     scope=sourceScope();label='cache-'+pathlib.Path(tracePath).stem+'-'+str(index);pixels=capture(label,scope)
     child=number('child');grand=number('grand');nested=state['nested'] and state['childExists'] and child!=0
     grandPixels=16*12 if nested and grand!=0 else 0
     expectedBlue=(64*48-grandPixels) if child==1 else 0
     expectedYellow=((64*48-grandPixels) if child==2 else 0)+(grandPixels if grand==2 else 0)
     expectedCyan=grandPixels if grand==3 else 0
     check(label+'ModelPixels',pixels['blue']==expectedBlue and pixels['yellow']==expectedYellow and pixels['cyan']==expectedCyan and pixels['red']==320*240-expectedBlue-expectedYellow-expectedCyan,expected={'blue':expectedBlue,'yellow':expectedYellow,'cyan':expectedCyan},pixels=pixels)
     if state['hold'] and before is not None:check(label+'QueuedContextHeld',scope['context']==before['context'],before=before,after=scope)
     if cmd in ['child-blue','child-yellow','child-detach','child-empty','grand-yellow','grand-desync','child-desync']:
      check(label+'NoArtificialRootCommit',logs()[-1]['rootCommits']==priorCounts['rootCommits'],before=priorCounts,after=logs()[-1])
     steps.append({'index':index,'command':cmd,'modelState':state,'actualScope':scope,'pixels':pixels,'fixture':logs()[-1]});before=scope
    r['cacheTraceReplay'].append({'trace':tracePath,'sha256':traceHash,'statesCompared':len(steps),'steps':steps})
   check('allFiveSelectedCacheTracesReplayed',len(r['cacheTraceReplay'])==5)
   command('child-destroy');command('child-create');layoutBase=sourceScope();baselinePixels=capture('layout-baseline',layoutBase);check('layoutBaselineVisibleBlue',baselinePixels['blue']==64*48 and baselinePixels['points']['old']==[0,0,255,255] and baselinePixels['points']['moved']==[255,0,0,255],pixels=baselinePixels);counts=logs()[-1];command('child-move-pending');pending=sourceScope();pixels=capture('layout-position-pending',pending)
   check('layoutPositionPendingNoRootCommit',logs()[-1]['rootCommits']==counts['rootCommits'])
   check('layoutPositionPendingHeld',pending['context']==layoutBase['context'] and pixels['points']['old']==[0,0,255,255] and pixels['points']['moved']==[255,0,0,255],before=layoutBase,after=pending,pixels=pixels)
   command('root-commit');positionApplied=sourceScope();pixels=capture('layout-position-applied',positionApplied);check('layoutPositionParentApplies',positionApplied['context']!=layoutBase['context'] and pixels['points']['old']==[255,0,0,255] and pixels['points']['moved']==[0,0,255,255],pixels=pixels);stale('layoutPosition',layoutBase)
   counts=logs()[-1];command('child-below-pending');pending=sourceScope();pixels=capture('layout-below-pending',pending)
   check('layoutBelowPendingNoRootCommit',logs()[-1]['rootCommits']==counts['rootCommits'])
   check('layoutBelowPendingHeld',pending['context']==positionApplied['context'] and pixels['blue']==64*48,pixels=pixels)
   command('root-commit');belowApplied=sourceScope();pixels=capture('layout-below-applied',belowApplied);check('layoutBelowParentApplies',belowApplied['context']!=positionApplied['context'] and pixels['blue']==0 and pixels['points']['moved']==[255,0,0,255],pixels=pixels);stale('layoutBelow',positionApplied)
   counts=logs()[-1];command('child-above-pending');pending=sourceScope();pixels=capture('layout-above-pending',pending)
   check('layoutAbovePendingNoRootCommit',logs()[-1]['rootCommits']==counts['rootCommits'])
   check('layoutAbovePendingHeld',pending['context']==belowApplied['context'] and pixels['blue']==0,pixels=pixels)
   command('root-commit');aboveApplied=sourceScope();pixels=capture('layout-above-applied',aboveApplied);check('layoutAboveParentApplies',aboveApplied['context']!=belowApplied['context'] and pixels['blue']==64*48,pixels=pixels);stale('layoutAbove',belowApplied)
   childRecord=next(row for _,row in s.host.processes if row['name']=='hyprland');config=private/'provider-authority.json';config.write_text(json.dumps({'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':childRecord['pid'],'expected_start':int(childRecord['start']),'binary_sha256':pre['pair']['core']['sha256']}));config.chmod(0o600)
   probe=s.host.launch('own-client-provider',[pre['providerProbe'],str(config),subject,str(private/'own-provider-client.png')],env=env);probe.wait(timeout=10);check('ownProviderNormalExit',probe.returncode==0,stderr=(private/'own-client-provider.stderr').read_text() if (private/'own-client-provider.stderr').exists() else '')
   providerReport=json.loads((private/'own-client-provider.log').read_text());check('actualOwnProviderClientImportAndPhysicalReceipts',providerReport['passed'] and providerReport['checks']>=25 and not providerReport['previewEligible'] and providerReport['providerPID']==probe.pid,report=providerReport);r['providerReport']=providerReport
   decoder=s.host.launch('pixels-own-provider',[pre['pixelOracle'],str(private/'own-provider-client.png')],env=env);decoder.wait(timeout=5);check('ownProviderPixelsDecoderNormalExit',decoder.returncode==0);providerPixels=json.loads((private/'pixels-own-provider.log').read_text());check('ownProviderActualChildPixelsAndPeerExclusion',providerPixels['blue']==64*48 and providerPixels['green']==0 and providerPixels['points']['moved']==[0,0,255,255],pixels=providerPixels);r['providerPixels']=providerPixels
   # Existing Taskbar.primary opens a picker only for multiple admitted families.
   companion=s.host.launch('same-app-companion',[pre['fixtureClient']],env=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(private/'companion-control')))
   wait(lambda:len(s.data('clients'))==3)
   scene=request('scene-facts-request',minimumWatermark='0')
   check('fullHostRealTwoFamilyGroupFixture',len([w for w in scene['facts']['windows'] if w['application']=='warlock-child-probe'])==2)
   # Full real Main/Bar/Popup and own native producer, after all native768.
   web=s.host.launch('full-client-provider',[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-client',subject,'--qa-preview-snapshot',str(private/'full-webkit-client.png')],env=env)
   fullLogName='full-client-provider'
   def fullLog():
    data=(private/(fullLogName+'.log')).read_text()
    if data and not data.endswith('\n') and web is not None and web.poll() is None:return data[:data.rfind('\n')+1]
    return data
   def sourceButton():
    reports=[json.loads(line.split(': ',1)[1]) for line in fullLog().splitlines() if line.startswith('surface-inspection: ')]
    bars=[json.loads(line[len('surface-report: origin=bar '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=bar ')]
    if not reports or not bars:return None
    inspection=reports[-1];bar=bars[-1]['body']
    if inspection['body']['phase']!='Coherent' or inspection['publication']!=bar['publication'] or inspection['lease']!=bar['lease']:return None
    groups=[g for g in inspection['body']['groups'] if g['title']=='WARLOCK-CHILD-PROBE']
    if len(groups)!=1:return None
    rows=[b for b in bar['buttons'] if b['id']==groups[0]['domId'] and not b['disabled']]
    return rows[0] if len(rows)==1 else None
   target=wait(sourceButton);check('fullHostOwnSourceGroupRendered',target['width']>0 and target['height']>0,button=target)
   x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('fullHostNativePointerTargetInOutput',0<x<800 and 0<y<48)
   pointerOutput=private/'full-host-pointer.log'
   with pointerOutput.open('xb') as output:
    pointer=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(pointer.pid);record.update(name='full-host-pointer',command=[pre['pointer'],'800','600'],log=str(pointerOutput));s.host.processes.append((pointer,record))
   pointer.communicate(('move '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('fullHostNativePointerNormalExit',pointer.returncode==0)
   wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   check('fullHostActualElmAcquireAfterNativeSource', 'native-client-start:' in fullLog() and 'native-client-command: {"kind":"acquire"' in fullLog())
   batches=[json.loads(line[len('native-client-events: '):]) for line in fullLog().splitlines() if line.startswith('native-client-events: ')]
   seeds=[event for batch in batches for event in batch if event['kind']=='source-seed'];offers=[event['event']['frame'] for batch in batches for event in batch if event['kind']=='event' and event['event']['kind']=='offer']
   check('fullHostOwnTypedSourceUnqualified',len(seeds)==1 and seeds[0]['source']['previewEligible'] is False and seeds[0]['source']['kind']=='preview-client-scope' and seeds[0]['identity']=='family:'+subject and seeds[0]['source']['binding']!=attached['binding'],seed=seeds)
   check('fullHostActualNativeClientPacket',len(offers)==1 and offers[0]['fidelity']=='client' and offers[0]['coverage']==['client'],offer=offers)
   images=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('fullHostExactURIAndClientDimensions',images and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+offers[0]['handle'] and row[0]['naturalWidth']==320 and row[0]['naturalHeight']==240 and row[0]['width']==160 and row[0]['height']==120 for row in images),images=images)
   decoder=s.host.launch('pixels-full-webkit',[pre['pixelOracle'],str(private/'full-webkit-client.png')],env=env);decoder.wait(timeout=5);check('fullHostIndependentWebKitDecoderNormalExit',decoder.returncode==0)
   rendered=json.loads((private/'pixels-full-webkit.log').read_text());check('fullHostRenderedIsolatedChildPixels',rendered['blue']==32*24 and rendered['red']==320*240//4-32*24 and rendered['green']==0,pixels=rendered);r['fullHostPixels']=rendered
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   check('fullHostActualElmReleaseAndFinalACK','native-client-command: {"kind":"release"' in fullLog() and 'native-client-ack:' in fullLog())
   check('fullHostPhysicalBeforeExactACK',fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'))
   web.terminate();web.wait(timeout=5);check('fullHostNormalExit',web.returncode==0)
   check('fullHostCleanNativeExitEvidence','shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native client teardown incomplete:' not in fullLog())
   # Actual ordinary product path: no fixed QA subjects and no capture scope.
   fullLogName='ordinary-catalog-provider'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=env)
   def ordinaryReadyButton():
    lines=fullLog().splitlines()
    nativeGeometry=[json.loads(line[len('backend-frame: '):]) for line in lines if line.startswith('backend-frame: ') and '"kind":"geometry-facts"' in line]
    if not nativeGeometry:return None
    inspections=[json.loads(line.split(': ',1)[1]) for line in lines if line.startswith('surface-inspection: ')]
    visible=[json.loads(line[line.index('{'):]) for line in lines if line.startswith('view-report: id=1 ')]
    if not inspections or not visible:return None
    inspection=inspections[-1];bar=visible[-1]['body']
    if inspection['body']['phase']!='Coherent' or inspection['publication']!=bar['publication'] or inspection['lease']!=bar['lease']:return None
    groups=[group for group in inspection['body']['groups'] if group['title']=='WARLOCK-CHILD-PROBE']
    if len(groups)!=1:return None
    buttons=[button for button in bar['buttons'] if button['id']==groups[0]['domId'] and not button['disabled']]
    return buttons[0] if len(buttons)==1 else None
   ordinaryTarget=wait(ordinaryReadyButton);ox=round(ordinaryTarget['x']+ordinaryTarget['width']/2);oy=round(ordinaryTarget['y']+ordinaryTarget['height']/2)
   check('ordinaryCatalogActualGroupPointerInOutput',0<ox<800 and 0<oy<48)
   with (private/'ordinary-catalog-pointer.log').open('xb') as output:
    ordinaryPointer=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ordinaryPointer.pid);record.update(name='ordinary-catalog-pointer',command=[pre['pointer'],'800','600'],log=str(private/'ordinary-catalog-pointer.log'));s.host.processes.append((ordinaryPointer,record))
   ordinaryPointer.communicate(('move '+str(ox)+' '+str(oy)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5)
   check('ordinaryCatalogActualGroupPointerNormalExit',ordinaryPointer.returncode==0)
   def ordinaryFallback():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in reversed(rows) if row['body']['text'].count('Preview unavailable')==4),None)
   ordinaryRendered=wait(ordinaryFallback)
   check('ordinaryCatalogTwoActualElmUnavailableEntries',len([button for button in ordinaryRendered['body']['buttons'] if 'Preview unavailable' in button['label']])==2 and 'WARLOCK-CHILD-PROBE' in ordinaryRendered['body']['text'],rendered=ordinaryRendered)
   check('ordinaryCatalogNoFixedCaptureEnrollmentOrAcquire','native-client-start:' not in fullLog() and 'native-client-command:' not in fullLog() and 'native-imported-start:' not in fullLog())
   r['ordinaryCatalogEvidence']={'rendered':ordinaryRendered,'ownHostPID':web.pid,'fixedQualificationSubjects':False,'nativeScopeCreated':False,'nativeCaptureEligible':False,'scope':'Actual normal host own authenticated catalog to ordinary picker and same Elm metadata-only unavailable entries; no native capture/resource/hardware/full-S09 acceptance.'}
   web.terminate();web.wait(timeout=5);check('ordinaryCatalogFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   # A separate actual host exercises semantic observation updates while the
   # first full783 behavior remains unchanged and retained above.
   fullLogName='full-client-changing'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-client',subject,'--qa-preview-snapshot',str(private/'changing-webkit-client.png')],env=env)
   changingTarget=wait(sourceButton);cx=round(changingTarget['x']+changingTarget['width']/2);cy=round(changingTarget['y']+changingTarget['height']/2)
   check('changingHostPointerTargetInOutput',0<cx<800 and 0<cy<48)
   with (private/'changing-pointer.log').open('xb') as output:
    pointer=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(pointer.pid);record.update(name='changing-host-pointer',command=[pre['pointer'],'800','600'],log=str(private/'changing-pointer.log'));s.host.processes.append((pointer,record))
   pointer.communicate(('move 10 550\nsleep 100\nmove '+str(cx)+' '+str(cy)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('changingHostPointerNormalExit',pointer.returncode==0)
   wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   def changingEvents():return [event for line in fullLog().splitlines() if line.startswith('native-client-events: ') for event in json.loads(line[len('native-client-events: '):])]
   first=next(event for event in changingEvents() if event['kind']=='source-seed');owned=next(event['event']['frame'] for event in changingEvents() if event['kind']=='event' and event['event']['kind']=='offer')
   before=logs()[-1];changed=command('child-yellow')
   check('changingHostActualChildOnlyCommit',changed['rootCommits']==before['rootCommits'] and changed['childCommits']==before['childCommits']+1)
   def updatedSource():
    return next((event for event in changingEvents() if event['kind']=='source-seed' and int(event['source']['scope']['context']['content'])>int(first['source']['scope']['context']['content'])),None)
   fresh=wait(updatedSource)
   check('changingHostOwnTypedUpdatedFacts',fresh['source']['binding']==first['source']['binding'] and fresh['identity']==first['identity'] and fresh['source']['previewEligible'] is False and fresh['source']['scope']['now']>first['source']['scope']['now'],source=fresh)
   def historicalReport():
    reports=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in reports if 'Historical preview' in row['body']['text']),None)
   historical=wait(historicalReport)
   check('changingHostActualElmHistorical',historical['body']['publication']==fresh['publication'] and historical['body']['lease']==fresh['lease'],report=historical)
   check('changingHostNoCaptureOrDeadlineRenewal',len([event for event in changingEvents() if event['kind']=='event' and event['event']['kind']=='offer'])==1 and len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1)
   check('changingHostOriginalHandleRetained',all(row[0]['uri']=='elm-shell://preview/'+owned['handle'] for row in [json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]))
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   expired=next(event['event']['frame'] for event in changingEvents() if event['kind']=='event' and event['event']['kind']=='expired')
   check('changingHostOriginalExpirationAndJob',expired['job']==owned['job'] and expired['handle']==owned['handle'] and expired['expires']==owned['expires'],original=owned,expired=expired)
   check('changingHostActualElmReleaseACK','native-client-command: {"kind":"release"' in fullLog() and 'native-client-ack:' in fullLog())
   web.terminate();web.wait(timeout=5);check('changingHostNormalExit',web.returncode==0)
   check('changingHostCleanExitEvidence','shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native client teardown incomplete:' not in fullLog())
   # Native-v7 additions follow every original changed-source control.
   def events():return [event for line in fullLog().splitlines() if line.startswith('native-client-events: ') for event in json.loads(line[len('native-client-events: '):])]
   def ownership():return [json.loads(line[len('native-client-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-client-ownership: ')]
   def writeControl(path,command):
    temp=path.with_suffix('.tmp');temp.write_text(command+'\n');temp.chmod(0o600);temp.replace(path)
   def openQualification(tag,qualified_subject=None):
    global fullLogName,web
    fullLogName='full-client-'+tag
    extra=['--qa-preview-reader-control',str(reuseReaderControl)] if tag=='reuse' else ['--qa-icon-reader-control',str(iconReaderControl)] if tag=='locked' else []
    web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-client',qualified_subject or subject,'--qa-preview-snapshot',str(private/(tag+'-webkit-client.png')),*extra],env=lockedIconEnv if tag=='locked' else env)
    target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check(tag+'PointerTargetInOutput',0<x<800 and 0<y<48)
    pointerLog=private/(tag+'-pointer.log')
    with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
    record=host.original.process(ptr.pid);record.update(name=tag+'-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
    ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check(tag+'PointerNormalExit',ptr.returncode==0)
    wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
    offers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];check(tag+'OneOriginalNativePacket',len(offers)==1)
    return offers[0]
   def beginWitness(tag,subject_=None):
    global witness,witnessControl
    witnessControl=s.host.runtime/(tag+'-witness-control');writeControl(witnessControl,'hold')
    witness=s.host.launch(tag+'-native-witness',[pre['denialWitness'],str(config),subject_ or subject,str(witnessControl)],env=env)
    def samples():return [json.loads(line) for line in (private/(tag+'-native-witness.log')).read_text().splitlines() if line.startswith('{')]
    ready=wait(lambda:next((row for row in samples() if row['stage']=='ready'),None));check(tag+'WitnessActualOwnedFDAndCharge',int(ready['status']['charge'])>0 and ready['status']['records']==1 and not ready['status']['mappedFDClosed'])
    return samples,ready
   def retainedOriginal(tag,owned):
    allOffers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']
    check(tag+'NoCaptureOrLifetimeRenewal',allOffers==[owned] and len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1)
    releases=[json.loads(line[len('native-client-command: '):])['frame'] for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"release"')]
    check(tag+'ExactOriginalElmRelease',len(releases)==1 and releases[0]['job']==owned['job'] and releases[0]['handle']==owned['handle'] and releases[0]['expires']==owned['expires'])
   def beginLock(tag):
    global locker,lockControl
    lockControl=s.host.runtime/(tag+'-control');writeControl(lockControl,'hold')
    display=pathlib.Path(env['WAYLAND_DISPLAY']);display=display if display.is_absolute() else s.host.runtime/display
    socketStat=display.stat();lockEnv=dict(env,WARLOCK_PRIVATE_LOCK_FIXTURE='1',WARLOCK_LOCK_CONTROL_PATH=str(lockControl),WAYLAND_DISPLAY=display.name,WARLOCK_LOCK_SOCKET_DEV=str(socketStat.st_dev),WARLOCK_LOCK_SOCKET_INO=str(socketStat.st_ino),WARLOCK_LOCK_SERVER_PID=str(childRecord['pid']))
    locker=s.host.launch(tag,[pre['lockFixture']],env=lockEnv)
    def samples():return [json.loads(line) for line in (private/(tag+'.log')).read_text().splitlines() if line.startswith('{')]
    wait(lambda:any(row['event']=='locked' for row in samples()));check(tag+'ActualPrivateSessionLocked',locker.poll() is None)
    return samples
   witnessSamples,witnessReady=beginWitness('locked')
   lockSamples=beginLock('witness-lock')
   writeControl(witnessControl,'deny');denied=wait(lambda:next((row for row in witnessSamples() if row['stage']=='native-uri-denied-before-policy'),None))
   check('lockedIndependentNativeHeldAndNewURIDenial',denied['status']['job']==witnessReady['status']['job'] and int(denied['status']['charge'])>0 and not denied['status']['mappedFDClosed'])
   pending=wait(lambda:next((row for row in witnessSamples() if row['stage']=='cleanup'),None))['status']
   check('lockedWitnessPhysicalRetirementPending',pending['job']==witnessReady['status']['job'] and pending['mappedFDClosed'] and pending['exportReleased'] and not pending['producerRetired'] and pending['retirementPending'] and int(pending['charge'])>0 and pending['records']==1,status=pending)
   writeControl(lockControl,'unlock');locker.wait(timeout=5);check('sessionLockFixtureNormalExitAfterUnlock',locker.returncode==0 and any(row['event']=='unlock-synced' for row in lockSamples()))
   writeControl(witnessControl,'poll');polled=wait(lambda:next((row for row in witnessSamples() if row['stage']=='polled'),None))['status']
   check('unlockedWitnessActualProducerRetired',polled['job']==pending['job'] and polled['charge']=='0' and polled['records']==1 and polled['producerRetired'] and not polled['retirementPending'],status=polled)
   writeControl(witnessControl,'finish');witness.wait(timeout=5);check('lockedWitnessExactACKAndNormalExit',witness.returncode==0 and witnessSamples()[-1]['status']['records']==0)
   # Actual GTK application resolution stays private to this owning host.
   iconReaderControl=s.host.runtime/'locked-icon-reader-control';writeControl(iconReaderControl,'hold')
   lockIconData=private/'locked-icon-data';(lockIconData/'applications').mkdir(parents=True,mode=0o700)
   def lockPngChunk(kind,value):return struct.pack('>I',len(value))+kind+value+struct.pack('>I',zlib.crc32(kind+value)&0xffffffff)
   lockScan=b''.join(b'\0'+bytes([224,34,221,255]*8) for _ in range(8))
   lockOwnIcon=lockIconData/'own-icon.png';lockOwnIcon.write_bytes(b'\x89PNG\r\n\x1a\n'+lockPngChunk(b'IHDR',struct.pack('>IIBBBBB',8,8,8,6,0,0,0))+lockPngChunk(b'IDAT',zlib.compress(lockScan))+lockPngChunk(b'IEND',b''));lockOwnIcon.chmod(0o600)
   lockDesktop=lockIconData/'applications/warlock-child-probe.desktop';lockDesktop.write_text('[Desktop Entry]\nType=Application\nName=Warlock own locked icon fixture\nExec=/usr/bin/true\nIcon='+str(lockOwnIcon)+'\n');lockDesktop.chmod(0o600)
   lockedIconEnv=dict(env,XDG_DATA_DIRS=str(lockIconData)+':'+env.get('XDG_DATA_DIRS','/usr/local/share:/usr/share'))
   lockedPacket=openQualification('locked')
   def iconRows(label):return [json.loads(line[len(label)+2:]) for line in fullLog().splitlines() if line.startswith(label+': ')]
   iconReady=wait(lambda:next(iter(iconRows('native-icon-reader-ready')),None))
   lockMetadata=next(event for event in events() if event['kind']=='metadata')
   check('iconLockActualOwnApplicationTokenAndPhysicalReader',lockMetadata['iconKind']=='application' and lockMetadata['binding']==lockedPacket['job']['binding'] and lockMetadata['subject']==subject and iconReady['uri']=='elm-shell://icon/'+lockMetadata['icon'] and iconReady['request']==lockedPacket['job']['request'] and iconReady['firstByte']==137 and iconReady['bytes']>0 and iconReady['icons']['readers']==1 and iconReady['icons']['assets']==1 and iconReady['icons']['bytes']>0 and iconReady['status']['job']==lockedPacket['job'] and int(iconReady['status']['charge'])>0 and not iconReady['status']['mappedFDClosed'],metadata=lockMetadata,evidence=iconReady)
   def lockPixels(name,path,expected=None):
    argv=[pre['pixelOracle'],str(path)] if expected is None else [pre['fallbackPixelOracle'],str(path),*map(str,expected)]
    decoder=s.host.launch(name,argv,env=env);decoder.wait(timeout=5);check(name+'DecoderNormalExit',decoder.returncode==0);return json.loads((private/(name+'.log')).read_text())
   lockedBefore=lockPixels('icon-lock-before-pixels',private/'locked-webkit-client.png')
   check('iconLockOriginalPreviewPixelsPresent',lockedBefore['red']>128 and lockedBefore['yellow']>0 and lockedBefore['green']==0,pixels=lockedBefore)
   check('lockedWitnessDistinctOwnBinding',witnessReady['status']['job']['binding']!=lockedPacket['job']['binding'])
   lockSamples=beginLock('gui-lock')
   writeControl(iconReaderControl,'probe');iconProbe=wait(lambda:next(iter(iconRows('native-icon-reader-probe')),None))
   check('iconLockHeldAndNewActualEndpointDeniedBeforePolicy',iconProbe['uri']==iconReady['uri'] and iconProbe['request']==iconReady['request'] and iconProbe['heldRead']==-1 and iconProbe['heldDenied'] and iconProbe['freshDenied'] and iconProbe['icons']==iconReady['icons'] and iconProbe['status']['job']==lockedPacket['job'] and int(iconProbe['status']['charge'])>0 and not iconProbe['status']['mappedFDClosed'] and not iconProbe['status']['exportReleased'] and not any(event['kind']=='event' and event['event']['kind']=='source-denied' for event in events()) and 'native-client-command: {"kind":"release"' not in fullLog(),evidence=iconProbe)
   writeControl(iconReaderControl,'release');iconReleased=wait(lambda:next(iter(iconRows('native-icon-reader-released')),None))
   check('iconLockActualCloseRetainsAssetAccounting',iconReleased['request']==iconReady['request'] and iconReleased['icons']['readers']==0 and iconReleased['icons']['assets']==1 and iconReleased['icons']['bytes']==iconReady['icons']['bytes'],evidence=iconReleased)
   denial=wait(lambda:next((event['event'] for event in events() if event['kind']=='event' and event['event']['kind']=='source-denied'),None))
   check('lockedFullHostExactTypedScopeDenial',denial=={'kind':'source-denied','job':lockedPacket['job'],'reason':'locked'})
   held=wait(lambda:next((row for row in ownership() if row['retirementPending']),None))
   check('lockedActualElmCleanupStillPhysicallyOwned',held['job']==lockedPacket['job'] and held['mappedFDClosed'] and held['exportReleased'] and not held['producerRetired'] and int(held['charge'])>0 and held['records']==1 and 'native-client-ack:' not in fullLog() and 'native-client-complete:' not in fullLog(),status=held)
   retainedOriginal('locked',lockedPacket)
   concealed=wait(lambda:next(iter(iconRows('native-client-concealed-fallback')),None))
   lockImage=private/'locked-webkit-client.png.locked.png';wait(lambda:lockImage.exists() and ('path='+str(lockImage)) in fullLog())
   check('iconLockActualElmConcealedBeforeProducerRetired',concealed['fallbacks']==[{'state':'unavailable','title':'Preview unavailable','icons':[]}] and concealed['status']['job']==lockedPacket['job'] and concealed['status']['mappedFDClosed'] and concealed['status']['exportReleased'] and concealed['status']['retirementPending'] and not concealed['status']['producerRetired'] and int(concealed['status']['charge'])>0 and 'native-client-ack:' not in fullLog() and 'native-client-complete:' not in fullLog(),evidence=concealed)
   lockedAfter=lockPixels('icon-lock-after-pixels',lockImage);lockedIconPixels=lockPixels('icon-lock-application-pixels',lockImage,[255,0,0,255])
   carrierEvents=[line for line in fullLog().splitlines() if line.startswith('native-icon-snapshot-carrier: ')];check('iconLockSameWebKitCarrierRetiresAfterRealPopupDestruction',carrierEvents==['native-icon-snapshot-carrier: created=1 sameView=1 hardwarePresentation=0','native-icon-snapshot-carrier: destroyed=1 sameView=1 hardwarePresentation=0'] and fullLog().index('surface-popup-closed:')<fullLog().index(carrierEvents[0])<fullLog().index('native-client-concealed-fallback:')<fullLog().index(carrierEvents[1])<fullLog().index('native-icon-controller-flushed:'),evidence=carrierEvents)
   controllerHeld=[line for line in fullLog().splitlines() if line.startswith('native-icon-controller-held: ')];controllerFlushed=[line for line in fullLog().splitlines() if line.startswith('native-icon-controller-flushed: ')]
   check('iconLockOriginalControllerCommitsBoundedAndFlushedOnce',0<len(controllerHeld)<=4 and len(controllerFlushed)==len(controllerHeld) and controllerFlushed[-1]=='native-icon-controller-flushed: remaining=0' and fullLog().index('native-client-concealed-fallback:')<fullLog().index('native-icon-controller-flushed:'),held=controllerHeld,flushed=controllerFlushed)
   check('iconLockBitmapHasActualOpaqueSurfaceAndText',lockedAfter['opaque']==lockedAfter['width']*lockedAfter['height'] and lockedIconPixels['opaqueBackgroundPixels']>128 and lockedIconPixels['renderedLightTextPixels']>16,pixels=lockedAfter,textPixels=lockedIconPixels)
   check('iconLockActualWebKitExcludesOldPreviewAndIconPixels',all(lockedAfter[key]==0 for key in ['red','yellow','blue','green']) and lockedIconPixels['ownApplicationIconPixels']==0 and lockedIconPixels['oldSourceExactNativePixels']==0 and lockedIconPixels['foreignGreenPixels']==0,pixels=lockedAfter,iconPixels=lockedIconPixels)
   r['iconLockEvidence']={'scenarioIds':['WARLOCK-ICONLOCK-001','WARLOCK-ICONLOCK-002'],'metadata':lockMetadata,'originalFrame':lockedPacket,'readerReady':iconReady,'readerProbe':iconProbe,'readerReleased':iconReleased,'concealedDOM':concealed,'beforePixels':lockedBefore,'afterPixels':lockedAfter,'afterIconPixels':lockedIconPixels,'iconAssetSHA256':sha(lockOwnIcon),'desktopEntrySHA256':sha(lockDesktop),'actualNativeLock':True,'hardwarePresentation':False,'ordinaryProductEnrollmentQualified':False,'fullReleaseAccepted':False}
   writeControl(lockControl,'unlock');locker.wait(timeout=5);check('guiSessionLockFixtureNormalExitAfterUnlock',locker.returncode==0 and any(row['event']=='unlock-synced' for row in lockSamples()))
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   check('unlockedActualElmACKAfterPhysicalRetire','native-client-ack:' in fullLog() and any(row['charge']=='0' and row['producerRetired'] for row in ownership()) and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'))
   web.terminate();web.wait(timeout=5);check('lockedFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   check('iconLockSeparatePhysicalIconRetirement',iconRows('native-icon-retired')==[{'assets':0,'readers':0,'bytes':0}],evidence=iconRows('native-icon-retired'))
   # Reopen on a genuinely new GUI lease after the same host's lock cleanup.
   recoveryPacket=openQualification('resumed')
   firstSeed=next(event for event in events() if event['kind']=='source-seed')
   def decodeSnapshot(tag,path):
    decoder=s.host.launch('pixels-'+tag,[pre['pixelOracle'],str(path)],env=env);decoder.wait(timeout=5);check(tag+'DecoderNormalExit',decoder.returncode==0)
    return json.loads((private/('pixels-'+tag+'.log')).read_text())
   originalPixels=decodeSnapshot('resumed-original',private/'resumed-webkit-client.png')
   check('resumedOriginalYellowPixels',originalPixels['yellow']==32*24 and originalPixels['blue']==0 and originalPixels['red']==320*240//4-32*24 and originalPixels['green']==0,pixels=originalPixels)
   recoveryLock=beginLock('resumed-gui-lock')
   denial=wait(lambda:next((event['event'] for event in events() if event['kind']=='event' and event['event']['kind']=='source-denied'),None))
   check('resumedOriginalExactLockedDenial',denial=={'kind':'source-denied','job':recoveryPacket['job'],'reason':'locked'})
   held=wait(lambda:next((row for row in ownership() if row['retirementPending']),None))
   check('resumedOriginalPhysicalPending',held['job']==recoveryPacket['job'] and held['mappedFDClosed'] and held['exportReleased'] and not held['producerRetired'] and int(held['charge'])>0 and held['records']==1 and 'native-client-ack:' not in fullLog(),status=held)
   retainedOriginal('resumed',recoveryPacket)
   writeControl(lockControl,'unlock');locker.wait(timeout=5);check('resumedLockNormalUnlockExit',locker.returncode==0 and any(row['event']=='unlock-synced' for row in recoveryLock()))
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   acks=lambda:[json.loads(line[len('native-client-ack: '):]) for line in fullLog().splitlines() if line.startswith('native-client-ack: ')]
   check('resumedOriginalPhysicalBeforeExactACK3',acks()==[{'kind':'acknowledge','job':recoveryPacket['job'],'sequence':'3'}] and any(row['job']==recoveryPacket['job'] and row['charge']=='0' and row['producerRetired'] for row in ownership()) and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'))
   check('resumedNativePopupActuallyClosed','surface-popup-closed: lease='+firstSeed['lease'] in fullLog())
   before=logs()[-1];changed=command('child-blue');currentScope=sourceScope()
   check('resumedActualChildOnlyBlueCommit',changed['rootCommits']==before['rootCommits'] and changed['childCommits']==before['childCommits']+1)
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('resumedReopenPointerTargetInOutput',0<x<800 and 0<y<48)
   pointerLog=private/'resumed-reopen-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='resumed-reopen-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('resumedReopenPointerNormalExit',ptr.returncode==0)
   secondSnapshot=private/'resumed-webkit-client.png.request-2.png'
   wait(lambda:'native-client-webkit-snapshot-job: request=2 path='+str(secondSnapshot) in fullLog())
   allOffers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];check('resumedExactlyTwoNativePackets',len(allOffers)==2 and allOffers[0]==recoveryPacket)
   newer=allOffers[1];fresh=next(event for event in events() if event['kind']=='source-seed' and int(event['lease'])>int(firstSeed['lease']))
   check('resumedOwnFreshNativeScope',fresh['identity']==firstSeed['identity'] and fresh['source']['binding']==firstSeed['source']['binding'] and fresh['source']['previewEligible'] is False and fresh['source']['scope']['context']==currentScope['context'] and int(fresh['source']['scope']['observation'])>int(firstSeed['source']['scope']['observation']) and int(fresh['source']['requestId'])>int(firstSeed['source']['requestId']) and int(fresh['source']['scope']['now'])>int(firstSeed['source']['scope']['now']),source=fresh)
   check('resumedExactNewJobAndIssuedDeadline',newer['job']['request']=='2' and newer['job']['origin']==fresh['lease'] and newer['job']['binding']==recoveryPacket['job']['binding'] and newer['job']['clock']==recoveryPacket['job']['clock'] and newer['job']['context']==fresh['source']['scope']['context'] and int(newer['job']['deadline'])==int(fresh['source']['scope']['now'])+2000000000 and newer['handle']!=recoveryPacket['handle'],new=newer,original=recoveryPacket)
   acquisitions=[json.loads(line[len('native-client-command: '):]) for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')]
   check('resumedActualElmOwnAcquireTwice',acquisitions==[{'kind':'acquire','job':recoveryPacket['job']},{'kind':'acquire','job':newer['job']}])
   check('resumedOriginalACKBeforeNewAcquire',fullLog().index('native-client-ack:')<fullLog().index('native-client-resume:')<fullLog().index('native-client-command: '+json.dumps(acquisitions[1],separators=(',',':'))))
   images=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('resumedExactSecondURIAndDimensions',any(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+newer['handle'] and row[0]['naturalWidth']==320 and row[0]['naturalHeight']==240 and row[0]['width']==160 and row[0]['height']==120 for row in images),images=images)
   newPixels=decodeSnapshot('resumed-new',secondSnapshot)
   check('resumedNewBluePixelsAndPeerExclusion',newPixels['blue']==32*24 and newPixels['yellow']==0 and newPixels['red']==320*240//4-32*24 and newPixels['green']==0,pixels=newPixels)
   r['resumedPixels']={'original':originalPixels,'new':newPixels,'hardwarePresentation':False}
   wait(lambda:len(acks())==2 and fullLog().rfind('native-client-complete: physical=0 journal=0 previewEligible=0')>fullLog().rfind('native-client-ack:'))
   expired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired']
   check('resumedNewOriginalExpiryAndJob',len(expired)==1 and expired[0]['job']==newer['job'] and expired[0]['handle']==newer['handle'] and expired[0]['expires']==newer['expires'])
   releases=[json.loads(line[len('native-client-command: '):])['frame'] for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"release"')]
   check('resumedBothExactElmReleaseAndACK6',len(releases)==2 and releases[0]['job']==recoveryPacket['job'] and releases[1]=={**newer,'signaled':True} and acks()==[{'kind':'acknowledge','job':recoveryPacket['job'],'sequence':'3'},{'kind':'acknowledge','job':newer['job'],'sequence':'6'}])
   check('resumedNewPhysicalRetirementBeforeACK6',any(row['job']==newer['job'] and row['charge']=='0' and row['producerRetired'] for row in ownership()) and fullLog().index('native-client-command: '+json.dumps({'kind':'release','frame':releases[1]},separators=(',',':')))<fullLog().index('native-client-ack: '+json.dumps(acks()[1],separators=(',',':')))<fullLog().rindex('native-client-complete:'))
   web.terminate();web.wait(timeout=5);check('resumedFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native client teardown incomplete:' not in fullLog())
   # Stop is real native minimization, distinct from retirement of owned pixels.
   stoppedPacket=openQualification('stopped')
   firstStoppedSeed=next(event for event in events() if event['kind']=='source-seed')
   stoppedPixels=decodeSnapshot('stopped-original',private/'stopped-webkit-client.png')
   check('stoppedOriginalBluePixels',stoppedPixels['blue']==32*24 and stoppedPixels['yellow']==0 and stoppedPixels['green']==0,pixels=stoppedPixels)
   effectSequence=0
   def actualEffect(operation):
    global effectSequence
    effectSequence+=1;facts=request('scene-facts-request',minimumWatermark='0')
    intent={'request':str(effectSequence),'generation':str(effectSequence),'incarnation':subject,'operation':operation,'context':{'lifetime':attached['binding']['lifetime'],'epoch':attached['binding']['frontend'],'output':facts['outputGeneration'],'revision':facts['revision']}}
    result=observe({'protocolVersion':3,'kind':'window-effect','binding':attached['binding'],'effectProtocol':1,'intent':intent})
    check('stopped'+operation.title()+'ExactCommittedNativeEffect',result.get('kind')=='effect-outcome' and result['binding']==attached['binding'] and result['intent']==intent and result['status']=='Committed' and result['reason']=='applied',outcome=result)
    return result
   minimizeOutcome=actualEffect('minimize')
   minimizedFacts=request('scene-facts-request',minimumWatermark='0');minimizedMember=next(row for row in minimizedFacts['facts']['windows'] if row['incarnation']==subject)
   check('stoppedActualFirstClassMinimized',minimizedMember['minimized'] is True,window=minimizedMember,outcome=minimizeOutcome)
   stoppedScope=sourceScope()
   check('stoppedActualPresentNotSourceLive',stoppedScope['present'] and not stoppedScope['sourceLive'] and not stoppedScope['locked'] and stoppedScope['gpuReady'] and int(stoppedScope['context']['scene'])>int(firstStoppedSeed['source']['scope']['context']['scene']),scope=stoppedScope)
   def stoppedObservation():
    return next((event for event in events() if event['kind']=='source-seed' and event['source']['scope']['sourceLive'] is False and int(event['lease'])>int(firstStoppedSeed['lease'])),None)
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('stoppedReopenTargetInOutput',0<x<800 and 0<y<48)
   pointerLog=private/'stopped-reopen-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='stopped-reopen-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('stoppedReopenPointerNormalExit',ptr.returncode==0)
   stoppedSeed=wait(stoppedObservation)
   check('stoppedNewLeaseRetainsOriginalNativeJob',int(stoppedSeed['lease'])>int(firstStoppedSeed['lease']) and stoppedPacket['job']['origin']==firstStoppedSeed['lease'] and 'native-client-resume:' not in fullLog())
   check('stoppedOwnCoherentNativeScope',stoppedSeed['identity']==firstStoppedSeed['identity'] and stoppedSeed['source']['binding']==firstStoppedSeed['source']['binding'] and stoppedSeed['source']['previewEligible'] is False and stoppedSeed['source']['scope']['context']==stoppedScope['context'],source=stoppedSeed)
   def stoppedHistorical():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in rows if row['body']['publication']==stoppedSeed['publication'] and row['body']['lease']==stoppedSeed['lease'] and 'Historical preview' in row['body']['text']),None)
   historical=wait(stoppedHistorical)
   check('stoppedActualElmHistoricalVisible',historical is not None,report=historical)
   offers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']
   check('stoppedNoRecaptureOrLifetimeRenewal',offers==[stoppedPacket] and len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1 and 'native-client-command: {"kind":"release"' not in fullLog())
   images=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('stoppedOriginalURIAndPixelsRetained',images and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+stoppedPacket['handle'] and row[0]['naturalWidth']==320 and row[0]['naturalHeight']==240 for row in images),images=images)
   check('stoppedIndependentOriginalPhysicalOwnership',any(row['job']==stoppedPacket['job'] and int(row['charge'])>0 and row['records']==1 and not row['mappedFDClosed'] and not row['producerRetired'] for row in ownership()))
   denied=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(stoppedScope['now'])+2000000000),context=stoppedScope['context'])
   check('stoppedNativeRefusesNewCapture',denied.get('kind')=='refused' and denied.get('reason')=='preview-client-source-unavailable',reply=denied)
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   expired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired']
   check('stoppedOriginalExpiryAndJob',len(expired)==1 and expired[0]['job']==stoppedPacket['job'] and expired[0]['handle']==stoppedPacket['handle'] and expired[0]['expires']==stoppedPacket['expires'])
   retainedOriginal('stopped',stoppedPacket)
   check('stoppedActualPhysicalBeforeExactACK3',acks()==[{'kind':'acknowledge','job':stoppedPacket['job'],'sequence':'3'}] and any(row['job']==stoppedPacket['job'] and row['charge']=='0' and row['producerRetired'] for row in ownership()))
   # End this owned popup before a focus-changing restore is requested.
   web.terminate();web.wait(timeout=5);check('stoppedFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   restoreOutcome=actualEffect('restore');restoredFacts=request('scene-facts-request',minimumWatermark='0');restoredMember=next(row for row in restoredFacts['facts']['windows'] if row['incarnation']==subject)
   check('stoppedActuallyRestoredOriginalSource',restoredMember['minimized'] is False and restoredMember['workspace']==minimizedMember['workspace'],window=restoredMember,outcome=restoreOutcome)
   liveAgain=sourceScope();check('stoppedSourceActuallyLiveAgain',liveAgain['present'] and liveAgain['sourceLive'] and int(liveAgain['context']['scene'])>int(stoppedScope['context']['scene']),scope=liveAgain)
   # Real importer owns two distinct sources after both native capture/export
   # reservations are retired. Local mappings/readers/Broker stay independent.
   check('importedPeerSeparatedForDistinctSources',s.ctl('dispatch',"hl.dsp.window.move({x=440,y=80,window='address:"+unrelated['address']+"'})").strip()=='ok')
   importSnapshot=request('snapshot-request',minimumWatermark='0');importPeer=next(row['incarnation'] for row in importSnapshot['windows'] if row['label']=='ELM-ACTIVATION-PEER');importFacts=request('scene-facts-request',minimumWatermark='0');check('importedPeerExactNativeSubject',any(row['incarnation']==importPeer and row['application']==unrelated['class'] and row['geometry']==[440,80,320,240] for row in importFacts['facts']['windows']))
   importControl=s.host.runtime/'imported-witness-control';writeControl(importControl,'hold')
   importWitness=s.host.launch('imported-native-witness',[pre['importedWitness'],str(config),subject,importPeer,str(importControl),str(private/'imported-native-pixels')],env=env)
   def importSamples():return [json.loads(line) for line in (private/'imported-native-witness.log').read_text().splitlines() if line.startswith('{')]
   ready=wait(lambda:next((row for row in importSamples() if row['stage']=='ready'),None));imports=[row for row in importSamples() if row['stage'].startswith('imported-')]
   check('importedTwoActualEarlyNativeRetirements',len(imports)==2 and all(row['nativeRegistryAbsent'] and row['status']['exportReleased'] and row['status']['producerRetired'] and not row['status']['mappedFDClosed'] and int(row['status']['charge'])>0 for row in imports),samples=imports)
   check('importedOneGrantOneBrokerDistinctSubjects',ready['first']['records']==2 and ready['second']['records']==2 and ready['first']['charge']==ready['second']['charge'] and ready['first']['job']['binding']==ready['second']['job']['binding'] and ready['first']['job']['context']['incarnation']==subject and ready['second']['job']['context']['incarnation']==importPeer and subject!=importPeer,status=ready)
   first=decodeSnapshot('imported-first',private/'imported-native-pixels.1.png');second=decodeSnapshot('imported-second',private/'imported-native-pixels.2.png')
   check('importedFirstClientPixelsExcludePeer',first['width']==320 and first['height']==240 and first['blue']==64*48 and first['green']==0 and first['red']==320*240-64*48,pixels=first)
   check('importedSecondPeerPixelsExcludeFirst',second['width']==320 and second['height']==240 and second['points']['root']==[0,255,0,255] and second['green']>0 and second['red']==0 and second['blue']==0,pixels=second)
   r['importedPixels']={'first':first,'second':second,'hardwarePresentation':False}
   def importedEffect(operation,tag="imported"):
    global effectSequence
    effectSequence+=1;facts=request('scene-facts-request',minimumWatermark='0');intent={'request':str(effectSequence),'generation':str(effectSequence),'incarnation':subject,'operation':operation,'context':{'lifetime':attached['binding']['lifetime'],'epoch':attached['binding']['frontend'],'output':facts['outputGeneration'],'revision':facts['revision']}}
    result=observe({'protocolVersion':3,'kind':'window-effect','binding':attached['binding'],'effectProtocol':1,'intent':intent});check(tag+operation.title()+'ExactNativeEffect',result.get('kind')=='effect-outcome' and result['binding']==attached['binding'] and result['intent']==intent and result['status']=='Committed' and result['reason']=='applied',reply=result);return result
   importedEffect('minimize');stoppedImported=sourceScope();check('importedActualNativeSourceStopped',stoppedImported['present'] and not stoppedImported['sourceLive'],scope=stoppedImported)
   writeControl(importControl,'stopped');historical=wait(lambda:next((row for row in importSamples() if row['stage']=='historical'),None));check('importedOriginalHistoricalJobAndMapping',historical['first']['job']==ready['first']['job'] and int(historical['first']['charge'])>0 and not historical['first']['mappedFDClosed'] and historical['first']['producerRetired'],sample=historical)
   importLock=beginLock('imported-session-lock');writeControl(importControl,'deny');denied=wait(lambda:next((row for row in importSamples() if row['stage']=='native-uri-denied-before-policy'),None))
   check('importedBothNativeURIGuardsBeforePolicy',all(denied[name]['job']==ready[name]['job'] and int(denied[name]['charge'])>0 and not denied[name]['mappedFDClosed'] and denied[name]['producerRetired'] for name in ['first','second']),sample=denied)
   writeControl(importControl,'finish');importWitness.wait(timeout=5);check('importedWitnessNormalExit',importWitness.returncode==0)
   held=next(row for row in importSamples() if row['stage']=='held-cleanup');physical=next(row for row in importSamples() if row['stage']=='physical-retired');complete=next(row for row in importSamples() if row['stage']=='complete')
   check('importedHeldReadersRetainPhysicalCharge',held['first']['records']==2 and held['second']['records']==2 and all(int(held[name]['charge'])>0 and not held[name]['mappedFDClosed'] for name in ['first','second']),sample=held)
   check('importedLocalPhysicalRetirementBeforeACK',physical['first']['charge']=='0' and physical['first']['records']==2 and all(physical[name]['mappedFDClosed'] and physical[name]['producerRetired'] and physical[name]['job']==ready[name]['job'] for name in ['first','second']),sample=physical)
   check('importedExactACKsEmptySharedBroker',all(complete[name]['charge']=='0' and complete[name]['records']==0 for name in ['first','second']),sample=complete)
   writeControl(lockControl,'unlock');locker.wait(timeout=5);check('importedSessionLockNormalUnlockExit',locker.returncode==0 and any(row['event']=='unlock-synced' for row in importLock()))
   importedEffect('restore');check('importedActualSourceRestored',sourceScope()['sourceLive'])
   # Native per-entry resumption on the same Broker while the sibling reader remains physically held.
   command('child-blue');asymmetricControl=s.host.runtime/'asymmetric-witness-control';writeControl(asymmetricControl,'hold')
   importControl=asymmetricControl;importWitness=s.host.launch('asymmetric-native-witness',[pre['asymmetricWitness'],str(config),subject,importPeer,str(asymmetricControl),str(private/'asymmetric-native-pixels')],env=env)
   def asymmetricSamples():return [json.loads(line) for line in (private/'asymmetric-native-witness.log').read_text().splitlines() if line.startswith('{')]
   asymmetricReady=wait(lambda:next((row for row in asymmetricSamples() if row['stage']=='ready'),None));originalFirst=asymmetricReady['first']['job'];originalSecond=asymmetricReady['second']['job']
   check('asymmetricNativeBothOriginalChargedMappings',asymmetricReady['first']['records']==2 and all(int(asymmetricReady[name]['charge'])>0 and not asymmetricReady[name]['mappedFDClosed'] and asymmetricReady[name]['producerRetired'] for name in ['first','second']),sample=asymmetricReady)
   initialPixels=decodeSnapshot('asymmetric-original-first',private/'asymmetric-native-pixels.1.png');siblingPixels=decodeSnapshot('asymmetric-original-sibling',private/'asymmetric-native-pixels.2.png');check('asymmetricActualOriginalDistinctSourcePixels',initialPixels['blue']==64*48 and initialPixels['red']==320*240-64*48 and initialPixels['green']==0 and siblingPixels['green']>0 and siblingPixels['red']==0 and siblingPixels['blue']==0,pixels=[initialPixels,siblingPixels])
   writeControl(asymmetricControl,'retire-first');firstACKed=wait(lambda:next((row for row in asymmetricSamples() if row['stage']=='first-acked-sibling-held'),None))
   readerBlocked=next(row for row in asymmetricSamples() if row['stage']=='own-reader-blocked');journalBlocked=next(row for row in asymmetricSamples() if row['stage']=='own-journal-blocked')
   check('asymmetricOwnHeldReaderBlocksResume',readerBlocked['first']['job']==originalFirst and not readerBlocked['first']['mappedFDClosed'] and readerBlocked['first']['records']==2 and readerBlocked['second']['job']==originalSecond,sample=readerBlocked)
   check('asymmetricOwnTerminalJournalBlocksResume',journalBlocked['first']['job']==originalFirst and journalBlocked['first']['mappedFDClosed'] and journalBlocked['first']['records']==2 and not journalBlocked['second']['mappedFDClosed'] and int(journalBlocked['second']['charge'])>0,sample=journalBlocked)
   check('asymmetricExactFirstACKLeavesHeldSibling',firstACKed['first']['records']==1 and firstACKed['first']['mappedFDClosed'] and firstACKed['second']['job']==originalSecond and not firstACKed['second']['mappedFDClosed'] and int(firstACKed['second']['charge'])>0,sample=firstACKed)
   command('child-yellow');writeControl(asymmetricControl,'resume-first');resumed=wait(lambda:next((row for row in asymmetricSamples() if row['stage']=='resumed-first-sibling-held'),None));demand=next(row for row in asymmetricSamples() if row['stage']=='resumed-demand');newJob=resumed['first']['job'];seed=next(event for event in demand['events'] if event['kind']=='source-seed');requested=next(event['event']['trigger'] for event in demand['events'] if event['kind']=='event' and event['event']['kind']=='request')
   check('asymmetricNewRequestRetainsNativeGrantClock',newJob['binding']==requested['binding'] and newJob['context']==requested['context'] and newJob['deadline']==requested['deadline'] and newJob['binding']==originalFirst['binding'] and newJob['clock']==originalFirst['clock'] and newJob['context']['incarnation']==subject and newJob['request']=='2' and newJob['origin']=='2' and seed['lease']=='2' and seed['identity']=='family:'+subject,sample=demand)
   check('asymmetricNewOriginalNativeTwoSecondDeadline',int(newJob['deadline'])>int(originalFirst['deadline']) and int(newJob['deadline'])==int(seed['source']['scope']['now'])+2000000000,sample=demand)
   check('asymmetricSiblingStillOriginalChargedHeld',resumed['first']['records']==2 and resumed['second']['job']==originalSecond and not resumed['second']['mappedFDClosed'] and int(resumed['second']['charge'])>0,sample=resumed)
   nativeImports=[row for row in asymmetricSamples() if row['stage'].startswith('imported-')];oldFrame=nativeImports[0]['events'][1]['event']['frame'];siblingFrame=nativeImports[1]['events'][1]['event']['frame'];newFrame=nativeImports[2]['events'][1]['event']['frame']
   check('asymmetricNewTokenCannotAliasEitherOriginal',newFrame['job']==newJob and len({oldFrame['handle'],siblingFrame['handle'],newFrame['handle']})==3 and siblingFrame['job']==originalSecond,frames=[oldFrame,siblingFrame,newFrame])
   newPixels=decodeSnapshot('asymmetric-new-first',private/'asymmetric-native-pixels.1.request-2.png');check('asymmetricRealNativeChangedPixelsExcludeSibling',newPixels['width']==320 and newPixels['height']==240 and newPixels['yellow']==64*48 and newPixels['blue']==0 and newPixels['green']==0 and newPixels['red']==320*240-64*48,pixels=newPixels)
   writeControl(asymmetricControl,'finish-resume');importWitness.wait(timeout=5);check('asymmetricWitnessNormalExit',importWitness.returncode==0)
   asymmetricHeld=next(row for row in asymmetricSamples() if row['stage']=='asymmetric-held-cleanup');asymmetricPhysical=next(row for row in asymmetricSamples() if row['stage']=='asymmetric-physical-retired');asymmetricComplete=next(row for row in asymmetricSamples() if row['stage']=='asymmetric-complete')
   check('asymmetricBothFinalHeldReadersRetainCharge',asymmetricHeld['first']['records']==2 and all(int(asymmetricHeld[name]['charge'])>0 and not asymmetricHeld[name]['mappedFDClosed'] for name in ['first','second']),sample=asymmetricHeld)
   check('asymmetricPhysicalDrainPrecedesExactACK8And9',asymmetricPhysical['first']['records']==2 and asymmetricPhysical['first']['charge']=='0' and all(asymmetricPhysical[name]['mappedFDClosed'] and asymmetricPhysical[name]['producerRetired'] for name in ['first','second']) and asymmetricPhysical['first']['job']==newJob and asymmetricPhysical['second']['job']==originalSecond,sample=asymmetricPhysical)
   check('asymmetricExactACKsEmptyOwnerBeforeNormalClose',all(asymmetricComplete[name]['records']==0 and asymmetricComplete[name]['charge']=='0' for name in ['first','second']),sample=asymmetricComplete)
   command('child-blue')
   # Both same-application roots are admitted by one real Elm picker gate.
   guiFacts=request('scene-facts-request',minimumWatermark='0');guiCompanions=[row['incarnation'] for row in guiFacts['facts']['windows'] if row['application']=='warlock-child-probe' and row['incarnation']!=subject];check('guiImportedDistinctOwnCompanion',len(guiCompanions)==1)
   guiOther=guiCompanions[0];fullLogName='full-imported-gui'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-imported',subject,guiOther,'--qa-preview-snapshot',str(private/'gui-imported-webkit.png')],env=env)
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('guiImportedPointerTargetInOutput',0<x<800 and 0<y<48)
   pointerLog=private/'gui-imported-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='gui-imported-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('guiImportedPointerNormalExit',ptr.returncode==0)
   wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   seeds=[event for event in events() if event['kind']=='source-seed'];offers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];check('guiImportedTwoNativeSeedAndPacketOwners',len(seeds)==2 and len(offers)==2 and {seed['identity'] for seed in seeds}=={'family:'+subject,'family:'+guiOther} and seeds[0]['publication']==seeds[1]['publication'] and seeds[0]['lease']==seeds[1]['lease'],seeds=seeds,offers=offers)
   commands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')]
   acquire=[command for command in commands if command['kind']=='acquire'];check('guiImportedActualElmAcquireBothExactJobs',len(acquire)==2 and {json.dumps(command['job'],sort_keys=True) for command in acquire}=={json.dumps(frame['job'],sort_keys=True) for frame in offers},commands=acquire)
   check('guiImportedOneBindingNativeClockOriginalDeadlines',offers[0]['job']['binding']==offers[1]['job']['binding'] and offers[0]['job']['clock']==offers[1]['job']['clock'] and offers[0]['handle']!=offers[1]['handle'] and all(frame['job']['request']=='1' and frame['job']['origin']==seed['lease'] and int(frame['job']['deadline'])==int(seed['source']['scope']['now'])+2000000000 and frame['job']['context']==seed['source']['scope']['context'] for frame in offers for seed in seeds if seed['identity']=='family:'+frame['job']['context']['incarnation']))
   imageRows=[json.loads(line[len('native-imported-image: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-image: ')]
   check('guiImportedTwoActualLoadedOwnedURIs',imageRows and any(len(rows)==2 and {row['uri'] for row in rows}=={'elm-shell://preview/'+frame['handle'] for frame in offers} and all(row['complete'] and row['naturalWidth']==320 and row['naturalHeight']==240 and row['width']==160 and row['height']==120 for row in rows) for rows in imageRows),images=imageRows)
   guiPixels=decodeSnapshot('gui-imported',private/'gui-imported-webkit.png');check('guiImportedVisibleBothSourcePixelsExcludePeer',guiPixels['blue']==32*24 and guiPixels['red']>=2*160*120-32*24 and guiPixels['green']==0,pixels=guiPixels);r['guiImportedPixels']={'pixels':guiPixels,'hardwarePresentation':False}
   wait(lambda:'native-imported-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   commands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')];releases=[command['frame'] for command in commands if command['kind']=='release'];acksImported=[json.loads(line[len('native-imported-ack: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')]
   check('guiImportedBothExactElmReleaseAndFinalACK',len(releases)==2 and {json.dumps(frame['job'],sort_keys=True) for frame in releases}=={json.dumps(frame['job'],sort_keys=True) for frame in offers} and len(acksImported)==2 and {ack['sequence'] for ack in acksImported}=={'5','6'} and {json.dumps(ack['job'],sort_keys=True) for ack in acksImported}=={json.dumps(frame['job'],sort_keys=True) for frame in offers},releases=releases,acks=acksImported)
   importedStatus=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   check('guiImportedActualPhysicalBeforeTerminalACK',any(all(row['charge']=='0' and row['mappedFDClosed'] and row['producerRetired'] for row in rows) for rows in importedStatus) and fullLog().index('native-imported-command: {\"kind\":\"release\"')<fullLog().index('native-imported-ack:')<fullLog().index('native-imported-complete:'),status=importedStatus)
   # A new actual picker lease resumes both entries only after exact original ACKs.
   firstJobs={frame['job']['context']['incarnation']:frame for frame in offers}
   before=logs()[-1];changed=command('child-yellow');check('guiResumedActualChildOnlyChange',changed['rootCommits']==before['rootCommits'] and changed['childCommits']==before['childCommits']+1)
   pointerLog=private/'gui-resumed-dismiss-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='gui-resumed-dismiss-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(b'move 10 550\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',timeout=5);check('guiResumedDismissPointerNormalExit',ptr.returncode==0)
   wait(lambda:'surface-popup-closed: lease='+seeds[0]['lease'] in fullLog());check('guiResumedOriginalPickerActuallyClosed','surface-popup-closed: lease='+seeds[0]['lease'] in fullLog())
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('guiResumedReopenTargetInOutput',0<x<800 and 0<y<48)
   pointerLog=private/'gui-resumed-reopen-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='gui-resumed-reopen-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('guiResumedReopenPointerNormalExit',ptr.returncode==0)
   secondSnapshot=private/'gui-imported-webkit.png.request-2.png';wait(lambda:'native-client-webkit-snapshot-job: request=2 path='+str(secondSnapshot) in fullLog())
   allOffers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];newOffers=[frame for frame in allOffers if frame['job']['request']=='2'];freshSeeds=[event for event in events() if event['kind']=='source-seed' and int(event['lease'])>int(seeds[0]['lease'])]
   check('guiResumedExactlyFourDistinctOwnedPackets',len(allOffers)==4 and len(newOffers)==2 and len(freshSeeds)==2 and {seed['identity'] for seed in freshSeeds}=={'family:'+member for member in firstJobs} and len({frame['handle'] for frame in allOffers})==4 and {frame['job']['context']['incarnation'] for frame in newOffers}==set(firstJobs),offers=allOffers,seeds=freshSeeds)
   check('guiResumedSameAuthorityAndNewOriginalNativeDeadlines',all(frame['job']['binding']==firstJobs[frame['job']['context']['incarnation']]['job']['binding'] and frame['job']['clock']==firstJobs[frame['job']['context']['incarnation']]['job']['clock'] and frame['job']['origin']==seed['lease'] and frame['job']['context']==seed['source']['scope']['context'] and int(frame['job']['deadline'])==int(seed['source']['scope']['now'])+2000000000 and int(seed['source']['scope']['observation'])>int(oldSeed['source']['scope']['observation']) and int(seed['source']['requestId'])>int(oldSeed['source']['requestId']) for frame in newOffers for seed in freshSeeds for oldSeed in seeds if seed['identity']==oldSeed['identity']=='family:'+frame['job']['context']['incarnation']))
   commands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')];newAcquire=[command for command in commands if command['kind']=='acquire' and command['job']['request']=='2']
   check('guiResumedActualElmAcquiresBothNewJobs',len(newAcquire)==2 and {json.dumps(command['job'],sort_keys=True) for command in newAcquire}=={json.dumps(frame['job'],sort_keys=True) for frame in newOffers},commands=newAcquire)
   firstACKEnd=max(fullLog().index('native-imported-ack: '+json.dumps(ack,separators=(',',':'))) for ack in acksImported)
   check('guiResumedOwnOriginalACKBeforeNewAcquire',firstACKEnd<fullLog().index('native-imported-resume:')<min(fullLog().index('native-imported-command: '+json.dumps(command,separators=(',',':'))) for command in newAcquire))
   images=[json.loads(line[len('native-imported-image: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-image: ')]
   check('guiResumedBothNewOwnedURIAndDimensions',any(len(rows)==2 and {row['uri'] for row in rows}=={'elm-shell://preview/'+frame['handle'] for frame in newOffers} and all(row['complete'] and row['naturalWidth']==320 and row['naturalHeight']==240 and row['width']==160 and row['height']==120 for row in rows) for rows in images))
   newPixels=decodeSnapshot('gui-resumed',secondSnapshot);check('guiResumedVisibleNewYellowBothSourcesExcludePeer',newPixels['yellow']==32*24 and newPixels['blue']==0 and newPixels['green']==0 and newPixels['red']>=2*160*120-32*24,pixels=newPixels);r['guiResumedPixels']={'original':guiPixels,'new':newPixels,'hardwarePresentation':False}
   wait(lambda:fullLog().rfind('native-imported-complete: physical=0 journal=0 previewEligible=0')>fullLog().rfind('native-imported-ack:') and len([line for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')])==4)
   allACKs=[json.loads(line[len('native-imported-ack: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')];lastACKs=[ack for ack in allACKs if ack['job']['request']=='2'];allReleases=[command['frame'] for command in [json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')] if command['kind']=='release'];newReleases=[frame for frame in allReleases if frame['job']['request']=='2']
   check('guiResumedBothExactFinalReleaseACK11And12',len(allACKs)==4 and len(lastACKs)==2 and {ack['sequence'] for ack in lastACKs}=={'11','12'} and len(newReleases)==2 and {json.dumps(frame['job'],sort_keys=True) for frame in newReleases}=={json.dumps(frame['job'],sort_keys=True) for frame in newOffers} and {json.dumps(ack['job'],sort_keys=True) for ack in lastACKs}=={json.dumps(frame['job'],sort_keys=True) for frame in newOffers},acks=lastACKs,releases=newReleases)
   status=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   check('guiResumedActualNewPhysicalBeforeFinalACK',any(all(row['job']['request']=='2' and row['charge']=='0' and row['mappedFDClosed'] and row['producerRetired'] for row in rows) for rows in status) and max(fullLog().index('native-imported-ack: '+json.dumps(ack,separators=(',',':'))) for ack in lastACKs)<fullLog().rindex('native-imported-complete:'))
   web.terminate();web.wait(timeout=5);check('guiImportedFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native imported teardown incomplete:' not in fullLog())
   # Reopen the actual shared picker under a new lease after native source minimization.
   command('child-blue');fullLogName='full-imported-historical'
   historicalPNG=private/'gui-shared-historical.png'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-imported',subject,guiOther,'--qa-preview-snapshot',str(historicalPNG)],env=env)
   def sharedHistoricalPointer(tag):
    target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check(tag+'TargetInOutput',0<x<800 and 0<y<48)
    pointerLog=private/(tag+'-pointer.log')
    with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
    record=host.original.process(ptr.pid);record.update(name=tag+'-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
    ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check(tag+'PointerNormalExit',ptr.returncode==0)
   sharedHistoricalPointer('sharedHistoricalOpen')
   wait(lambda:'native-client-webkit-snapshot-job: request=1 path='+str(historicalPNG) in fullLog())
   historicalOffers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];historicalSeeds=[event for event in events() if event['kind']=='source-seed'];originals={frame['job']['context']['incarnation']:frame for frame in historicalOffers}
   check('sharedHistoricalTwoOriginalOwnedSources',len(historicalOffers)==2 and len(historicalSeeds)==2 and set(originals)=={subject,guiOther} and {seed['identity'] for seed in historicalSeeds}=={'family:'+subject,'family:'+guiOther} and len({frame['handle'] for frame in historicalOffers})==2,offers=historicalOffers,seeds=historicalSeeds)
   importedEffect('minimize','sharedHistorical');nativeStopped=sourceScope();check('sharedHistoricalActualNativeSourceStopped',nativeStopped['present'] and not nativeStopped['sourceLive'] and not nativeStopped['locked'] and nativeStopped['gpuReady'],scope=nativeStopped)
   sharedHistoricalPointer('sharedHistoricalReopen')
   def stoppedSharedSeed():return next((event for event in events() if event['kind']=='source-seed' and event['identity']=='family:'+subject and not event['source']['scope']['sourceLive'] and int(event['lease'])>int(historicalSeeds[0]['lease'])),None)
   newHistoricalSeed=wait(stoppedSharedSeed);reopenedStopped=sourceScope()
   check('sharedHistoricalNewLeaseOwnNativeScope',newHistoricalSeed['source']['binding']==originals[subject]['job']['binding'] and newHistoricalSeed['source']['previewEligible'] is False and newHistoricalSeed['source']['scope']['context']==reopenedStopped['context'] and reopenedStopped['present'] and not reopenedStopped['sourceLive'] and int(reopenedStopped['context']['scene'])>=int(nativeStopped['context']['scene']) and int(reopenedStopped['context']['content'])>=int(nativeStopped['context']['content']) and newHistoricalSeed['source']['scope']['clock']==originals[subject]['job']['clock'] and int(newHistoricalSeed['lease'])>int(originals[subject]['job']['origin']),seed=newHistoricalSeed)
   def historicalSharedReport():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in rows if row['body']['publication']==newHistoricalSeed['publication'] and row['body']['lease']==newHistoricalSeed['lease'] and 'Historical preview' in row['body']['text']),None)
   historicalDisplay=wait(historicalSharedReport);check('sharedHistoricalActualElmLabelAndNewLease',historicalDisplay is not None,report=historicalDisplay)
   retainedSnapshot=private/'gui-shared-historical.png.request-2.png';wait(lambda:'native-client-webkit-snapshot-job: request=2 path='+str(retainedSnapshot) in fullLog())
   retainedPixels=decodeSnapshot('shared-historical-visible',retainedSnapshot);check('sharedHistoricalVisibleOriginalPixelsExcludePeer',retainedPixels['blue']==32*24 and retainedPixels['yellow']==0 and retainedPixels['green']==0 and retainedPixels['red']>=2*160*120-32*24,pixels=retainedPixels)
   onlyOffers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer'];commands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')];acquires=[command['job'] for command in commands if command['kind']=='acquire']
   check('sharedHistoricalNoRecaptureRenewalOrPrematureRelease',onlyOffers==historicalOffers and len(acquires)==2 and {json.dumps(job,sort_keys=True) for job in acquires}=={json.dumps(frame['job'],sort_keys=True) for frame in historicalOffers} and not any(command['kind']=='release' for command in commands) and 'native-imported-resume:' not in fullLog(),commands=commands)
   images=[json.loads(line[len('native-imported-image: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-image: ')]
   check('sharedHistoricalExactOriginalOpaqueURIsAndSizes',images and all(len(rows)==2 and {row['uri'] for row in rows}=={'elm-shell://preview/'+frame['handle'] for frame in historicalOffers} and all(row['complete'] and row['naturalWidth']==320 and row['naturalHeight']==240 and row['width']==160 and row['height']==120 for row in rows) for rows in images),images=images)
   ownershipShared=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   check('sharedHistoricalRetainsOriginalPhysicalSharedMappings',any(len(rows)==2 and all(row['job']==originals[row['job']['context']['incarnation']]['job'] and row['records']==2 and int(row['charge'])>0 and not row['mappedFDClosed'] and row['producerRetired'] for row in rows) for rows in ownershipShared),status=ownershipShared)
   refused=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(nativeStopped['now'])+2000000000),context=nativeStopped['context']);check('sharedHistoricalNativeRefusesNewStoppedCapture',refused.get('kind')=='refused' and refused.get('reason')=='preview-client-source-unavailable',reply=refused)
   wait(lambda:'native-imported-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   expired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired'];check('sharedHistoricalOriginalPacketExpiryPreserved',len(expired)==2 and all(frame['job']==originals[frame['job']['context']['incarnation']]['job'] and frame['handle']==originals[frame['job']['context']['incarnation']]['handle'] and frame['expires']==originals[frame['job']['context']['incarnation']]['expires'] for frame in expired),frames=expired)
   commands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')];releases=[command['frame'] for command in commands if command['kind']=='release'];acksHistorical=[json.loads(line[len('native-imported-ack: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')]
   check('sharedHistoricalExactElmReleaseFinalACK5And6',len(releases)==2 and len(acksHistorical)==2 and {ack['sequence'] for ack in acksHistorical}=={'5','6'} and {json.dumps(frame['job'],sort_keys=True) for frame in releases}=={json.dumps(frame['job'],sort_keys=True) for frame in historicalOffers} and {json.dumps(ack['job'],sort_keys=True) for ack in acksHistorical}=={json.dumps(frame['job'],sort_keys=True) for frame in historicalOffers},releases=releases,acks=acksHistorical)
   finalOwnership=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   check('sharedHistoricalPhysicalDrainBeforeFinalACK',any(all(row['charge']=='0' and row['mappedFDClosed'] and row['producerRetired'] for row in rows) for rows in finalOwnership) and fullLog().index('native-imported-command: {"kind":"release"')<fullLog().index('native-imported-ack:')<fullLog().index('native-imported-complete:'),status=finalOwnership)
   web.terminate();web.wait(timeout=5);check('sharedHistoricalFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native imported teardown incomplete:' not in fullLog())
   importedEffect('restore','sharedHistorical');check('sharedHistoricalOriginalNativeSourceRestored',sourceScope()['sourceLive'])
   # A real independent xdg_popup has a separate role and configure/commit lifecycle.
   def popupSnapshot(name):
    observed=request('preview-capture-probe-scope-request',subjectIncarnation=subject);check(name+'OwnUnqualifiedSnapshotScope',observed.get('kind')=='preview-capture-probe-scope' and observed['previewEligible'] is False and observed['scope']['binding']==attached['binding'],reply=observed)
    scope=observed['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-capture-probe-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context']);check(name+'ActualOwningRendererSnapshot',captured.get('kind')=='preview-capture-probe-owned' and captured['previewEligible'] is False and captured['planeSpace']=='monitor-physical-unqualified',reply=captured)
    h,rights=exchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     check(name+'ExactNativeSnapshotFD',h[22]==7 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[800,600],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'SealedSnapshotPNG',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'ImmutableSnapshotChecksum',zlib.crc32(blob)==h[17]);image=private/(name+'.png');image.write_bytes(blob);image.chmod(0o600)
     pixels=decodeSnapshot(name,image)
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Snapshot descriptor unexpectedly live')
    except OSError as error:check(name+'PhysicalSnapshotFDClosed',error.errno==9)
    released,_=exchange(2,captured['captureRequest'],h[16]);check(name+'SnapshotExportReleased',released[16]==h[16]);retired=request('preview-capture-probe-retire-request');check(name+'SnapshotNativeProducerRetired',retired.get('kind')=='preview-capture-probe-retired' and retired['ownedBytes']=='0');return pixels,scope
   def popupNativeScope():
    value=request('preview-popup-scope-request',subjectIncarnation=subject)
    assert value.get('kind')=='preview-popup-scope' and value['previewEligible'] is False and value['scopeKind']=='isolated-root-popup-unqualified',value
    scope=value['scope'];assert scope['binding']==attached['binding'] and scope['clock']==attached['binding']['lifetime'] and scope['present'] and scope['sourceLive'] and not scope['locked'] and scope['gpuReady']
    assert scope['context']['incarnation']==subject and int(value['maximumTransferBytes'])>800*600*4
    return scope
   def popupCapture(name,scope):
    deadline=int(scope['now'])+2000000000
    captured=request('preview-popup-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'ExactTypedPopupCapture',captured.get('kind')=='preview-popup-owned' and captured['previewEligible'] is False and captured['planeSpace']=='root-popup-monitor-unqualified',reply=captured)
    state=request('preview-popup-state-request');check(name+'TypedStateMatchesCapture',state.get('kind')=='preview-popup-owned' and state['captureRequest']==captured['captureRequest'])
    old=request('preview-capture-probe-state-request');check(name+'RootStateDoesNotAliasPopup',old.get('reason')=='preview-probe-unavailable')
    old=request('preview-capture-probe-retire-request');check(name+'RootRetireCannotErasePopup',old.get('reason')=='preview-probe-plane-mismatch')
    old=request('preview-client-retire-request');check(name+'ClientRetireCannotErasePopup',old.get('reason')=='preview-client-plane-mismatch')
    h,rights=exchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];check(name+'ExactNewPlaneAndNativeContext',h[22]==19 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[800,600] and h[3]==int(context['lifetime']) and h[8]==int(context['incarnation']) and [h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['output','privacy','rendering','scene','content']],header=list(h),scope=scope)
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualSealedPopupFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'ActualPopupChecksum',zlib.crc32(blob)==h[17]);image=private/(name+'.png');image.write_bytes(blob);image.chmod(0o600);pixels=decodeSnapshot(name,image)
     held=request('preview-popup-retire-request');check(name+'NativeHeldExportRefusesRetirement',held.get('reason')=='preview-probe-import-outstanding')
     r['popupCaptureSamples'].append({'name':name,'scope':scope,'header':list(h),'pixels':pixels,'hardwarePresentation':False,'previewEligible':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Popup snapshot descriptor unexpectedly live')
    except OSError as error:check(name+'PhysicalPopupFDClosed',error.errno==9)
    released,_=exchange(2,captured['captureRequest'],h[16]);check(name+'ExactPopupExportReleased',released[16]==h[16]);retired=request('preview-popup-retire-request');check(name+'NativePopupProducerRetired',retired.get('kind')=='preview-popup-retired' and retired['ownedBytes']=='0')
    return pixels
   def popupStale(name,old):
    now=popupNativeScope();value=request('preview-popup-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(now['now'])+2000000000),context=old['context'])
    check(name+'OldPopupContextRefused',value.get('reason')=='preview-probe-context-stale',reply=value,old=old,current=now)
    state=request('preview-popup-state-request');check(name+'NoAcceptedPopupProducer',state.get('reason')=='preview-probe-unavailable')
   def familyNativeScope():
    value=request('preview-family-scope-request',subjectIncarnation=subject)
    assert value.get('kind')=='preview-family-scope' and value['previewEligible'] is False and value['scopeKind']=='isolated-root-popup-modal-unqualified',value
    scope=value['scope'];assert scope['binding']==attached['binding'] and scope['clock']==attached['binding']['lifetime'] and scope['context']['incarnation']==subject and scope['present'] and scope['sourceLive'] and not scope['locked'] and scope['gpuReady']
    rows=value['members'];assert 1<=len(rows)<=256 and len({row['incarnation'] for row in rows})==len(rows)
    roots=[row for row in rows if row['parent'] is None];assert len(roots)==1 and roots[0]['incarnation']==subject
    for row in rows:assert int(row['content'])>0 and 0<=row['renderOrder']<256 and 0<=row['flags']<256 and len(row['geometry'])==8
    return value
   def familyAdvanced(name,old):
    fresh=familyNativeScope();check(name+'NativeFamilyContentAdvances',int(fresh['scope']['context']['content'])>int(old['scope']['context']['content']) and fresh['scope']['clock']==old['scope']['clock'] and fresh['scope']['binding']==old['scope']['binding'],before=old,after=fresh);return fresh
   familyRoot=familyNativeScope();familyRepeated=familyNativeScope();check('familyObserverRepeatedRootStable',familyRepeated['scope']['context']==familyRoot['scope']['context'] and familyRepeated['members']==familyRoot['members'] and int(familyRepeated['scope']['observation'])>int(familyRoot['scope']['observation']),before=familyRoot,after=familyRepeated)
   foreign=dict(attached['binding']);foreign['session']=str(int(foreign['session'])+1)
   refused=request('preview-family-scope-request',binding=foreign,subjectIncarnation=subject);check('familyObserverForeignGrantRefused',refused.get('reason')=='binding-mismatch',reply=refused)
   refused=request('preview-family-scope-request',subjectIncarnation=subject,members=familyRoot['members']);check('familyObserverFrontendMembershipRefused',refused.get('reason')=='preview-client-schema',reply=refused)
   popupBase=popupNativeScope();popupRepeated=popupNativeScope()
   check('popupObserverStableRootContextAndNativeClock',popupRepeated['context']==popupBase['context'] and int(popupRepeated['observation'])>int(popupBase['observation']) and int(popupRepeated['now'])>=int(popupBase['now']),before=popupBase,after=popupRepeated)
   foreign=dict(attached['binding']);foreign['session']=str(int(foreign['session'])+1)
   refused=request('preview-popup-scope-request',binding=foreign,subjectIncarnation=subject)
   check('popupObserverForeignGrantRefused',refused.get('reason')=='binding-mismatch',reply=refused)
   refused=request('preview-popup-scope-request',subjectIncarnation=subject,context=popupBase['context'])
   check('popupObserverExtraContextRefused',refused.get('reason')=='preview-client-schema',reply=refused)
   popupBefore=logs()[-1];command('popup-create');popupConfigured=wait(lambda:next((row for row in logs() if row['event']=='popup-configured'),None))
   check('familyPopupActualConfigureACKAndPixels',popupConfigured['popupSerial']>0 and popupConfigured['popupCommits']==2 and popupConfigured['popupGeometry']==[291,211,64,48] and any(row['event']=='popup-buffercommit' and row['popupSerial']==popupConfigured['popupSerial'] and row['popupColor']==0xff00ffff for row in logs()),sample=popupConfigured)
   check('familyPopupExtendsBeyondRootClientCrop',popupConfigured['popupGeometry'][0]+popupConfigured['popupGeometry'][2]>320 and popupConfigured['popupGeometry'][1]+popupConfigured['popupGeometry'][3]>240)
   familyPopupCreated=familyAdvanced('familyPopupMap',familyRoot)
   popupCreated=popupNativeScope();check('popupObserverActualMapAdvancesContent',int(popupCreated['context']['content'])>int(popupBase['context']['content']),before=popupBase,after=popupCreated)
   cyanSnapshot,cyanScope=popupSnapshot('family-popup-cyan-snapshot');check('familyPopupActualInclusiveCyanPixelsExcludePeer',cyanSnapshot['cyan']==64*48 and cyanSnapshot['blue']==64*48 and cyanSnapshot['green']==0,pixels=cyanSnapshot)
   popupCyan=popupCapture('popup-bound-cyan',popupNativeScope());check('popupBoundActualCyanPixels',popupCyan['cyan']==64*48 and popupCyan['blue']==64*48 and popupCyan['green']==0,pixels=popupCyan)
   popupScope=sourceScope();popupClient=capture('family-popup-client-boundary',popupScope)
   check('familyPopupNotPromotedIntoUnqualifiedClientImage',popupClient['width']==320 and popupClient['height']==240 and popupClient['cyan']==0 and popupClient['yellow']==0 and popupClient['blue']==64*48 and popupClient['green']==0 and popupClient['red']==320*240-64*48,pixels=popupClient)
   previousPopup=next(row for row in reversed(logs()) if row['event']=='popup-buffercommit');command('popup-yellow');changedPopup=wait(lambda:next((row for row in logs() if row['event']=='popup-buffercommit' and row['popupColor']==0xffffff00),None))
   check('familyPopupOwnChangedCommitPreservesParentIdentity',changedPopup['popupSerial']==previousPopup['popupSerial'] and changedPopup['popupCommits']==previousPopup['popupCommits']+1 and changedPopup['rootCommits']==previousPopup['rootCommits'] and changedPopup['childCommits']==previousPopup['childCommits'],before=previousPopup,after=changedPopup)
   familyPopupPainted=familyAdvanced('familyPopupPaint',familyPopupCreated)
   popupChanged=popupNativeScope();check('popupObserverActualIndependentCommitAdvancesContent',int(popupChanged['context']['content'])>int(popupCreated['context']['content']),before=popupCreated,after=popupChanged)
   yellowSnapshot,yellowScope=popupSnapshot('family-popup-yellow-snapshot');check('familyPopupActualInclusiveChangedYellowPixelsExcludePeer',yellowSnapshot['yellow']==64*48 and yellowSnapshot['cyan']==0 and yellowSnapshot['blue']==64*48 and yellowSnapshot['green']==0,pixels=yellowSnapshot);r['popupSnapshotPixels']={'cyan':cyanSnapshot,'yellow':yellowSnapshot,'cyanScope':cyanScope,'yellowScope':yellowScope,'scope':'Actual own root/decor/popup snapshot on unqualified plane7; production complete family epochs/geometry/coverage and hardware separate','hardwarePresentation':False}
   popupStale('popupCommit',popupCreated);popupYellow=popupCapture('popup-bound-yellow',popupNativeScope());check('popupBoundActualChangedYellowPixels',popupYellow['yellow']==64*48 and popupYellow['cyan']==0 and popupYellow['blue']==64*48 and popupYellow['green']==0,pixels=popupYellow)
   command('popup-reposition');repositioned=wait(lambda:next((row for row in logs() if row['event']=='popup-repositioned'),None));movedPopup=wait(lambda:next((row for row in logs() if row['event']=='popup-configured' and row['popupGeometry']==[101,81,64,48]),None))
   check('familyPopupExactRepositionTokenAndReconfigure',repositioned['repositionToken']==1 and movedPopup['popupSerial']!=popupConfigured['popupSerial'] and movedPopup['popupCommits']==changedPopup['popupCommits']+1,token=repositioned,configured=movedPopup)
   familyPopupMoved=familyAdvanced('familyPopupMove',familyPopupPainted)
   popupMoved=popupNativeScope();check('popupObserverActualRepositionAdvancesContent',int(popupMoved['context']['content'])>int(popupChanged['context']['content']),before=popupChanged,after=popupMoved)
   popupStale('popupPosition',popupChanged);popupMovedPixels=popupCapture('popup-bound-moved',popupNativeScope());check('popupBoundActualRepositionedPixels',popupMovedPixels['yellow']==64*48 and popupMovedPixels['green']==0,pixels=popupMovedPixels)
   command('popup-destroy');destroyedPopup=wait(lambda:next((row for row in logs() if row['event']=='popup-destroyed'),None));check('familyPopupActualOrderedDestroyControl',destroyedPopup['controlSequence']==commandSequence and any(row['event']=='server-barrier' and row['command']=='popup-destroy' and row['barrierControl']==commandSequence for row in logs()),sample=destroyedPopup)
   familyPopupGone=familyAdvanced('familyPopupDestroy',familyPopupMoved)
   popupDestroyed=popupNativeScope();check('popupObserverActualDestroyAdvancesContent',int(popupDestroyed['context']['content'])>int(popupMoved['context']['content']),before=popupMoved,after=popupDestroyed)
   popupStale('popupDestroy',popupMoved);popupAbsent=popupCapture('popup-bound-absent',popupNativeScope());check('popupBoundActualDestroyedPixelsAbsent',popupAbsent['cyan']==0 and popupAbsent['yellow']==0 and popupAbsent['blue']==64*48 and popupAbsent['green']==0,pixels=popupAbsent)
   freshDeadline=popupNativeScope()
   for tag,value in [('elapsed',int(freshDeadline['now'])-1),('renewed',int(freshDeadline['now'])+4000000000)]:
    denied=request('preview-popup-scoped-request',subjectIncarnation=subject,deadlineNs=str(value),context=freshDeadline['context']);check('popupOriginalDeadline'+tag,denied.get('reason')=='preview-probe-deadline',reply=denied)
   replacedBefore=popupNativeScope();n=len(logs());command('popup-create');wait(lambda:any(row['event']=='popup-buffercommit' and row['popupColor']==0xff00ffff for row in logs()[n:]));popupStale('popupReplacement',replacedBefore);popupReplacement=popupCapture('popup-bound-replacement',popupNativeScope());check('popupBoundActualReplacementCyanPixels',popupReplacement['cyan']==64*48 and popupReplacement['yellow']==0 and popupReplacement['green']==0,pixels=popupReplacement);command('popup-destroy')
   for tracePath,traceHash in sorted(pre['popupTraces'].items()):
    check('popupTraceHash'+pathlib.Path(tracePath).stem,sha(tracePath)==traceHash)
    trace=json.loads(pathlib.Path(tracePath).read_text());before=None;steps=[]
    for index,state in enumerate(trace['states']):
     cmd=state['command'];prior=logs()[-1];startIndex=len(logs())
     if cmd not in ['reset','inspect']:
      command(cmd)
      if cmd=='popup-create':wait(lambda:any(row['event']=='popup-buffercommit' and row['popupColor']==0xff00ffff for row in logs()[startIndex:]))
      elif cmd=='popup-yellow':wait(lambda:any(row['event']=='popup-buffercommit' and row['popupColor']==0xffffff00 for row in logs()[startIndex:]))
      elif cmd=='popup-reposition':wait(lambda:any(row['event']=='popup-configured' and row['popupGeometry']==[101,81,64,48] for row in logs()[startIndex:]))
     scope=popupNativeScope();label='popup-model-'+pathlib.Path(tracePath).stem+'-'+str(index)
     if before is not None:
      current=int(scope['context']['content']);old=int(before['context']['content'])
      check(label+'NativeRevisionMatchesProjection',(current>old if state['changed'] else current==old),before=before,after=scope,projection=state)
      check(label+'OriginalNativeClockAndOwner',scope['clock']==before['clock'] and scope['binding']==before['binding'] and scope['context']['incarnation']==before['context']['incarnation'] and int(scope['now'])>=int(before['now']))
     check(label+'NoArtificialParentCommit',logs()[-1]['rootCommits']==prior['rootCommits'] and logs()[-1]['childCommits']==prior['childCommits'],before=prior,after=logs()[-1])
     steps.append({'index':index,'command':cmd,'modelState':state,'actualScope':scope,'fixture':logs()[-1]});before=scope
    r['popupRevisionReplay'].append({'trace':tracePath,'sha256':traceHash,'statesCompared':len(steps),'steps':steps})
   check('allFourSelectedNativePopupTracesReplayed',len(r['popupRevisionReplay'])==4)
   # Separate real xdg toplevel and dialog object; native parent/hint facts.
   def modalFacts():return request('scene-facts-request',minimumWatermark='0')
   def modalMember(facts):return next((row for row in facts['facts']['windows'] if row['application']=='warlock-modal-probe'),None)
   def modalPixels(name,incarnation):
    observed=request('preview-client-scope-request',subjectIncarnation=incarnation);check(name+'OwnNativeClientScope',observed.get('kind')=='preview-client-scope' and observed['previewEligible'] is False and observed['scope']['context']['incarnation']==incarnation,reply=observed)
    scope=observed['scope'];deadline=int(scope['now'])+2000000000;owned=request('preview-client-scoped-request',subjectIncarnation=incarnation,deadlineNs=str(deadline),context=scope['context']);check(name+'ActualModalCapture',owned.get('kind')=='preview-client-owned' and owned['previewEligible'] is False,reply=owned)
    h,rights=exchange(1,owned['captureRequest'],captureSubject=incarnation);fd=rights[0];memory=None
    try:
     check(name+'ExactOwnModalFDContext',h[22]==11 and h[8]==int(incarnation) and list(h[12:14])==[96,64] and h[21]==int(scope['context']['content']) and h[23]==deadline and h[10]<deadline,header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'RealSealedModalFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'ModalImmutableChecksum',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     decoder=s.host.launch('pixels-'+name,[pre['modalPixelOracle'],str(path)],env=env);decoder.wait(timeout=5);check(name+'ModalDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     held=request('preview-client-retire-request');check(name+'HeldModalExportRefusesRetirement',held.get('reason')=='preview-client-import-outstanding')
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Modal FD unexpectedly live')
    except OSError as error:check(name+'PhysicalModalFDClosed',error.errno==9)
    released,_=exchange(2,owned['captureRequest'],h[16],captureSubject=incarnation);check(name+'ExactModalExportReleased',released[16]==h[16]);retired=request('preview-client-retire-request');check(name+'NativeModalProducerRetired',retired.get('kind')=='preview-client-retired' and retired['ownedBytes']=='0');return pixels,scope
   familyBeforeModal=familyNativeScope()
   parentCounts=logs()[-1];n=len(logs());command('modal-create');configuredModal=wait(lambda:next((row for row in logs()[n:] if row['event']=='modal-configured'),None));firstModal=wait(lambda:modalMember(modalFacts()))
   check('familyModalActualParentRelationAndOwnSerial',firstModal['owner']==subject and firstModal['incarnation']!=subject and configuredModal['modalSerial']>0 and configuredModal['modalCommits']==2 and logs()[-1]['rootCommits']==parentCounts['rootCommits'] and logs()[-1]['childCommits']==parentCounts['childCommits'],window=firstModal,configured=configuredModal)
   familyModalCreated=familyAdvanced('familyModalMap',familyBeforeModal);check('familyObserverActualTwoNativeMembers',len(familyModalCreated['members'])==2 and {row['incarnation'] for row in familyModalCreated['members']}=={subject,firstModal['incarnation']} and next(row for row in familyModalCreated['members'] if row['incarnation']==firstModal['incarnation'])['parent']==subject and next(row for row in familyModalCreated['members'] if row['incarnation']==firstModal['incarnation'])['flags']&64,source=familyModalCreated)
   refused=request('preview-family-scope-request',subjectIncarnation=firstModal['incarnation']);check('familyObserverLinkedChildCannotRetargetRoot',refused.get('reason')=='preview-client-scope-source-unavailable',reply=refused)
   modalSubject=firstModal['incarnation'];magenta,modalScope=modalPixels('family-modal-magenta',modalSubject);check('familyModalActualOwnMagentaPixels',magenta['width']==96 and magenta['height']==64 and magenta['magenta']==96*64 and magenta['green']==0 and magenta['yellow']==0,pixels=magenta)
   importedEffect('activate','familyModalSet');focus=modalFacts();check('familyModalNativeHintChoosesModalRecipient',focus['facts']['focused']==modalSubject,facts=focus)
   counts=logs()[-1];command('modal-yellow');yellow,changedModalScope=modalPixels('family-modal-yellow',modalSubject);check('familyModalIndependentCommitAndPixels',yellow['yellow']==96*64 and yellow['magenta']==0 and yellow['green']==0 and logs()[-1]['rootCommits']==counts['rootCommits'] and logs()[-1]['childCommits']==counts['childCommits'] and int(changedModalScope['context']['content'])>int(modalScope['context']['content']),pixels=yellow,before=modalScope,after=changedModalScope)
   familyModalPainted=familyAdvanced('familyModalPaint',familyModalCreated)
   command('modal-unset');familyModalUnset=familyAdvanced('familyModalHintUnset',familyModalPainted);check('familyObserverUnsetHintNativeFlag',not next(row for row in familyModalUnset['members'] if row['incarnation']==modalSubject)['flags']&64);importedEffect('activate','familyModalUnset');focus=modalFacts();check('familyModalUnsetNativeRecipientReturnsRoot',focus['facts']['focused']==subject,facts=focus)
   command('modal-set');familyModalSet=familyAdvanced('familyModalHintSet',familyModalUnset);check('familyObserverSetHintNativeFlag',next(row for row in familyModalSet['members'] if row['incarnation']==modalSubject)['flags']&64);importedEffect('activate','familyModalReset');focus=modalFacts();check('familyModalResetNativeRecipientChoosesModal',focus['facts']['focused']==modalSubject,facts=focus)
   command('modal-unparent');familyModalUnlinked=familyAdvanced('familyModalUnlink',familyModalSet);check('familyObserverUnlinkedWindowExcluded',len(familyModalUnlinked['members'])==1 and familyModalUnlinked['members'][0]['incarnation']==subject);unparented=modalFacts();check('familyModalActualNativeOwnerUnlinked',modalMember(unparented)['owner'] is None,facts=unparented);importedEffect('activate','familyModalUnparent');check('familyModalUnparentNotRetargetedAsRootFamily',modalFacts()['facts']['focused']==subject)
   command('modal-reparent');familyModalRelinked=familyAdvanced('familyModalRelink',familyModalUnlinked);check('familyObserverRelinkExactSameNativeMember',len(familyModalRelinked['members'])==2 and any(row['incarnation']==modalSubject and row['parent']==subject for row in familyModalRelinked['members']));reparented=modalFacts();check('familyModalActualNativeOwnerRelinked',modalMember(reparented)['owner']==subject and modalMember(reparented)['incarnation']==modalSubject,facts=reparented);importedEffect('activate','familyModalReparent');check('familyModalReparentRestoresNativeRecipient',modalFacts()['facts']['focused']==modalSubject)
   importedEffect('minimize','familyModal');minimized=modalFacts();familyRows=[row for row in minimized['facts']['windows'] if row['incarnation'] in [subject,modalSubject]];check('familyModalNativeMinimizeBothOwnedMembers',len(familyRows)==2 and all(row['minimized'] for row in familyRows),facts=minimized)
   stoppedModal=request('preview-client-scope-request',subjectIncarnation=modalSubject);check('familyModalMinimizedOwnSourceStopped',stoppedModal.get('kind')=='preview-client-scope' and stoppedModal['scope']['present'] and not stoppedModal['scope']['sourceLive'],reply=stoppedModal)
   importedEffect('restore','familyModal');restored=modalFacts();familyRows=[row for row in restored['facts']['windows'] if row['incarnation'] in [subject,modalSubject]];check('familyModalNativeRestoreBothAndModalFocus',len(familyRows)==2 and all(not row['minimized'] for row in familyRows) and restored['facts']['focused']==modalSubject,facts=restored)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None);retired=request('preview-client-scope-request',subjectIncarnation=modalSubject);check('familyModalDestroyedIncarnationRefused',retired.get('reason')=='preview-client-scope-source-unavailable',reply=retired)
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));replacementModal=wait(lambda:modalMember(modalFacts()));check('familyModalReplacementFreshNativeIncarnation',replacementModal['owner']==subject and int(replacementModal['incarnation'])>int(modalSubject),previous=firstModal,replacement=replacementModal)
   replacementPixels,replacementScope=modalPixels('family-modal-replacement',replacementModal['incarnation']);check('familyModalReplacementOwnOriginalMagentaPixels',replacementPixels['magenta']==96*64 and replacementPixels['green']==0,pixels=replacementPixels)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None);r['modalFixtureQualification']={'firstSubject':modalSubject,'replacementSubject':replacementModal['incarnation'],'magenta':magenta,'yellow':yellow,'replacement':replacementPixels,'scope':'Actual xdg parent/hint/window focus, native family minimize/restore facts and independent client pixels; no complete family capture or raw key/AT/hardware qualification','productionFamilyCapture':False}
   for tracePath,traceHash in sorted(pre['familyTraces'].items()):
    check('familyTraceHash'+pathlib.Path(tracePath).stem,sha(tracePath)==traceHash);trace=json.loads(pathlib.Path(tracePath).read_text());before=None;steps=[];actualModal=None
    for index,state in enumerate(trace['states']):
     cmd=state['command'];n=len(logs())
     if cmd=='modal-create':
      command(cmd);wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));actualModal=wait(lambda:modalMember(modalFacts()))
     elif cmd=='modal-move':
      modalWindow=next(row for row in s.data('clients') if row['title']=='WARLOCK-MODAL-PROBE');check('family-model-'+pathlib.Path(tracePath).stem+'-'+str(index)+'NativeMoveCommitted',s.ctl('dispatch',"hl.dsp.window.move({x=260,y=190,window='address:"+modalWindow['address']+"'})").strip()=='ok');wait(lambda:modalMember(modalFacts())['geometry'][:2]==[260,190])
     elif cmd not in ['reset','inspect']:
      command(cmd)
      if cmd=='modal-destroy':wait(lambda:modalMember(modalFacts()) is None)
     fresh=familyNativeScope();label='family-model-'+pathlib.Path(tracePath).stem+'-'+str(index)
     check(label+'NativeMembershipMatchesProjection',len(fresh['members'])==(2 if state['linked'] else 1) and (not state['linked'] or any(row['incarnation']==actualModal['incarnation'] and row['parent']==subject for row in fresh['members'])),projection=state,source=fresh)
     if state['linked']:
      row=next(row for row in fresh['members'] if row['incarnation']==actualModal['incarnation']);check(label+'NativeModalHintMatchesProjection',bool(row['flags']&64)==state['modal'])
      if cmd=='modal-move':check(label+'NativeGeometryMatchesProjection',row['geometry'][:4]==[260,190,96,64],member=row)
     if before is not None:
      new=int(fresh['scope']['context']['content']);old=int(before['scope']['context']['content']);check(label+'NativeRevisionMatchesProjection',(new>old if state['changed'] else new==old),projection=state,before=before,after=fresh)
      check(label+'OriginalNativeOwnerAndClock',fresh['scope']['binding']==before['scope']['binding'] and fresh['scope']['clock']==before['scope']['clock'] and int(fresh['scope']['now'])>=int(before['scope']['now']))
     steps.append({'index':index,'command':cmd,'modelState':state,'actualSource':fresh});before=fresh
    r['familyRevisionReplay'].append({'trace':tracePath,'sha256':traceHash,'statesCompared':len(steps),'steps':steps})
   check('allSixSelectedNativeFamilyTracesReplayed',len(r['familyRevisionReplay'])==6)
   def familyCapture(name,value,dialog=None):
    scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedFamilyCapture',captured.get('kind')=='preview-family-owned' and captured['planeSpace']=='root-popup-modal-monitor-unqualified' and captured['previewEligible'] is False,reply=captured)
    state=request('preview-family-state-request');check(name+'OwnFamilyState',state.get('kind')=='preview-family-owned' and state['captureRequest']==captured['captureRequest'])
    for op,reason in [('preview-capture-probe-state-request','preview-probe-unavailable'),('preview-popup-state-request','preview-probe-unavailable'),('preview-capture-probe-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasFamily',reply.get('reason')==reason,reply=reply)
    h,rights=exchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];check(name+'ExactFamilyPlaneContextDeadline',h[22]==35 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[800,600] and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualFamilySealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'FamilyCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     argv=[pre['familyPixelOracle'],str(path)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);check(name+'NativeDialogGeometry',all(float(x).is_integer() for x in geom) and geom[2:]==[96,64],geometry=geom);argv.extend(str(int(x)) for x in geom)
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'FamilyDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     desktopPath=private/(name+'-native-output.png');grab=s.host.launch('output-'+name,['/usr/bin/grim','-o','WAYLAND-1',str(desktopPath)],env=env);grab.wait(timeout=5);check(name+'ActualNativeOutputCaptureNormalExit',grab.returncode==0)
     outputDecoder=s.host.launch('output-pixels-'+name,[pre['familyPixelOracle'],str(desktopPath)],env=env);outputDecoder.wait(timeout=5);check(name+'NativeOutputDecoderNormalExit',outputDecoder.returncode==0);nativePixels=json.loads((private/('output-pixels-'+name+'.log')).read_text())
     check(name+'ExactNativeRootStylingAndGeometry',pixels['rootRGBA']==nativePixels['rootRGBA'] and pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:]==[0,0,255],familyPixels=pixels,nativePixels=nativePixels)
     check(name+'ExactNativePopupStylingAndBounds',pixels['styledCyan']==nativePixels['styledCyan'] and pixels['styledCyanUniform'] and pixels['styledCyanRGBA']==nativePixels['styledCyanRGBA'] and pixels['styledCyanBox']==nativePixels['styledCyanBox'],familyPixels=pixels,nativePixels=nativePixels)
     check(name+'ActualOwnRootAndPeerExcluded',pixels['green']==0,pixels=pixels)
     check(name+'NativeOutputSampleRetainsExactFamilyContext',familyNativeScope()['scope']['context']==scope['context'])
     held=request('preview-family-retire-request');check(name+'ExportPhysicallyHeld',held.get('reason')=='preview-probe-import-outstanding')
     r['familyCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Family FD unexpectedly live')
    except OSError as error:check(name+'PhysicalFamilyFDClosed',error.errno==9)
    released,_=exchange(2,captured['captureRequest'],h[16]);check(name+'ExactFamilyExportReleased',released[16]==h[16]);retired=request('preview-family-retire-request');check(name+'NativeFamilyProducerRetired',retired.get('kind')=='preview-family-retired' and retired['ownedBytes']=='0')
    return pixels
   def familyStale(name,old):
    value=familyNativeScope();scope=value['scope'];reply=request('preview-family-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(scope['now'])+2000000000),context=old['scope']['context']);check(name+'OldFamilyContextRefused',reply.get('reason')=='preview-probe-context-stale',reply=reply);check(name+'NoAcceptedFamilyProducer',request('preview-family-state-request').get('reason')=='preview-probe-unavailable');return value
   familyOnly=familyNativeScope();plain=familyCapture('combined-family-root',familyOnly);check('combinedFamilyRootOnlyNoDialogOrPopup',plain['magenta']==plain['cyan']==0)
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));dialog=wait(lambda:modalMember(modalFacts()))['incarnation'];mapped=familyStale('combinedModalMap',familyOnly)
   combinedMagenta=familyCapture('combined-family-magenta',mapped,dialog);check('combinedFamilyActualDialogInteriorAndRoot',combinedMagenta['interiorArea']==80*48 and combinedMagenta['interiorMagenta']==80*48 and combinedMagenta['magenta']>0 and combinedMagenta['cyan']==0,pixels=combinedMagenta)
   command('modal-yellow');painted=familyStale('combinedModalPaint',mapped);combinedYellow=familyCapture('combined-family-yellow',painted,dialog);check('combinedFamilyOwnDialogPaintChangesPixels',combinedYellow['interiorYellow']==80*48 and combinedYellow['magenta']==0,pixels=combinedYellow)
   command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()));withPopup=familyStale('combinedPopupMap',painted);combinedPopup=familyCapture('combined-family-popup-dialog',withPopup,dialog);check('combinedFamilyRootPopupAndDialogInOneImage',combinedPopup['styledCyan']==64*48 and combinedPopup['styledCyanBox']==[371,291,64,48] and combinedPopup['interiorYellow']==80*48 and combinedPopup['rootRGBA'][0]>0 and combinedPopup['green']==0,pixels=combinedPopup)
   command('popup-destroy');withoutPopup=familyStale('combinedPopupDestroy',withPopup);command('modal-unparent');unlinked=familyStale('combinedModalUnlink',withoutPopup);excluded=familyCapture('combined-family-unlinked',unlinked);check('combinedFamilyUnlinkedDialogExcludedPixels',excluded['yellow']==excluded['magenta']==excluded['cyan']==0,pixels=excluded)
   command('modal-reparent');relinked=familyStale('combinedModalRelink',unlinked);returned=familyCapture('combined-family-relinked',relinked,dialog);check('combinedFamilyReparentedDialogReturnsOwnPixels',returned['interiorYellow']==80*48,pixels=returned)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None);destroyed=familyStale('combinedModalDestroy',relinked);absent=familyCapture('combined-family-destroyed',destroyed);check('combinedFamilyDestroyedDialogAbsentPixels',absent['magenta']==absent['yellow']==absent['cyan']==0,pixels=absent)
   r['cropCaptureSamples']=[]
   def cropExchange(op,capture,transfer=0,version=2,expectedStatus=0):
    query=[magic,version,op,lifetime,session,frontend,4000+op,int(capture),int(subject),int(transfer)];count=28 if version==2 else 25
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child);assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(count*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==count*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC);words=struct.unpack('!'+str(count)+'Q',data);assert words[:3]==(magic,version,expectedStatus) and len(rights)==(1 if op==1 and expectedStatus==0 else 0)
     if expectedStatus==0:assert words[3:6]==(lifetime,session,frontend) and words[6]==4000+op and words[7]==int(capture) and words[8]==int(subject)
     return words,rights
   def cropCapture(name,value,dialog=None):
    beforeWindows=s.data('clients');scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedNativeCropCapture',captured.get('kind')=='preview-family-crop-owned' and captured['planeSpace']=='native-family-cropped-pixels-unqualified' and captured['previewEligible'] is False,reply=captured)
    cropOrigin=[int(captured['pixelX']),int(captured['pixelY'])];scale=captured['pixelScale'];check(name+'NativeOutputScale',scale==1)
    boxes=[row['geometry'][4:8] for row in value['members']];left=math.floor(min(b[0] for b in boxes)*scale);top=math.floor(min(b[1] for b in boxes)*scale);right=math.ceil(max(b[0]+b[2] for b in boxes)*scale);bottom=math.ceil(max(b[1]+b[3] for b in boxes)*scale)
    check(name+'NativeContributorUnionBounds',cropOrigin==[left,top] and [captured['width'],captured['height']]==[right-left,bottom-top],source=value,captured=captured)
    state=request('preview-family-crop-state-request');check(name+'TypedNativeCropState',state.get('kind')=='preview-family-crop-owned' and state['captureRequest']==captured['captureRequest'] and state['pixelX']==captured['pixelX'] and state['pixelY']==captured['pixelY'])
    for op,reason in [('preview-family-state-request','preview-probe-unavailable'),('preview-family-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasCrop',reply.get('reason')==reason,reply=reply)
    refused,_=cropExchange(1,captured['captureRequest'],version=1,expectedStatus=9);check(name+'LegacyFDVersionCannotImportCrop',refused[2]==9)
    h,rights=cropExchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]));nativeScale=struct.unpack('!d',struct.pack('!Q',h[27]))[0]
     check(name+'ExactCropPlaneContextOriginDeadline',h[22]==67 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[captured['width'],captured['height']] and list(origin)==cropOrigin and nativeScale==scale and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualCropSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CropCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     rootGeom=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(rootGeom[0]+20)-cropOrigin[0],int(rootGeom[1]+20)-cropOrigin[1]]
     argv=[pre['cropPixelOracle'],str(path),*map(str,point)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);argv.extend(str(int(x)) for x in [geom[0]-cropOrigin[0],geom[1]-cropOrigin[1],geom[2],geom[3]])
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'CropDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     check(name+'NativeRootPixelsPeerExcluded',pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:]==[0,0,255] and pixels['green']==0,pixels=pixels)
     check(name+'CaptureNeverRelocatesNativeWindows',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     check(name+'NativeCropRetainsExactFamilyContext',familyNativeScope()['scope']['context']==scope['context'])
     check(name+'CropHeldExportRefusesRetire',request('preview-family-crop-retire-request').get('reason')=='preview-probe-import-outstanding')
     r['cropCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Crop FD unexpectedly live')
    except OSError as error:check(name+'PhysicalCropFDClosed',error.errno==9)
    released,_=cropExchange(2,captured['captureRequest'],h[16]);check(name+'ExactCropExportReleased',released[16]==h[16]);retired=request('preview-family-crop-retire-request');check(name+'NativeCropProducerRetired',retired.get('kind')=='preview-family-crop-retired' and retired['ownedBytes']=='0');return pixels,cropOrigin
   bareCrop,bareOrigin=cropCapture('crop-root',familyNativeScope());check('cropRootMatchesNativeMonitorStyle',bareCrop['rootRGBA']==absent['rootRGBA'] and bareOrigin==[73,73] and [bareCrop['width'],bareCrop['height']]==[334,254])
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));cropDialog=wait(lambda:modalMember(modalFacts()))['incarnation'];command('modal-yellow');command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()))
   combinedCrop,combinedOrigin=cropCapture('crop-popup-modal',familyNativeScope(),cropDialog);check('cropActualRootPopupDialogInOnePlane',combinedCrop['styledCyan']==64*48 and [combinedCrop['styledCyanBox'][i]+combinedOrigin[i] for i in [0,1]]==[371,291] and combinedCrop['interiorYellow']==80*48,pixels=combinedCrop)
   command('popup-destroy');cropModalWindow=next(w for w in s.data('clients') if w['title']=='WARLOCK-MODAL-PROBE');target='address:'+cropModalWindow['address'];check('cropNegativeModalNativeMove',s.ctl('dispatch',"hl.dsp.window.move({x=-40,y=130,window='"+target+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==cropModalWindow['address'])['at']==[-40,130])
   negativeCrop,negativeOrigin=cropCapture('crop-negative-modal',familyNativeScope(),cropDialog);check('cropNegativeOriginRetainsEntireNativeModal',negativeOrigin[0]<0 and negativeCrop['interiorYellow']==80*48,pixels=negativeCrop)
   check('cropFullyOffscreenModalNativeMove',s.ctl('dispatch',"hl.dsp.window.move({x=-180,y=130,window='"+target+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==cropModalWindow['address'])['at']==[-180,130]);offscreen=familyNativeScope();offMember=next(row for row in offscreen['members'] if row['incarnation']==cropDialog);check('cropNativeModalGenuinelyOutsideMonitor',offMember['geometry'][4]+offMember['geometry'][6]<0 and bool(offMember['flags']&16) and not offMember['flags']&32,member=offMember)
   offCrop,offOrigin=cropCapture('crop-offscreen-modal',offscreen,cropDialog);check('cropFullyOffscreenNativeModalRetainsPixels',offOrigin[0]<-180 and offCrop['interiorYellow']==80*48 and offCrop['yellow']==negativeCrop['yellow'] and offCrop['rootRGBA']==negativeCrop['rootRGBA'],pixels=offCrop)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None)
   r['familyStyleSamples']=[]
   def styleScope(name='styleNativeReadonlyScope'):
    value=request('preview-family-style-scope-request',subjectIncarnation=subject);check(name,value.get('kind')=='preview-family-style-scope' and value['scopeKind']=='native-family-style-channels-unqualified' and value['previewEligible'] is False,reply=value);r['familyStyleSamples'].append(value);return value
   def rootStyle(value):return next(row for row in value['styles'] if row['incarnation']==subject)
   check('styleNativeRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address']);initialStyle=styleScope();sameStyle=styleScope();check('styleUnchangedObservationRetainsEpoch',sameStyle['scope']['context']==initialStyle['scope']['context'] and sameStyle['styles']==initialStyle['styles'])
   counts=logs()[-1];check('styleNativePeerFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+unrelated['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==unrelated['address']);inactiveStyle=styleScope();check('styleNativeFocusChangesSource',int(inactiveStyle['scope']['context']['content'])>int(initialStyle['scope']['context']['content']),before=initialStyle,after=inactiveStyle)
   check('styleFocusNoRootClientCommit',logs()[-1]['rootCommits']==counts['rootCommits'],before=counts,after=logs()[-1])
   check('styleConfigureNativeDimming',s.ctl('eval','hl.config({decoration={dim_inactive=true,dim_strength=0.3}})').strip()=='ok');styleDimInitial=styleScope();wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7]-.3)<1e-6 else None)(styleScope('styleDimPendingNativeReadonlyScope')));dimmedStyle=styleScope();check('styleExactNativeDimmingChannel',abs(rootStyle(dimmedStyle)['channels'][7]-.3)<1e-6)
   check('styleConfigureNoRootClientCommit',logs()[-1]['rootCommits']==counts['rootCommits'],before=counts,after=logs()[-1]);check('styleConfigurationAdvancesNativeEpoch',int(dimmedStyle['scope']['context']['content'])>int(inactiveStyle['scope']['context']['content']),before=inactiveStyle,after=dimmedStyle)
   unmodifiedFamily=familyNativeScope();check('styleSetNativeDimStrengthAgain',s.ctl('eval','hl.config({decoration={dim_strength=0.6}})').strip()=='ok');wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7]-.6)<1e-6 else None)(styleScope('styleAgainDimPendingNativeReadonlyScope')));changedStyle=styleScope();check('styleAgainFinalAppliedNativeDim',abs(rootStyle(changedStyle)['channels'][7]-.6)<1e-6);unchangedFamily=familyNativeScope()
   check('styleOnlyChangeNoFamilyClientRevision',unchangedFamily['members']==unmodifiedFamily['members'] and unchangedFamily['scope']['context']['content']==unmodifiedFamily['scope']['context']['content'],before=unmodifiedFamily,after=unchangedFamily)
   check('styleOnlyChangeAdvancesDistinctStyleRevision',int(changedStyle['scope']['context']['content'])>int(dimmedStyle['scope']['context']['content']) and logs()[-1]['rootCommits']==counts['rootCommits'],before=dimmedStyle,after=changedStyle)
   check('styleRestorePrivateNativeConfiguration',s.ctl('eval','hl.config({decoration={dim_inactive=false,dim_strength=0.5}})').strip()=='ok');restoreInitial=styleScope()
   if abs(rootStyle(restoreInitial)['channels'][7])>=1e-6:wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7])<1e-6 else None)(styleScope('styleRestoreIntermediateReadonlyScope')))
   restoredStyle=styleScope();check('styleRestoreFinalActualNativeZeroDim',abs(rootStyle(restoredStyle)['channels'][7])<1e-6)
   check('styleConfigurationRestoreLaterEpoch',int(restoredStyle['scope']['context']['content'])>int(changedStyle['scope']['context']['content']))
   check('styleReturnNativeRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   r['styleCropCaptureSamples']=[]
   def styleCropScope(name='styleCropNativeReadonlyScope'):
    value=request('preview-family-style-crop-scope-request',subjectIncarnation=subject);check(name,value.get('kind')=='preview-family-style-crop-scope' and value['scopeKind']=='native-family-style-crop-channels-unqualified' and value['previewEligible'] is False,reply=value);return value
   def styleCropExchange(op,capture,transfer=0,version=3,expectedStatus=0):
    query=[magic,version,op,lifetime,session,frontend,5000+op,int(capture),int(subject),int(transfer)];count=29 if version==4 else 28 if version in [2,3] else 25
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child);assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(count*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==count*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC);words=struct.unpack('!'+str(count)+'Q',data);assert words[:3]==(magic,version,expectedStatus) and len(rights)==(1 if op==1 and expectedStatus==0 else 0)
     if expectedStatus==0:assert words[3:6]==(lifetime,session,frontend) and words[6]==5000+op and words[7]==int(capture) and words[8]==int(subject)
     return words,rights
   def styleCropCapture(name,value,dialog=None):
    beforeWindows=s.data('clients');scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedNativeCropCapture',captured.get('kind')=='preview-family-style-crop-owned' and captured['planeSpace']=='native-family-style-cropped-pixels-unqualified' and captured['previewEligible'] is False,reply=captured)
    cropOrigin=[int(captured['pixelX']),int(captured['pixelY'])];scale=captured['pixelScale'];check(name+'NativeOutputScale',scale==1)
    geometry=value['crop'];check(name+'ExactNativeScopeCropBounds',cropOrigin==[int(geometry['pixelX']),int(geometry['pixelY'])] and [captured['width'],captured['height']]==[geometry['width'],geometry['height']] and scale==geometry['scale'],source=value,captured=captured)
    state=request('preview-family-style-crop-state-request');check(name+'TypedNativeCropState',state.get('kind')=='preview-family-style-crop-owned' and state['captureRequest']==captured['captureRequest'] and state['pixelX']==captured['pixelX'] and state['pixelY']==captured['pixelY'])
    for op,reason in [('preview-family-crop-state-request','preview-probe-unavailable'),('preview-family-crop-retire-request','preview-probe-plane-mismatch'),('preview-family-state-request','preview-probe-unavailable'),('preview-family-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasCrop',reply.get('reason')==reason,reply=reply)
    for oldVersion in [1,2]:
     refused,_=styleCropExchange(1,captured['captureRequest'],version=oldVersion,expectedStatus=9);check(name+'OldFDVersion'+str(oldVersion)+'CannotImportStyleCrop',refused[2]==9)
    h,rights=styleCropExchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]));nativeScale=struct.unpack('!d',struct.pack('!Q',h[27]))[0]
     check(name+'ExactCropPlaneContextOriginDeadline',h[22]==131 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[captured['width'],captured['height']] and list(origin)==cropOrigin and nativeScale==scale and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualCropSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CropCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     rootGeom=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(rootGeom[0]+20)-cropOrigin[0],int(rootGeom[1]+20)-cropOrigin[1]]
     argv=[pre['cropPixelOracle'],str(path),*map(str,point)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);argv.extend(str(int(x)) for x in [geom[0]-cropOrigin[0],geom[1]-cropOrigin[1],geom[2],geom[3]])
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'CropDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     check(name+'NativeRootPixelsPeerExcluded',pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:]==[0,0,255] and pixels['green']==0,pixels=pixels)
     desktopPath=private/(name+'-native-output.png');grab=s.host.launch('output-'+name,['/usr/bin/grim','-o','WAYLAND-1',str(desktopPath)],env=env);grab.wait(timeout=5);check(name+'ActualNativeOutputCaptureNormalExit',grab.returncode==0)
     outputDecoder=s.host.launch('output-pixels-'+name,[pre['cropPixelOracle'],str(desktopPath),str(int(rootGeom[0]+20)),str(int(rootGeom[1]+20))],env=env);outputDecoder.wait(timeout=5);check(name+'NativeOutputDecoderNormalExit',outputDecoder.returncode==0);nativePixels=json.loads((private/('output-pixels-'+name+'.log')).read_text())
     check(name+'ExactIndependentNativeRootStyle',pixels['rootRGBA']==nativePixels['rootRGBA'],familyPixels=pixels,nativePixels=nativePixels)
     check(name+'ExactIndependentNativePopupStyle',pixels['styledCyan']==nativePixels['styledCyan'] and pixels['styledCyanRGBA']==nativePixels['styledCyanRGBA'] and (not pixels['styledCyan'] or [pixels['styledCyanBox'][0]+cropOrigin[0],pixels['styledCyanBox'][1]+cropOrigin[1],*pixels['styledCyanBox'][2:]]==nativePixels['styledCyanBox']),familyPixels=pixels,nativePixels=nativePixels)
     check(name+'CaptureNeverRelocatesNativeWindows',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     check(name+'NativeCropRetainsExactFamilyContext',styleCropScope()['scope']['context']==scope['context'])
     check(name+'CropHeldExportRefusesRetire',request('preview-family-style-crop-retire-request').get('reason')=='preview-probe-import-outstanding')
     r['styleCropCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Crop FD unexpectedly live')
    except OSError as error:check(name+'PhysicalCropFDClosed',error.errno==9)
    released,_=styleCropExchange(2,captured['captureRequest'],h[16]);check(name+'ExactCropExportReleased',released[16]==h[16]);retired=request('preview-family-style-crop-retire-request');check(name+'NativeCropProducerRetired',retired.get('kind')=='preview-family-style-crop-retired' and retired['ownedBytes']=='0');return pixels,cropOrigin
   check('styleCropPeerMovedAwayFromOracle',s.ctl('dispatch',"hl.dsp.window.move({x=500,y=80,window='address:"+unrelated['address']+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==unrelated['address'])['at']==[500,80])
   check('styleCropNativePeerFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+unrelated['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==unrelated['address'])
   check('styleCropConfigureDimThreeTenths',s.ctl('eval','hl.config({decoration={dim_inactive=true,dim_strength=0.3}})').strip()=='ok');dimInitial=styleCropScope()
   if abs(rootStyle(dimInitial)['channels'][7]-.3)>=1e-6:wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7]-.3)<1e-6 else None)(styleCropScope('styleCropDimIntermediateReadonlyScope')))
   dimThree=styleCropScope();check('styleCropDimFinalExactNativeThreeTenths',abs(rootStyle(dimThree)['channels'][7]-.3)<1e-6)
   stableFamily=familyNativeScope();stableCommits=logs()[-1];firstStyled,_=styleCropCapture('style-crop-dim-three',dimThree)
   check('styleCropConfigureDimSixTenths',s.ctl('eval','hl.config({decoration={dim_strength=0.6}})').strip()=='ok');dimSix=wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7]-.6)<1e-6 else None)(styleCropScope()));stillFamily=familyNativeScope()
   check('styleCropOnlyNativeStyleChanged',stableFamily['members']==stillFamily['members'] and stableFamily['scope']['context']['content']==stillFamily['scope']['context']['content'] and stableCommits['rootCommits']==logs()[-1]['rootCommits'] and int(dimSix['scope']['context']['content'])>int(dimThree['scope']['context']['content']),before=dimThree,after=dimSix)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(dimSix['scope']['now'])+2000000000),context=dimThree['scope']['context']);check('styleCropOldStyleScopeRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied);check('styleCropStaleScopeAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   freshSix=styleCropScope();secondStyled,_=styleCropCapture('style-crop-dim-six',freshSix);check('styleCropChangedStyleChangesActualPixels',firstStyled['rootRGBA'][0]>secondStyled['rootRGBA'][0]>0,first=firstStyled,second=secondStyled)
   check('styleCropRestoreNativeDim',s.ctl('eval','hl.config({decoration={dim_inactive=false,dim_strength=0.5}})').strip()=='ok');wait(lambda:(lambda value:value if abs(rootStyle(value)['channels'][7])<1e-6 else None)(styleCropScope()))
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));styledDialog=wait(lambda:modalMember(modalFacts()))['incarnation'];command('modal-yellow');command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()))
   styledModalWindow=next(w for w in s.data('clients') if w['title']=='WARLOCK-MODAL-PROBE');styledTarget='address:'+styledModalWindow['address'];check('styleCropMoveModalFullyOutsideMonitor',s.ctl('dispatch',"hl.dsp.window.move({x=-180,y=130,window='"+styledTarget+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==styledModalWindow['address'])['at']==[-180,130]);styledFamily=styleCropScope()
   styledPixels,styledOrigin=styleCropCapture('style-crop-popup-offscreen-modal',styledFamily,styledDialog);check('styleCropWholeOffscreenModalAndPopupRetained',styledOrigin[0]<-180 and styledPixels['yellow']==96*64 and styledPixels['interiorYellow']==80*48 and styledPixels['styledCyan']==64*48,pixels=styledPixels,origin=styledOrigin)
   command('popup-destroy');command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None)
   check('styleCropRestoreRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   # Actual family FD3 pixels traverse the existing single Main/Bar/Popup policy.
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));webDialog=wait(lambda:modalMember(modalFacts()))['incarnation']
   command('modal-yellow');n=len(logs());command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()[n:]))
   webModal=next(w for w in s.data('clients') if w['title']=='WARLOCK-MODAL-PROBE')
   check('familyWebMoveActualModalOffscreen',s.ctl('dispatch',"hl.dsp.window.move({x=-180,y=130,window='address:"+webModal['address']+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==webModal['address'])['at']==[-180,130])
   fullLogName='full-family-provider'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-family',subject,'--qa-preview-snapshot',str(private/'family-webkit.png')],env=env)
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check('familyWebActualCoherentGroupAndPointerTarget',0<x<800 and 0<y<48,button=target)
   pointerLog=private/'family-web-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='family-web-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('familyWebPointerNormalExit',ptr.returncode==0)
   wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   seeds=[event for event in events() if event['kind']=='source-seed'];offers=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']
   check('familyWebOneOwnTypedSourceAndNativePacket',len(seeds)>=1 and len(offers)==1 and seeds[0]['source']['kind']=='preview-family-style-crop-scope' and seeds[0]['source']['previewEligible'] is False and seeds[0]['identity']=='family:'+subject and seeds[0]['source']['binding']!=attached['binding'],seeds=seeds,offers=offers)
   fences=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='fence']
   check('familyWebExactReadinessFenceAfterUnsignaledOffer',not offers[0]['signaled'] and len(fences)==1 and fences[0]=={**offers[0],'signaled':True},offers=offers,fences=fences)
   seeded=seeds[0]['source'];owned=fences[0];crop=seeded['crop']
   check('familyWebOriginalNativeJobScopeClockAndDeadline',owned['job']['binding']==seeded['scope']['binding'] and owned['job']['context']==seeded['scope']['context'] and owned['job']['clock']==seeded['scope']['clock'] and 0<int(owned['job']['deadline'])-int(seeded['scope']['now'])<=2000000000,seed=seeded,frame=owned)
   check('familyWebCanonicalFamilyCoverage',owned['fidelity']=='family' and owned['coverage']==['client','decoration','modal','popup'] and owned['owned'] and owned['signaled'],frame=owned)
   check('familyWebNativeOffscreenMemberAndSignedCrop',int(crop['pixelX'])<-180 and any(member['incarnation']==webDialog and member['geometry'][4]+member['geometry'][6]<0 for member in seeded['members']) and {row['incarnation'] for row in seeded['styles']}=={row['incarnation'] for row in seeded['members']},source=seeded)
   images=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('familyWebExactURIAndNativeCropDimensions',images and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+owned['handle'] and row[0]['naturalWidth']==crop['width'] and row[0]['naturalHeight']==crop['height'] and row[0]['width']==160 and 0<row[0]['height']<=120 for row in images),images=images)
   decoder=s.host.launch('pixels-family-webkit',[pre['familyWebPixelOracle'],str(private/'family-webkit.png')],env=env);decoder.wait(timeout=5);check('familyWebIndependentPixelDecoderNormalExit',decoder.returncode==0)
   rendered=json.loads((private/'pixels-family-webkit.log').read_text());check('familyWebActualRootPopupOffscreenModalPixelsAndForeignExclusion',rendered['styledRoot']>0 and rendered['styledPopup']>0 and rendered['modalYellow']>0 and rendered['foreignGreen']==0,pixels=rendered)
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('familyWeb',offers[0])
   zero=[row for row in ownership() if row['job']==owned['job'] and row['charge']=='0' and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending']]
   check('familyWebPhysicalCloseExportReleaseAndProducerRetireBeforeExactACK',zero and acks()==[{'kind':'acknowledge','job':owned['job'],'sequence':'3'}] and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ownership: '+json.dumps(zero[0],separators=(',',':')))<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'),ownership=ownership(),acks=acks())
   r['familyWebKitEvidence']={'source':seeded,'frame':owned,'pixels':rendered,'ownership':ownership(),'acks':acks(),'previewEligible':False,'hardwarePresentation':False}
   web.terminate();web.wait(timeout=5);check('familyWebNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native client teardown incomplete:' not in fullLog())
   command('popup-destroy');command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None)
   check('familyWebRestoreRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   # Fresh native observation remains independent of retained pixel eligibility.
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));historicalDialog=wait(lambda:modalMember(modalFacts()))['incarnation']
   command('modal-yellow');n=len(logs());command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()[n:]))
   historicalModal=next(w for w in s.data('clients') if w['title']=='WARLOCK-MODAL-PROBE');check('familyHistoricalModalOffscreen',s.ctl('dispatch',"hl.dsp.window.move({x=-180,y=130,window='address:"+historicalModal['address']+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==historicalModal['address'])['at']==[-180,130])
   fullLogName='full-family-historical'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-family',subject,'--qa-preview-snapshot',str(private/'family-historical-webkit.png')],env=env)
   def familyHistoricalPointer(tag):
    target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2);check(tag+'PointerTarget',0<x<800 and 0<y<48)
    pointerLog=private/(tag+'-pointer.log')
    with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
    record=host.original.process(ptr.pid);record.update(name=tag+'-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
    ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check(tag+'PointerNormalExit',ptr.returncode==0)
   familyHistoricalPointer('familyHistoricalOpen');wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   firstFamilySeed=next(event for event in events() if event['kind']=='source-seed');firstFamilyOffer=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer');familyReady=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='fence')
   check('familyHistoricalOriginalFamilyReadiness',familyReady=={**firstFamilyOffer,'signaled':True} and familyReady['fidelity']=='family' and familyReady['coverage']==['client','decoration','modal','popup'])
   def familyHistoricalEffect(operation):
    global effectSequence
    effectSequence+=1;facts=request('scene-facts-request',minimumWatermark='0');intent={'request':str(effectSequence),'generation':str(effectSequence),'incarnation':subject,'operation':operation,'context':{'lifetime':attached['binding']['lifetime'],'epoch':attached['binding']['frontend'],'output':facts['outputGeneration'],'revision':facts['revision']}}
    result=observe({'protocolVersion':3,'kind':'window-effect','binding':attached['binding'],'effectProtocol':1,'intent':intent});check('familyHistorical'+operation.title()+'ExactCommittedNativeEffect',result.get('kind')=='effect-outcome' and result['binding']==attached['binding'] and result['intent']==intent and result['status']=='Committed' and result['reason']=='applied',outcome=result);return result
   familyHistoricalPointer('familyHistoricalClose');wait(lambda:'surface-popup-closed: lease='+firstFamilySeed['lease'] in fullLog());check('familyHistoricalActualPickerClosedBeforeMinimize','native-client-command: {"kind":"release"' not in fullLog())
   n=len(logs());command('popup-destroy');check('familyHistoricalNativePopupDismissedBeforeMinimize',any(row['event']=='popup-destroyed' and row['controlSequence']==commandSequence for row in logs()[n:]))
   familyHistoricalEffect('minimize');minimizedFamilyFacts=request('scene-facts-request',minimumWatermark='0');minimizedRoot=next(row for row in minimizedFamilyFacts['facts']['windows'] if row['incarnation']==subject)
   check('familyHistoricalActualFirstClassMinimize',minimizedRoot['minimized'] is True and any(row['incarnation']==historicalDialog and row['minimized'] for row in minimizedFamilyFacts['facts']['windows']),facts=minimizedFamilyFacts)
   current=request('preview-family-style-crop-scope-request',subjectIncarnation=subject)
   check('familyHistoricalFreshActualReadonlyScopeAfterMinimize',current.get('kind')=='preview-family-style-crop-scope' and current['scope']['present'] and not current['scope']['sourceLive'] and int(current['scope']['context']['scene'])>int(firstFamilySeed['source']['scope']['context']['scene']) and current['previewEligible'] is False,scope=current)
   familyHistoricalPointer('familyHistoricalReopen')
   def familyStoppedSeed():
    return next((event for event in events() if event['kind']=='source-seed' and event['source']['scope']['present'] and not event['source']['scope']['sourceLive'] and int(event['lease'])>int(firstFamilySeed['lease'])),None)
   stoppedFamilySeed=wait(familyStoppedSeed)
   check('familyHistoricalNewLeaseRetainsNativeJob',stoppedFamilySeed['source']['binding']==firstFamilySeed['source']['binding'] and stoppedFamilySeed['identity']==firstFamilySeed['identity'] and firstFamilyOffer['job']['origin']==firstFamilySeed['lease'] and 'native-client-resume:' not in fullLog(),source=stoppedFamilySeed)
   def familyHistoricalProjection():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in rows if row['body']['publication']==stoppedFamilySeed['publication'] and row['body']['lease']==stoppedFamilySeed['lease'] and 'Historical preview' in row['body']['text']),None)
   projection=wait(familyHistoricalProjection);check('familyHistoricalActualSharedElmLabel',projection is not None,report=projection)
   familyImages=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('familyHistoricalOriginalURIAndPixelDimensions',familyImages and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+firstFamilyOffer['handle'] and row[0]['naturalWidth']==firstFamilySeed['source']['crop']['width'] and row[0]['naturalHeight']==firstFamilySeed['source']['crop']['height'] for row in familyImages),images=familyImages)
   check('familyHistoricalOriginalOwnershipAndNoRecapture',any(row['job']==firstFamilyOffer['job'] and int(row['charge'])>0 and row['records']==1 and not row['mappedFDClosed'] and not row['producerRetired'] for row in ownership()) and [event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']==[firstFamilyOffer] and len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1 and 'native-client-command: {"kind":"release"' not in fullLog())
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(current['scope']['now'])+2000000000),context=current['scope']['context']);check('familyHistoricalMinimizedNewCaptureRefused',denied.get('kind')=='refused' and denied.get('reason')=='preview-probe-source-unavailable',reply=denied)
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('familyHistorical',firstFamilyOffer)
   expired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired'];check('familyHistoricalOriginalExpiryNoRenewal',expired==[familyReady],expired=expired)
   check('familyHistoricalPhysicalRetirementBeforeExactACK',acks()==[{'kind':'acknowledge','job':firstFamilyOffer['job'],'sequence':'3'}] and any(row['job']==firstFamilyOffer['job'] and row['charge']=='0' and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] for row in ownership()) and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'),ownership=ownership(),acks=acks())
   r['familyHistoricalEvidence']={'firstSource':firstFamilySeed,'stoppedSource':stoppedFamilySeed,'frame':firstFamilyOffer,'projection':projection,'ownership':ownership(),'acks':acks(),'captureRefusal':denied,'previewEligible':False,'hardwarePresentation':False}
   web.terminate();web.wait(timeout=5);check('familyHistoricalHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   familyHistoricalEffect('restore');restored=request('scene-facts-request',minimumWatermark='0');restoredRoot=next(row for row in restored['facts']['windows'] if row['incarnation']==subject);check('familyHistoricalRestoreSameNativeWorkspace',not restoredRoot['minimized'] and restoredRoot['workspace']==minimizedRoot['workspace'],window=restoredRoot)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None)
   check('familyHistoricalRestoreRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   def configStyleScope():
    value=request('preview-family-style-crop-scope-request',subjectIncarnation=subject);check('configStyleActualNativeReadonlyScope',value.get('kind')=='preview-family-style-crop-scope' and value['previewEligible'] is False,reply=value);return value
   def configStyleCapture(name,value,dialog=None):
    beforeWindows=s.data('clients');scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedNativeCropCapture',captured.get('kind')=='preview-family-style-crop-owned' and captured['planeSpace']=='native-family-style-cropped-pixels-unqualified' and captured['previewEligible'] is False,reply=captured)
    cropOrigin=[int(captured['pixelX']),int(captured['pixelY'])];scale=captured['pixelScale'];check(name+'NativeOutputScale',scale==1)
    geometry=value['crop'];check(name+'ExactNativeScopeCropBounds',cropOrigin==[int(geometry['pixelX']),int(geometry['pixelY'])] and [captured['width'],captured['height']]==[geometry['width'],geometry['height']] and scale==geometry['scale'],source=value,captured=captured)
    state=request('preview-family-style-crop-state-request');check(name+'TypedNativeCropState',state.get('kind')=='preview-family-style-crop-owned' and state['captureRequest']==captured['captureRequest'] and state['pixelX']==captured['pixelX'] and state['pixelY']==captured['pixelY'])
    for op,reason in [('preview-family-crop-state-request','preview-probe-unavailable'),('preview-family-crop-retire-request','preview-probe-plane-mismatch'),('preview-family-state-request','preview-probe-unavailable'),('preview-family-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasCrop',reply.get('reason')==reason,reply=reply)
    for oldVersion in [1,2]:
     refused,_=styleCropExchange(1,captured['captureRequest'],version=oldVersion,expectedStatus=9);check(name+'OldFDVersion'+str(oldVersion)+'CannotImportStyleCrop',refused[2]==9)
    h,rights=styleCropExchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]));nativeScale=struct.unpack('!d',struct.pack('!Q',h[27]))[0]
     check(name+'ExactCropPlaneContextOriginDeadline',h[22]==131 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[captured['width'],captured['height']] and list(origin)==cropOrigin and nativeScale==scale and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualCropSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CropCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     rootGeom=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(rootGeom[0]+20)-cropOrigin[0],int(rootGeom[1]+20)-cropOrigin[1]]
     argv=[pre['cropPixelOracle'],str(path),*map(str,point)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);argv.extend(str(int(x)) for x in [geom[0]-cropOrigin[0],geom[1]-cropOrigin[1],geom[2],geom[3]])
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'CropDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     check(name+'NativeRootPixelsPeerExcluded',pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:]==[0,0,255] and pixels['green']==0,pixels=pixels)
     desktopPath=private/(name+'-native-output.png');grab=s.host.launch('output-'+name,['/usr/bin/grim','-o','WAYLAND-1',str(desktopPath)],env=env);grab.wait(timeout=5);check(name+'ActualNativeOutputCaptureNormalExit',grab.returncode==0)
     outputDecoder=s.host.launch('output-pixels-'+name,[pre['cropPixelOracle'],str(desktopPath),str(int(rootGeom[0]+20)),str(int(rootGeom[1]+20))],env=env);outputDecoder.wait(timeout=5);check(name+'NativeOutputDecoderNormalExit',outputDecoder.returncode==0);nativePixels=json.loads((private/('output-pixels-'+name+'.log')).read_text())
     check(name+'ExactIndependentNativeRootStyle',pixels['rootRGBA']==nativePixels['rootRGBA'],familyPixels=pixels,nativePixels=nativePixels)
     check(name+'ExactIndependentNativePopupStyle',pixels['styledCyan']==nativePixels['styledCyan'] and pixels['styledCyanRGBA']==nativePixels['styledCyanRGBA'] and (not pixels['styledCyan'] or [pixels['styledCyanBox'][0]+cropOrigin[0],pixels['styledCyanBox'][1]+cropOrigin[1],*pixels['styledCyanBox'][2:]]==nativePixels['styledCyanBox']),familyPixels=pixels,nativePixels=nativePixels)
     check(name+'CaptureNeverRelocatesNativeWindows',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     check(name+'NativeCropRetainsExactFamilyContext',configStyleScope()['scope']['context']==scope['context'])
     check(name+'CropHeldExportRefusesRetire',request('preview-family-style-crop-retire-request').get('reason')=='preview-probe-import-outstanding')
     r['styleCropCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Crop FD unexpectedly live')
    except OSError as error:check(name+'PhysicalCropFDClosed',error.errno==9)
    released,_=styleCropExchange(2,captured['captureRequest'],h[16]);check(name+'ExactCropExportReleased',released[16]==h[16]);retired=request('preview-family-style-crop-retire-request');check(name+'NativeCropProducerRetired',retired.get('kind')=='preview-family-style-crop-retired' and retired['ownedBytes']=='0');return pixels,cropOrigin
   check('configStyleSetActualShadowPowerOne',s.ctl('eval','hl.config({decoration={shadow={enabled=true,range=16,render_power=1}}})').strip()=='ok')
   def configAppliedShadowBounds():
    value=configStyleScope();geometry=next(row['geometry'] for row in value['members'] if row['incarnation']==subject)
    # The owning renderer publishes shadow extents on its next frame.
    # Observe actual extents before issuing any original two-second capture.
    return value if geometry[6]>=geometry[2]+2*16 and geometry[7]>=geometry[3]+2*16 else None
   configOne=wait(configAppliedShadowBounds);check('configStyleShadowRangeActuallyApplied',True,source=configOne)
   counts=logs()[-1];powerOne,_=configStyleCapture('config-shadow-power-one',configOne)
   check('configStyleSetActualShadowPowerFour',s.ctl('eval','hl.config({decoration={shadow={render_power=4}}})').strip()=='ok')
   configFour=configStyleScope()
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(configFour['scope']['now'])+2000000000),context=configOne['scope']['context']);check('configStyleOldConfigurationScopeRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('configStyleStaleConfigurationAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   powerFour,_=configStyleCapture('config-shadow-power-four',configFour)
   one=r['styleCropCaptureSamples'][-2];four=r['styleCropCaptureSamples'][-1]
   r['renderConfigurationEvidence']={'before':one,'after':four,'bytesChanged':sha(private/'config-shadow-power-one.png')!=sha(private/'config-shadow-power-four.png'),'styleEpochChanged':configFour['scope']['context']['content']!=configOne['scope']['context']['content'],'nativeScopeBefore':configOne,'nativeScopeAfter':configFour,'rootCommitsUnchanged':counts['rootCommits']==logs()[-1]['rootCommits'],'previewEligible':False,'hardwarePresentation':False}
   check('configStyleRestorePrivateShadowDefaults',s.ctl('eval','hl.config({decoration={shadow={enabled=true,range=4,render_power=3}}})').strip()=='ok')
   # A live native source can have historical retained pixels after config changes.
   check('familyConfigurationSetNativeShadowOne',s.ctl('eval','hl.config({decoration={shadow={enabled=true,range=16,render_power=1}}})').strip()=='ok');wait(configAppliedShadowBounds)
   fullLogName='full-family-configuration'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-family',subject,'--qa-preview-snapshot',str(private/'family-configuration-webkit.png')],env=env)
   familyHistoricalPointer('familyConfigurationOpen');wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   configSeed=next(event for event in events() if event['kind']=='source-seed');configOffer=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer');configReady=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='fence')
   check('familyConfigurationOriginalNativeScopeJobAndReadiness',configReady=={**configOffer,'signaled':True} and configReady['fidelity']=='family' and configReady['coverage']==['client','decoration','modal','popup'] and configOffer['job']['binding']==configSeed['source']['scope']['binding'] and configOffer['job']['context']==configSeed['source']['scope']['context'] and configOffer['job']['clock']==configSeed['source']['scope']['clock'] and 0<int(configOffer['job']['deadline'])-int(configSeed['source']['scope']['now'])<=2000000000)
   familyHistoricalPointer('familyConfigurationClose');wait(lambda:'surface-popup-closed: lease='+configSeed['lease'] in fullLog());check('familyConfigurationOriginalStorageHeldAfterClose','native-client-command: {"kind":"release"' not in fullLog())
   check('familyConfigurationSetNativeShadowFour',s.ctl('eval','hl.config({decoration={shadow={render_power=4}}})').strip()=='ok')
   changedConfig=configStyleScope();check('familyConfigurationNativeLiveSourceHasNewContentEpoch',changedConfig['scope']['present'] and changedConfig['scope']['sourceLive'] and int(changedConfig['scope']['context']['content'])>int(configSeed['source']['scope']['context']['content']),source=changedConfig)
   familyHistoricalPointer('familyConfigurationReopen')
   def familyChangedConfigSeed():
    return next((event for event in events() if event['kind']=='source-seed' and int(event['lease'])>int(configSeed['lease']) and event['source']['scope']['present'] and event['source']['scope']['sourceLive'] and int(event['source']['scope']['context']['content'])>int(configOffer['job']['context']['content'])),None)
   configNewSeed=wait(familyChangedConfigSeed)
   def familyConfigurationProjection():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in rows if row['body']['publication']==configNewSeed['publication'] and row['body']['lease']==configNewSeed['lease'] and 'Historical preview' in row['body']['text']),None)
   configProjection=wait(familyConfigurationProjection);check('familyConfigurationActualSharedElmHistoricalLabelWithLiveSource',configProjection is not None and configNewSeed['source']['scope']['sourceLive'],report=configProjection,source=configNewSeed)
   configImages=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   check('familyConfigurationOriginalURIAndDimensionsAfterNewSourceEpoch',configImages and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+configOffer['handle'] and row[0]['naturalWidth']==configSeed['source']['crop']['width'] and row[0]['naturalHeight']==configSeed['source']['crop']['height'] for row in configImages),images=configImages)
   check('familyConfigurationOneOriginalCaptureNoRenewalOrResume',len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1 and [event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']==[configOffer] and 'native-client-resume:' not in fullLog() and 'native-client-command: {"kind":"release"' not in fullLog())
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('familyConfiguration',configOffer)
   configExpired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired'];check('familyConfigurationOriginalImageExpiry',configExpired==[configReady],expired=configExpired)
   check('familyConfigurationPhysicalRetirementBeforeExactACK',acks()==[{'kind':'acknowledge','job':configOffer['job'],'sequence':'3'}] and any(row['job']==configOffer['job'] and row['charge']=='0' and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] for row in ownership()) and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'),ownership=ownership(),acks=acks())
   r['familyConfigurationHistoricalEvidence']={'initialSource':configSeed,'changedLiveSource':configNewSeed,'frame':configOffer,'projection':configProjection,'images':configImages,'ownership':ownership(),'acks':acks(),'previewEligible':False,'hardwarePresentation':False}
   web.terminate();web.wait(timeout=5);check('familyConfigurationHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   check('familyConfigurationRestorePrivateShadowDefaults',s.ctl('eval','hl.config({decoration={shadow={enabled=true,range=4,render_power=3}}})').strip()=='ok')
   def glowAppliedNativeFrame(tag):
    path=private/(tag+'-applied-native-output.png');grab=s.host.launch(tag+'-applied-output',['/usr/bin/grim','-o','WAYLAND-1',str(path)],env=env);grab.wait(timeout=5)
    check(tag+'ActualOwningNativeFrameBarrier',grab.returncode==0 and path.is_file())
   # Actual private fixture; this does not install a global product halo policy.
   check('glowSetActualNativeVioletPowerOne',s.ctl('eval','hl.config({decoration={glow={enabled=true,range=8,render_power=1,color="rgba(b7a2ff29)"}}})').strip()=='ok')
   glowAppliedNativeFrame('glow-one');glowOne=configStyleScope();glowCommits=logs()[-1]['rootCommits'];glowBefore,_=configStyleCapture('config-glow-power-one',glowOne)
   check('glowSetActualNativePowerFour',s.ctl('eval','hl.config({decoration={glow={render_power=4}}})').strip()=='ok')
   glowAppliedNativeFrame('glow-four');glowFour=configStyleScope()
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(glowFour['scope']['now'])+2000000000),context=glowOne['scope']['context']);check('glowOldConfigurationScopeRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('glowStaleConfigurationAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   glowAfter,_=configStyleCapture('config-glow-power-four',glowFour)
   rootGeometry=next(row['geometry'] for row in glowOne['members'] if row['incarnation']==subject);glowCrop=glowOne['crop']
   argv=[pre['glowPixelOracle'],*[str(private/(name+'.png')) for name in ['config-glow-power-one','config-glow-power-four','config-glow-power-one-native-output','config-glow-power-four-native-output']],glowCrop['pixelX'],glowCrop['pixelY'],*map(lambda x:str(int(x)),rootGeometry[:4])]
   decoder=s.host.launch('pixels-glow-delta',argv,env=env);decoder.wait(timeout=5);check('glowIndependentDecoderNormalExit',decoder.returncode==0);glowPixels=json.loads((private/'pixels-glow-delta.log').read_text())
   check('glowActualIndependentNativePixelFidelity',glowPixels['passed'] and glowPixels['changedFamilyPixels']>0 and glowPixels['changedFamilyPixels']==glowPixels['changedOutputPixels'] and glowPixels['mismatchedBefore']==0 and glowPixels['mismatchedAfter']==0 and glowPixels['changedCenterPixels']==0,pixels=glowPixels)
   r['glowConfigurationEvidence']={'before':glowOne,'after':glowFour,'pixels':glowPixels,'rootCommitsUnchanged':glowCommits==logs()[-1]['rootCommits'],'previewEligible':False,'hardwarePresentation':False,'globalProductHaloPolicyInstalled':False}
   check('glowConfigurationOnlyChangeAdvancesEpoch',r['glowConfigurationEvidence']['rootCommitsUnchanged'] and glowOne['members']==glowFour['members'] and glowOne['styles']==glowFour['styles'] and glowOne['crop']==glowFour['crop'] and {k:v for k,v in glowOne['scope']['context'].items() if k!='content'}=={k:v for k,v in glowFour['scope']['context'].items() if k!='content'} and int(glowFour['scope']['context']['content'])>int(glowOne['scope']['context']['content']),evidence=r['glowConfigurationEvidence'])
   check('glowRestorePrivateNativeDefaults',s.ctl('eval','hl.config({decoration={glow={enabled=false,range=10,render_power=3,color="rgba(33ccffee)"}}})').strip()=='ok')
   def opacityStyleScope():
    value=request('preview-family-style-crop-scope-request',subjectIncarnation=subject);check('opacityActualNativeReadonlyScope',value.get('kind')=='preview-family-style-crop-scope' and value['previewEligible'] is False,reply=value);return value
   def opacityStyleCapture(name,value,dialog=None):
    beforeWindows=s.data('clients');scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedNativeCropCapture',captured.get('kind')=='preview-family-style-crop-owned' and captured['planeSpace']=='native-family-style-cropped-pixels-unqualified' and captured['previewEligible'] is False,reply=captured)
    cropOrigin=[int(captured['pixelX']),int(captured['pixelY'])];scale=captured['pixelScale'];check(name+'NativeOutputScale',scale==1)
    geometry=value['crop'];check(name+'ExactNativeScopeCropBounds',cropOrigin==[int(geometry['pixelX']),int(geometry['pixelY'])] and [captured['width'],captured['height']]==[geometry['width'],geometry['height']] and scale==geometry['scale'],source=value,captured=captured)
    state=request('preview-family-style-crop-state-request');check(name+'TypedNativeCropState',state.get('kind')=='preview-family-style-crop-owned' and state['captureRequest']==captured['captureRequest'] and state['pixelX']==captured['pixelX'] and state['pixelY']==captured['pixelY'])
    for op,reason in [('preview-family-crop-state-request','preview-probe-unavailable'),('preview-family-crop-retire-request','preview-probe-plane-mismatch'),('preview-family-state-request','preview-probe-unavailable'),('preview-family-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasCrop',reply.get('reason')==reason,reply=reply)
    for oldVersion in [1,2]:
     refused,_=styleCropExchange(1,captured['captureRequest'],version=oldVersion,expectedStatus=9);check(name+'OldFDVersion'+str(oldVersion)+'CannotImportStyleCrop',refused[2]==9)
    h,rights=styleCropExchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]));nativeScale=struct.unpack('!d',struct.pack('!Q',h[27]))[0]
     check(name+'ExactCropPlaneContextOriginDeadline',h[22]==131 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[captured['width'],captured['height']] and list(origin)==cropOrigin and nativeScale==scale and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualCropSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CropCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     rootGeom=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(rootGeom[0]+20)-cropOrigin[0],int(rootGeom[1]+20)-cropOrigin[1]]
     argv=[pre['cropPixelOracle'],str(path),*map(str,point)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);argv.extend(str(int(x)) for x in [geom[0]-cropOrigin[0],geom[1]-cropOrigin[1],geom[2],geom[3]])
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'CropDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     check(name+'NativeRootPixelsPeerExcluded',pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:3]==[0,0] and 0<pixels['rootRGBA'][3]<=255 and pixels['green']==0,pixels=pixels)
     desktopPath=private/(name+'-native-output.png');grab=s.host.launch('output-'+name,['/usr/bin/grim','-o','WAYLAND-1',str(desktopPath)],env=env);grab.wait(timeout=5);check(name+'ActualNativeOutputCaptureNormalExit',grab.returncode==0)
     outputDecoder=s.host.launch('output-pixels-'+name,[pre['cropPixelOracle'],str(desktopPath),str(int(rootGeom[0]+20)),str(int(rootGeom[1]+20))],env=env);outputDecoder.wait(timeout=5);check(name+'NativeOutputDecoderNormalExit',outputDecoder.returncode==0);nativePixels=json.loads((private/('output-pixels-'+name+'.log')).read_text())
     check(name+'IndependentNativeCompositedRoot',nativePixels['rootRGBA'][1:]==[0,0,255] and 0<nativePixels['rootRGBA'][0]<=pixels['rootRGBA'][0] and (pixels['rootRGBA'][3]<255 or pixels['rootRGBA']==nativePixels['rootRGBA']),familyPixels=pixels,nativePixels=nativePixels)
     check(name+'ExactIndependentNativePopupStyle',pixels['styledCyan']==nativePixels['styledCyan'] and pixels['styledCyanRGBA']==nativePixels['styledCyanRGBA'] and (not pixels['styledCyan'] or [pixels['styledCyanBox'][0]+cropOrigin[0],pixels['styledCyanBox'][1]+cropOrigin[1],*pixels['styledCyanBox'][2:]]==nativePixels['styledCyanBox']),familyPixels=pixels,nativePixels=nativePixels)
     check(name+'CaptureNeverRelocatesNativeWindows',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     check(name+'NativeCropRetainsExactFamilyContext',opacityStyleScope()['scope']['context']==scope['context'])
     check(name+'CropHeldExportRefusesRetire',request('preview-family-style-crop-retire-request').get('reason')=='preview-probe-import-outstanding')
     r['styleCropCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Crop FD unexpectedly live')
    except OSError as error:check(name+'PhysicalCropFDClosed',error.errno==9)
    released,_=styleCropExchange(2,captured['captureRequest'],h[16]);check(name+'ExactCropExportReleased',released[16]==h[16]);retired=request('preview-family-style-crop-retire-request');check(name+'NativeCropProducerRetired',retired.get('kind')=='preview-family-style-crop-retired' and retired['ownedBytes']=='0');return pixels,cropOrigin
   check('opacityPrivateBlackBackgroundApplied',s.ctl('eval','hl.config({misc={background_color="#000000"}})').strip()=='ok')
   check('opacityActualNativeRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   def opacityProperty(prop,value,tag):
    check(tag,s.ctl('dispatch',"hl.dsp.window.set_prop({window='address:"+source['address']+"',prop='"+prop+"',value='"+value+"'})").strip()=='ok')
   for window in s.data('clients'):
    if window['address']!=source['address']:
     check('opacityPrivateForeignWindowMoved-'+window['address'],s.ctl('dispatch',"hl.dsp.window.move({x=480,y=340,window='address:"+window['address']+"'})").strip()=='ok')
   wait(lambda:all(window['address']==source['address'] or window['at']==[480,340] for window in s.data('clients')))
   check('opacityPrivateSourceRaised',s.ctl('dispatch',"hl.dsp.window.alter_zorder({mode='top',window='address:"+source['address']+"'})").strip()=='ok')
   check('opacityPrivateCursorOutsideRoot',s.ctl('dispatch','hl.dsp.cursor.move({x=790,y=590})').strip()=='ok')
   opacityProperty('no_blur','1','opacityPrivateDisableBackgroundDependentBlur')
   opacityProperty('opaque','0','opacityNativeDisableOpaqueOverride');opacityProperty('opacity','0.5','opacityNativeHalfActive');opacityProperty('opacity_inactive','0.5','opacityNativeHalfInactive');glowAppliedNativeFrame('opacity-half')
   opacityHalf=opacityStyleScope();check('opacityOriginalNativeHalfAlphaChannel',abs(rootStyle(opacityHalf)['channels'][1]-.5)<1e-6)
   opacityCommits=logs()[-1]['rootCommits'];halfPixels,_=opacityStyleCapture('config-opacity-half',opacityHalf)
   opacityProperty('opaque','1','opacityNativeEnableOpaqueOverride');glowAppliedNativeFrame('opacity-opaque');opacityOpaque=opacityStyleScope()
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(opacityOpaque['scope']['now'])+2000000000),context=opacityHalf['scope']['context']);check('opacityOldRuleContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('opacityStaleRuleAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   opaquePixels,_=opacityStyleCapture('config-opacity-opaque',opacityOpaque)
   check('opacityActualChangedNativePixelsAndAlpha',halfPixels['rootRGBA'][3] in [127,128] and opaquePixels['rootRGBA'][3]==255 and opaquePixels['rootRGBA'][0]>0,before=halfPixels,after=opaquePixels)
   r['opacityConfigurationEvidence']={'before':opacityHalf,'after':opacityOpaque,'beforePixels':halfPixels,'afterPixels':opaquePixels,'bytesChanged':sha(private/'config-opacity-half.png')!=sha(private/'config-opacity-opaque.png'),'styleEpochChanged':opacityHalf['scope']['context']['content']!=opacityOpaque['scope']['context']['content'],'rootCommitsUnchanged':opacityCommits==logs()[-1]['rootCommits'],'previewEligible':False,'hardwarePresentation':False}
   rootGeometry=next(row['geometry'] for row in opacityHalf['members'] if row['incarnation']==subject);opacityCrop=opacityHalf['crop']
   argv=[pre['opacityPixelOracle'],*[str(private/(name+'.png')) for name in ['config-opacity-half','config-opacity-opaque','config-opacity-half-native-output','config-opacity-opaque-native-output']],opacityCrop['pixelX'],opacityCrop['pixelY'],*map(lambda x:str(int(x)),rootGeometry[:4])]
   decoder=s.host.launch('pixels-opacity-delta',argv,env=env);decoder.wait(timeout=5);check('opacityWholeRootIndependentDecoderNormalExit',decoder.returncode==0);opacityWhole=json.loads((private/'pixels-opacity-delta.log').read_text())
   check('opacityWholeRootIndependentNativeComposition',opacityWhole['passed'] and opacityWhole['comparedRootPixels']==76800 and opacityWhole['mismatchedBefore']==opacityWhole['mismatchedAfter']==0,pixels=opacityWhole)
   r['opacityConfigurationEvidence']['wholeRootPixels']=opacityWhole;r['opacityConfigurationEvidence']['backgroundDependentBlurQualified']=False;r['opacityConfigurationEvidence']['privateNoBlurRule']=True
   def sameOtherFacts(before,after):
    return before['members']==after['members'] and before['styles']==after['styles'] and before['crop']==after['crop'] and {k:v for k,v in before['scope']['context'].items() if k!='content'}=={k:v for k,v in after['scope']['context'].items() if k!='content'}
   check('opacityOnlyNativeRuleAdvancesEpoch',r['opacityConfigurationEvidence']['rootCommitsUnchanged'] and sameOtherFacts(opacityHalf,opacityOpaque) and int(opacityOpaque['scope']['context']['content'])>int(opacityHalf['scope']['context']['content']),evidence=r['opacityConfigurationEvidence'])
   opacityProperty('opaque','1','opacitySetSameNativeRule');glowAppliedNativeFrame('opacity-stable');opacityStable=opacityStyleScope();check('opacitySameRuleRetainsExactSourceContext',opacityStable['scope']['context']==opacityOpaque['scope']['context'] and sameOtherFacts(opacityOpaque,opacityStable))
   opacityProperty('opaque','0','opacityRestoreNativeOpaqueDefault');opacityProperty('opacity','1','opacityRestoreNativeActiveDefault');opacityProperty('opacity_inactive','1','opacityRestoreNativeInactiveDefault')
   opacityProperty('no_blur','0','opacityRestoreNativeBlurRuleDefault')
   check('opacityRestorePrivateBackgroundDefault',s.ctl('eval','hl.config({misc={background_color="#111111"}})').strip()=='ok')
   opacityProperty('nearest_neighbor','0','samplingNativeNearestDisabled');glowAppliedNativeFrame('sampling-initial');samplingBefore=opacityStyleScope();samplingCommits=logs()[-1]['rootCommits']
   opacityProperty('nearest_neighbor','1','samplingNativeNearestEnabled');glowAppliedNativeFrame('sampling-rule');samplingRule=opacityStyleScope()
   check('samplingOnlyNativeRuleAdvancesEpoch',sameOtherFacts(samplingBefore,samplingRule) and samplingCommits==logs()[-1]['rootCommits'] and int(samplingRule['scope']['context']['content'])>int(samplingBefore['scope']['context']['content']),before=samplingBefore,after=samplingRule)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(samplingRule['scope']['now'])+2000000000),context=samplingBefore['scope']['context']);check('samplingOldRuleContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('samplingStaleRuleAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   opacityProperty('nearest_neighbor','1','samplingSetSameNativeRule');glowAppliedNativeFrame('sampling-rule-stable');samplingStable=opacityStyleScope();check('samplingSameRuleRetainsExactSourceContext',samplingStable['scope']['context']==samplingRule['scope']['context'] and sameOtherFacts(samplingStable,samplingRule))
   opacityProperty('nearest_neighbor','0','samplingRestoreNativeNearestDefault');glowAppliedNativeFrame('sampling-rule-restored');samplingRestored=opacityStyleScope();check('samplingRestoredRuleUsesLaterRevision',sameOtherFacts(samplingRestored,samplingRule) and int(samplingRestored['scope']['context']['content'])>int(samplingRule['scope']['context']['content']))
   check('samplingDisableNativeXwaylandFilter',s.ctl('eval','hl.config({xwayland={use_nearest_neighbor=false}})').strip()=='ok');glowAppliedNativeFrame('sampling-config-zero');samplingZero=opacityStyleScope()
   check('samplingEnableNativeXwaylandFilter',s.ctl('eval','hl.config({xwayland={use_nearest_neighbor=true}})').strip()=='ok');glowAppliedNativeFrame('sampling-config-one');samplingOne=opacityStyleScope()
   check('samplingOnlyNativeConfigurationAdvancesEpoch',sameOtherFacts(samplingZero,samplingOne) and samplingCommits==logs()[-1]['rootCommits'] and int(samplingOne['scope']['context']['content'])>int(samplingZero['scope']['context']['content']),before=samplingZero,after=samplingOne)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(samplingOne['scope']['now'])+2000000000),context=samplingZero['scope']['context']);check('samplingOldConfigurationContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('samplingStaleConfigurationAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   check('samplingSetSameNativeConfiguration',s.ctl('eval','hl.config({xwayland={use_nearest_neighbor=true}})').strip()=='ok');glowAppliedNativeFrame('sampling-config-stable');samplingConfigStable=opacityStyleScope();check('samplingSameConfigurationRetainsExactSourceContext',samplingConfigStable['scope']['context']==samplingOne['scope']['context'] and sameOtherFacts(samplingConfigStable,samplingOne))
   r['samplingConfigurationEvidence']={'ruleBefore':samplingBefore,'ruleAfter':samplingRule,'ruleStable':samplingStable,'ruleRestored':samplingRestored,'configurationBefore':samplingZero,'configurationAfter':samplingOne,'configurationStable':samplingConfigStable,'rootCommitsUnchanged':samplingCommits==logs()[-1]['rootCommits'],'nativeRuleTransitionsQualified':True,'nativeConfigurationTransitionsQualified':True,'samplingPixelFidelityQualified':False,'xwaylandEnabled':False,'previewEligible':False,'hardwarePresentation':False}
   backgroundBefore=opacityStyleScope();backgroundCommits=logs()[-1]['rootCommits']
   command('background-create');backgroundCreated=opacityStyleScope()
   check('backgroundProtocolCreationDoesNotCommitBuffer',logs()[-1]['rootCommits']==backgroundCommits and sameOtherFacts(backgroundBefore,backgroundCreated),before=backgroundBefore,after=backgroundCreated)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(backgroundCreated['scope']['now'])+2000000000),context=backgroundBefore['scope']['context']);check('backgroundCreatedOldContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('backgroundCreatedStaleContextAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   command('background-region-pending');backgroundPending=opacityStyleScope();check('backgroundPendingRegionPreservesAppliedContext',backgroundPending['scope']['context']==backgroundCreated['scope']['context'] and logs()[-1]['rootCommits']==backgroundCommits)
   command('root-commit');backgroundApplied=opacityStyleScope();check('backgroundAppliedRegionUsesNewCommittedSource',logs()[-1]['rootCommits']==backgroundCommits+1 and int(backgroundApplied['scope']['context']['content'])>int(backgroundPending['scope']['context']['content']))
   command('background-region-pending-two');backgroundChangedPending=opacityStyleScope();check('backgroundChangedPendingRegionPreservesAppliedContext',backgroundChangedPending['scope']['context']==backgroundApplied['scope']['context'] and logs()[-1]['rootCommits']==backgroundCommits+1)
   command('root-commit');backgroundChanged=opacityStyleScope();check('backgroundChangedAppliedRegionUsesLaterRevision',logs()[-1]['rootCommits']==backgroundCommits+2 and int(backgroundChanged['scope']['context']['content'])>int(backgroundApplied['scope']['context']['content']))
   command('background-clear-pending');backgroundClearPending=opacityStyleScope();check('backgroundPendingClearPreservesAppliedContext',backgroundClearPending['scope']['context']==backgroundChanged['scope']['context'])
   command('root-commit');backgroundCleared=opacityStyleScope();check('backgroundAppliedClearUsesLaterRevision',logs()[-1]['rootCommits']==backgroundCommits+3 and int(backgroundCleared['scope']['context']['content'])>int(backgroundChanged['scope']['context']['content']))
   command('background-destroy');backgroundDestroyPending=opacityStyleScope();check('backgroundPendingDestroyPreservesAppliedContext',backgroundDestroyPending['scope']['context']==backgroundCleared['scope']['context'])
   command('root-commit');backgroundRemoved=opacityStyleScope();check('backgroundAppliedDestroyUsesLaterRevision',logs()[-1]['rootCommits']==backgroundCommits+4 and int(backgroundRemoved['scope']['context']['content'])>int(backgroundCleared['scope']['context']['content']))
   r['backgroundEffectEvidence']={'before':backgroundBefore,'created':backgroundCreated,'regionPending':backgroundPending,'regionApplied':backgroundApplied,'changedRegionPending':backgroundChangedPending,'changedRegionApplied':backgroundChanged,'clearPending':backgroundClearPending,'cleared':backgroundCleared,'destroyPending':backgroundDestroyPending,'removed':backgroundRemoved,'creationProcessedWithoutBufferCommit':True,'creationEpochAdvanced':int(backgroundCreated['scope']['context']['content'])>int(backgroundBefore['scope']['context']['content']),'backgroundPixelFidelityQualified':False,'nestedEffectFactsQualified':False,'previewEligible':False,'hardwarePresentation':False}
   def effectFacts():
    value=request('preview-family-effect-facts-request',subjectIncarnation=subject)
    check('nestedActualAuthenticatedNativeFacts',value.get('kind')=='preview-family-effect-facts' and value['previewEligible'] is False and value['scope']['binding']==attached['binding'],reply=value)
    return value
   def nativeMember(value):return next(member for member in value['effectFacts'] if member['incarnation']==subject)
   def nativeLeaf(value,identity):return next(leaf for leaf in nativeMember(value)['surfaces'] if leaf['identity']==identity)
   def sameAppliedFacts(a,b):return a['effectFacts']==b['effectFacts'] and a['scope']['context']==b['scope']['context']
   command('child-desync');childBefore=effectFacts();childRows=nativeMember(childBefore)['surfaces'];check('nestedOneExistingOwnedNativeChild',len(childRows)==1 and not childRows[0]['hasEffect'] and childRows[0]['blurRegion']==[] and childRows[0]['identity']!=nativeMember(childBefore)['root']['identity'],facts=childBefore)
   childIdentity=childRows[0]['identity'];nestedCommits=logs()[-1]['rootCommits'];nestedChildCommits=logs()[-1]['childCommits']
   command('background-child-create');childCreated=effectFacts();check('nestedChildCreateBeforeAnyBufferCommit',logs()[-1]['rootCommits']==nestedCommits and logs()[-1]['childCommits']==nestedChildCommits and nativeLeaf(childCreated,childIdentity)['hasEffect'] and nativeLeaf(childCreated,childIdentity)['blurRegion']==[] and not nativeMember(childCreated)['root']['hasEffect'] and int(childCreated['scope']['context']['content'])>int(childBefore['scope']['context']['content']),before=childBefore,after=childCreated)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(childCreated['scope']['now'])+2000000000),context=childBefore['scope']['context']);check('nestedChildOldContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied)
   check('nestedChildStaleContextAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   command('background-child-region-pending');childPending=effectFacts();check('nestedChildPendingRegionRetainsExactFacts',sameAppliedFacts(childCreated,childPending) and logs()[-1]['rootCommits']==nestedCommits and logs()[-1]['childCommits']==nestedChildCommits)
   command('background-child-apply');childApplied=effectFacts();check('nestedChildAppliedExactRegion',nativeLeaf(childApplied,childIdentity)['blurRegion']==[[0,20,100,220]] and logs()[-1]['rootCommits']==nestedCommits and logs()[-1]['childCommits']==nestedChildCommits+1 and int(childApplied['scope']['context']['content'])>int(childCreated['scope']['context']['content']),facts=childApplied)
   command('background-child-region-two');childChangedPending=effectFacts();check('nestedChildChangedPendingRetainsExactFacts',sameAppliedFacts(childApplied,childChangedPending))
   command('background-child-apply');childChanged=effectFacts();check('nestedChildChangedExactCopiedRegion',nativeLeaf(childChanged,childIdentity)['blurRegion']==[[10,20,110,220]] and nativeLeaf(childApplied,childIdentity)['blurRegion']==[[0,20,100,220]] and int(childChanged['scope']['context']['content'])>int(childApplied['scope']['context']['content']),before=childApplied,after=childChanged)
   command('background-child-clear-pending');childClearPending=effectFacts();check('nestedChildClearPendingRetainsExactFacts',sameAppliedFacts(childChanged,childClearPending));command('background-child-apply');childCleared=effectFacts();check('nestedChildAppliedClearKeepsEffectPreference',nativeLeaf(childCleared,childIdentity)['hasEffect'] and nativeLeaf(childCleared,childIdentity)['blurRegion']==[])
   command('background-child-destroy');childDestroyPending=effectFacts();check('nestedChildPendingDestroyRetainsExactFacts',sameAppliedFacts(childCleared,childDestroyPending));command('background-child-apply');childRemoved=effectFacts();check('nestedChildAppliedDestroyClearsNativePreference',not nativeLeaf(childRemoved,childIdentity)['hasEffect'] and nativeLeaf(childRemoved,childIdentity)['blurRegion']==[] and logs()[-1]['rootCommits']==nestedCommits and logs()[-1]['childCommits']==nestedChildCommits+4)
   command('popup-create');wait(lambda:any(row['event']=='popup-configured' and row['controlSequence']==commandSequence for row in logs()));popupBefore=effectFacts();existingIDs={leaf['identity'] for leaf in nativeMember(childRemoved)['surfaces']};popupNew=[leaf for leaf in nativeMember(popupBefore)['surfaces'] if leaf['identity'] not in existingIDs];check('nestedOneNewOwnedNativePopup',len(popupNew)==1 and not popupNew[0]['hasEffect'] and popupNew[0]['blurRegion']==[],facts=popupBefore)
   popupIdentity=popupNew[0]['identity'];popupCommits=next(row['popupCommits'] for row in reversed(logs()) if row['event']=='popup-configured');rootBeforePopup=logs()[-1]['rootCommits'];childBeforePopup=logs()[-1]['childCommits']
   command('background-popup-create');popupCreated=effectFacts();check('nestedPopupCreateBeforeRootChildBufferCommit',logs()[-1]['rootCommits']==rootBeforePopup and logs()[-1]['childCommits']==childBeforePopup and nativeLeaf(popupCreated,popupIdentity)['hasEffect'] and nativeLeaf(popupCreated,popupIdentity)['blurRegion']==[] and int(popupCreated['scope']['context']['content'])>int(popupBefore['scope']['context']['content']),before=popupBefore,after=popupCreated)
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(popupCreated['scope']['now'])+2000000000),context=popupBefore['scope']['context']);check('nestedPopupOldContextRejectedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied);check('nestedPopupStaleContextAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   command('background-popup-region-pending');popupPending=effectFacts();check('nestedPopupPendingRegionRetainsExactFacts',sameAppliedFacts(popupCreated,popupPending));command('background-popup-apply');popupApplied=effectFacts();check('nestedPopupAppliedExactRegion',nativeLeaf(popupApplied,popupIdentity)['blurRegion']==[[0,20,100,220]] and int(popupApplied['scope']['context']['content'])>int(popupCreated['scope']['context']['content']))
   command('background-popup-region-two');popupChangedPending=effectFacts();check('nestedPopupChangedPendingRetainsExactFacts',sameAppliedFacts(popupApplied,popupChangedPending));command('background-popup-apply');popupChanged=effectFacts();check('nestedPopupChangedExactCopiedRegion',nativeLeaf(popupChanged,popupIdentity)['blurRegion']==[[10,20,110,220]] and nativeLeaf(popupApplied,popupIdentity)['blurRegion']==[[0,20,100,220]])
   command('background-popup-clear-pending');popupClearPending=effectFacts();check('nestedPopupClearPendingRetainsExactFacts',sameAppliedFacts(popupChanged,popupClearPending));command('background-popup-apply');popupCleared=effectFacts();check('nestedPopupAppliedClearKeepsEffectPreference',nativeLeaf(popupCleared,popupIdentity)['hasEffect'] and nativeLeaf(popupCleared,popupIdentity)['blurRegion']==[])
   command('background-popup-destroy');popupDestroyPending=effectFacts();check('nestedPopupPendingDestroyRetainsExactFacts',sameAppliedFacts(popupCleared,popupDestroyPending));command('background-popup-apply');popupRemoved=effectFacts();check('nestedPopupAppliedDestroyClearsNativePreference',not nativeLeaf(popupRemoved,popupIdentity)['hasEffect'] and nativeLeaf(popupRemoved,popupIdentity)['blurRegion']==[] and logs()[-1]['rootCommits']==rootBeforePopup and logs()[-1]['childCommits']==childBeforePopup)
   check('nestedPopupOnlyFourApplyingCommits',max(row['popupCommits'] for row in logs() if row['event']=='background-commit')==popupCommits+4)
   command('popup-destroy');nestedFinal=effectFacts();check('nestedDestroyedPopupRetiresItsNativeIdentity',popupIdentity not in {leaf['identity'] for leaf in nativeMember(nestedFinal)['surfaces']} and {leaf['identity'] for leaf in nativeMember(nestedFinal)['surfaces']}==existingIDs)
   malformed=request('preview-family-effect-facts-request',subjectIncarnation=subject,unexpected=True);check('nestedExactReadonlyFactSchemaRejectsExtraField',malformed.get('reason')=='preview-client-schema',reply=malformed)
   r['nestedBackgroundEffectEvidence']={'childBefore':childBefore,'childCreated':childCreated,'childPending':childPending,'childApplied':childApplied,'childChangedPending':childChangedPending,'childChanged':childChanged,'childClearPending':childClearPending,'childCleared':childCleared,'childDestroyPending':childDestroyPending,'childRemoved':childRemoved,'popupBefore':popupBefore,'popupCreated':popupCreated,'popupPending':popupPending,'popupApplied':popupApplied,'popupChangedPending':popupChangedPending,'popupChanged':popupChanged,'popupClearPending':popupClearPending,'popupCleared':popupCleared,'popupDestroyPending':popupDestroyPending,'popupRemoved':popupRemoved,'final':nestedFinal,'childIdentity':childIdentity,'popupIdentity':popupIdentity,'actualNativeChildPopupFactsQualified':True,'backgroundPixelFidelityQualified':False,'previewEligible':False,'hardwarePresentation':False}
   # Exact successfully linked inputs, rather than configured path or later disk bytes.
   check('shaderWholeCropPrivateBlackBackgroundApplied',s.ctl('eval','hl.config({misc={background_color="#000000"}})').strip()=='ok');glowAppliedNativeFrame('shader-black-background')
   shaderReserved=s.data('monitors')[0]['reserved'];shaderBefore=effectFacts();check('shaderInitialAppliedProgramOff',shaderBefore['appliedShader']=={'complete':True,'enabled':False,'contextualUniforms':False,'vertex':'','fragment':''})
   shaderCommits=(logs()[-1]['rootCommits'],logs()[-1]['childCommits']);shaderPath=private/'applied-screen.glsl'
   shaderPrefix='#version 300 es\nprecision highp float;\nin vec2 v_texcoord;\nuniform sampler2D tex;\nout vec4 fragColor;\n'
   shaderA=shaderPrefix+'void main(){fragColor=texture(tex,v_texcoord); }\n'
   shaderB=shaderPrefix+'void main(){fragColor=texture(tex,v_texcoord)*vec4(0.8,1.0,1.0,1.0); }\n'
   def shaderConfiguration(name):
    check(name,s.ctl('eval','hl.config({decoration={screen_shader='+json.dumps(str(shaderPath))+'}})').strip()=='ok')
   def appliedShader(fragment):
    value=request('preview-family-effect-facts-request',subjectIncarnation=subject)
    return value if value.get('kind')=='preview-family-effect-facts' and value['appliedShader']['enabled'] and value['appliedShader']['fragment']==fragment else None
   r['shaderPixelSamples']=[]
   def shaderPixels(name,backdrop=False):
    value=request('preview-family-backdrop-crop-scope-request',subjectIncarnation=subject) if backdrop else configStyleScope();scope=value['scope'];deadline=int(scope['now'])+2000000000;beforeWindows=s.data('clients')
    captured=request('preview-family-backdrop-crop-scoped-request' if backdrop else 'preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedCapture',captured.get('kind')==('preview-family-backdrop-crop-owned' if backdrop else 'preview-family-style-crop-owned') and captured['planeSpace']==('native-generated-backdrop-family-style-cropped-pixels-unqualified' if backdrop else 'native-family-style-cropped-pixels-unqualified') and captured['previewEligible'] is False,reply=captured)
    if backdrop:
     check(name+'ObservedNativeGeneratedColor',value['generatedBackdrop']==captured['generatedBackdrop']=={'kind':'native-opaque-generated-color','colorARGB':'4294967295'})
     wrong,_=styleCropExchange(1,captured['captureRequest'],version=3,expectedStatus=9);check(name+'LegacyFD3CannotImportBackdrop',wrong[2]==9)
     refused=request('preview-family-style-crop-retire-request');check(name+'LegacyPlaneCannotRetireBackdrop',refused.get('reason')=='preview-probe-plane-mismatch')
    h,rights=styleCropExchange(1,captured['captureRequest'],version=4 if backdrop else 3);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]))
     check(name+'OriginalContextAndDeadline',h[22]==(259 if backdrop else 131) and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']])
     check(name+'ExactScopeCrop',list(origin)==[int(value['crop']['pixelX']),int(value['crop']['pixelY'])] and list(h[12:14])==[value['crop']['width'],value['crop']['height']] and captured['pixelScale']==value['crop']['scale']==1)
     if backdrop:check(name+'FD4NativeColorAndPlane',h[1]==4 and h[28]==int(value['generatedBackdrop']['colorARGB']) and h[22]==259)
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CRC',zlib.crc32(blob)==h[17]);image=private/(name+'.png');image.write_bytes(blob);image.chmod(0o600)
     geometry=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(geometry[0]+20),int(geometry[1]+20)]
     family=s.host.launch(name+'-family-pixels',[pre['cropPixelOracle'],str(image),str(point[0]-origin[0]),str(point[1]-origin[1])],env=env);family.wait(timeout=5);check(name+'FamilyDecoderNormalExit',family.returncode==0);familyPixels=json.loads((private/(name+'-family-pixels.log')).read_text())
     output=private/(name+'-native-output.png');grab=s.host.launch(name+'-output',['/usr/bin/grim','-o','WAYLAND-1',str(output)],env=env);grab.wait(timeout=5);check(name+'IndependentOutputNormalExit',grab.returncode==0)
     decoder=s.host.launch(name+'-output-pixels',[pre['cropPixelOracle'],str(output),str(point[0]),str(point[1])],env=env);decoder.wait(timeout=5);check(name+'OutputDecoderNormalExit',decoder.returncode==0);nativePixels=json.loads((private/(name+'-output-pixels.log')).read_text())
     check(name+'NoNativeWindowRelocation',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     sample={'name':name,'source':value,'header':list(h),'familyPixels':familyPixels,'nativePixels':nativePixels,'equalRoot':familyPixels['rootRGBA']==nativePixels['rootRGBA'],'previewEligible':False,'hardwarePresentation':False};r['shaderPixelSamples'].append(sample)
    finally:
     if memory is not None:memory.close()
     os.close(fd)
     try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Shader capture FD unexpectedly live')
     except OSError as error:check(name+'PhysicalFDClosed',error.errno==9)
     released,_=styleCropExchange(2,captured['captureRequest'],h[16],version=4 if backdrop else 3);check(name+'ExactExportReleased',released[16]==h[16]);retired=request('preview-family-backdrop-crop-retire-request' if backdrop else 'preview-family-style-crop-retire-request');check(name+'ProducerRetired',retired.get('kind')==('preview-family-backdrop-crop-retired' if backdrop else 'preview-family-style-crop-retired') and retired['ownedBytes']=='0')
    return sample
   shaderPath.write_text(shaderA);shaderConfiguration('shaderConfigureActualRegularFile');shaderLoaded=wait(lambda:appliedShader(shaderA))
   check('shaderActualLinkedInputsCopied',shaderLoaded['appliedShader']['complete'] and not shaderLoaded['appliedShader']['contextualUniforms'] and '#version 300 es' in shaderLoaded['appliedShader']['vertex'] and int(shaderLoaded['scope']['context']['content'])>int(shaderBefore['scope']['context']['content']))
   shaderIdentityPixels=shaderPixels('shader-identity-pixels')
   shaderPath.write_text(shaderB);shaderDiskChanged=effectFacts();check('shaderDiskEditDoesNotChangeAppliedProgram',shaderDiskChanged['appliedShader']==shaderLoaded['appliedShader'] and shaderDiskChanged['scope']['context']==shaderLoaded['scope']['context'])
   shaderConfiguration('shaderReloadSamePathActualConfig');shaderReloaded=wait(lambda:appliedShader(shaderB))
   check('shaderSamePathNewLinkedSourceAdvancesContent',int(shaderReloaded['scope']['context']['content'])>int(shaderLoaded['scope']['context']['content']) and shaderReloaded['appliedShader']['vertex']==shaderLoaded['appliedShader']['vertex'] and shaderLoaded['appliedShader']['fragment']==shaderA)
   shaderTintPixels=shaderPixels('shader-tint-pixels')
   check('shaderWholeRootSameGeometry',shaderIdentityPixels['source']['crop']==shaderTintPixels['source']['crop'] and shaderIdentityPixels['source']['members']==shaderTintPixels['source']['members'])
   crop=shaderIdentityPixels['source']['crop'];geometry=next(row['geometry'] for row in shaderIdentityPixels['source']['members'] if row['incarnation']==subject)
   paths=[private/name for name in ['shader-identity-pixels.png','shader-tint-pixels.png','shader-identity-pixels-native-output.png','shader-tint-pixels-native-output.png']]
   compare=s.host.launch('shader-whole-root-pixels',[pre['shaderPixelOracle'],*[str(path) for path in paths],crop['pixelX'],crop['pixelY'],*[str(int(v)) for v in geometry[:4]]],env=env);compare.wait(timeout=5)
   check('shaderWholeRootDecoderCompleted',compare.returncode in [0,2]);r['shaderWholeRootPixels']=json.loads((private/'shader-whole-root-pixels.log').read_text())

   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(int(request('preview-client-clock-request')['nowNs'])+2000000000),context=shaderLoaded['scope']['context']);check('shaderOldAppliedProgramContextRefusedBeforeAllocation',denied.get('reason')=='preview-probe-context-stale',reply=denied);check('shaderStaleProgramAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   shaderConfiguration('shaderIdenticalStaticReload');glowAppliedNativeFrame('shader-identical');shaderStable=effectFacts();check('shaderIdenticalStaticProgramKeepsContent',shaderStable['appliedShader']==shaderReloaded['appliedShader'] and shaderStable['scope']['context']==shaderReloaded['scope']['context'])
   check('shaderHalfActualNativeRootFocus',s.ctl('dispatch',"hl.dsp.focus({window='address:"+source['address']+"'})").strip()=='ok');wait(lambda:s.data('activewindow').get('address')==source['address'])
   shaderHalfCursor=s.data('cursorpos');check('shaderHalfPrivateCursorOutsideBody',s.ctl('dispatch','hl.dsp.cursor.move({x=790,y=590})').strip()=='ok');check('shaderHalfNativeCursorOutsideBodyObserved',s.data('cursorpos')=={'x':790,'y':590})
   opacityProperty('no_blur','1','shaderHalfBodyExplicitNoBlur');opacityProperty('opaque','0','shaderHalfBodyNoOpaqueOverride');opacityProperty('opacity','0.5','shaderHalfBodyActiveHalf');opacityProperty('opacity_inactive','0.5','shaderHalfBodyInactiveHalf');glowAppliedNativeFrame('shader-half-body')
   shaderHalfScope=configStyleScope();check('shaderHalfBodyNativeDeclaredAlpha',abs(rootStyle(shaderHalfScope)['channels'][1]-.5)<1e-6)
   shaderPixels('shader-half-body-pixels');r['shaderHalfBodyPixels']=r['shaderPixelSamples'].pop()
   halfCrop=r['shaderHalfBodyPixels']['source']['crop'];halfGeometry=next(row['geometry'] for row in r['shaderHalfBodyPixels']['source']['members'] if row['incarnation']==subject);halfImages=[private/name for name in ['shader-half-body-pixels.png','shader-half-body-pixels-native-output.png']]
   halfDecoder=s.host.launch('shader-half-body-comparison',[pre['shaderHalfBodyPixelOracle'],*[str(path) for path in halfImages],halfCrop['pixelX'],halfCrop['pixelY'],*[str(int(v)) for v in halfGeometry[:4]]],env=env);halfDecoder.wait(timeout=5);check('shaderHalfBodyDecoderCompleted',halfDecoder.returncode==0);r['shaderHalfBodyComparison']=json.loads((private/'shader-half-body-comparison.log').read_text());r['shaderHalfBodyExplicitNoBlur']=True
   blurKeys=['enabled','size','passes','new_optimizations','xray','ignore_opacity','brightness','contrast','vibrancy','vibrancy_darkness','noise'];blurSaved={key:s.data('getoption','decoration:blur:'+key) for key in blurKeys}
   blurSavedValues={key:next(value[k] for k in ['int','float','bool'] if k in value) for key,value in blurSaved.items()}
   check('blurBodyNativeRootHasNoProtocolOverride',not nativeMember(effectFacts())['root']['hasEffect'])
   opacityProperty('no_blur','0','blurBodyNativeBlurAllowed')
   check('blurBodyPrivateWhiteBackdropApplied',s.ctl('eval','hl.config({misc={background_color="#ffffff"},decoration={blur={enabled=true,size=8,passes=2,new_optimizations=false,xray=false,ignore_opacity=false,brightness=0.5,contrast=1,vibrancy=0,vibrancy_darkness=0,noise=0}}})').strip()=='ok');glowAppliedNativeFrame('blur-body-half-brightness')
   check('blurBodyActualHalfBrightnessObserved',s.data('getoption','decoration:blur:brightness')['float']==.5)
   shaderPixels('blur-body-half-brightness',backdrop=True);blurFirst=r['shaderPixelSamples'].pop()
   check('blurBodyConfigureFullBrightness',s.ctl('eval','hl.config({decoration={blur={brightness=1}}})').strip()=='ok');glowAppliedNativeFrame('blur-body-full-brightness')
   check('blurBodyActualFullBrightnessObserved',s.data('getoption','decoration:blur:brightness')['float']==1)
   shaderPixels('blur-body-full-brightness',backdrop=True);blurSecond=r['shaderPixelSamples'].pop()
   check('blurBodyOnlyConfigurationChangesSource',blurFirst['source']['members']==blurSecond['source']['members'] and blurFirst['source']['styles']==blurSecond['source']['styles'] and blurFirst['source']['crop']==blurSecond['source']['crop'] and int(blurSecond['source']['scope']['context']['content'])>int(blurFirst['source']['scope']['context']['content']))
   blurCrop=blurFirst['source']['crop'];blurGeometry=next(row['geometry'] for row in blurFirst['source']['members'] if row['incarnation']==subject);blurImages=[private/name for name in ['blur-body-half-brightness.png','blur-body-full-brightness.png','blur-body-half-brightness-native-output.png','blur-body-full-brightness-native-output.png']]
   blurDecoder=s.host.launch('blur-body-delta-comparison',[pre['blurBodyDeltaOracle'],*[str(path) for path in blurImages],blurCrop['pixelX'],blurCrop['pixelY'],*[str(int(v)) for v in blurGeometry[:4]]],env=env);blurDecoder.wait(timeout=5);check('blurBodyDecoderCompleted',blurDecoder.returncode==0);r['blurBodyEvidence']={'before':blurFirst,'after':blurSecond,'configurationBeforeExperiment':blurSaved,'pixels':json.loads((private/'blur-body-delta-comparison.log').read_text()),'generatedBackdrop':'#ffffff','nativeBlurExplicitlyAllowed':True,'previewEligible':False}
   r['blurBodyExactPixels']=[]
   for blurSample in [blurFirst,blurSecond]:
    name=blurSample['name'];crop=blurSample['source']['crop'];geometry=next(row['geometry'] for row in blurSample['source']['members'] if row['incarnation']==subject);paths=[private/(name+suffix) for suffix in ['.png','-native-output.png']];comparison=s.host.launch(name+'-body-equality',[pre['blurBodyPixelOracle'],*[str(path) for path in paths],crop['pixelX'],crop['pixelY'],*[str(int(v)) for v in geometry[:4]]],env=env);comparison.wait(timeout=5);check(name+'ExactBodyDecoderCompleted',comparison.returncode==0);r['blurBodyExactPixels'].append({'name':name,'pixels':json.loads((private/(name+'-body-equality.log')).read_text())})
   # Same full shared GUI35 owns the new FD4 source with its own child grant.
   fullLogName='full-generated-backdrop-provider'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-backdrop-family',subject,'--qa-preview-snapshot',str(private/'backdrop-webkit.png')],env=env)
   familyHistoricalPointer('backdropWebOpen');wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   backdropSeed=next(event for event in events() if event['kind']=='source-seed');backdropOffer=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer');backdropReady=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='fence')
   check('backdropWebOwnTypedNativeChildGrant',backdropSeed['source']['kind']=='preview-family-backdrop-crop-scope' and backdropSeed['source']['scopeKind']=='native-generated-backdrop-family-crop-unqualified' and backdropSeed['source']['generatedBackdrop']=={'kind':'native-opaque-generated-color','colorARGB':'4294967295'} and backdropSeed['source']['binding']!=attached['binding'] and backdropSeed['source']['scope']['binding']==backdropSeed['source']['binding'] and backdropSeed['identity']=='family:'+subject and backdropSeed['source']['previewEligible'] is False,source=backdropSeed)
   check('backdropWebOriginalDeadlineAndCompleteFamilyFence',backdropOffer['job']['binding']==backdropSeed['source']['binding'] and backdropOffer['job']['context']==backdropSeed['source']['scope']['context'] and backdropOffer['job']['clock']==backdropSeed['source']['scope']['clock'] and int(backdropOffer['job']['deadline'])==int(backdropSeed['source']['scope']['now'])+2000000000 and backdropOffer['job']['origin']==backdropSeed['lease'] and not backdropOffer['signaled'] and backdropReady=={**backdropOffer,'signaled':True} and backdropReady['fidelity']=='family' and backdropReady['coverage']==['client','decoration','modal','popup'],offer=backdropOffer,fence=backdropReady)
   backdropImages=[json.loads(line[len('native-client-image: '):]) for line in fullLog().splitlines() if line.startswith('native-client-image: ')]
   backdropCrop=backdropSeed['source']['crop'];backdropScale=min(160/backdropCrop['width'],120/backdropCrop['height']);backdropDisplay=[round(backdropCrop['width']*backdropScale),round(backdropCrop['height']*backdropScale)]
   check('backdropWebActualSharedURIAndNativeCropDimensions',backdropImages and all(len(row)==1 and row[0]['uri']=='elm-shell://preview/'+backdropOffer['handle'] and row[0]['naturalWidth']==backdropSeed['source']['crop']['width'] and row[0]['naturalHeight']==backdropSeed['source']['crop']['height'] and [row[0]['width'],row[0]['height']]==backdropDisplay for row in backdropImages),images=backdropImages)
   backdropDecoder=s.host.launch('backdrop-web-pixel-comparison',[pre['backdropWebPixelOracle'],str(private/'backdrop-webkit.png'),*map(str,blurSecond['nativePixels']['rootRGBA'])],env=env);backdropDecoder.wait(timeout=5);check('backdropWebIndependentPixelDecoderNormalExit',backdropDecoder.returncode==0);backdropWebPixels=json.loads((private/'backdrop-web-pixel-comparison.log').read_text())
   familyHistoricalPointer('backdropWebClose');wait(lambda:'surface-popup-closed: lease='+backdropSeed['lease'] in fullLog());check('backdropWebClosedPresentationRetainsOriginalResource','native-client-command: {"kind":"release"' not in fullLog())
   backdropCommits=logs()[-1]['rootCommits'];check('backdropWebActualGeneratedNativeColorChanged',s.ctl('eval','hl.config({misc={background_color="#000000"}})').strip()=='ok')
   familyHistoricalPointer('backdropWebReopen')
   def changedBackdropSeed():
    return next((event for event in events() if event['kind']=='source-seed' and int(event['lease'])>int(backdropSeed['lease']) and event['source'].get('generatedBackdrop',{}).get('colorARGB')=='4278190080'),None)
   backdropChanged=wait(changedBackdropSeed)
   check('backdropWebNativeColorRevisionAdvancesExistingSourceEpoch',backdropChanged['source']['binding']==backdropSeed['source']['binding'] and backdropChanged['source']['scope']['sourceLive'] and int(backdropChanged['source']['scope']['context']['content'])>int(backdropSeed['source']['scope']['context']['content']) and backdropCommits==logs()[-1]['rootCommits'],before=backdropSeed,after=backdropChanged)
   def backdropHistoricalProjection():
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in rows if row['body']['publication']==backdropChanged['publication'] and row['body']['lease']==backdropChanged['lease'] and 'Historical preview' in row['body']['text']),None)
   backdropProjection=wait(backdropHistoricalProjection)
   check('backdropWebSharedElmRetainsOriginalHistoricalImage',backdropProjection is not None and [event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer']==[backdropOffer] and len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1 and 'native-client-resume:' not in fullLog() and 'native-client-command: {"kind":"release"' not in fullLog(),projection=backdropProjection)
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('backdropWeb',backdropOffer)
   backdropExpired=[event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='expired'];check('backdropWebExpiryKeepsExactOriginalFrameAndDeadline',backdropExpired==[backdropReady],expired=backdropExpired)
   backdropZero=[row for row in ownership() if row['job']==backdropOffer['job'] and row['charge']=='0' and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending']]
   check('backdropWebFD4PhysicalRetirementBeforeExactReceiptACK',backdropZero and acks()==[{'kind':'acknowledge','job':backdropOffer['job'],'sequence':'3'}] and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ownership: '+json.dumps(backdropZero[0],separators=(',',':')))<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'),ownership=ownership(),acks=acks())
   r['backdropWebKitEvidence']={'initialSource':backdropSeed,'changedLiveSource':backdropChanged,'originalFrame':backdropOffer,'historicalProjection':backdropProjection,'images':backdropImages,'pixels':backdropWebPixels,'ownership':ownership(),'acks':acks(),'previewEligible':False,'hardwarePresentation':False,'allBodyPixelEqualityClaimed':False}
   web.terminate();web.wait(timeout=5);check('backdropWebHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   check('backdropWebRestoreGeneratedWhiteBeforeOriginalCleanup',s.ctl('eval','hl.config({misc={background_color="#ffffff"}})').strip()=='ok')
   # Actual generated source loss must retire the original owned GUI frame.
   fullLogName='full-generated-backdrop-source-loss'
   # Private application desktop icon for the actual native class, never an installed override.
   iconData=private/'fallback-data';(iconData/'applications').mkdir(parents=True,mode=0o700)
   iconBytes=bytearray([224,34,221,255]*64)
   def pngChunk(kind,value):return struct.pack('>I',len(value))+kind+value+struct.pack('>I',zlib.crc32(kind+value)&0xffffffff)
   scan=b''.join(b'\0'+bytes(iconBytes[row*32:(row+1)*32]) for row in range(8))
   ownIcon=iconData/'own-icon.png';ownIcon.write_bytes(b'\x89PNG\r\n\x1a\n'+pngChunk(b'IHDR',struct.pack('>IIBBBBB',8,8,8,6,0,0,0))+pngChunk(b'IDAT',zlib.compress(scan))+pngChunk(b'IEND',b''));ownIcon.chmod(0o600)
   desktop=iconData/'applications/warlock-child-probe.desktop';desktop.write_text('[Desktop Entry]\nType=Application\nName=Warlock own fallback fixture\nExec=/usr/bin/true\nIcon='+str(ownIcon)+'\n');desktop.chmod(0o600)
   fallbackEnv=dict(env,XDG_DATA_DIRS=str(iconData)+':'+env.get('XDG_DATA_DIRS','/usr/local/share:/usr/share'))
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-backdrop-family',subject,'--qa-preview-snapshot',str(private/'backdrop-loss-webkit.png')],env=fallbackEnv)
   familyHistoricalPointer('backdropLossOpen');wait(lambda:'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   lossSeed=next(event for event in events() if event['kind']=='source-seed');lossOffer=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer');lossReady=next(event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='fence')
   check('backdropLossOriginalOwnGeneratedSourceAndCompleteFrame',lossSeed['source']['kind']=='preview-family-backdrop-crop-scope' and lossSeed['source']['generatedBackdrop']['colorARGB']=='4294967295' and lossSeed['source']['binding']!=attached['binding'] and lossOffer['job']['binding']==lossSeed['source']['binding'] and lossReady=={**lossOffer,'signaled':True} and lossReady['fidelity']=='family' and lossReady['coverage']==['client','decoration','modal','popup'],source=lossSeed,frame=lossOffer)
   fallbackMetadata=next(event for event in events() if event['kind']=='metadata')
   check('fallbackActualTitleClassAndApplicationIconIdentity',lossSeed['title']=='WARLOCK-CHILD-PROBE' and lossSeed['application']=='warlock-child-probe' and fallbackMetadata['binding']==lossOffer['job']['binding'] and fallbackMetadata['subject']==subject and fallbackMetadata['identity']=='family:'+subject and fallbackMetadata['title']==lossSeed['title'] and fallbackMetadata['application']==lossSeed['application'] and fallbackMetadata['iconKind']=='application' and re.fullmatch('[0-9a-f]{64}',fallbackMetadata['icon']) and int(fallbackMetadata['revision'])>0,metadata=fallbackMetadata,source=lossSeed)
   fallbackExpected=blurSecond['nativePixels']['rootRGBA']
   def fallbackPixels(name,path):
    decoder=s.host.launch(name,[pre['fallbackPixelOracle'],str(path),*map(str,fallbackExpected)],env=env);decoder.wait(timeout=5);check(name+'DecoderNormalExit',decoder.returncode==0);return json.loads((private/(name+'.log')).read_text())
   fallbackBefore=fallbackPixels('fallback-before-pixels',private/'backdrop-loss-webkit.png');check('fallbackOriginalActualNativeSourcePixelsPresent',fallbackBefore['oldSourceExactNativePixels']>128 and fallbackBefore['foreignGreenPixels']==0,pixels=fallbackBefore)
   lossCommits=logs()[-1]['rootCommits'];check('backdropLossActualNonopaqueNativeColorApplied',s.ctl('eval','hl.config({misc={background_color="rgba(ffffff80)"}})').strip()=='ok')
   lossNative=request('preview-family-backdrop-crop-scope-request',subjectIncarnation=subject);check('backdropLossExactAuthenticatedNativeUnavailable',lossNative.get('kind')=='refused' and lossNative.get('reason')=='preview-family-backdrop-source-unavailable' and lossCommits==logs()[-1]['rootCommits'],reply=lossNative)
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('backdropLoss',lossOffer)
   lossEvents=[event['event'] for event in events() if event['kind']=='event' and event['event']['kind']=='source-denied'];check('backdropLossTypedDenialUsesExactOriginalJobWithoutFabricatedScope',lossEvents==[{'kind':'source-denied','job':lossOffer['job'],'reason':'source-unavailable'}],events=lossEvents)
   check('backdropLossNoReplayOrDeadlineRenewal',len([line for line in fullLog().splitlines() if line.startswith('native-client-command: {"kind":"acquire"')])==1 and 'native-client-resume:' not in fullLog() and int(lossOffer['job']['deadline'])==int(lossSeed['source']['scope']['now'])+2000000000 and not any(event['kind']=='event' and event['event']['kind']=='expired' for event in events()))
   lossZero=[row for row in ownership() if row['job']==lossOffer['job'] and row['charge']=='0' and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending']]
   check('backdropLossPhysicalFD4RetirementBeforeOriginalTerminalACK',lossZero and acks()==[{'kind':'acknowledge','job':lossOffer['job'],'sequence':'3'}] and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ownership: '+json.dumps(lossZero[0],separators=(',',':')))<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'),ownership=ownership(),acks=acks())
   r['backdropSourceLossEvidence']={'source':lossSeed,'frame':lossOffer,'denial':lossNative,'events':lossEvents,'ownership':ownership(),'acks':acks(),'rootCommitsUnchanged':lossCommits==logs()[-1]['rootCommits'],'previewEligible':False,'hardwarePresentation':False,'frontendStallQualified':False}
   def fallbackReport():
    rows=[json.loads(line[len('native-client-fallback: '):]) for line in fullLog().splitlines() if line.startswith('native-client-fallback: ')]
    return rows[-1] if rows else None
   fallbackShown=wait(fallbackReport);fallbackImage=private/'backdrop-loss-webkit.png.fallback.png';wait(lambda:fallbackImage.exists() and ('path='+str(fallbackImage)) in fullLog())
   check('fallbackActualUnavailableTitleAndResolvedIconInPopup',len(fallbackShown)==1 and fallbackShown[0]['state']=='unavailable' and fallbackShown[0]['title']=='WARLOCK-CHILD-PROBE' and len(fallbackShown[0]['icons'])==1 and fallbackShown[0]['icons'][0]['uri']=='elm-shell://icon/'+fallbackMetadata['icon'] and fallbackShown[0]['icons'][0]['complete'] and all(0<fallbackShown[0]['icons'][0][key]<=128 for key in ['naturalWidth','naturalHeight','width','height']),dom=fallbackShown)
   fallbackAfter=fallbackPixels('fallback-after-pixels',fallbackImage);check('fallbackActualOwnApplicationIconExcludesOldAndForeignPixels',fallbackAfter['ownApplicationIconPixels']>=128 and fallbackAfter['oldSourceExactNativePixels']==0 and fallbackAfter['foreignGreenPixels']==0,pixels=fallbackAfter)
   r['fallbackMetadataEvidence']={'scenarioId':'ELM-UX-007 ux-007','metadata':fallbackMetadata,'actualNativeTitle':lossSeed['title'],'actualNativeApplication':lossSeed['application'],'originalJob':lossOffer['job'],'unavailableDenial':lossNative,'dom':fallbackShown,'beforePixels':fallbackBefore,'afterPixels':fallbackAfter,'iconAssetSHA256':sha(ownIcon),'desktopEntrySHA256':sha(desktop),'hardwarePresentation':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'lockedConcealmentNativeQualified':False,'ordinaryProductEnrollmentQualified':False}
   web.terminate();web.wait(timeout=5);check('backdropLossHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   check('backdropLossRestoreGeneratedWhiteBeforeOriginalCleanup',s.ctl('eval','hl.config({misc={background_color="#ffffff"}})').strip()=='ok')
   blurRestore=','.join(key+'='+('true' if value is True else 'false' if value is False else str(value)) for key,value in blurSavedValues.items());check('blurBodyRestoreOriginalNativeConfiguration',s.ctl('eval','hl.config({misc={background_color="#000000"},decoration={blur={'+blurRestore+'}}})').strip()=='ok');glowAppliedNativeFrame('blur-body-restored')
   check('blurBodyExactOriginalNativeConfigurationObserved',all(next(s.data('getoption','decoration:blur:'+key)[k] for k in ['int','float','bool'] if k in blurSaved[key])==value for key,value in blurSavedValues.items()))
   opacityProperty('opacity','1','shaderHalfBodyRestoreActive');opacityProperty('opacity_inactive','1','shaderHalfBodyRestoreInactive');opacityProperty('no_blur','0','shaderHalfBodyRestoreBlurDefault');glowAppliedNativeFrame('shader-half-body-restored')
   check('shaderHalfRestoreOriginalNativeCursor',s.ctl('dispatch','hl.dsp.cursor.move({x='+str(shaderHalfCursor['x'])+',y='+str(shaderHalfCursor['y'])+'})').strip()=='ok');check('shaderHalfOriginalNativeCursorObserved',s.data('cursorpos')==shaderHalfCursor);r['shaderHalfCursorEvidence']={'before':shaderHalfCursor,'measurement':{'x':790,'y':590},'restored':s.data('cursorpos')}
   shaderCoordinate=shaderPrefix+'void main(){fragColor=vec4(v_texcoord.x,v_texcoord.y,0.0,1.0); }\n'
   shaderPath.write_text(shaderCoordinate);shaderConfiguration('shaderLoadActualCoordinateProgram');coordinateLoaded=wait(lambda:appliedShader(shaderCoordinate))
   check('shaderCoordinateProgramIsStaticAndSourceTracked',coordinateLoaded['appliedShader']['complete'] and not coordinateLoaded['appliedShader']['contextualUniforms'] and int(coordinateLoaded['scope']['context']['content'])>int(shaderStable['scope']['context']['content']))
   shaderPixels('shader-coordinate-pixels');r['shaderCoordinatePixels']=r['shaderPixelSamples'].pop()
   r['shaderCompositedCropPixels']=[]
   for sample in r['shaderPixelSamples']:
    name=sample['name'];crop=sample['source']['crop'];paths=[private/(name+suffix) for suffix in ['.png','-native-output.png']]
    composite=s.host.launch(name+'-whole-composite',[pre['compositedCropPixelOracle'],*[str(p) for p in paths],crop['pixelX'],crop['pixelY']],env=env);composite.wait(timeout=5);check(name+'WholeCompositeDecoderCompleted',composite.returncode==0);r['shaderCompositedCropPixels'].append({'name':name,'pixels':json.loads((private/(name+'-whole-composite.log')).read_text())})

   coordinateSample=r['shaderCoordinatePixels'];coordinateCrop=coordinateSample['source']['crop'];coordinateGeometry=next(row['geometry'] for row in coordinateSample['source']['members'] if row['incarnation']==subject)
   coordinateImages=[private/name for name in ['shader-coordinate-pixels.png','shader-coordinate-pixels-native-output.png']]
   wholeCoordinates=s.host.launch('shader-whole-coordinate-pixels',[pre['coordinatePixelOracle'],*[str(p) for p in coordinateImages],coordinateCrop['pixelX'],coordinateCrop['pixelY'],*[str(int(v)) for v in coordinateGeometry[:4]]],env=env);wholeCoordinates.wait(timeout=5);check('shaderWholeCoordinateDecoderCompleted',wholeCoordinates.returncode in [0,2]);r['shaderWholeCoordinatePixels']=json.loads((private/'shader-whole-coordinate-pixels.log').read_text())

   # Active contextual uniforms cannot claim a current source without their dependencies.
   shaderDynamic=shaderPrefix+'uniform float time;\nvoid main(){fragColor=texture(tex,v_texcoord)*vec4(0.5+0.1*sin(time),1.0,1.0,1.0); }\n'
   shaderPath.write_text(shaderDynamic);shaderConfiguration('shaderLoadActualTimeUniform')
   shaderUnavailable=wait(lambda:(lambda value:value if value.get('reason')=='preview-family-style-source-unavailable' else None)(request('preview-family-effect-facts-request',subjectIncarnation=subject)))
   denied=request('preview-family-style-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(time.monotonic_ns()+2000000000),context=shaderStable['scope']['context']);check('shaderContextualProgramRefusesCapture',denied.get('reason')=='preview-probe-source-epoch-unavailable',reply=denied);check('shaderContextualProgramAllocatesNoProducer',request('preview-family-style-crop-state-request').get('reason')=='preview-probe-unavailable')
   shaderPath.write_text(shaderB);shaderConfiguration('shaderRecoverActualStaticProgram');shaderRecovered=wait(lambda:appliedShader(shaderB));check('shaderRecoveryAdvancesPastPriorProgram',int(shaderRecovered['scope']['context']['content'])>int(shaderStable['scope']['context']['content']))
   shaderPath.write_text('this is not GLSL\n');shaderConfiguration('shaderCompileFailureActualReload');glowAppliedNativeFrame('shader-failed')
   def shaderOff():
    value=request('preview-family-effect-facts-request',subjectIncarnation=subject)
    return value if value.get('kind')=='preview-family-effect-facts' and value['appliedShader']==shaderBefore['appliedShader'] else None
   shaderFailed=wait(shaderOff);check('shaderFailedCompilationRetiresOldAppliedSource',int(shaderFailed['scope']['context']['content'])>int(shaderRecovered['scope']['context']['content']))
   check('shaderDisablePrivateConfiguration',s.ctl('eval','hl.config({decoration={screen_shader=""}})').strip()=='ok');glowAppliedNativeFrame('shader-disabled');shaderDisabled=effectFacts();check('shaderDisabledAppliedProgramOff',shaderDisabled['appliedShader']==shaderBefore['appliedShader'])
   shaderErrorReserved=s.data('monitors')[0]['reserved'];check('shaderCompileFaultProducesNativeErrorReservedArea',shaderErrorReserved!=shaderReserved,before=shaderReserved,after=shaderErrorReserved)
   check('shaderPrivateErrorOverlayCleanup',s.ctl('seterror','disable').strip()=='ok');glowAppliedNativeFrame('shader-error-cleanup');wait(lambda:s.data('monitors')[0]['reserved']==shaderReserved)
   check('shaderPrivateReservedAreaActuallyRestored',s.data('monitors')[0]['reserved']==shaderReserved,before=shaderReserved,after=s.data('monitors')[0]['reserved'])
   check('shaderWholeCropPrivateBackgroundRestored',s.ctl('eval','hl.config({misc={background_color="#111111"}})').strip()=='ok');glowAppliedNativeFrame('shader-background-restored')
   check('shaderAllSourceChangesWithoutBufferCommits',(logs()[-1]['rootCommits'],logs()[-1]['childCommits'])==shaderCommits)
   r['appliedShaderEvidence']={'before':shaderBefore,'loaded':shaderLoaded,'diskChanged':shaderDiskChanged,'reloaded':shaderReloaded,'stable':shaderStable,'contextualUnavailable':shaderUnavailable,'recovered':shaderRecovered,'failed':shaderFailed,'disabled':shaderDisabled,'privateReservedAreaBefore':shaderReserved,'privateErrorReservedArea':shaderErrorReserved,'privateReservedAreaAfter':s.data('monitors')[0]['reserved'],'rootChildCommitsUnchanged':True,'actualAppliedShaderFactsQualified':True,'shaderPixelFidelityQualified':False,'backgroundPixelFidelityQualified':False,'previewEligible':False,'hardwarePresentation':False}
   # Original ELM-REN-004 address reuse: a real full GUI owns this old lease.
   reuseBefore=request('scene-facts-request',minimumWatermark='0');reuseOldIDs={w['incarnation'] for w in reuseBefore['facts']['windows']}
   reuseControl=private/'reuse-source-control';reuseReaderControl=private/'reuse-reader-control';writeControl(reuseReaderControl,'hold')
   reuseSource=s.host.launch('reuse-old-source',[pre['fixtureClient']],env=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(reuseControl)))
   reuseWindow=wait(lambda:next((w for w in s.data('clients') if w['pid']==reuseSource.pid and w['title']=='WARLOCK-CHILD-PROBE'),None))
   reuseScene=request('scene-facts-request',minimumWatermark='0');reuseSubjects=[w['incarnation'] for w in reuseScene['facts']['windows'] if w['incarnation'] not in reuseOldIDs and w['application']=='warlock-child-probe'];check('reuseSeparateActualNativeSource',len(reuseSubjects)==1)
   reuseSubject=reuseSubjects[0];reusePacket=openQualification('reuse',reuseSubject)
   def readerSamples(prefix):return [json.loads(line[len(prefix):]) for line in fullLog().splitlines() if line.startswith(prefix)]
   readerReady=wait(lambda:next(iter(readerSamples('native-client-reader-ready: ')),None))
   check('reuseFullGUIHeldSameEndpointOriginalPhysicalFrame',readerReady['uri']=='elm-shell://preview/'+reusePacket['handle'] and readerReady['request']==reusePacket['job']['request'] and readerReady['status']['job']==reusePacket['job'] and int(readerReady['status']['charge'])>0 and not readerReady['status']['mappedFDClosed'] and readerReady['firstByte']==137,evidence=readerReady)
   reuseOldAddress=reuseWindow['address'];reuseAttempts=[]
   writeControl(reuseControl,'1 quit');reuseSource.wait(timeout=5);check('reuseOldNativeSourceNormalExit',reuseSource.returncode==0)
   wait(lambda:not any(w['address']==reuseOldAddress for w in s.data('clients')))
   reuseSeenIDs={w['incarnation'] for w in request('scene-facts-request',minimumWatermark='0')['facts']['windows']}
   replacement=None
   for attempt in range(1,13):
    reuseControl.unlink()  # Previous process consumed its quit; no stimulus is inherited.
    reuseSource=s.host.launch('reuse-replacement-'+str(attempt),[pre['fixtureClient']],env=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(reuseControl)))
    newWindow=wait(lambda:next((w for w in s.data('clients') if w['pid']==reuseSource.pid and w['title']=='WARLOCK-CHILD-PROBE'),None))
    newScene=request('scene-facts-request',minimumWatermark='0');freshIDs=[w['incarnation'] for w in newScene['facts']['windows'] if w['incarnation'] not in reuseSeenIDs and w['application']=='warlock-child-probe'];check('reuseAttempt'+str(attempt)+'OneFreshNativeIncarnation',len(freshIDs)==1)
    freshSubject=freshIDs[0];freshScope=request('preview-client-scope-request',subjectIncarnation=freshSubject)
    check('reuseAttempt'+str(attempt)+'OriginalClockBeforeExpiry',freshScope['kind']=='preview-client-scope' and freshScope['scope']['clock']==reusePacket['job']['clock'] and int(freshScope['scope']['now'])<int(reusePacket['expires']) and int(freshSubject)>int(reuseSubject),scope=freshScope)
    reuseAttempts.append({'attempt':attempt,'oldAddress':reuseOldAddress,'newAddress':newWindow['address'],'oldSubject':reuseSubject,'newSubject':freshSubject,'scope':freshScope['scope']})
    if newWindow['address']==reuseOldAddress:
     replacement={'window':newWindow,'subject':freshSubject,'scope':freshScope['scope']};break
    writeControl(reuseControl,'1 quit');reuseSource.wait(timeout=5);check('reuseAttempt'+str(attempt)+'UnreusedSourceNormalExit',reuseSource.returncode==0)
    wait(lambda:not any(w['pid']==reuseSource.pid for w in s.data('clients')))
    reuseSeenIDs={w['incarnation'] for w in request('scene-facts-request',minimumWatermark='0')['facts']['windows']}
   r['addressReuseAttempts']=reuseAttempts
   check('reuseActuallyObservedEqualNativeAddressFreshIncarnation',replacement is not None,attempts=reuseAttempts)
   oldScope=request('preview-client-scope-request',subjectIncarnation=reuseSubject)
   check('reuseOldIncarnationScopeActuallyRefused',oldScope.get('kind')=='refused' and oldScope.get('reason')=='preview-client-scope-source-unavailable',reply=oldScope)
   def replacementPopup():
    rows=[json.loads(line[len('surface-report: origin=popup '):])['body'] for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    if not rows:return None
    body=rows[-1];ids=[w['id'] for w in body['buttons'] if w['id'].startswith('picker:')]
    return body if any(x.endswith(':'+replacement['subject']) for x in ids) and not any(x.endswith(':'+reuseSubject) for x in ids) else None
   # Native source replacement closes the picker under existing policy.
   # Reopen through real pointer input after the replacement is mapped.
   target=wait(sourceButton);x=round(target['x']+target['width']/2);y=round(target['y']+target['height']/2)
   check('reuseReplacementPointerTargetInOutput',0<x<800 and 0<y<48)
   pointerLog=private/'reuse-reopen-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='reuse-reopen-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n').encode(),timeout=5);check('reuseReplacementPointerNormalExit',ptr.returncode==0)
   replacementDOM=wait(replacementPopup)
   writeControl(reuseReaderControl,'probe');probe=wait(lambda:next(iter(readerSamples('native-client-reader-probe: ')),None))
   probeScope=request('preview-client-scope-request',subjectIncarnation=replacement['subject'])
   check('reuseDeniedBeforeOriginalExpiry',probeScope['kind']=='preview-client-scope' and probeScope['scope']['clock']==reusePacket['job']['clock'] and int(probeScope['scope']['now'])<int(reusePacket['expires']),scope=probeScope)
   check('reuseHeldAndFreshURIRefusedBeforeElmNativeEffects',probe['heldDenied'] and probe['freshDenied'] and probe['heldRead']==-1 and probe['uri']==readerReady['uri'] and probe['status']['job']==reusePacket['job'] and int(probe['status']['charge'])>0 and not probe['status']['mappedFDClosed'] and not probe['status']['exportReleased'] and not probe['status']['producerRetired'] and not any(line.startswith('native-client-command: {"kind":"release"') for line in fullLog().splitlines()) and not any(event['kind']=='event' and event['event']['kind']=='source-denied' for event in events()),evidence=probe)
   writeControl(reuseReaderControl,'release')
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   afterImage=private/'reuse-webkit-client.png.after-reuse.png';wait(lambda:afterImage.exists() and any('path='+str(afterImage) in line for line in fullLog().splitlines() if line.startswith('native-client-webkit-snapshot-job: ')))
   reusePixels=[]
   for tag,image in [('before',private/'reuse-webkit-client.png'),('after',afterImage)]:
    decoder=s.host.launch('reuse-popup-'+tag,[pre['familyWebPixelOracle'],str(image)],env=env);decoder.wait(timeout=5);check('reusePopup'+tag.title()+'PixelOracleNormalExit',decoder.returncode==0)
    reusePixels.append(json.loads((private/('reuse-popup-'+tag+'.log')).read_text()))
   check('reuseFullElmReplacementContainsNoOldPreviewPixels',reusePixels[0]['styledRoot']>128 and reusePixels[1]['styledRoot']==0 and reusePixels[1]['foreignGreen']==0,pixels=reusePixels,report=replacementDOM)
   retainedOriginal('reuse',reusePacket)
   reuseOwnership=ownership()[-1]
   check('reuseOriginalPhysicalRetirementBeforeTerminalACK',reuseOwnership['job']==reusePacket['job'] and reuseOwnership['charge']=='0' and reuseOwnership['mappedFDClosed'] and reuseOwnership['exportReleased'] and reuseOwnership['producerRetired'] and 'native-client-ack:' in fullLog() and fullLog().index('native-client-reader-released:')<fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:'),status=reuseOwnership)
   check('reuseNoOriginalIncarnationEnrollmentAsReplacement',len([event for event in events() if event['kind']=='source-seed'])==1 and not any('native-client-resume:' in line for line in fullLog().splitlines()))
   r['addressReuseEvidence']={'scenarioId':'ELM-REN-004 ren-004','oldAddress':reuseOldAddress,'replacementAddress':replacement['window']['address'],'oldSubject':reuseSubject,'replacementSubject':replacement['subject'],'originalFrame':reusePacket,'readerReady':readerReady,'beforePolicyProbe':probe,'probeNativeScope':probeScope['scope'],'actualElmReplacementDOM':replacementDOM,'webkitPixels':reusePixels,'terminalStatus':reuseOwnership,'actualAddressReuse':True,'heldAndFreshDeniedBeforePolicyEffects':True,'hardwarePresentation':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
   web.terminate();web.wait(timeout=5);check('reuseFullGUINormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   writeControl(reuseControl,'1 quit');reuseSource.wait(timeout=5);check('reuseReplacementNativeSourceNormalExit',reuseSource.returncode==0)
   wait(lambda:not any(w['pid']==reuseSource.pid for w in s.data('clients')))
   sourceBefore=request('scene-facts-request',minimumWatermark='0');oldIDs={w['incarnation'] for w in sourceBefore['facts']['windows']}
   witnessSource=s.host.launch('gone-witness-source',[pre['fixtureClient']],env=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(private/'gone-source-control')))
   wait(lambda:len(s.data('clients'))==4)
   sourceAfter=request('scene-facts-request',minimumWatermark='0');newSubjects=[w['incarnation'] for w in sourceAfter['facts']['windows'] if w['incarnation'] not in oldIDs and w['application']=='warlock-child-probe'];check('goneWitnessSeparateRealSource',len(newSubjects)==1)
   witnessSamples,witnessReady=beginWitness('gone',newSubjects[0])
   writeControl(private/'gone-source-control','1 quit');witnessSource.wait(timeout=5);check('goneWitnessSourceActuallyExited',witnessSource.returncode==0)
   writeControl(witnessControl,'deny');independent=wait(lambda:next((row for row in witnessSamples() if row['stage']=='native-uri-denied-before-policy'),None))
   check('goneIndependentNativeHeldAndNewURIDenial',independent['status']['job']==witnessReady['status']['job'] and int(independent['status']['charge'])>0)
   goneCleanup=wait(lambda:next((row for row in witnessSamples() if row['stage']=='cleanup'),None))['status']
   check('goneWitnessActualPhysicalRetirement',goneCleanup['job']==witnessReady['status']['job'] and goneCleanup['charge']=='0' and goneCleanup['mappedFDClosed'] and goneCleanup['exportReleased'] and goneCleanup['producerRetired'] and goneCleanup['records']==1)
   writeControl(witnessControl,'finish');witness.wait(timeout=5);check('goneWitnessExactACKAndNormalExit',witness.returncode==0 and witnessSamples()[-1]['status']['records']==0)
   gonePacket=openQualification('gone')
   command('quit');fixture.wait(timeout=5);check('sourceLossFixtureActuallyExited',fixture.returncode==0)
   denial=wait(lambda:next((event['event'] for event in events() if event['kind']=='event' and event['event']['kind']=='source-denied'),None))
   check('goneFullHostExactTypedScopeDenial',denial=={'kind':'source-denied','job':gonePacket['job'],'reason':'source-unavailable'})
   wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog());retainedOriginal('gone',gonePacket)
   check('goneActualElmReleaseAndExactACK','native-client-ack:' in fullLog() and fullLog().index('native-client-command: {"kind":"release"')<fullLog().index('native-client-ack:')<fullLog().index('native-client-complete:'))
   web.terminate();web.wait(timeout=5);check('goneFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog())
   temp=private/'companion-control.tmp';temp.write_text('1 quit\n');temp.chmod(0o600);temp.replace(private/'companion-control');companion.wait(timeout=5);check('sameAppCompanionNormalExit',companion.returncode==0)
   if fixture.poll() is None:command('quit')
   fixture.wait(timeout=5);check('childNormalExit',fixture.returncode==0);peerQuit();peer.wait(timeout=5);check('peerNormalExit',peer.returncode==0);wait(lambda:not s.data('clients'));r['passed']=True
  finally:
   if reuseReaderControl and web and web.poll() is None and fullLogName=='full-client-reuse':
    writeControl(reuseReaderControl,'release');wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   if reuseSource and reuseSource.poll() is None:
    writeControl(reuseControl,'1 quit');reuseSource.wait(timeout=5);check('reuseSourceFailureCleanupNormalExit',reuseSource.returncode==0)
   if locker and locker.poll() is None:
    writeControl(lockControl,'unlock');locker.wait(timeout=5);check('sessionLockCleanupNormalExit',locker.returncode==0)
   if witnessSource and witnessSource.poll() is None:
    writeControl(private/'gone-source-control','1 quit');witnessSource.wait(timeout=5);check('goneWitnessSourceCleanupNormalExit',witnessSource.returncode==0)
   if importWitness and importWitness.poll() is None:
    importWitness.terminate();importWitness.wait(timeout=5);r['importWitnessFailureCleanupExit']=importWitness.returncode
   if witness and witness.poll() is None:
    witness.terminate();witness.wait(timeout=5);r['witnessFailureCleanupExit']=witness.returncode
   if web and web.poll() is None:
    if fullLogName=='full-client-locked' and 'native-client-command: {"kind":"release"' in fullLog():wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
    if fullLogName in ['full-generated-backdrop-provider','full-generated-backdrop-source-loss'] and 'native-client-start:' in fullLog():wait(lambda:'native-client-complete: physical=0 journal=0 previewEligible=0' in fullLog())
    if fullLogName=='full-imported-historical' and 'native-imported-start:' in fullLog():wait(lambda:'native-imported-complete: physical=0 journal=0 previewEligible=0' in fullLog())
    web.terminate();web.wait(timeout=5);check('fullHostCleanupNormalExit',web.returncode==0)
   if companion and companion.poll() is None:
    temp=private/'companion-control.tmp';temp.write_text('1 quit\n');temp.chmod(0o600);temp.replace(private/'companion-control');companion.wait(timeout=5);check('sameAppCompanionCleanupNormalExit',companion.returncode==0)
   if fixture and fixture.poll() is None:command('quit');fixture.wait(timeout=5);check('childCleanupNormalExit',fixture.returncode==0)
   if peer and peer.poll() is None:peerQuit();peer.wait(timeout=5);check('peerCleanupNormalExit',peer.returncode==0)
   if loaded:wait(lambda:not s.data('clients'));check('clientsEmptyBeforePluginUnload',not s.data('clients'));check('pluginUnloadsAfterConsumers',s.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
 r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes];check('allOwnedProcessesNormalExit',all(row['exitCode']==0 for row in r['ownedExitCodes']),exits=r['ownedExitCodes'])
 baseline=json.loads(pathlib.Path(pre['retainedNativeReport']).read_text());names=[row['name'] for row in baseline['checks']];check('allOriginal828OrderedAssertionsRetained',len(names)==828 and [row['name'] for row in r['checks'] if row['name'] in set(names)]==names)
 freshBaseline=json.loads(pathlib.Path(pre['retainedFreshDemandReport']).read_text());freshNames=[row['name'] for row in freshBaseline['checks']];check('allOriginal857OrderedAssertionsRetained',len(freshNames)==857 and [row['name'] for row in r['checks'] if row['name'] in set(freshNames)]==freshNames)
 historicalBaseline=json.loads(pathlib.Path(pre['retainedHistoricalReport']).read_text());historicalNames=[row['name'] for row in historicalBaseline['checks']];check('allOriginal883OrderedAssertionsRetained',len(historicalNames)==883 and [row['name'] for row in r['checks'] if row['name'] in set(historicalNames)]==historicalNames)
 importedBaseline=json.loads(pathlib.Path(pre['retainedImportedReport']).read_text());importedNames=[row['name'] for row in importedBaseline['checks']];check('allOriginal904OrderedAssertionsRetained',len(importedNames)==904 and [row['name'] for row in r['checks'] if row['name'] in set(importedNames)]==importedNames)
 guiBaseline=json.loads(pathlib.Path(pre['retainedCBridgeReport']).read_text());guiNames=[row['name'] for row in guiBaseline['checks']];check('allOriginal905OrderedAssertionsRetained',len(guiNames)==905 and [row['name'] for row in r['checks'] if row['name'] in set(guiNames)]==guiNames)
 fullGUIBaseline=json.loads(pathlib.Path(pre['retainedFullGUIReport']).read_text());fullGUINames=[row['name'] for row in fullGUIBaseline['checks']];check('allOriginal918OrderedAssertionsRetained',len(fullGUINames)==918 and [row['name'] for row in r['checks'] if row['name'] in set(fullGUINames)]==fullGUINames)
 resumedBaseline=json.loads(pathlib.Path(pre['retainedResumeReport']).read_text());resumedNames=[row['name'] for row in resumedBaseline['checks']];check('allOriginal933OrderedAssertionsRetained',len(resumedNames)==933 and [row['name'] for row in r['checks'] if row['name'] in set(resumedNames)]==resumedNames)
 asymmetricBaseline=json.loads(pathlib.Path(pre['retainedAsymmetricReport']).read_text());asymmetricNames=[row['name'] for row in asymmetricBaseline['checks']];check('allOriginal951OrderedAssertionsRetained',len(asymmetricNames)==951 and [row['name'] for row in r['checks'] if row['name'] in set(asymmetricNames)]==asymmetricNames)
 historicalBaseline=json.loads(pathlib.Path(pre['retainedSharedHistoricalReport']).read_text());historicalNames=[row['name'] for row in historicalBaseline['checks']];check('allOriginal973OrderedAssertionsRetained',len(historicalNames)==973 and [row['name'] for row in r['checks'] if row['name'] in set(historicalNames)]==historicalNames)
 popupBaseline=json.loads(pathlib.Path(pre['retainedPopupLifecycleReport']).read_text());popupNames=[row['name'] for row in popupBaseline['checks']];check('allOriginal990OrderedAssertionsRetained',len(popupNames)==990 and [row['name'] for row in r['checks'] if row['name'] in set(popupNames)]==popupNames)
 popupSnapshotBaseline=json.loads(pathlib.Path(pre['retainedPopupSnapshotReport']).read_text());popupSnapshotNames=[row['name'] for row in popupSnapshotBaseline['checks']];check('allOriginal1011OrderedAssertionsRetained',len(popupSnapshotNames)==1011 and [row['name'] for row in r['checks'] if row['name'] in set(popupSnapshotNames)]==popupSnapshotNames)
 popupObserverBaseline=json.loads(pathlib.Path(pre['retainedPopupObserverReport']).read_text());popupObserverNames=[row['name'] for row in popupObserverBaseline['checks']];check('allOriginal1079OrderedAssertionsRetained',len(popupObserverNames)==1079 and [row['name'] for row in r['checks'] if row['name'] in set(popupObserverNames)]==popupObserverNames)
 popupCaptureBaseline=json.loads(pathlib.Path(pre['retainedPopupCaptureReport']).read_text());popupCaptureNames=[row['name'] for row in popupCaptureBaseline['checks']];check('allOriginal1160OrderedAssertionsRetained',len(popupCaptureNames)==1160 and [row['name'] for row in r['checks'] if row['name'] in set(popupCaptureNames)]==popupCaptureNames)
 modalFixtureBaseline=json.loads(pathlib.Path(pre['retainedModalFixtureReport']).read_text());modalFixtureNames=[row['name'] for row in modalFixtureBaseline['checks']];check('allOriginal1214OrderedAssertionsRetained',len(modalFixtureNames)==1214 and [row['name'] for row in r['checks'] if row['name'] in set(modalFixtureNames)]==modalFixtureNames)
 familyObserverBaseline=json.loads(pathlib.Path(pre['retainedFamilyObserverReport']).read_text());familyObserverNames=[row['name'] for row in familyObserverBaseline['checks']];check('allOriginal1351OrderedAssertionsRetained',len(familyObserverNames)==1351 and [row['name'] for row in r['checks'] if row['name'] in set(familyObserverNames)]==familyObserverNames)
 combinedBaseline=json.loads(pathlib.Path(pre['retainedCombinedFamilyReport']).read_text());combinedNames=[row['name'] for row in combinedBaseline['checks']];check('allOriginal1524OrderedAssertionsRetained',len(combinedNames)==1524 and [row['name'] for row in r['checks'] if row['name'] in set(combinedNames)]==combinedNames)
 cropBaseline=json.loads(pathlib.Path(pre['retainedNativeCropReport']).read_text());cropNames=[row['name'] for row in cropBaseline['checks']];check('allOriginal1612OrderedAssertionsRetained',len(cropNames)==1612 and [row['name'] for row in r['checks'] if row['name'] in set(cropNames)]==cropNames)
 resumedStyleBaseline=json.loads(pathlib.Path(pre['retainedNativeStyleReport']).read_text());styleNames=[row['name'] for row in resumedStyleBaseline['checks']];check('allOriginal1636OrderedAssertionsRetained',len(styleNames)==1636 and [row['name'] for row in r['checks'] if row['name'] in set(styleNames)]==styleNames)
 styleCropBaseline=json.loads(pathlib.Path(pre['retainedNativeStyleCropReport']).read_text());styleCropNames=[row['name'] for row in styleCropBaseline['checks']];check('allOriginal1739OrderedAssertionsRetained',len(styleCropNames)==1739 and [row['name'] for row in r['checks'] if row['name'] in set(styleCropNames)]==styleCropNames)
 familyWebBaseline=json.loads(pathlib.Path(pre['retainedNativeFamilyWebReport']).read_text());familyWebNames=[row['name'] for row in familyWebBaseline['checks']];check('allOriginal1756OrderedAssertionsRetained',len(familyWebNames)==1756 and [row['name'] for row in r['checks'] if row['name'] in set(familyWebNames)]==familyWebNames)
 historicalBaseline=json.loads(pathlib.Path(pre['retainedNativeHistoricalFamilyReport']).read_text());historicalNames=[row['name'] for row in historicalBaseline['checks']];check('allOriginal1783OrderedAssertionsRetained',len(historicalNames)==1783 and [row['name'] for row in r['checks'] if row['name'] in set(historicalNames)]==historicalNames)
 configProof=r['renderConfigurationEvidence'];before=configProof['nativeScopeBefore'];after=configProof['nativeScopeAfter']
 check('configStyleNativeConfigurationOnlyChange',configProof['rootCommitsUnchanged'] and before['members']==after['members'] and before['styles']==after['styles'] and before['crop']==after['crop'] and {k:v for k,v in before['scope']['context'].items() if k!='content'}=={k:v for k,v in after['scope']['context'].items() if k!='content'},evidence=configProof)
 check('configStyleNativePixelsActuallyChanged',configProof['bytesChanged'],evidence=configProof)
 check('configStyleChangedNativePixelsRequireNewStyleEpoch',not configProof['bytesChanged'] or configProof['styleEpochChanged'],evidence=configProof)
 opacityProof=r['opacityConfigurationEvidence'];check('opacityChangedNativePixelsRequireNewStyleEpoch',not opacityProof['bytesChanged'] or opacityProof['styleEpochChanged'],evidence=opacityProof)
 backgroundProof=r['backgroundEffectEvidence'];check('backgroundCreationBeforeCommitRequiresNewEpoch',backgroundProof['creationEpochAdvanced'],evidence=backgroundProof)
 check('shaderActualNativeTintRequiresMatchingFamilyPixels',len(r['shaderPixelSamples'])==2 and all(row['equalRoot'] for row in r['shaderPixelSamples']),evidence=r['shaderPixelSamples'])
 check('shaderActualWholeRootMatchesIndependentNativeOutput',r['shaderWholeRootPixels']['passed'],evidence=r['shaderWholeRootPixels'])
 check('shaderActualGlobalCoordinatesMatchIndependentNativeOutput',r['shaderCoordinatePixels']['equalRoot'],evidence=r['shaderCoordinatePixels'])
 check('shaderActualWholeRootCoordinatesMatchIndependentNativeOutput',r['shaderWholeCoordinatePixels']['passed'],evidence=r['shaderWholeCoordinatePixels'])
 check('shaderActualWholeCropCompositesMatchControlledNativeOutput',len(r['shaderCompositedCropPixels'])==2 and all(sample['pixels']['passed'] for sample in r['shaderCompositedCropPixels']),evidence=r['shaderCompositedCropPixels'])
 check('shaderHalfBodyMatchesDeclaredAlphaAndIndependentNativeOutput',r['shaderHalfBodyComparison']['passed'],evidence=r['shaderHalfBodyComparison'])
 r['nativeShaderHalfBodyOverBlackNoBlurQualified']=True
 check('blurBodyActualNativeBrightnessDeltasRequireMatchingFamilyPixels',r['blurBodyEvidence']['pixels']['passed'],evidence=r['blurBodyEvidence']['pixels'])
 check('blurBodyEveryGeneratedCapturePixelMatchesIndependentNativeOutput',all(row['pixels']['passed'] for row in r['blurBodyExactPixels']),evidence=r['blurBodyExactPixels'])
 check('backdropWebActualOwnedBlurPixelsMatchIndependentNativeColor',r['backdropWebKitEvidence']['pixels']['passed'],evidence=r['backdropWebKitEvidence']['pixels'])
 check('backdropLossActualTypedUnavailableRetiresExactOriginalFrame',r['backdropSourceLossEvidence']['rootCommitsUnchanged'] and len(r['backdropSourceLossEvidence']['events'])==1,evidence=r['backdropSourceLossEvidence'])
 # Prior88 includes runtime pointer suffixes and optional read-only polls.
 # Retain every raw assertion and compare the stable ordered identities instead.
 prior88=json.loads(pathlib.Path(pre['retainedNative88Report']).read_text())
 readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
 def stableNames(rows):
  return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$', 'opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
 prior88Stable=stableNames(prior88['checks']);currentStable=stableNames(r['checks']);priorNames=set(prior88Stable)
 check('allPriorNative88StableOrderedAssertionsRetained',len(prior88['checks'])==2341 and [name for name in currentStable if name in priorNames]==prior88Stable,stableControls=len(prior88Stable),priorRawControls=2341)
 r['priorNative88Retention']={'stableOrderedControls':len(prior88Stable),'originalRawControls':2341,'actualRawRetainedControls':len([row for row in r['checks'] if row['name'] in {x['name'] for x in prior88['checks']}]),'readonlyPollingNames':sorted(readonly),'nativeAddressSuffixNormalizedOnlyForComparison':True,'allActualChecksPassed':all(row['passed'] for row in r['checks'])}
 prior92=json.loads(pathlib.Path(pre['retainedNative92Report']).read_text());prior92Stable=stableNames(prior92['checks']);prior92Names=set(prior92Stable)
 check('allPriorNative92StableOrderedAssertionsRetained',len(prior92['checks'])==2363 and [name for name in stableNames(r['checks']) if name in prior92Names]==prior92Stable)
 prior93=json.loads(pathlib.Path(pre['retainedNative93Report']).read_text());prior93Stable=stableNames(prior93['checks']);prior93Names=set(prior93Stable)
 check('allPriorNative93StableOrderedAssertionsRetained',len(prior93['checks'])==2372 and [name for name in stableNames(r['checks']) if name in prior93Names]==prior93Stable)
 prior97=json.loads(pathlib.Path(pre['retainedNative97Report']).read_text());prior97Stable=stableNames(prior97['checks']);prior97Names=set(prior97Stable)
 check('allPriorNative97StableOrderedAssertionsRetained',len(prior97['checks'])==2386 and [name for name in stableNames(r['checks']) if name in prior97Names]==prior97Stable,stableControls=len(prior97Stable),priorRawControls=2386)
 r['ordinaryNativeCatalogBoundedQualified']=True
 r['nativeIconLockBoundedQualified']=True
 r['nativeTitleIconFallbackBoundedQualified']=True
 r['nativeAddressReuseFullGUIQualified']=True
 r['nativeSharedGeneratedBackdropSourceLossQualified']=True
 r['nativeSharedGeneratedBackdropGUIQualified']=True
 r['nativeBlurBodyBrightnessQualified']=True
 r['nativeShaderWholeCropOverBlackQualified']=True
 r['nativeShaderOpaqueRootCoordinatesQualified']=True
 r['nativeShaderGlobalCoordinateSampleQualified']=True
 r['nativeShaderOpaqueRootPixelsQualified']=True
 r['nativeShaderRootPixelSamplesQualified']=True;r['completeShaderFidelityQualified']=False;r['backgroundPixelFidelityQualified']=False
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
 if s:
  r['privateHost']=s.host.evidence;r['cleanupPassed']=bool(s.host.evidence.get('runtimeGone') and not s.host.evidence.get('remainingDescendants') and not s.host.evidence.get('unexpectedInnerDescendants') and not s.host.evidence.get('cleanupErrors'));r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes]
 if private.exists():shutil.copytree(private,OUT/'private-evidence',symlinks=True)
 r['passed']=r['passed'] and r.get('cleanupPassed',False);r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not r['passed'])
