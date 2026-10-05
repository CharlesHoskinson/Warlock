"""Root-only actual picker/grab diagnostic. Import is inert; no eligibility grant."""
import json,os,pathlib,sys,time,subprocess,shutil,traceback,resource
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'qa'),str(ROOT/'qa/helpers')]
from preflight import verify,load,sha,packet,checked_guard
from actor import Actor,remaining
from owned_bus_host import derivative
from bounded import BoundedSession
from cleanup import cleanup_passed
import stamp,join,target,scene,observer as role_observer,map_failure,host_guard
from budget_timing import BudgetTiming
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'

def wait(session,fn,deadline):
 while remaining(deadline):
  session.guard();v=fn();remaining(deadline)
  if v:return v
  time.sleep(min(.02,remaining(deadline)))
def log(path):
 if not path.exists():return ''
 if path.stat().st_size>16*1024*1024:raise join.Refused('host log bound')
 return path.read_text(encoding='utf8',errors='strict')
def packets(path,prefix):
 return [json.loads(line[len(prefix):],object_pairs_hook=join.pairs,parse_constant=join.constant) for line in log(path).split('\n')[:-1] if line.startswith(prefix)]
def effects(path):return [p for p in packets(path,'frontend-request: ') if p.get('kind')=='window-effect']
def point(path,deadline):
 # Exact current inspection identity, never a guessed DOM prefix.
 import selector
 value=selector.select(log(path));remaining(deadline);return value

def checked_parent(guard,guard_files):
 # Native entry is source-executed; never ordinarily import the new wrapper.
 import hashlib,importlib.util,stdlib_origin
 path=ROOT/'qa/parent_loader.py';raw=stdlib_origin.read(path)
 if hashlib.sha256(raw).hexdigest()!='54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e':raise ValueError('parent wrapper source changed')
 expected=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
 cache=pathlib.Path(importlib.util.cache_from_source(str(path)));files={str(path):'54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e'}
 if cache.exists() or cache.is_symlink():
  cached=stdlib_origin.read(cache);stdlib_origin.cache_code(cached,expected);files[str(cache)]=hashlib.sha256(cached).hexdigest()
 spec=importlib.util.spec_from_file_location('verified_parent_wrapper391',path);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;exec(expected,module.__dict__)
 previous=stdlib_origin.CRITICAL;stdlib_origin.CRITICAL={**previous,module.__name__:('checked_parent','QualifiedParent','qualify_module','verified')}
 try:stdlib_origin.loaded_code(module,expected,path,cache,raw)
 finally:stdlib_origin.CRITICAL=previous
 qualified,dependencies=module.checked_parent(guard,guard_files,wrapper=(module,raw,path));files.update(dependencies)
 return qualified,files

def parent_collect(qualified,guard,*,pid,start,pgid,deadline):
 # Validate from the source-executed entry before any wrapper-owned method.
 import hashlib,importlib.util,stdlib_origin
 remaining(deadline)
 wrapper,wrapper_raw,wrapper_path=qualified.wrapper
 if wrapper_path!=ROOT/'qa/parent_loader.py' or type(wrapper_raw) is not bytes or hashlib.sha256(wrapper_raw).hexdigest()!='54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e':raise ValueError('external parent wrapper origin')
 def validate(module,raw,path,digest,critical):
  if type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('external parent code buffer')
  expected=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
  previous=stdlib_origin.CRITICAL;stdlib_origin.CRITICAL={**previous,module.__name__:critical}
  try:stdlib_origin.loaded_code(module,expected,path,pathlib.Path(importlib.util.cache_from_source(str(path))),raw)
  finally:stdlib_origin.CRITICAL=previous
 validate(wrapper,wrapper_raw,wrapper_path,'54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e',('checked_parent','QualifiedParent','qualify_module','verified'))
 if type(qualified) is not wrapper.QualifiedParent or qualified.guard is not guard or 'collect' in qualified.__dict__ or 'qualify' in qualified.__dict__:raise ValueError('external parent instance binding')
 if qualified.path!=ROOT.parent/'elm-own-popup-parent-map-parallel-v382/parent_maps.py' or qualified.guard_path!=ROOT.parent/'elm-own-popup-runtime-index-guard-v364/guard.py':raise ValueError('external parent dependency path')
 validate(qualified.module,qualified.raw,qualified.path,'ae370586e5957100e13d1b940f8bc59c8f52fc6864b8721b833429719572f6e9',('collect','_parallel_rows','Refused'))
 validate(guard,qualified.guard_raw,qualified.guard_path,'785a2c3b1717e949ed5628eb7048479c6c8897560be55b50117f098625bb71a9',('fingerprint','process_identity','parse_maps','map_identity','read_text_bounded','remaining','_MountInfo','Refused','UncertainWorkers'))
 remaining(deadline)
 return wrapper.QualifiedParent.collect(qualified,pid=pid,start=start,pgid=pgid,deadline=deadline)

def run():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=ROOT/'qa'/('native-'+str(time.time_ns()));out.mkdir();output=pathlib.Path('/home/hoskinson/window-integration-qa')/('own-popup-'+str(time.time_ns()))
 r={'passed':False,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'fullGTKCampaignPassed':False,'scope':'actual picker whole-grab/map/close/fresh-observation diagnostic only','checks':[]};session=None;actor=None;web=None;loaded=[]
 timing=BudgetTiming(r)
 original_wait=globals()['wait']
 def wait(session,fn,deadline):return timing.call('wait:'+timing.label(fn),deadline,lambda:original_wait(session,fn,deadline))
 def check(name,value,**evidence):r['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
 try:
  host,core,observer,fixture,host_binary,build,files=timing.call('preflight',None,verify);r['inputs']=files
  guard,guard_files=timing.call('guardQualification',None,checked_guard);r['inputs'].update(guard_files)
  parent_collector,parent_files=timing.call('parentCollectorQualification',None,lambda:checked_parent(guard,guard_files));r['inputs'].update(parent_files)
  initial_deadline=time.monotonic()+6;tuple_evidence=timing.call('initialTuple',initial_deadline,lambda:guard.verify_tuple(deadline=initial_deadline));r['runtimeClosure']=tuple_evidence
  with timing.context('privateSession',None,derivative(host)(output,dict(os.environ),800,600,LUA,mesa_vendor=True)) as session:
   try:
    owned=next(row for _,row in session.host.processes if row['name']=='hyprland');r['nativeOwner']=owned
    def process_guard(deadline):
     try:return timing.call('fullProcessGuard',deadline,lambda:guard.verify_process(pid=owned['pid'],start=int(owned['start']),tuple_evidence=tuple_evidence,deadline=deadline))
     except BaseException as failure:
      r['mapGuardRefusal']=repr(failure)
      try:r['sameReadMapFailure']=map_failure.archive(failure,out/'map-failure',pid=owned['pid'],start=owned['start'])
      except BaseException as archive_error:r['mapFailureArchiveError']=repr(archive_error)
      raise
    check('load-exact-authority',session.ctl('plugin','load',core['plugin']['path']).strip()=='ok');loaded.append(core['plugin']['path'])
    check('load-exact-observer',session.ctl('plugin','load',observer['binary']).strip()=='ok');loaded.append(observer['binary'])
    boot=time.monotonic()+6;bounded=BoundedSession(session,output/'ipc',boot)
    r['processMaps']=process_guard(boot)
    def query(call):
     # The same kernel instance and exact tuple bracket every observer read.
     before=process_guard(bounded.deadline)
     value=timing.call('queryCallback:'+timing.label(call),bounded.deadline,call)
     after=process_guard(bounded.deadline)
     remaining(bounded.deadline);r.setdefault('queryMapGuards',[]).append({'before':before,'after':after});return value
    # Actual parent proof is inherited247 module with exact private host and maps.
    parent=next(row for _,row in session.host.processes if row['name']=='weston');probe=json.loads((ROOT/'runtime/parent-probe-build.json').read_text())
    def parent_map():
     try:return timing.call('privateParentMap',boot,lambda:parent_collect(parent_collector,guard,pid=parent['pid'],start=int(parent['start']),pgid=int(parent['pgid']),deadline=boot))
     except BaseException as failure:
      r['parentMapGuardRefusal']=repr(failure)
      try:r['sameReadParentMapFailure']=map_failure.archive(failure,out/'parent-map-failure',pid=parent['pid'],start=parent['start'])
      except BaseException as archive_error:r['parentMapFailureArchiveError']=repr(archive_error)
      raise
    pm=parent_map()
    check('actual-private-parent-module-map',pm['files'].get(str(pathlib.Path(probe['module']['path']).resolve()))==probe['module']['sha256'])
    actor=timing.call('GTKLaunch',boot,lambda:Actor(bounded,host,fixture['artifact']['path'],output/'gtk',boot));timing.call('GTKCreateOwners',boot,lambda:actor.send('create-owners',boot));timing.call('GTKInspect',boot,lambda:actor.send('inspect',boot))
    wait(bounded,lambda:[c for c in bounded.data('clients') if c['pid']==actor.pid] if len([c for c in bounded.data('clients') if c['pid']==actor.pid])==2 else None,boot)
    native_before=bounded.data('clients');rows_before=actor.read();r['targetBefore']={'clients':native_before,'journal':rows_before}
    config={'runtime':str(session.host.runtime),'instance':session.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':owned['pid'],'expected_start':str(owned['start']),'binary_sha256':core['sha256']}
    config_path=output/'authority.json';fd=os.open(config_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(config,f)
    web=timing.call('WebHostLaunch',boot,lambda:session.host.launch('elm-webview',[str(host_binary),'--assets',str(build/'inputs/assets'),'--backend',str(build/'inputs/adapter/daemon.py'),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(session.env,WAYLAND_DEBUG='client')))
    host_log=output/'elm-webview.log';p=wait(bounded,lambda:point(host_log,boot),boot)
    host_identity=host.original.process(web.pid)
    actual_exe=pathlib.Path('/proc',str(web.pid),'exe');expected_stat=host_binary.stat();exe_stat=actual_exe.stat()
    check('actual-owned-host-executable-inode',sha(actual_exe)==sha(host_binary) and (exe_stat.st_dev,exe_stat.st_ino)==(expected_stat.st_dev,expected_stat.st_ino) and host.original.same_process(host_identity),identity=host_identity)
    host_report_path=ROOT.parent/'elm-own-popup-host-surface-stamp-v310/qa/build-1791153652664233159/report.json';host_report=packet(host_report_path,files[str(host_report_path)])
    host_maps=timing.call('hostRuntimeGuard',boot,lambda:host_guard.verify(guard,binary=host_binary,report=host_report,pid=web.pid,start=int(host_identity['start']),deadline=boot,directory=out/'host-map-failure',diagnostics=r))
    check('actual-stamped-host-and-library-maps',host_maps['requiredArtifacts']==[str(host_binary)] and host_maps['mappedLibraryCount']==len(host_report['linkedLibraries']),maps=host_maps,identity=host_identity)
    # A separate read-only observer keeps its exact peer binding; no effect API is called.
    sys.path.insert(0,str(build/'inputs/adapter'));endpoint_class=load('diagnostic_observer_budget',ROOT/'qa/ancestor-observer_endpoint.py').ObserverEndpoint
    endpoint=endpoint_class(**config);endpoint.parentDeadline=boot;hello=query(endpoint.hello);query(lambda:endpoint.geometry_attach('1'))
    snapshot=query(lambda:endpoint.snapshot('2'));r['prePopupFacts']={'legacy':query(lambda:endpoint.scene_facts('3')),'geometry':query(lambda:endpoint.geometry_facts('4'))}
    def target_records(snapshot,facts,deadline):
     actor.send('inspect',deadline)
     result={}
     roles=role_observer.roles(json.loads(query(lambda:bounded.ctl('elm_role_state'))),compositor_pid=owned['pid'])
     for name in ('A','C'):
      bound=wait(bounded,lambda:query(lambda:scene.bind(actor,bounded,name,require_landmark=False)),deadline)
      native_role=role_observer.selected(roles,address=bound['native']['address'],pid=actor.pid,parent_address='0x0',modal=False)
      joined=target.join_target(bound,snapshot,facts,pid=actor.pid,binding=hello['binding']);joined['nativeRole']=native_role;result[name]=joined
     return result
    r['targetsBefore']=target_records(snapshot,r['prePopupFacts']['legacy'],boot)
    baseline=effects(host_log);check('no-bootstrap-native-effect',baseline==[]);shell=load('ancestor_diagnostic_shell',ROOT/'qa/ancestor-shell.py').Shell(bounded,host,build,config_path,output,None);shell.web=web
    # One six-second budget covers the actual gesture, whole-grab join, close and fresh facts.
    deadline=time.monotonic()+6;bounded.deadline=deadline;endpoint.parentDeadline=deadline
    r['stage']={'deadline':deadline,'seconds':6}
    process_guard(deadline)
    shell.pointer({'point':p,'visible':True},272,deadline)
    mapped_raw=wait(bounded,lambda:next((line[len('host-popup-native: '):].encode() for line in reversed(log(host_log).split('\n')[:-1]) if line.startswith('host-popup-native: ') and 'host-popup-mapped' in line),None),deadline)
    attached=[a for a in packets(host_log,'backend-frame: ') if a.get('kind')=='attached'][-1];web_identity=host.original.process(web.pid)
    mapped=stamp.parse(mapped_raw,pid=web.pid,start=web_identity['start'],binding=attached['binding']);r['mappedStamp']=mapped
    inspection=wait(bounded,lambda:next((i for i in reversed(packets(host_log,'surface-inspection: ')) if i['publication']==mapped['publication'] and i['lease']==mapped['lease']),None),deadline)
    check('actual-host-current-publication-lease',inspection['publication']==mapped['publication'] and inspection['lease']==mapped['lease'],inspection=inspection)
    before_raw=query(lambda:bounded.ctl('elm_xdg_grab_join')).encode();(out/'grab-mapped.json').write_bytes(before_raw)
    native_snapshot=join.parse(before_raw,core_pid=owned['pid']);matched=join.match_layer_popup(native_snapshot,host_pid=web.pid,host_uid=os.getuid(),popup_id=mapped['popupSurface'],root_id=mapped['rootSurface']);r['wholeGrab']=matched
    r['duringPopupFacts']={'legacy':query(lambda:endpoint.scene_facts('5')),'geometry':query(lambda:endpoint.geometry_facts('6'))}
    check('diagnostic-only-no-policy-grant',matched['authenticated'] is False and matched['ownBlockerGrantQualified'] is False)
    shell.keys('key 1 1\nkey 1 0\n',deadline)
    closed_raw=wait(bounded,lambda:next((line[len('host-popup-native: '):].encode() for line in reversed(log(host_log).split('\n')[:-1]) if line.startswith('host-popup-native: ') and 'host-popup-sync-complete' in line),None),deadline)
    closed=stamp.parse(closed_raw,pid=web.pid,start=web_identity['start'],binding=attached['binding'],previous=int(mapped['sequence']));check('exact-map-retired-after-actual-display-sync',stamp.retired(mapped,closed),stamp=closed)
    after_raw=query(lambda:bounded.ctl('elm_xdg_grab_join')).encode();(out/'grab-closed.json').write_bytes(after_raw);after=join.parse(after_raw,core_pid=owned['pid'],previous_sequence=native_snapshot.sequence)
    check('actual-popup-and-grab-retired',not after.grab and not after.xdg and not any(p.surface.id==mapped['popupSurface'] and p.surface.pid==web.pid for p in after.popups))
    r['freshAfterClose']={'legacy':query(lambda:endpoint.scene_facts('7')),'geometry':query(lambda:endpoint.geometry_facts('8'))};remaining(deadline)
    fresh_snapshot=query(lambda:endpoint.snapshot('9'));r['targetsAfter']=target_records(fresh_snapshot,r['freshAfterClose']['legacy'],deadline)
    check('actual-GTK-resource-ACK-native-incarnation-identity-retained',all(target.same(r['targetsBefore'][name],r['targetsAfter'][name]) for name in ('A','C')),before=r['targetsBefore'],after=r['targetsAfter'])
    before_scene=r['prePopupFacts']['legacy']['facts']['windows'];after_scene=r['freshAfterClose']['legacy']['facts']['windows']
    check('original-native-incarnations-and-family-owners-retained',sorted((w['incarnation'],w['owner'],w['application']) for w in before_scene)==sorted((w['incarnation'],w['owner'],w['application']) for w in after_scene))
    check('no-native-effect-issued',effects(host_log)==baseline,effectJournal=baseline)
    current=bounded.data('clients');before_ids={(x['pid'],x['address']) for x in native_before if x['pid']==actor.pid};check('actual-target-native-identities-retained',before_ids=={(x['pid'],x['address']) for x in current if x['pid']==actor.pid})
    remaining(deadline);r['stage']['completed']=time.monotonic()
    end=time.monotonic()+6;bounded.deadline=end;actor.close(end);web.terminate();web.wait(timeout=min(3,remaining(end)));remaining(end);check('normal-web-host-exit',web.returncode==0)
    check('direct-broker-normal-EOF-waited-exit', 'backend-exit: waited=1 normal=1 code=0' in log(host_log).split('\n')[:-1])
    wait(bounded,lambda:bounded.data('clients')==[],end);check('empty-native-client-census-before-unload',True)
    for path in reversed(loaded):check('normal-plugin-unload',bounded.ctl('plugin','unload',path).strip()=='ok')
    loaded=[];r['passed']=True
   finally:
    if actor is not None and actor.process.poll() is None:actor.abort()
    if web is not None and web.poll() is None:web.terminate();web.wait(timeout=3)
    if loaded:
     try:
      end=time.monotonic()+3
      while time.monotonic()<end and session.data('clients')!=[]:time.sleep(.02)
      assert session.data('clients')==[]
      for path in reversed(loaded):session.ctl('plugin','unload',path)
     except BaseException as e:r['failureCleanupError']=repr(e)
 except BaseException as e:
  r.update(passed=False,error=repr(e),traceback=traceback.format_exc())
  try:
   owner=r.get('nativeOwner',{})
   if 'sameReadMapFailure' not in r and 'mapFailureArchiveError' not in r and 'hostMapGuardRefusal' not in r and 'parentMapGuardRefusal' not in r:r['sameReadMapFailure']=map_failure.archive(e,out/'map-failure',pid=owner.get('pid'),start=owner.get('start'))
  except BaseException as archive_error:r['mapFailureArchiveError']=repr(archive_error)
 finally:
  if session:r['cleanup']=session.evidence;r['cleanupPassed']=cleanup_passed(session.evidence);r['passed']=r['passed'] and r['cleanupPassed'] and not r.get('failureCleanupError')
  if output.exists():shutil.copytree(output,out/'native-evidence',symlinks=True)
  r['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(out/'report.json')
 return r
if __name__=='__main__':raise SystemExit(not run()['passed'])
