"""Root-owned serialized native authority proof; isolated compositor and GTK clients."""
import hashlib,importlib.util,json,os,socket,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
HOST=REPO/'implementation/maximized-stack-v2/candidate_host.py'
spec=importlib.util.spec_from_file_location('elm_authority_private_host',HOST);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(ROOT/'adapter'));from endpoint import Endpoint,Refused,start_time
host.original.qa.require_qa_scope()
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-authority-'+str(time.time_ns()))
report={'passed':False,'scope':'Read-only event-thread native window projection, peer/session checks and actual Elm replay; no effect, GPU or full scene-policy acceptance','mainDesktopActions':False,'output':str(OUTPUT),'checks':[]}
s=None;apps=[];loaded=False;operations=[];request_number=0;watermark='0'
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def record(name,passed,**evidence):
 report['checks'].append({'name':name,'passed':bool(passed),**evidence});assert passed,name
try:
 build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(ROOT/relative)==digest,relative
 for file,digest in build['dependencies'].items():assert host.digest(file)==digest,file
 plugin=build['binary'];assert host.digest(plugin)==build['binarySHA256'];assert host.digest(build['core']['path'])==build['core']['sha256']
 report['buildReport']=str(build_path);report['buildReportSHA256']=host.digest(build_path)
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   if s.ctl('plugin','load',plugin).strip()!='ok':raise RuntimeError('Owning authority plugin load failed')
   loaded=True
   row=next(row for proc,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':row['pid'],'expected_start':start_time(row['pid']),'binary_sha256':build['core']['sha256']}
   client=Endpoint(**config);hello=client.hello();report['handshake']=hello
   operations.append({'op':'attach','binding':hello['binding']})
   record('verified-peer-and-native-session',hello['compositor']['pid']==row['pid'] and hello['compositor']['instance']==config['instance'])
   record('no-effect-or-minimize-capability',hello['capabilities']=={'observe':True,'effects':False,'minimizedState':False})
   def snapshot():
    global request_number,watermark
    s.guard();request_number+=1
    if request_number>1:operations.append({'op':'refresh'})
    response=client.snapshot(str(request_number),watermark);watermark=response['sequence'];operations.append({'op':'observe','event':response});return response
   baseline=snapshot();again=snapshot()
   record('same-projection-stable-revision',baseline['windows']==again['windows'] and baseline['revision']==again['revision'] and int(again['sequence'])>int(baseline['sequence']))
   def refusal(name,payload):
    try:client.request(payload)
    except Refused as error:record(name,True,reason=str(error))
    else:record(name,False)
   payload={'protocolVersion':3,'kind':'snapshot-request','binding':client.bound,'requestId':'9007199254740993','minimumWatermark':watermark}
   refusal('wrong-native-lifetime-refused',{**payload,'binding':{**client.bound,'lifetime':'0'}})
   refusal('wrong-session-refused',{**payload,'binding':{**client.bound,'session':'1' if client.bound['session']!='1' else '2'}})
   refusal('wrong-frontend-refused',{**payload,'binding':{**client.bound,'frontend':'999'}})
   refusal('numeric-request-identity-refused',{**payload,'requestId':9007199254740993})
   refusal('unknown-action-refused',{'protocolVersion':3,'kind':'activate'})
   refusal('arbitrary-field-refused',{**payload,'path':'/etc/passwd'})
   try:Endpoint(**{**config,'binary_sha256':'0'*64})
   except Refused:record('wrong-owning-binary-refused',True)
   else:record('wrong-owning-binary-refused',False)
   with host.original.qa.owned_runtime() as fake_path:
    fake_runtime=Path(fake_path)
    (fake_runtime/'hypr').mkdir(mode=0o700);fake_parent=fake_runtime/'hypr'/config['instance'];fake_parent.mkdir(mode=0o700)
    fake_socket=fake_parent/'.socket.sock'
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as impostor:
     impostor.bind(str(fake_socket));impostor.listen(1)
     impostor_client=Endpoint(**{**config,'runtime':str(fake_runtime)})
     try:impostor_client.hello()
     except Refused as error:record('wrong-socket-peer-refused',str(error)=='Endpoint peer mismatch',reason=str(error))
     else:record('wrong-socket-peer-refused',False)
    fake_socket.unlink();fake_socket.symlink_to(client.path)
    try:Endpoint(**{**config,'runtime':str(fake_runtime)})
    except Refused as error:record('symlink-socket-refused',str(error)=='Unsafe endpoint socket',reason=str(error))
    else:record('symlink-socket-refused',False)
    fake_socket.unlink();fake_runtime.chmod(0o777)
    try:Endpoint(**{**config,'runtime':str(fake_runtime)})
    except Refused as error:record('unsafe-runtime-refused',str(error)=='Unsafe endpoint directory',reason=str(error))
    else:record('unsafe-runtime-refused',False)
    fake_runtime.chmod(0o700)
   borrowed=OUTPUT/'peer-config.json';borrowed.write_text(json.dumps({**config,'borrowed':client.bound}));borrowed.chmod(0o600)
   peer=s.host.launch('authority-peer',['/usr/bin/python3','-B',str(ROOT/'qa/peer_probe.py'),str(borrowed)],env=s.env);peer.wait(timeout=8)
   record('second-process-binding-isolation',peer.returncode==0,exitCode=peer.returncode,reply=(OUTPUT/'authority-peer.log').read_text())
   # Native JSON parser must reject duplicate fields before handshake mutation.
   before=client.bound.copy()
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as raw:
    raw.settimeout(2);raw.connect(str(client.path));pid,uid,_=struct.unpack('3i',raw.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==client.pid and uid==os.getuid()
    raw.sendall(b'j/elm_observe {"protocolVersion":3,"protocolVersion":3,"kind":"hello"}');raw.shutdown(socket.SHUT_WR)
    response=bytearray()
    while True:
     chunk=raw.recv(4096)
     if not chunk:break
     response.extend(chunk)
   duplicate=json.loads(response);record('duplicate-json-key-refused',duplicate.get('kind')=='refused',reply=duplicate)
   client.snapshot('9007199254740993',watermark)
   record('lossless-request-id-roundtrip',True)
   env=dict(s.env,GTK_A11Y='none',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   app=s.host.launch('authority-fixture',['/usr/bin/python3','-B',str(ROOT/'qa/fixture.py'),str(control)],env=env);apps.append(app)
   def wait_window(present):
    end=time.monotonic()+6
    while time.monotonic()<end:
     data=snapshot();fixture=[w for w in data['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE']
     if bool(fixture)==present:return data,fixture
     time.sleep(.04)
    raise RuntimeError('Native fixture observation deadline')
   opened_data,windows=wait_window(True);first=windows[0]['incarnation']
   record('actual-wayland-window-projected',windows[0]['minimized'] is None,incarnation=first)
   stable=snapshot();record('incarnation-stable-across-snapshots',next(w['incarnation'] for w in stable['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')==first)
   def control_(op):
    staging=control.with_suffix('.tmp');staging.write_text(json.dumps({'op':op}));staging.replace(control)
   control_('hide');hidden,_=wait_window(False);record('unmap-retires-projection',not any(w['incarnation']==first for w in hidden['windows']))
   control_('show');remapped,windows=wait_window(True);second=windows[0]['incarnation']
   record('remap-has-fresh-incarnation',int(second)>int(first),before=first,after=second)
   control_('quit');app.wait(timeout=5);record('fixture-normal-exit',app.returncode==0,exitCode=app.returncode)
   final,_=wait_window(False);record('closed-window-retires',not any(w['incarnation']==second for w in final['windows']))
   old_binding=client.bound.copy();operations.append({'op':'disconnect'})
   if s.ctl('plugin','unload',plugin).strip()!='ok':raise RuntimeError('Authority unload failed')
   loaded=False
   if s.ctl('plugin','load',plugin).strip()!='ok':raise RuntimeError('Authority reload failed')
   loaded=True
   refusal('reloaded-authority-refuses-old-binding',{**payload,'binding':old_binding})
   hello=client.hello();record('reload-rebinds-authority-lifetime',hello['binding']['lifetime']!=old_binding['lifetime'])
   operations.append({'op':'attach','binding':hello['binding']});request_number=0;watermark='0';snapshot()
   (OUT/'transcripts.json').write_text(json.dumps({'operations':operations},indent=2)+'\n')
   environment=dict(os.environ,ELM_REPLAY=str(build_path.parent/'replay.js'))
   replay=subprocess.run(['node',str(ROOT/'qa/native_replay.cjs'),str(OUT/'transcripts.json'),str(OUT/'elm-report.json')],env=environment,capture_output=True,text=True,timeout=15)
   (OUT/'elm.stdout').write_text(replay.stdout);(OUT/'elm.stderr').write_text(replay.stderr);record('actual-native-to-elm-replay',replay.returncode==0)
   if s.ctl('plugin','unload',plugin).strip()!='ok':raise RuntimeError('Final authority unload failed')
   loaded=False;record('plugin-unloaded-before-compositor',not s.data('plugin','list'))
   registered={row['pid'] for _,row in s.host.processes};auxiliary=[row for row in s.host.descendants() if row['pid'] not in registered]
   report['auxiliaryRetirement']=[{'identity':row,'scope':'Explicit SIGTERM/identity disappearance, not normal wait-status evidence'} for row in auxiliary]
   for row in reversed(auxiliary):s.host.stop(row)
   report['passed']=True
  finally:
   for proc in reversed(apps):
    if proc.poll() is None:
     try:
      owned=next(row for registered,row in s.host.processes if registered is proc)
      s.host.stop(owned,proc);proc.wait(timeout=5)
     except Exception as error:report.setdefault('nativeCleanupErrors',[]).append(repr(error))
   if loaded:
    try:
     s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
    except Exception as error:report.setdefault('nativeCleanupErrors',[]).append(repr(error))
   registered={row['pid'] for _,row in s.host.processes}
   for row in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):
    try:s.host.stop(row)
    except Exception as error:report.setdefault('nativeCleanupErrors',[]).append(repr(error))

except Exception as error:report['error']=repr(error)
report['privateHost']=s.evidence if s else None
if s:
 report['cleanupPassed']=not s.evidence.get('cleanupErrors') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone',False)
 report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('nativeCleanupErrors')
report['currentInputs']={str(p.relative_to(ROOT)):host.digest(p) for p in [ROOT/'native/authority.cpp',ROOT/'adapter/endpoint.py',ROOT/'qa/native.py',ROOT/'qa/fixture.py',ROOT/'qa/peer_probe.py',ROOT/'qa/native_replay.cjs']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'output':str(OUTPUT),'error':report.get('error')}));raise SystemExit(not report['passed'])
