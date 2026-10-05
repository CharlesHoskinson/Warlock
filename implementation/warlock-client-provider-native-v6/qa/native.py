"""Real native child-only commits and independent pixels on the exact owning tuple."""
import array,fcntl,hashlib,importlib.util,json,mmap,os,pathlib,resource,shutil,socket,struct,subprocess,sys,time,traceback,zlib
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
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'pair':pre['pair'],'scope':'Desynchronized child-only pixels/context; synchronized queued-versus-applied state; nested geometry/stack/membership/retirement. No eligible production/family/minimized/output/WebKit or full release acceptance.','checks':[],'samples':[]}
s=None;fixture=None;peer=None;web=None;companion=None;loaded=False;commandSequence=0;requestId=1
r['cacheTraceReplay']=[]
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
 lua=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
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
   def exchange(op,capture,transfer=0):
    query=[magic,1,op,lifetime,session,frontend,2000+op,int(capture),int(subject),int(transfer)]
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child);assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(25*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==25*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC);words=struct.unpack('!25Q',data);assert words[:3]==(magic,1,0) and words[3:6]==(lifetime,session,frontend) and words[6]==2000+op and words[7]==int(capture) and words[8]==int(subject);assert len(rights)==(1 if op==1 else 0);return words,rights
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
   def fullLog():return (private/(fullLogName+'.log')).read_text()
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
   temp=private/'companion-control.tmp';temp.write_text('1 quit\n');temp.chmod(0o600);temp.replace(private/'companion-control');companion.wait(timeout=5);check('sameAppCompanionNormalExit',companion.returncode==0)
   command('quit');fixture.wait(timeout=5);check('childNormalExit',fixture.returncode==0);peerQuit();peer.wait(timeout=5);check('peerNormalExit',peer.returncode==0);wait(lambda:not s.data('clients'));r['passed']=True
  finally:
   if web and web.poll() is None:web.terminate();web.wait(timeout=5);check('fullHostCleanupNormalExit',web.returncode==0)
   if companion and companion.poll() is None:
    temp=private/'companion-control.tmp';temp.write_text('1 quit\n');temp.chmod(0o600);temp.replace(private/'companion-control');companion.wait(timeout=5);check('sameAppCompanionCleanupNormalExit',companion.returncode==0)
   if fixture and fixture.poll() is None:command('quit');fixture.wait(timeout=5);check('childCleanupNormalExit',fixture.returncode==0)
   if peer and peer.poll() is None:peerQuit();peer.wait(timeout=5);check('peerCleanupNormalExit',peer.returncode==0)
   if loaded:wait(lambda:not s.data('clients'));check('clientsEmptyBeforePluginUnload',not s.data('clients'));check('pluginUnloadsAfterConsumers',s.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
 r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes];check('allOwnedProcessesNormalExit',all(row['exitCode']==0 for row in r['ownedExitCodes']),exits=r['ownedExitCodes'])
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
 if s:
  r['privateHost']=s.host.evidence;r['cleanupPassed']=bool(s.host.evidence.get('runtimeGone') and not s.host.evidence.get('remainingDescendants') and not s.host.evidence.get('unexpectedInnerDescendants') and not s.host.evidence.get('cleanupErrors'));r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes]
 if private.exists():shutil.copytree(private,OUT/'private-evidence',symlinks=True)
 r['passed']=r['passed'] and r.get('cleanupPassed',False);r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not r['passed'])
