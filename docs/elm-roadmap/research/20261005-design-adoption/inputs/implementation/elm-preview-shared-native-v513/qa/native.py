import hashlib,importlib.util,json,os,pathlib,resource,shutil,signal,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((ROOT/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for p,h in pre['inputs'].items():assert sha(p)==h,p
runtime=REPO/'implementation/elm-preview-shared-runtime-v512';spec=importlib.util.spec_from_file_location('exact_shared_native_host',runtime/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(ROOT/'qa'));from session_bus import isolate_session_host;from system_isolation import supply,validate;from inspection import Collector
isolate_session_host(host)
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir(mode=0o700);private=pathlib.Path('/home/hoskinson/window-integration-qa')/('elm-shared-preview-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full509 controller/bar/popup and backend native coexistence with492 descriptor hello; actual physical picker input, native incarnation labels and default image fallback. No installed capture provider, images, supervised drain or full native release acceptance','checks':[],'pair':pre['pair']}
s=None;fixture=web=None;loaded=False
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
def frames(prefix):return [json.loads(line[len(prefix):]) for line in log.read_text(errors='replace').splitlines() if line.startswith(prefix)]
def click(item):
 assert item['visible'];x,y=map(round,item['point']);assert 0<x<800 and 0<y<600
 commands=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n';p=subprocess.run([pre['pointer'],'800','600'],input=commands,text=True,capture_output=True,env=env,timeout=5);check('ownedPhysicalPointerNormalExit',p.returncode==0,commands=commands,stderr=p.stderr)
try:
 lua=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
 s=host.PrivateHyprSession(private,dict(os.environ),1600,1000,lua,mesa_vendor=True)
 with s:
  try:
   plugin=pre['pair']['plugin']['path'];check('exactSourceProducerPluginLoaded',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory')
   fixture=s.host.launch('source',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(private/'fixture-control.json')],env=env);wait(lambda:len(s.data('clients'))==2)
   child=next(row for _,row in s.host.processes if row['name']=='hyprland');config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':child['pid'],'expected_start':host.original.process(child['pid'])['start'],'binary_sha256':pre['pair']['core']['sha256']};cfg=private/'authority-config.json';cfg.write_text(json.dumps(config));cfg.chmod(0o600)
   command=[pre['hostBinary'],'--assets',pre['guiAssets'],'--backend',pre['backend'],'--authority-config',str(cfg),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'];web=s.host.launch('shared-host',command,env=dict(env,WAYLAND_DEBUG='client'));log=private/'shared-host.log';dom=Collector()
   def projection():return dom.read(log.read_text(errors='replace')) if log.exists() else None
   initial=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['groups'] else None)
   attached=next(frame for frame in frames('backend-frame: ') if frame['kind']=='attached');check('actualBackendAcceptsExactNativeDescriptor',attached['previewFdAddress']=='elm-preview-'+str(child['pid'])+'-'+attached['binding']['lifetime'],attached=attached)
   check('actualFullControllerBarPopupStarted','shared-host-start: views=1 controllers=1 backend-clients=1 sandbox=1' in log.read_text() and 'view-process-policy: related=1 distinct-manager=1' in log.read_text(),initial=initial)
   check('actualCompiledMainNativeCoherentProjection',initial['phase']=='Coherent' and len(initial['groups'])==1)
   click(initial['groups'][0]);picker=wait(lambda:projection() if projection() and projection()['picker'] else None);selections=picker['picker']['selections'];check('physicalGroupedWindowPickerOpens',len(selections)==2 and all(not v['disabled'] and v['visible'] for v in selections),picker=picker)
   check('actualNativeFixtureFallbackLabels',sorted(v['label'] for v in selections)==['Activate ELM-ACTIVATION-PEER','Activate ELM-AUTHORITY-FIXTURE'],selections=selections)
   click(picker['picker']['close']);closed=wait(lambda:projection() if projection() and not projection()['picker'] and projection()['mode']=='closed' else None);check('physicalPickerCloseCurrentLease',closed['phase']=='Coherent' and int(closed['publication'])>int(picker['publication']),closed=closed)
   web.send_signal(signal.SIGTERM);web.wait(timeout=5);check('fullSharedHostNormalExit',web.returncode==0);check('owningBackendNormalExit','backend-exit: waited=1 normal=1 code=0' in log.read_text())
   control({'op':'quit'});fixture.wait(timeout=5);check('sourceApplicationNormalExit',fixture.returncode==0);wait(lambda:not s.data('clients'));r['passed']=True
  finally:
   if web and web.poll() is None:web.send_signal(signal.SIGTERM);web.wait(timeout=5);check('sharedHostCleanupNormalExit',web.returncode==0)
   if fixture and fixture.poll() is None:control({'op':'quit'});fixture.wait(timeout=5);check('sourceCleanupNormalExit',fixture.returncode==0)
   if loaded:wait(lambda:not s.data('clients'));check('clientsEmptyBeforePluginUnload',not s.data('clients'));check('sourcePluginUnloadsAfterConsumers',s.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
 r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes];check('allOwnedProcessesNormalExit',all(v['exitCode']==0 for v in r['ownedExitCodes']),exits=r['ownedExitCodes'])
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
 if s:r['privateHost']=s.host.evidence;r['cleanupPassed']=bool(s.host.evidence.get('runtimeGone') and not s.host.evidence.get('remainingDescendants') and not s.host.evidence.get('unexpectedInnerDescendants') and not s.host.evidence.get('cleanupErrors'))
 if private.exists():shutil.copytree(private,OUT/'private-evidence',symlinks=True)
 r['passed']=r['passed'] and r.get('cleanupPassed',False);r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not r['passed'])
