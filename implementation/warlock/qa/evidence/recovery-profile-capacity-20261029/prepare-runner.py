#!/usr/bin/env python3
"""Root-only actual private descriptor/production Profile.prepare phase.

Creates the owned compositor/bus fixture and the profile-manager process only.
Never launches candidate or predecessor; no rollback or UI-020 acceptance.
"""
import hashlib,importlib.util,json,os,pathlib,resource,socket,stat,struct,sys,time,traceback
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
REPO=pathlib.Path('/home/charles/Warlock');PRODUCT=REPO/'implementation/warlock'
TRIAL=BASE/'omarchy-recovery-trial-v1'
CANDIDATE=HERE/'fresh_candidate.py'
CANDIDATE_SHA='6b9b460c7255e7b3c57ee79741e0c5943f421c761c854b35106114396190cf75'
DESCRIPTOR=BASE/'omarchy-recovery-predecessor-v1/predecessor-descriptor-proposal.json'
DESCRIPTOR_SHA='1a60b21da78072bc198d36bf130098572efff5dac9cddb20edc437f35cb8b02c'
INVENTORY=BASE/'omarchy-profile-closure-terra3-v1/inventory.json'
INVENTORY_SHA='c05cf3c1dbf0cdf5771d73c7761167b83ffe6f9c0755d9e8fadb1e75cce9cbe7'
BOUNDARY=TRIAL/'boundary.py';BOUNDARY_SHA='55483418f93b85cdb2ab4b63a03adb15d5b9883947152c37a2f95c6b4263cbe8'
EXEC_WRAPPER=TRIAL/'exec-predecessor.py';EXEC_SHA='5caf5229e4f8d9e74c233a2820b44c6f7f25dd51bff842c22ba358fed305b058'
CONFIG=TRIAL/'private-shell.json';CONFIG_SHA='f1f862c25a20461662720ff360da74e5902c74afa0518b609819fb225ce62a3f'
THEME=pathlib.Path('/usr/share/omarchy/themes/tokyo-night/colors.toml');THEME_SHA='8b5f53ba35b9305aafa72776dd56ea2029faaf29015e2e42db5e19ef698a8e0e'
WORKER=HERE/'prepare-worker.py';WORKER_SHA='afc87ee77c69f6d3c8bcbda8fa9869f00199f62c0f529a4a1540408d360eecad'
ASSET_REPORT=BASE/'context-keyup-assets-v1/output/report.json';ASSET_SHA='69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955'
HOST_REPORT=BASE/'taskbar-host-rebuild-v1/output/report.json';HOST_SHA='13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def checked(path,expected):
 raw=pathlib.Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('reviewed input changed: '+str(path))
 return raw
def module(path,expected,name):
 raw=checked(path,expected);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def private_copy(path,body):
 path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('no arguments; protected no-bytecode launcher only')
 sys.path.insert(0,str(REPO/'window-integration-qa'))
 from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit must remain (1,1)')
 failed=BASE/'omarchy-profile-measure-terra-2-v1/profile-prepare-1793301796817080134'
 checked(failed/'report.json','191265a54b07e13f1fc89c70f66443495ee7359c5aa210a1da47861c628dfe71')
 old_manifest=checked(failed/'actual-profile-manifest.json','2aedc25e50b8cb59ea2fedfde4e1eb00e1fd0b74bc08751d444abfbd2ffe7d07')
 if len(old_manifest)!=76694:raise RuntimeError('Prior measured failure manifest size changed')
 checked(WORKER,WORKER_SHA);host=module(CANDIDATE,CANDIDATE_SHA,'fresh_candidate');boundary=module(BOUNDARY,BOUNDARY_SHA,'omarchy_boundary')
 sys.path.insert(0,str(REPO/'implementation/warlock-client-provider-native-v204/qa'));sys.path.insert(0,str(PRODUCT/'adapter'))
 checked(PRODUCT/'adapter/recovery_profile.py','ace346503b5afd2c691748e7c2e1c25394fd81cc0a90be60525ff6cd85a78142')
 checked(REPO/'implementation/warlock-client-provider-native-v204/qa/system_isolation.py','029a41bc8aae39936c69dc591857795aabd43df17b1f9a86b02b6c6a83dddc0e')
 checked(REPO/'implementation/warlock-client-provider-native-v204/qa/session_bus.py','d8f945a68a8e772ffd26458e8e60beac8c8ad79849f08a2daf4110f5c8178916')
 from session_bus import isolate_session_host
 import system_isolation as isolation
 from endpoint import start_time
 # The inherited session creates its host from the original module globals.
 isolate_session_host(host.original)
 predecessor_base=json.loads(checked(DESCRIPTOR,DESCRIPTOR_SHA));audit=json.loads(checked(INVENTORY,INVENTORY_SHA))
 if len(predecessor_base['files'])!=439 or audit['predecessorDescriptorSHA256']!=DESCRIPTOR_SHA:raise RuntimeError('Predecessor inventory mismatch')
 if predecessor_base['argv']!=['/usr/bin/quickshell','-n','-p','/usr/share/omarchy/shell'] or predecessor_base['cwd']!='/usr/share/omarchy/shell':raise RuntimeError('Predecessor command changed')
 for path,h in predecessor_base['files'].items():checked(path,h)
 config=checked(CONFIG,CONFIG_SHA);theme=checked(THEME,THEME_SHA);checked(EXEC_WRAPPER,EXEC_SHA)
 assets=json.loads(checked(ASSET_REPORT,ASSET_SHA));host_report=json.loads(checked(HOST_REPORT,HOST_SHA));tup=host.verify_tuple();slots=tup['slots']
 if not assets.get('passed') or not host_report.get('passed') or len(assets['assets'])!=19 or len(host_report['linkedProviders'])!=144:raise RuntimeError('Current resource reports invalid')
 run=HERE/('profile-prepare-'+str(time.time_ns()));run.mkdir(mode=0o700)
 output=pathlib.Path.home()/'window-integration-qa'/('omarchy-profile-prepare-'+str(time.time_ns()))
 report={'scope':'Actual descriptor materialization and production Profile.prepare only; neither host launched','nativeAcceptance':False,'offlineRecoveryObserved':False,'passed':False,'prepareInvoked':False,'sourceQualification':host.verify_sources(),'checks':[],'inventoryScope':'conservative predecessor 439 files plus observed/generated fixture inputs and 144 recorded candidate host providers; not complete release or dynamic runtime closure'}
 session=None
 def check(name,condition,**data):
  report['checks'].append({'name':name,'passed':bool(condition),**data})
  if not condition:raise RuntimeError(name)
 try:
  with host.PrivateHyprSession(output,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
   session=s;runtime=pathlib.Path(s.host.runtime);home=pathlib.Path(s.env['HOME'])
   private_config=home/'.config/omarchy/shell.json';private_theme=home/'.local/state/omarchy/current/theme/colors.toml'
   private_copy(private_config,config);private_copy(private_theme,theme);(home/'.config/omarchy/plugins').mkdir(mode=0o700,parents=True,exist_ok=True)
   check('ActivationFreeSessionBus',s.evidence.get('sessionActivationDisabled') is True and s.evidence.get('sessionListenerOwned') is True)
   bus_proc=next(proc for proc,row in s.host.processes if row['name']=='privateBus');bus=runtime/'bus';st=bus.lstat()
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
    conn.settimeout(2);conn.connect(str(bus));pid,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   check('PrivateBusPeerMatchesOwnedProcess',bus_proc.poll() is None and pid==bus_proc.pid and uid==os.getuid())
   private_base=dict(s.env)
   for key in boundary.AUDIO:private_base.pop(key,None)
   env=boundary.final_environment(s,private_base,isolation.supply,isolation.validate,(st.st_dev,st.st_ino,st.st_uid),s.env['XDG_STATE_HOME'])
   boundary.checked_guards();s.guard()
   config_path=run/'authority-config.json';broker_path=run/'search-broker-config.json';backend_path=run/'catalog-fixture-backend.py'
   native={'runtime':str(runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':s.evidence['compositorPID'],'expected_start':int(start_time(s.evidence['compositorPID'])),'binary_sha256':slots['core']['sha256']}
   catalog_root=pathlib.Path(env['XDG_DATA_HOME'])/'applications';catalog_root.mkdir(mode=0o700,parents=True,exist_ok=True)
   catalog_dirs=runtime/'empty-search-catalog';catalog_dirs.mkdir(mode=0o700)
   roots={'dataHome':env['XDG_DATA_HOME'],'dataDirs':[str(catalog_dirs)],'cacheDir':str(runtime/'search-catalog-cache')}
   private_copy(config_path,json.dumps(native).encode());private_copy(broker_path,json.dumps({**native,'catalogRoots':roots}).encode())
   backend='import os,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nos.execv("/usr/bin/python3",["/usr/bin/python3","-B",'+repr(str(PRODUCT/'adapter/daemon.py'))+','+repr(str(broker_path))+'])\n'
   private_copy(backend_path,backend.encode())
   prefiles=dict(predecessor_base['files'])
   for path in [pathlib.Path('/usr/bin/python3'),EXEC_WRAPPER,BOUNDARY,CONFIG,THEME,private_config,private_theme,*[boundary.GUARDS/name for name in boundary.NAMES]]:prefiles[str(path)]=sha(path)
   pred={'schema':1,'argv':['/usr/bin/python3','-B',str(EXEC_WRAPPER)],'cwd':'/usr/share/omarchy/shell','files':prefiles}
   candidate_files={str(pathlib.Path('/usr/bin/python3')):sha('/usr/bin/python3'),str(config_path):sha(config_path),str(broker_path):sha(broker_path),str(backend_path):sha(backend_path)}
   for row in assets['assets'].values():candidate_files[row['path']]=row['sha256']
   adapter_paths=sorted((PRODUCT/'adapter').glob('*.py'))
   for path in adapter_paths:candidate_files[str(path)]=sha(path)
   for name in ('core','authority','aquamarine','host'):
    row=slots[name];candidate_files[row['path']]=row['sha256']
   for path,h in host_report['linkedProviders'].items():candidate_files[path]=h
   for path,h in candidate_files.items():checked(path,h)
   for path,h in prefiles.items():checked(path,h)
   cand={'schema':1,'argv':[slots['host']['path'],'--assets',str(pathlib.Path(assets['assets']['elm.js']['path']).parent),'--authority-config',str(config_path),'--backend',str(backend_path),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],'cwd':str(run),'files':candidate_files}
   packet={'predecessor':pred,'candidate':cand,'profile':str(run/'recovery-profile'),'guardDirectory':str(boundary.GUARDS)}
   packet_path=run/'descriptors.json';private_copy(packet_path,(json.dumps(packet,sort_keys=True,separators=(',',':'))+'\n').encode())
   report.update(descriptorInputs={'path':str(packet_path),'sha256':sha(packet_path),'predecessorFiles':len(prefiles),'candidateFiles':len(candidate_files),'adapterPythonFiles':len(adapter_paths),'hostProviders':len(host_report['linkedProviders']),'generated':[{'path':str(p),'sha256':sha(p)} for p in (config_path,broker_path,backend_path,private_config,private_theme)],'actualCommand':cand['argv'],'privateRuntimePathsExpireAfterCleanup':True})
   # Revalidate routing immediately before the manager itself receives env.
   env=boundary.final_environment(s,private_base,isolation.supply,isolation.validate,(st.st_dev,st.st_ino,st.st_uid),s.env['XDG_STATE_HOME'])
   manager=s.host.launch('profile-prepare',['/usr/bin/python3','-B',str(WORKER),str(packet_path)],env=env)
   try:manager.wait(timeout=5)
   except BaseException:
    owned=next(row for proc,row in s.host.processes if proc is manager);s.host.stop(owned,manager);manager.wait(timeout=5);raise
   result_path=run/'prepare-result.json';measure_path=run/'actual-profile-measurement.json';manifest_path=run/'actual-profile-manifest.json'
   if not result_path.exists():raise RuntimeError('Profile manager produced no terminal report')
   result=json.loads(result_path.read_bytes());report.update(prepareResult=result,prepareInvoked=result.get('prepareInvoked') is True,managerExit=manager.returncode)
   if measure_path.exists():report['measurementArtifact']={'path':str(measure_path),'sha256':sha(measure_path),'value':json.loads(measure_path.read_bytes())}
   if manifest_path.exists():report['manifestArtifact']={'path':str(manifest_path),'sha256':sha(manifest_path),'bytes':manifest_path.stat().st_size}
   if result.get('passed') is True and manager.returncode==0:report['passed']=True
   else:report['error']='Production Profile.prepare did not complete; see retained result and exact measurement'
 except BaseException as error:
  report['error']=repr(error);report['traceback']=traceback.format_exc()
 if session is not None:
  e=session.evidence;report['cleanup']={k:e.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants','runtimeGone')}
  if e.get('cleanupErrors') or e.get('unexpectedInnerDescendants') or e.get('remainingDescendants') or not e.get('runtimeGone'):report['passed']=False
 private_copy(run/'report.json',(json.dumps(report,indent=2)+'\n').encode())
 print(json.dumps({'passed':report['passed'],'prepareInvoked':report['prepareInvoked'],'report':str(run/'report.json')}))
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
