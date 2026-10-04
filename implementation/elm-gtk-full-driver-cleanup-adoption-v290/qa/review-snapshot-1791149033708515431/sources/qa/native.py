"""Root-only full GTK01–08 orchestration. Import is inert; no bootstrap substitution."""
import argparse,hashlib,importlib.util,json,os,pathlib,resource,socket,struct,sys,time,traceback,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qa/helpers'))
sys.path.insert(0,str(ROOT/'qa'))
from preflight import verify,sha
from driver import Driver
from shell import Shell
from actor import Actor,remaining
from parent import Parent
from bounded import BoundedSession
from owned_bus_host import derivative
from cleanup import cleanup_passed
from types import SimpleNamespace
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def read_keymap(session,host,descriptor,directory,deadline,native):
 directory.mkdir(mode=0o700);process=None;record={'argv':[descriptor['binary']],'deadline':deadline}
 try:
  with (directory/'stdout').open('xb') as out,(directory/'stderr').open('xb') as err:
   process=subprocess.Popen(record['argv'],stdout=out,stderr=err,cwd=directory,env=dict(session.env,ELM_GTK_ROLE_QA='1'),start_new_session=True)
  owned=host.original.process(process.pid);owned.update(name='read-only-child-keymap',command=record['argv'],log=str(directory/'stderr'));session.host.processes.append((process,owned));record['owned']=owned
  process.wait(timeout=min(3,remaining(deadline)));remaining(deadline);session.guard()
  if process.returncode!=0:raise RuntimeError('actual keymap helper normal exit')
  raw=(directory/'stdout').read_bytes()
  if len(raw)>4096 or not raw.endswith(b'\n') or raw.count(b'\n')!=1:raise RuntimeError('one bounded keymap report')
  data=json.loads(raw);assert set(data)=={'seatRegistryId','xkbShiftMask','format','keymapBytes'} and all(type(v) is int and v>0 for v in data.values()) and data['format']==1 and data['xkbShiftMask']<2**32 and data['xkbShiftMask']&(data['xkbShiftMask']-1)==0
  assert (directory/'stderr').read_bytes()==('keymap-peer-pid:'+str(native['pid'])+'\n').encode(), 'actual Wayland connection belongs to owning child'
  keymap=directory/'keymap.xkb';assert keymap.stat().st_size==data['keymapBytes']<=1024*1024
  record.update(report=data,keymapSHA256=sha(keymap));return SimpleNamespace(xkb_shift_mask=data['xkbShiftMask'],gdk_shift_mask=descriptor['constants']['shiftMask'])
 finally:
  if process is not None:
   if process.poll() is None:
    process.terminate()
    try:process.wait(timeout=.5)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=.5)
   record['exit']=process.poll()
  (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')

def run(profile):
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=ROOT/'qa'/('native-'+str(time.time_ns()));out.mkdir();output=pathlib.Path('/home/hoskinson/window-integration-qa')/('gtk-full-'+str(time.time_ns()));report={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False,'profile':profile,'checks':[],'faultCompanionRequired':True};actor=None;shell=None;session=None;loaded=False;observer_loaded=False
 def check(name,value,**extra):
  report['checks'].append({'name':name,'passed':bool(value),**extra});assert value,name
 try:
  host,core,fixture,observer,probe,build,keymap,files=verify();report['inputs']=files;(out/'inputs.json').write_text(json.dumps(files,indent=2)+'\n')
  for name in ('driver.py','shell.py','popup.py','keyboard.py','native.py','preflight.py'):(out/name).write_bytes((ROOT/'qa'/name).read_bytes())
  with derivative(host)(output,dict(os.environ),800,600,LUA,mesa_vendor=True) as session:
   try:
    native=next(row for _,row in session.host.processes if row['name']=='hyprland');parent=next(row for _,row in session.host.processes if row['name']=='weston')
    check('exact-core-AQ-parent-mapped',session.evidence['hyprlandMaps']['files'].get(str(pathlib.Path(core['binary']).resolve()))==core['sha256'] and session.evidence['privateAquamarine']['mappedVerified'] is True and host.original.mapped_files(parent['pid'])['files'].get(str(pathlib.Path(probe['module']['path']).resolve()))==probe['module']['sha256'])
    check('authority-load',session.ctl('plugin','load',core['plugin']['path']).strip()=='ok');loaded=True
    check('observer-load',session.ctl('plugin','load',observer['binary']).strip()=='ok');observer_loaded=True
    maps=host.original.mapped_files(native['pid']);check('actual-authority-observer-maps',maps['files'].get(str(pathlib.Path(core['plugin']['path']).resolve()))==core['plugin']['sha256'] and maps['files'].get(str(pathlib.Path(observer['binary']).resolve()))==observer['binarySHA256'])
    deadline=time.monotonic()+6;bounded=BoundedSession(session,output/'bounded-ipc',deadline)
    actor=Actor(bounded,host,fixture['artifact']['path'],output/'gtk-actor',deadline,profile=profile)
    masks=read_keymap(bounded,host,keymap,output/'owning-keymap',deadline,native)
    config={'runtime':str(session.host.runtime),'instance':session.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':pathlib.Path('/proc',str(native['pid']),'stat').read_text().rsplit(')',1)[1].split()[19],'binary_sha256':core['sha256']}
    config_path=output/'authority-config.json';fd=os.open(config_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(config,stream)
    sys.path.insert(0,str(build/'inputs/adapter'));endpoint_type=load('owned_budget_observer',ROOT/'qa/observer_endpoint.py').ObserverEndpoint;endpoint=endpoint_type(**config);endpoint.parentDeadline=deadline;hello=endpoint.hello();attach=endpoint.geometry_attach('1')
    collector=load('full_current525_collector',ROOT/'qa/original/inspection.py').Collector();shell=Shell(bounded,host,build,config_path,output,collector);shell.launch(deadline)
    check('separate-observer-peer-same-native-lifetime',hello['binding']['lifetime']==shell.geometry_attach()['binding']['lifetime'] and hello['binding']['session']!=shell.geometry_attach()['binding']['session'])
    parent_socket=pathlib.Path(session.host.runtime)/session.host.env['WAYLAND_DISPLAY'];original_socket=host.original.socket_identity(parent_socket,session.host.runtime)
    def parent_peer(until):
     remaining(until);bounded.guard();assert host.original.same_process(parent)
     assert host.original.socket_identity(parent_socket,session.host.runtime)==original_socket
     with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
      peer.settimeout(min(3,remaining(until)));peer.connect(str(parent_socket));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==parent['pid'] and uid==os.getuid()
     assert host.original.socket_identity(parent_socket,session.host.runtime)==original_socket and host.original.same_process(parent);remaining(until)
     return {'parent':parent,'socket':original_socket,'moduleSHA256':probe['module']['sha256']}
    import scene,observer as observer_api,pixels,geometry,journal,protocol
    helpers=SimpleNamespace(scene=scene,observer=observer_api,pixels=pixels,geometry=geometry,journal=journal,protocol=protocol,keymap=masks)
    def parent_factory(until):return Parent(bounded,host,probe['client']['path'],output/('parent-'+str(time.time_ns())),until,parent_peer)
    driver=Driver(actor,bounded,host,endpoint,parent_factory,shell,helpers,{k:v for k,v in keymap['constants'].items() if k!='shiftMask'},output/'full-driver');driver.read_id=1
    report['driver']=driver.run();report['passed']=True;report['fullCampaignPassed']=False
    deadline=time.monotonic()+6;bounded.deadline=deadline;actor.close(deadline)
    # Normal Gtk exit is local evidence; native census independently precedes unload.
    report['normalShellTeardown']=shell.close(deadline)
    while remaining(deadline):
     clients=bounded.data('clients')
     if clients==[]:break
     time.sleep(min(.02,remaining(deadline)))
    check('actual-empty-native-census-before-unload',clients==[] and actor.record.get('normalExit') is True)
    check('observer-unload',session.ctl('plugin','unload',observer['binary']).strip()=='ok');observer_loaded=False
    check('authority-unload',session.ctl('plugin','unload',core['plugin']['path']).strip()=='ok');loaded=False
   finally:
    if actor and actor.process.poll() is None:actor.abort()
    if shell and shell.web and shell.web.poll() is None:shell.web.terminate();shell.web.wait(timeout=3)
    if loaded or observer_loaded:
     end=time.monotonic()+3
     try:
      while time.monotonic()<end:
       clients=session.data('clients')
       if clients==[]:break
       time.sleep(.02)
      assert clients==[],'never unload while native fixture/shell clients remain'
      if observer_loaded:session.ctl('plugin','unload',observer['binary'])
      if loaded:session.ctl('plugin','unload',core['plugin']['path'])
     except BaseException as error:report['failureCleanupError']=repr(error)
 except BaseException as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
 finally:
  if session:report['cleanup']=session.evidence;report['cleanupPassed']=cleanup_passed(session.evidence);report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('failureCleanupError')
  if output.exists():shutil.copytree(output,out/'native-evidence',symlinks=True)
  report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--profile',choices=['independent-groups','default-group'],required=True);args=parser.parse_args();raise SystemExit(0 if run(args.profile)['passed'] else 1)
