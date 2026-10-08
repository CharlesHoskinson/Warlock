"""ELM-UI-007 restore feedback on the real private Wayland/Elm/native path.

Reuse immutable ABI/runtime by reference; no preview, supervisor or new source
lineage. Native/AT acceptance remain separate, with AT explicitly outstanding.
"""
import hashlib,importlib.util,json,os,pathlib,signal,subprocess,sys,time,traceback
FOCUS=sys.argv[1:]==['--taskbar-focus'];PRESENTATION=sys.argv[1:]==['--launcher-presentation'];SEARCH=sys.argv[1:]==['--launcher-search'] or PRESENTATION;PINS=sys.argv[1:]==['--taskbar-pins'];CATALOG=SEARCH or PINS;TASKVIEW=sys.argv[1:]==['--task-view'];assert not sys.argv[1:] or FOCUS or CATALOG or TASKVIEW
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
CURRENT=(ROOT/'qa/current-search-build.json').exists()
assert not (CATALOG or TASKVIEW) or CURRENT
if CURRENT:
 current=json.loads((ROOT/'qa/current-search-build.json').read_text());build_path=REPO/current['report'];assert sha(build_path)==current['reportSHA256'];build=json.loads(build_path.read_text());assert build['passed'];binary=build_path.parent/'elm-host';assert sha(binary)==build['binarySHA256'];assert all(sha(ROOT/p)==h for p,h in build['inputs'].items() if p.startswith(('src/','native/','adapter/')))
else:
 ancestry=json.loads((ROOT/'ANCESTRY.json').read_text());assert all(sha(ROOT/p)==h for p,h in ancestry['parentSources'].items() if p.startswith('native/'))
for row in pair.values():assert sha(row['path'])==row['sha256']
assets=ROOT/'assets';assert all(sha(assets/n)==h for n,h in json.loads((ROOT/'qa'/('current-search-build.json' if CURRENT else 'current-feedback-build.json')).read_text())['compiledAssets'].items())
subprocess.run(['node','--check',str(assets/'bar-adapter.js')],check=True)
OUT=ROOT/'qa/runs'/(('native-task-view-' if TASKVIEW else 'native-pins-' if PINS else 'native-search-' if SEARCH else 'native-taskbar-focus-' if FOCUS else 'native-feedback-')+str(time.time_ns()));OUT.mkdir(parents=True)
OUTPUT=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-window-feedback-'+str(time.time_ns()))
POINTER=pathlib.Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer');FIXTURE=RUNTIME/'fixture.py'
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual pointer/Elm/native effect feedback and private compositor pixels; no AT/IME/full release acceptance','nativeFeedbackObserved':False,'nativeAcceptance':False,'assistiveTechnologyAccepted':False,'fullReleaseAccepted':False,'mainDesktopActions':False,'passed':False,'checks':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','adapter','assets'] for p in (ROOT/folder).iterdir() if p.is_file()},'pair':pair,'nativeHost':{'path':str(binary),'sha256':sha(binary),'heldBuild':str(build_path),'heldBuildSHA256':sha(build_path)},'runtimeByReference':{'root':str(RUNTIME),'hostSHA256':sha(RUNTIME/'candidate_host.py')},'helpers':[],'nativeFixtures':[]};s=None;loaded=False;apps=[];broker=None;paused=False;sequence=0
if SEARCH:report.update(requirements=['ELM-UI-005','ELM-UX-029'],scenarios=['search-no-match','search-race','search-refused','launcher-refused'],scope='Actual current query and private catalog, native typing/Enter refusal and no duplicate launch; AT/IME and popup physical presentation acceptance remain pending',popupPresentationAccepted=False)
if PINS:report.update(requirements=['ELM-UI-004','ELM-UX-004'],scenarios=['taskbar-zero','ux-004'],scope='Actual native keyboard pin/reorder, shell restart, identity order and one current zero-window launch; popup physical presentation and AT acceptance remain separate',popupPresentationAccepted=False,nativePinJourneyObserved=False)
if TASKVIEW:report.update(requirements=['ELM-UX-017','ELM-UI-006'],scenarios=['ux-017','overview-cancel'],scope='Actual two populated native workspaces, exact window membership and active marker, keyboard/pointer local browsing and Escape recipient; independent and applicable AT acceptance remain pending',nativeTaskViewJourneyObserved=False)
if FOCUS:report.update(requirements=['ELM-UI-004','ELM-UX-024'],scenarios=['taskbar-group','ux-024'],scope='Actual native picker traversal and Escape/focus recipient diagnosis; menu/AT original acceptance remains pending')
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
   client=Endpoint(**config);client.hello();env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env['XDG_STATE_HOME']=str(s.host.runtime/'private-warlock-state');report['privateStateRoot']=env['XDG_STATE_HOME'];env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
   if CATALOG:
    catalog_root=pathlib.Path(env['XDG_DATA_HOME'])/'applications';catalog_root.mkdir(mode=0o700,parents=True,exist_ok=True)
    # Only explicitly owned fixture metadata is visible to this broker.
    catalog_dirs=s.host.runtime/'empty-search-catalog';catalog_dirs.mkdir(mode=0o700)
    roots={'dataHome':env['XDG_DATA_HOME'],'dataDirs':[str(catalog_dirs)],'cacheDir':str(s.host.runtime/'search-catalog-cache')}
    broker_config=OUTPUT/'search-broker-config.json';broker_config.write_text(json.dumps({**config,'catalogRoots':roots}));broker_config.chmod(0o600)
    backend_fixture=OUTPUT/'catalog-fixture-backend.py';backend_fixture.write_text('import os,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nos.execv("/usr/bin/python3",["/usr/bin/python3","-B",'+repr(str(ROOT/'adapter/daemon.py'))+','+repr(str(broker_config))+'])\n');backend_fixture.chmod(0o600)
    report['catalogFixture']={'backend':str(backend_fixture),'backendSHA256':sha(backend_fixture),'roots':roots,'originalConfigUnchanged':True}
    desktop=catalog_root/'warlock-files.desktop';desktop.write_text('[Desktop Entry]\nType=Application\nName=Files\nGenericName=File manager\nKeywords=folders;documents;\nExec=/usr/bin/true\n')
    (catalog_root/'warlock-editor.desktop').write_text('[Desktop Entry]\nType=Application\nName=Editor\nGenericName=Text editor\nExec=/usr/bin/true\n')
   control=OUTPUT/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')));wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')));
   if not (FOCUS or TASKVIEW):fixture_control('hide-peer');wait(lambda:len(s.data('clients'))==1)
   if TASKVIEW:
    peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
    check('OwnedPeerMovesToWorkspaceTwo',s.ctl('dispatch',"hl.dsp.window.move({workspace=2,follow=false,window='address:"+peer['address']+"'})").strip()=='ok')
    wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' and w['workspace']['id']==2 for w in s.data('clients')))
   w=next(w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE');selector='address:'+w['address']
   if not w['floating']:check('FixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+selector+"'})").strip()=='ok')
   check('FixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+selector+"'})").strip()=='ok')
   check('FixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=40,y=100,window='"+selector+"'})").strip()=='ok')
   check('FixtureFocus',s.ctl('dispatch',"hl.dsp.focus({window='"+selector+"'})").strip()=='ok')
   web=s.host.launch('warlock',['%s'%binary,'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture if CATALOG else ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock.log';collector=Collector()
   def text():return log.read_text(errors='replace')
   def projection():return collector.read(text())
   def group(operation):
    p=projection();return next((g for g in p['groups'] if (FOCUS or g['title']=='ELM-AUTHORITY-FIXTURE') and g['label'].startswith(operation+' ') and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='window-effect']
   def feedback(state):
    p=projection()
    if not p or p['transaction']!=state:return None
    rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
    return next((r for r in reversed(rows) if r['publication']==p['publication']),None)
   def click(item):
    check('PointerTargetWithinActualViewport',item['visible'],item=item);x,y=map(round,item['point']);helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   def facts():return client.scene_facts('441')
   initial=None if TASKVIEW else wait(lambda:group('Choose a window from' if FOCUS else 'Minimize'))
   target=next(w['incarnation'] for w in client.snapshot('442')['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')
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
   if CATALOG or TASKVIEW:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    def popup_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     return rows[-1] if rows else None
    def field_value():
     body=popup_body();fields=body.get('fields',[]) if body else []
     return next((f['value'] for f in fields if f['id']=='launcher-search'),None)
    def launches():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='application-launch']
    def popup_capture(stage):
     import re
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l]
     box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     body=popup_body();image=OUTPUT/('popup-'+stage+'.png');helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
     # Count only current control interiors. Whole-popup counts incorrectly
     # included the compositor's warning overlay above a black reopened popup.
     for button in body['buttons']:
      selected=button['accessibleName'].startswith('Browse workspace ') if TASKVIEW else button['accessibleName'] in ['Refresh applications','Open Files']
      if not selected or button['disabled'] or button['y']<0 or button['y']+button['height']>box[3]:continue
      left,top=max(0,int(box[0]+button['x'])+12),max(100,int(box[1]+button['y'])+6)
      right,bottom=min(800,int(box[0]+button['x']+min(220,button['width']))-12),min(600,box[1]+box[3],int(box[1]+button['y']+button['height'])-6)
      bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
      painted=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>15 for c in range(3)))
      regions.append({'accessibleName':button['accessibleName'],'brightPixels':bright,'paintedPixels':painted,'area':max(0,right-left)*max(0,bottom-top),'region':[left,top,right,bottom]})
     report.setdefault('popupCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'controlRegions':regions,'body':body,'drawObservations':[l for l in text().splitlines() if l.startswith('popup-draw-observation:')][-3:]})

    def bar_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
     return rows[-1] if rows else None
    def requests(kind):return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']==kind]
    def query(codes,expected):
     wait(lambda:(popup_body() or {}).get('focus')=='launcher-search')
     helper([str(keyboard)],'key 29 1\nkey 30 1\nsleep 50\nkey 30 0\nkey 29 0\nkey 14 1\nkey 14 0\nsleep 100\nsync\n')
     for code in codes:key(code)
     wait(lambda:field_value()==expected)
    def keyboard_button(label):
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
     for _ in range(len(popup_body()['buttons'])+2):
      if popup_body()['focus']==button['id']:break
      key(15)
     check('KeyboardReaches'+label,popup_body()['focus']==button['id'],body=popup_body())
     key(57)
    if TASKVIEW:
     wait(lambda:(projection() or {}).get('phase')=='Coherent')
     native_facts=facts();labels={w['incarnation']:w['label'] for w in client.snapshot('443')['windows']}
     membership=[{'incarnation':w['incarnation'],'label':labels[w['incarnation']],'workspace':w['workspace']} for w in native_facts['facts']['windows'] if w['incarnation'] in labels]
     active=s.data('monitors')[0]['activeWorkspace']['id'];before=len(journal());before_focus=native_facts['facts']['focused']
     check('TwoPopulatedNativeWorkspaceFixture',sorted((w['label'],w['workspace']) for w in membership)==[('ELM-ACTIVATION-PEER','2'),('ELM-AUTHORITY-FIXTURE','1')] and active==1,membership=membership,activeWorkspace=active)
     report['workspaceOracle']={'membership':membership,'activeWorkspace':str(active),'beforeFocus':before_focus}
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     body=wait(lambda:next((b for b in [popup_body()] if b and 'Task View' in b['text'] and 'active workspace' in b['text'].lower() and all(any(w['label']+' on workspace '+w['workspace'] in button['accessibleName'] for button in b['buttons']) for w in membership)),None))
     marker=next(b for b in body['buttons'] if b['accessibleName']=='Browse workspace 1; active workspace')
     wait(lambda:(popup_body() or {}).get('focus')==marker['id'])
     check('TaskViewGroupsMatchNativeMembership',all(any(w['label']+' on workspace '+w['workspace'] in b['accessibleName'] and 'Workspace '+w['workspace'] in b['label'] for b in body['buttons']) for w in membership),body=body)
     check('ActiveWorkspaceMarkerIsKeyboardSelected',popup_body()['focus']==marker['id'] and 'Active workspace' in marker['label'],body=popup_body())
     popup_capture('initial')
     keyboard_button('Browse workspace 2')
     body=wait(lambda:next((b for b in [popup_body()] if b and 'ELM-ACTIVATION-PEER' in b['text'] and 'ELM-AUTHORITY-FIXTURE' not in b['text'] and any(button['accessibleName']=='Browse workspace 2' and 'Selected' in button['label'] and button['id']==b['focus'] for button in b['buttons'])),None))
     check('KeyboardWorkspaceBrowseDoesNotMutateNative',len(journal())==before and facts()['facts']['focused']==before_focus and s.data('monitors')[0]['activeWorkspace']['id']==active,body=body)
     popup_capture('workspace-two')
     for capture in report['popupCaptures']:check('ActualTaskViewControlPixels'+capture['stage'],bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     report['nativeTaskViewMembershipObserved']=True
     all_windows=next(b for b in body['buttons'] if b['accessibleName']=='Browse all workspaces')
     import re
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     x,y=map(round,(box[0]+all_windows['x']+all_windows['width']/2,box[1]+all_windows['y']+all_windows['height']/2))
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     wait(lambda:all(w['label'] in (popup_body() or {}).get('text','') for w in membership))
     check('PointerAllWorkspacesRestoresGroupsWithoutMutation',len(journal())==before,body=popup_body())
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
     key(30);delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else []
     check('OverviewEscapeReturnsToEligibleOpener',facts()['facts']['focused']==before_focus and any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-AUTHORITY-FIXTURE' for e in delivered),events=delivered,before=before_focus,after=facts()['facts']['focused'])
     check('OverviewDismissalHasNoNativeMutation',len(journal())==before)
     report['nativeTaskViewJourneyObserved']=True
    elif PINS:
     state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/taskbar.json'
     def saved_order():return json.loads(state_file.read_text())['identities'] if state_file.exists() else []
     click(wait(lambda:(projection() or {}).get('openApplications')))
     wait(lambda:field_value()=='' and (popup_body() or {}).get('focus')=='launcher-search')
     query([33,23,38,18,31],'files');keyboard_button('Pin Files');wait(lambda:saved_order()==['warlock-files'])
     query([18,32,23,20,24,19],'editor');keyboard_button('Pin Editor');wait(lambda:saved_order()==['warlock-files','warlock-editor'])
     keyboard_button('Move Editor left');wait(lambda:saved_order()==['warlock-editor','warlock-files'])
     check('NativeKeyboardPinAndReorderWriteExactlyOnce',len(requests('taskbar-pins-write'))==3 and not launches() and not journal(),requests=requests('taskbar-pins-write'),storage=json.loads(state_file.read_text()))
     check('PinStorageIsPrivate',state_file.stat().st_mode&0o777==0o600 and state_file.parent.stat().st_mode&0o777==0o700)
     report['beforeRestartOrder']=saved_order();report['firstSessionRequests']=requests('taskbar-pins-write')
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
     owned=next(row for proc,row in s.host.processes if proc is web);s.host.stop(owned,web);web.wait(timeout=5);check('FirstShellExitsNormallyForRestart',web.returncode==0)
     web=s.host.launch('warlock-restarted',[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock-restarted.log';collector=Collector()
     def pins_on_bar():return [b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName'] in ('Open Editor','Open Files')]
     wait(lambda:len(pins_on_bar())==2 and (projection() or {}).get('phase')=='Coherent')
     buttons=pins_on_bar();check('ActualRestartRetainsBothIdentitiesInChosenOrder',[b['accessibleName'] for b in buttons]==['Open Editor','Open Files'] and saved_order()==report['beforeRestartOrder'],body=bar_body(),storage=json.loads(state_file.read_text()))
     check('RestartDoesNotReplayPinWriteOrLaunch',not requests('taskbar-pins-write') and not launches() and not journal())
     image=OUTPUT/'pins-after-restart.png';helper(['/usr/bin/grim',str(image)]);report['capture']={'path':str(image),'sha256':sha(image)}
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
     for button in buttons:
      left,top=max(0,int(button['x'])+4),max(0,int(button['y'])+4);right,bottom=min(800,int(button['x']+button['width'])-4),min(48,int(button['y']+button['height'])-4)
      bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
      check('RestartedPinHasNativeTextPixels'+button['accessibleName'],bright>15,brightPixels=bright,region=[left,top,right,bottom])
     chosen=buttons[0];click({'visible':0<=chosen['x']<800 and 0<=chosen['y']<48,'point':[chosen['x']+chosen['width']/2,chosen['y']+chosen['height']/2]})
     wait(lambda:len(launches())==1 and 'application-launch-outcome' in text())
     check('CurrentZeroWindowPinIssuesOneIdentityBoundLaunch',launches()[0]['intent']['entry']=='warlock-editor' and len(launches())==1 and not journal(),requests=launches())
     outcomes=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and 'application-launch-outcome' in l]
     report['launchOutcomes']=outcomes;check('NativeGioSubmissionConfirmed',len(outcomes)==1 and outcomes[0]['outcome']['status']=='Submitted',outcomes=outcomes)
     report['afterRestartOrder']=saved_order();report['afterRestartLaunches']=launches();report['nativePinJourneyObserved']=True
    else:
     click(wait(lambda:(projection() or {}).get('openApplications')));wait(lambda:field_value()=='' and any(b['accessibleName']=='Open Files' for b in (popup_body() or {}).get('buttons',[])));wait(lambda:(popup_body() or {}).get('focus')=='launcher-search')
     check('NativeCatalogAndEditableSearchHaveNames',popup_body()['focus']=='launcher-search',body=popup_body())
     if PRESENTATION:popup_capture('initial')
     for code in [33,23,38,18,31]:key(code)
     wait(lambda:field_value()=='files' and any(b['accessibleName']=='Open Files' and not b['disabled'] for b in (popup_body() or {}).get('buttons',[])))
     check('CurrentQueryFiltersNativeCatalog',not any(b['accessibleName']=='Open Editor' for b in popup_body()['buttons']),body=popup_body());check('TypingIsObservationOnly',not launches() and not journal())
     if PRESENTATION:popup_capture('filtered')
     # Remove the exact selected identity after its observed current result.
     desktop.unlink();key(28);wait(lambda:'refused' in (popup_body() or {}).get('text','').lower() and field_value()=='files' and (popup_body() or {}).get('focus')=='launcher-search')
     check('NativeEnterIssuesOneIdentityBoundLaunch',len(launches())==1 and launches()[0]['intent']['entry']=='warlock-files',requests=launches())
     check('RefusalPreservesQueryAndReachableFocus',popup_body()['focus']=='launcher-search' and field_value()=='files' and any(b['accessibleName']=='Refresh applications' and not b['disabled'] for b in popup_body()['buttons']),body=popup_body())
     if PRESENTATION:popup_capture('refused')
     body=popup_body();refresh=next(b for b in body['buttons'] if b['accessibleName']=='Refresh applications' and not b['disabled']);rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];import re;rect=tuple(map(int,re.search(r'configure\((\d+), (\d+), (\d+), (\d+)\)',rows[-1]).groups()));x,y=map(round,(rect[0]+refresh['x']+refresh['width']/2,rect[1]+refresh['y']+refresh['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     wait(lambda:field_value()=='files' and 'No matching' in (popup_body() or {}).get('text',''));key(28);check('RefreshAndNoMatchNeverLaunchReplacement',len(launches())==1,body=popup_body())
     screenshot_path=OUTPUT/'search-refused.png';helper(['/usr/bin/grim',str(screenshot_path)]);report['capture']={'path':str(screenshot_path),'sha256':sha(screenshot_path)}
     report['nativeSearchJourneyObserved']=True
     if PRESENTATION:
      popup_capture('no-match')
      for capture in report['popupCaptures']:check('ActualPopupControlPixels'+capture['stage'],bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
      report['popupControlsPhysicallyObserved']=True
   elif FOCUS:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
    report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    before=len(journal());before_focus=facts()['facts']['focused'];click(initial)
    picker=wait(lambda:(projection() or {}).get('picker'))
    wait(lambda:'surface-focus-applied:' in text())
    check('ActualGroupOpensWithoutWindowMutation',len(journal())==before and len(picker['selections'])==2,picker=picker)
    def popup_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     return rows[-1] if rows else None
    body=wait(popup_body);first_focus=body['focus'];check('NativePopupFocusNamesAnEligibleMember',first_focus in [row['domId'] for row in picker['selections']],body=body)
    key(15);next_body=wait(lambda:next((b for b in [popup_body()] if b and b['focus']!=first_focus),None))
    check('TabRemainsInsidePopup',next_body['focus'] in [b['id'] for b in next_body['buttons'] if not b['disabled']],body=next_body)
    order=[b['id'] for b in next_body['buttons'] if not b['disabled']]
    for _ in range(len(order)):
     old=popup_body()['focus'];expected=order[(order.index(old)+1)%len(order)];key(15)
     wrapped=wait(lambda:next((b for b in [popup_body()] if b and b['focus']==expected),None))
     check('ForwardTabWrapsInDocumentedPopupOrder',wrapped['focus']==expected,expected=expected,actual=wrapped['focus'])
    old=popup_body()['focus'];expected=order[(order.index(old)-1)%len(order)]
    helper([str(keyboard)],'key 42 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 42 0\nsleep 100\nsync\n')
    reverse=wait(lambda:next((b for b in [popup_body()] if b and b['focus']==expected),None))
    check('ShiftTabTraversesPopupInReverse',reverse['focus']==expected,expected=expected,actual=reverse['focus'])
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
    after_focus=facts()['facts']['focused'];report['focusReturn']={'before':before_focus,'after':after_focus,'bar':projection()}
    events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
    key(30);delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else [];report['keyboardRecipients']=delivered
    check('EscapeDismissalDoesNotDispatchWindowEffect',len(journal())==before)
    check('EscapeRestoresOriginalNativeRecipient',after_focus==before_focus and any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-AUTHORITY-FIXTURE' for e in delivered),before=before_focus,after=after_focus,events=delivered)
    click(wait(lambda:group('Choose a window from')));picker=wait(lambda:(projection() or {}).get('picker'));selected=next(x for x in picker['selections'] if x['title']=='ELM-ACTIVATION-PEER');click(selected)
    wait(lambda:transaction_state()=='Committed' and (projection() or {}).get('picker') is None)
    check('ChosenGroupMemberActuallyActivates',facts()['facts']['focused']==selected['incarnation'] and len(journal())==before+1 and journal()[-1]['intent']['incarnation']==selected['incarnation'],request=journal()[-1])
   else:
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
   report['nativeFeedbackObserved']=not FOCUS and not CATALOG and not TASKVIEW;report['nativeFocusJourneyObserved']=FOCUS;check('EveryRegisteredHelperExitedNormally',all(r['exitCode']==0 for r in report['helpers']));report['passed']=True
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
