"""ELM-UI-007 restore feedback on the real private Wayland/Elm/native path.

Reuse immutable ABI/runtime by reference; no preview, supervisor or new source
lineage. Native/AT acceptance remain separate, with AT explicitly outstanding.
"""
import hashlib,importlib.util,json,os,pathlib,signal,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143';RUNTIME=REPO/'implementation/warlock-client-provider-native-v204'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('feedback_private_host',RUNTIME/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope();sys.path.insert(0,str(RUNTIME/'qa'))
from session_bus import isolate_session_host
from system_isolation import supply,validate
from inspection import Collector
isolate_session_host(host)
sys.path.insert(0,str(ROOT/'adapter'));from effect_endpoint import Endpoint;from endpoint import start_time
pre=json.loads((RUNTIME/'qa/preflight.json').read_text());pair=pre['pair'];build_path=pathlib.Path(pre['controlledHostBuild']);build=json.loads(build_path.read_text());assert build['passed'];binary=build_path.parent/'elm-host';assert sha(binary)==build['binarySHA256']
ancestry=json.loads((ROOT/'ANCESTRY.json').read_text());assert all(sha(ROOT/p)==h for p,h in ancestry['parentSources'].items() if p.startswith('native/'))
for row in pair.values():assert sha(row['path'])==row['sha256']
assets=ROOT/'assets';assert all(sha(assets/n)==h for n,h in json.loads((ROOT/'qa/current-feedback-build.json').read_text())['compiledAssets'].items())
subprocess.run(['node','--check',str(assets/'bar-adapter.js')],check=True)
OUT=ROOT/'qa/runs'/('native-feedback-'+str(time.time_ns()));OUT.mkdir(parents=True)
OUTPUT=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-window-feedback-'+str(time.time_ns()))
POINTER=pathlib.Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer');FIXTURE=RUNTIME/'fixture.py'
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual pointer/Elm/native effect feedback and private compositor pixels; no AT/IME/full release acceptance','nativeFeedbackObserved':False,'nativeAcceptance':False,'assistiveTechnologyAccepted':False,'fullReleaseAccepted':False,'mainDesktopActions':False,'passed':False,'checks':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','adapter','assets'] for p in (ROOT/folder).iterdir() if p.is_file()},'pair':pair,'nativeHost':{'path':str(binary),'sha256':sha(binary),'heldBuild':str(build_path),'heldBuildSHA256':sha(build_path)},'runtimeByReference':{'root':str(RUNTIME),'hostSHA256':sha(RUNTIME/'candidate_host.py')},'helpers':[],'nativeFixtures':[]};s=None;loaded=False;apps=[];broker=None;paused=False;sequence=0
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,condition,**data):
 report['checks'].append({'name':name,'passed':bool(condition),**data});assert condition,name
def wait(fn,seconds=6):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  s.guard();value=fn()
  if value:return value
  time.sleep(.025)
 raise RuntimeError('Original observation deadline '+getattr(fn,'__name__',''))
def helper(command,input_text=None,timeout=5):
 global sequence
 sequence+=1;name='feedback-helper-'+str(sequence)
 if input_text is not None:
  p=OUTPUT/(name+'.input');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:f.write(input_text)
  command=['/usr/bin/python3','-B',str(RUNTIME/'qa/input_helper.py'),str(p),*command]
 proc=s.host.launch(name,command,env=s.env)
 try:proc.wait(timeout=timeout)
 except BaseException:
  owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5);raise
 row={'name':name,'pid':proc.pid,'exitCode':proc.returncode,'command':command};report['helpers'].append(row);check(name+'NormalExit',proc.returncode==0)
 return (OUTPUT/(name+'.log')).read_text(errors='replace')
def pause(value):
 global paused
 assert start_time(broker['pid'])==broker['start'] and pathlib.Path('/proc/'+str(broker['pid'])+'/exe').resolve()==pathlib.Path('/usr/bin/python3').resolve()
 os.kill(broker['pid'],signal.SIGSTOP if value else signal.SIGCONT);paused=value
 report.setdefault('brokerStops',[]).append({'stopped':value,'pid':broker['pid'],'start':broker['start'],'clock':time.monotonic()})
def fixture_control(op):
 temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':op}));temp.replace(control)
try:
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   plugin=pair['plugin']['path'];check('OwningPluginLoads',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':int(start_time(native['pid'])),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello();env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
   control=OUTPUT/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')));wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')));fixture_control('hide-peer');wait(lambda:len(s.data('clients'))==1)
   w=s.data('clients')[0];selector='address:'+w['address']
   if not w['floating']:check('FixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+selector+"'})").strip()=='ok')
   check('FixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+selector+"'})").strip()=='ok')
   check('FixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=40,y=100,window='"+selector+"'})").strip()=='ok')
   check('FixtureFocus',s.ctl('dispatch',"hl.dsp.focus({window='"+selector+"'})").strip()=='ok')
   web=s.host.launch('warlock',['%s'%binary,'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock.log';collector=Collector()
   def text():return log.read_text(errors='replace')
   def projection():return collector.read(text())
   def group(operation):
    p=projection();return next((g for g in p['groups'] if g['title']=='ELM-AUTHORITY-FIXTURE' and g['label'].startswith(operation+' ') and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='window-effect']
   def feedback(state):
    p=projection()
    if not p or p['transaction']!=state:return None
    rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
    return next((r for r in reversed(rows) if r['publication']==p['publication']),None)
   def click(item):
    check('PointerTargetWithinActualViewport',item['visible'],item=item);x,y=map(round,item['point']);helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   def facts():return client.scene_facts('441')
   initial=wait(lambda:group('Minimize'));target=next(w['incarnation'] for w in facts()['facts']['windows'] if w['application']=='GTK Application')
   initial_workspace=next(w['workspace'] for w in facts()['facts']['windows'] if w['incarnation']==target)
   def current_window():return next(w for w in facts()['facts']['windows'] if w['incarnation']==target)
   def transaction_state():return (projection() or {}).get('transaction')
   def private_effect(operation):
    before=facts();n=str(9000+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':target,'operation':operation,'context':client.context(before)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('ControlledNativeFixture'+operation,result['status']=='Committed',result=result)
   def screenshot(state):
    body=wait(lambda:feedback(state));o=body['feedback'];check(state+'VisibleCorrelatedMessage',o and o['width']>=180 and o['height']==48 and o['clip']=='none' and o['display']!='none' and o['accessibleName']==o['text'] and o['atomic']=='true' and o['live']=='polite',feedback=o)
    image=OUTPUT/(state+'.png');helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();left,top=int(o['x'])+5,int(o['y'])+3;right,bottom=min(800,int(o['x']+o['width'])-3),min(48,int(o['y']+o['height'])-3)
    bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(data[y*stride+x*channels+i]>170 for i in range(3)))
    check(state+'NativeTaskbarHasTextPixels',pix.get_width()==800 and pix.get_height()==600 and bright>30,image=str(image),sha256=sha(image),brightPixels=bright,region=[left,top,right,bottom]);report.setdefault('feedback',{})[state]=body
   # Current real taskbar primary action, before adding any fault.
   click(initial);wait(lambda:transaction_state()=='Committed' and current_window()['minimized']);check('TaskbarMinimizeActuallyCommits',journal()[-1]['intent']['operation']=='minimize')
   def find_broker():
    rows=[]
    for row in s.host.descendants():
     try:args=pathlib.Path('/proc/'+str(row['pid'])+'/cmdline').read_bytes().split(b'\0')
     except FileNotFoundError:continue
     if str(ROOT/'adapter/daemon.py').encode() in args and int(pathlib.Path('/proc/'+str(row['pid'])+'/stat').read_text().rsplit(')',1)[1].split()[1])==web.pid:rows.append({'pid':row['pid'],'start':start_time(row['pid'])})
    return rows[0] if len(rows)==1 else None
   broker=wait(find_broker);report['broker']=broker;restore=wait(lambda:group('Restore'));pause(True);before=len(journal());click(restore);screenshot('Pending');check('PendingDoesNotCommitOrDuplicate',current_window()['minimized'] and len(journal())==before+1)
   # Change native truth independently while its original UI intent is held.
   private_effect('restore');pause(False);wait(lambda:transaction_state()=='Refused');screenshot('Refused');check('RefusalProducesOneRestoreRequest',len(journal())==before+1 and journal()[-1]['intent']['operation']=='restore')
   private_effect('minimize');restore=wait(lambda:group('Restore'));pause(True);before=len(journal());click(restore);wait(lambda:transaction_state()=='Pending')
   # Genuine transport loss makes the issued request Unknown; no invented timer.
   os.kill(broker['pid'],signal.SIGTERM);pause(False);wait(lambda:transaction_state()=='Unknown');screenshot('Unknown');check('UnknownIsPersistentAndNeverAutoRetried',len(journal())==before+1 and current_window()['minimized'])
   body=feedback('Unknown');check('DisconnectedFeedbackNamesReachableRecovery','Reconnect' in body['feedback']['text'] and any(b['accessibleName'].startswith('Reconnect') and not b['disabled'] for b in body['buttons']))
   reconnect=next(b for b in body['buttons'] if b['accessibleName'].startswith('Reconnect') and not b['disabled']);x,y=map(round,(reconnect['x']+reconnect['width']/2,reconnect['y']+reconnect['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');wait(lambda:(projection() or {}).get('phase')=='Coherent');check('ReconnectReadsWithoutReplayingRestore',len(journal())==before+1 and current_window()['minimized'])
   body=feedback('Unknown');refresh=next(b for b in body['buttons'] if b['accessibleName'].startswith('Refresh window status') and not b['disabled']);x,y=map(round,(refresh['x']+refresh['width']/2,refresh['y']+refresh['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');check('RefreshQueuesNoSecondWindowEffect',len(journal())==before+1)
   wait(lambda:(projection() or {}).get('phase')=='Coherent');check('ReadOnlyRecoveryPreservesUnknownAndNoReplay',transaction_state()=='Unknown' and len(journal())==before+1 and current_window()['minimized'])
   check('NoScratchpadOrWorkspaceTransfer',current_window()['workspace']==initial_workspace,nativeWorkspace=current_window()['workspace'],originalWorkspace=initial_workspace)
   report['nativeFeedbackObserved']=True;check('EveryRegisteredHelperExitedNormally',all(r['exitCode']==0 for r in report['helpers']));report['passed']=True
  finally:
   if paused:pause(False)
   for proc in reversed(apps):
    if proc.poll() is None:
     if proc is fixture:fixture_control('quit');proc.wait(timeout=5)
     else:owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5)
    check('OwnedClientNormalExit',proc.returncode==0,pid=proc.pid,exitCode=proc.returncode)
   if loaded:s.guard();check('OwningPluginUnloads',s.ctl('plugin','unload',pair['plugin']['path']).strip()=='ok');loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for row in reversed([r for r in s.host.descendants() if r['pid'] not in registered]):s.host.stop(row)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
report['runtimeEvidenceDirectory']=str(OUTPUT);report['runnerSHA256']=sha(__file__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
