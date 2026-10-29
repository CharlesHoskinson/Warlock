"""Materialize and prepare the reviewed recovery profile in a caller-owned session.

The caller must apply isolate_session_host(host.original) BEFORE constructing
its session, and retain/clean that same session. This module never creates one.
"""
import hashlib,json,os,pathlib,resource,socket,stat,struct,sys
P=pathlib.Path('/home/charles/Warlock/implementation/warlock')
B=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
V=B/'omarchy-profile-measure-root-v3'; TRIAL=B/'omarchy-recovery-trial-v1'
FILES={
 V/'runner.py':'07a28ef50be34b8f3323552cc30913233d2815acbde9686e02dff9c1f1c43b84',
 V/'prepare-worker.py':'afc87ee77c69f6d3c8bcbda8fa9869f00199f62c0f529a4a1540408d360eecad',
 V/'fresh_candidate.py':'6b9b460c7255e7b3c57ee79741e0c5943f421c761c854b35106114396190cf75',
 B/'omarchy-recovery-predecessor-v1/predecessor-descriptor-proposal.json':'1a60b21da78072bc198d36bf130098572efff5dac9cddb20edc437f35cb8b02c',
 B/'omarchy-profile-closure-terra3-v1/inventory.json':'c05cf3c1dbf0cdf5771d73c7761167b83ffe6f9c0755d9e8fadb1e75cce9cbe7',
 TRIAL/'boundary.py':'55483418f93b85cdb2ab4b63a03adb15d5b9883947152c37a2f95c6b4263cbe8',
 TRIAL/'exec-predecessor.py':'5caf5229e4f8d9e74c233a2820b44c6f7f25dd51bff842c22ba358fed305b058',
 TRIAL/'private-shell.json':'f1f862c25a20461662720ff360da74e5902c74afa0518b609819fb225ce62a3f',
 pathlib.Path('/usr/share/omarchy/themes/tokyo-night/colors.toml'):'8b5f53ba35b9305aafa72776dd56ea2029faaf29015e2e42db5e19ef698a8e0e',
 B/'context-keyup-assets-v1/output/report.json':'69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955',
 B/'taskbar-host-rebuild-v1/output/report.json':'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a',
 P/'adapter/recovery_profile.py':'ace346503b5afd2c691748e7c2e1c25394fd81cc0a90be60525ff6cd85a78142',
 pathlib.Path('/home/charles/Warlock/implementation/warlock-client-provider-native-v204/qa/system_isolation.py'):'029a41bc8aae39936c69dc591857795aabd43df17b1f9a86b02b6c6a83dddc0e',
 pathlib.Path('/home/charles/Warlock/implementation/warlock-client-provider-native-v204/qa/session_bus.py'):'d8f945a68a8e772ffd26458e8e60beac8c8ad79849f08a2daf4110f5c8178916'}

HELPERS={
 '/usr/share/omarchy/bin/omarchy-shell':'538ece231aba80154c76ab48df8ab013b2f02c5171241d08bddbf08a5fe5ac34',
 '/usr/bin/omarchy-shell':'538ece231aba80154c76ab48df8ab013b2f02c5171241d08bddbf08a5fe5ac34',
 '/usr/bin/env':'a9ba02dcad338ee7f0b03e58a1cf44009b2bd645b09c2b423242e9791d202301',
 '/usr/bin/bash':'c14c8f498f3be96f076ceb07d65dba584a86dca3c86b5dce65ed0f6cae73358d',
 '/bin/bash':'c14c8f498f3be96f076ceb07d65dba584a86dca3c86b5dce65ed0f6cae73358d',
 '/usr/bin/timeout':'629cb6e82df4bb47188eec340f2ceb5f45def2e7b1aac1bd7443beecdcb42a6a',
 '/usr/bin/qs':'6c56d84cef7ac7d992de1628020f21ef722f957efb2233f2e66e1f2bb135e97c',
 '/usr/lib/libreadline.so.8':'c55b53a98e218df23f2f90ca1015974e122be2ee1d5fc93db1cc097440699b65',
 '/usr/lib/libncursesw.so.6':'7498a0b0f75deb5417e109d1853679f1a6b201e52e03b247c914fec0a36e3a5b',
 '/usr/lib/libc.so.6':'02c8c3d06180beee9c7d0392aa85736c7d19f274a81e7f8f0b3d9e28e0641524',
 '/usr/lib64/ld-linux-x86-64.so.2':'f5e11cc62f8f2c24dff532982559f4303dba3b17e7450551372a88c8e7ea8757'}
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def checked(path,digest):
 raw=pathlib.Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=digest:raise RuntimeError('reviewed input changed: '+str(path))
 return raw
def copy_private(path,body):
 path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(body);f.flush();os.fsync(f.fileno())
def materialize(session,run_directory,host,boundary,isolation,start_time):
 """Return live profile, descriptors, baseline and refreshable validated env.

 host is pinned v3 fresh_candidate module; boundary/isolation are pinned v3
 modules, start_time is endpoint.start_time. run_directory is a precreated,
 private empty directory; session remains open and owned by the caller.
 """
 if os.environ.get('PYTHONDONTWRITEBYTECODE')!='1' or resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('protected no-bytecode/core limit required')
 run=pathlib.Path(run_directory)
 if not run.is_absolute() or run.resolve()!=run:raise RuntimeError('run directory must be absolute, no symlinks')
 st=run.stat()
 if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid() or st.st_mode&0o077 or any(run.iterdir()):raise RuntimeError('run directory must be empty, private and owned')
 for path,digest in FILES.items():checked(path,digest)
 if pathlib.Path(host.__file__).resolve()!=(V/'fresh_candidate.py').resolve() or pathlib.Path(boundary.__file__).resolve()!=(TRIAL/'boundary.py').resolve() or pathlib.Path(isolation.__file__).resolve()!=pathlib.Path('/home/charles/Warlock/implementation/warlock-client-provider-native-v204/qa/system_isolation.py').resolve():raise RuntimeError('wrong qualified modules')
 source_qualification=host.verify_sources();slots=host.verify_tuple()['slots'];session.guard();session.host.verify()
 if session.evidence.get('sessionActivationDisabled') is not True or session.evidence.get('sessionListenerOwned') is not True:raise RuntimeError('host.original activation-free session isolation missing')
 runtime=pathlib.Path(session.host.runtime);home=pathlib.Path(session.env['HOME']);bus=runtime/'bus'
 bus_proc=next(proc for proc,row in session.host.processes if row['name']=='privateBus')
 bus_stat=bus.lstat();identity=(bus_stat.st_dev,bus_stat.st_ino,bus_stat.st_uid)
 def validated_environment():
  session.guard();session.host.verify()
  if bus_proc.poll() is not None:raise RuntimeError('owned session bus exited')
  now=bus.lstat()
  if (now.st_dev,now.st_ino,now.st_uid)!=identity:raise RuntimeError('session bus identity changed')
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
   conn.settimeout(2);conn.connect(str(bus));pid,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  if pid!=bus_proc.pid or uid!=os.getuid():raise RuntimeError('session bus peer mismatch')
  base=dict(session.env)
  for key in boundary.AUDIO:base.pop(key,None)
  return boundary.final_environment(session,base,isolation.supply,isolation.validate,identity,session.env['XDG_STATE_HOME'])
 env=validated_environment();private_config=home/'.config/omarchy/shell.json';private_theme=home/'.local/state/omarchy/current/theme/colors.toml'
 copy_private(private_config,checked(TRIAL/'private-shell.json',FILES[TRIAL/'private-shell.json']))
 theme=pathlib.Path('/usr/share/omarchy/themes/tokyo-night/colors.toml');copy_private(private_theme,checked(theme,FILES[theme]));(home/'.config/omarchy/plugins').mkdir(mode=0o700,parents=True,exist_ok=True)
 predecessor_base=json.loads(checked(B/'omarchy-recovery-predecessor-v1/predecessor-descriptor-proposal.json',FILES[B/'omarchy-recovery-predecessor-v1/predecessor-descriptor-proposal.json']))
 audit=json.loads(checked(B/'omarchy-profile-closure-terra3-v1/inventory.json',FILES[B/'omarchy-profile-closure-terra3-v1/inventory.json']))
 if len(predecessor_base['files'])!=439 or audit['predecessorDescriptorSHA256']!=FILES[B/'omarchy-recovery-predecessor-v1/predecessor-descriptor-proposal.json'] or predecessor_base['argv']!=['/usr/bin/quickshell','-n','-p','/usr/share/omarchy/shell'] or predecessor_base['cwd']!='/usr/share/omarchy/shell':raise RuntimeError('predecessor inventory or command changed')
 for path,h in predecessor_base['files'].items():checked(path,h)
 assets=json.loads(checked(B/'context-keyup-assets-v1/output/report.json',FILES[B/'context-keyup-assets-v1/output/report.json']));host_report=json.loads(checked(B/'taskbar-host-rebuild-v1/output/report.json',FILES[B/'taskbar-host-rebuild-v1/output/report.json']))
 if not assets.get('passed') or not host_report.get('passed') or len(assets['assets'])!=19 or len(host_report['linkedProviders'])!=144:raise RuntimeError('current resource reports invalid')
 config_path=run/'authority-config.json';broker_path=run/'search-broker-config.json';backend_path=run/'catalog-fixture-backend.py'
 native={'runtime':str(runtime),'instance':session.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':session.evidence['compositorPID'],'expected_start':int(start_time(session.evidence['compositorPID'])),'binary_sha256':slots['core']['sha256']}
 catalog_root=pathlib.Path(env['XDG_DATA_HOME'])/'applications';catalog_root.mkdir(mode=0o700,parents=True,exist_ok=True);catalog_dirs=runtime/'omarchy-recovery-empty-catalog';catalog_dirs.mkdir(mode=0o700)
 roots={'dataHome':env['XDG_DATA_HOME'],'dataDirs':[str(catalog_dirs)],'cacheDir':str(runtime/'omarchy-recovery-search-catalog-cache')}
 copy_private(config_path,json.dumps(native).encode());copy_private(broker_path,json.dumps({**native,'catalogRoots':roots}).encode())
 backend='import os,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nos.execv("/usr/bin/python3",["/usr/bin/python3","-B",'+repr(str(P/'adapter/daemon.py'))+','+repr(str(broker_path))+'])\n';copy_private(backend_path,backend.encode())
 prefiles=dict(predecessor_base['files']);prefiles.update(HELPERS)
 if pathlib.Path('/usr/share/omarchy/bin/omarchy-shell').resolve()!=pathlib.Path('/usr/bin/omarchy-shell').resolve() or pathlib.Path('/usr/bin/qs').resolve()!=pathlib.Path('/usr/bin/quickshell').resolve() or pathlib.Path('/bin/bash').resolve()!=pathlib.Path('/usr/bin/bash').resolve():raise RuntimeError('selected helper alias changed')
 wrapper=TRIAL/'exec-predecessor.py';config=TRIAL/'private-shell.json'
 for path in [pathlib.Path('/usr/bin/python3'),wrapper,TRIAL/'boundary.py',config,theme,private_config,private_theme,*[boundary.GUARDS/name for name in boundary.NAMES]]:prefiles[str(path)]=sha(path)
 pred={'schema':1,'argv':['/usr/bin/python3','-B',str(wrapper)],'cwd':'/usr/share/omarchy/shell','files':prefiles}
 candidate_files={str(p):sha(p) for p in [pathlib.Path('/usr/bin/python3'),config_path,broker_path,backend_path]}
 for row in assets['assets'].values():candidate_files[row['path']]=row['sha256']
 adapter_paths=sorted((P/'adapter').glob('*.py'))
 for path in adapter_paths:candidate_files[str(path)]=sha(path)
 for name in ('core','authority','aquamarine','host'):
  row=slots[name];candidate_files[row['path']]=row['sha256']
 candidate_files.update(host_report['linkedProviders'])
 for mapping in (prefiles,candidate_files):
  for name,digest in mapping.items():checked(name,digest)
 cand={'schema':1,'argv':[slots['host']['path'],'--assets',str(pathlib.Path(assets['assets']['elm.js']['path']).parent),'--authority-config',str(config_path),'--backend',str(backend_path),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],'cwd':str(run),'files':candidate_files}
 packet={'predecessor':pred,'candidate':cand,'profile':str(run/'recovery-profile'),'guardDirectory':str(boundary.GUARDS)};packet_path=run/'descriptors.json';copy_private(packet_path,(json.dumps(packet,sort_keys=True,separators=(',',':'))+'\n').encode())
 env=validated_environment();manager=session.host.launch('profile-prepare',['/usr/bin/python3','-B',str(V/'prepare-worker.py'),str(packet_path)],env=env)
 try:manager.wait(timeout=5)
 except BaseException:
  owned=next(row for proc,row in session.host.processes if proc is manager);session.host.stop(owned,manager);manager.wait(timeout=5);raise
 result_path=run/'prepare-result.json';measurement_path=run/'actual-profile-measurement.json';manifest_path=run/'actual-profile-manifest.json'
 result=json.loads(result_path.read_bytes())
 if manager.returncode!=0 or result.get('passed') is not True or result.get('prepareInvoked') is not True:raise RuntimeError('production prepare failed: '+str(result_path))
 measurement=json.loads(measurement_path.read_bytes());profile=run/'recovery-profile';actual=(profile/'profile.json').read_bytes()
 if actual!=manifest_path.read_bytes():raise RuntimeError('profile differs from measured manifest')
 baseline={name:(profile/'baseline'/name).read_bytes() for name in ('taskbar.json','settings.json','shortcuts.json','motion.json')}
 digests={name:hashlib.sha256(body).hexdigest() for name,body in baseline.items()}
 if digests!=measurement['baselineHashes']:raise RuntimeError('prepared baseline differs from measurement')
 generated=[config_path,broker_path,backend_path,private_config,private_theme,packet_path,result_path,measurement_path,manifest_path,profile/'profile.json']
 return {'profile':profile,'predecessor':pred,'candidate':cand,'privateHome':home,'privateConfig':private_config,'privateTheme':private_theme,'baselineBytes':baseline,'baselineDigests':digests,'environment':validated_environment(),'validated_environment':validated_environment,'runtimeInputHashes':{str(p):sha(p) for p in generated},'measurement':measurement,'prepareResult':result,'sourceQualification':source_qualification,'busIdentity':identity,'session':session}
