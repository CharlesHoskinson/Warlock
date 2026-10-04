"""Actual private parent-seat -> AQ viewport -> child -> GTK recipient probe."""
import importlib.util,json,os,re,shutil,socket,struct,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
host=module('parent_input_host',ROOT/'candidate_host.py');host.original.qa.require_qa_scope()
inspection=module('parent_input_inspection',ROOT/'qa/fixture-inspection.py')
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-parent-input-'+str(time.time_ns()))
report={'passed':False,'mainDesktopActions':False,'scope':'Actual parent atomic capability burst -> AQ publications/device list -> GTK physical pair; exact merged geometry73 plus first-anchor V89 core with guarded V79 AQ; no installed changes or full release acceptance','checks':[]}
s=None;fixture=None;cover=None
LUA=b'hl.config({debug={disable_logs=false,enable_stdout_logs=true},xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
def check(name,value,**data):
 report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name
def wait(function):
 until=time.monotonic()+6
 while time.monotonic()<until:
  s.guard();value=function()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged six-second observation deadline')
def control(operation):
 tmp=controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':operation}));tmp.replace(controls)
try:
 desc=json.loads((ROOT/'parent-probe-build.json').read_text());buildPath=Path(desc['buildReport']);assert host.digest(buildPath)==desc['buildReportSHA256'];build=json.loads(buildPath.read_text());assert build['passed']
 for rel,sha in build['inputs'].items():assert host.digest(ROOT/rel)==sha,rel
 assert host.digest(build['client'])==build['clientSHA256'] and host.digest(build['module'])==build['moduleSHA256']
 report.update(buildReport=str(buildPath),buildReportSHA256=host.digest(buildPath),inputs={str(p):host.digest(p) for p in [Path(__file__),ROOT/'candidate_host.py',ROOT/'parent-probe-build.json',ROOT/'aq-tuple.json',ROOT/'native-build-report.json',ROOT/'fixture.py',ROOT/'qa/fixture-inspection.py']})
 shutil.copy2(__file__,OUT/'native.py')
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   core=json.loads((ROOT/'native-build-report.json').read_text())
   check('exactReviewedCoreMapped',s.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve()))==core['sha256'])
   maps=s.evidence['westonMaps']['files'];check('exactParentInputModuleMapped',maps.get(str(Path(build['module']).resolve()))==build['moduleSHA256'])
   parent=next(row for proc,row in s.host.processes if row['name']=='weston');assert host.original.same_process(parent)
   path=s.host.runtime/'weston-host';identity=host.original.socket_identity(path,s.host.runtime)
   with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(2);connection.connect(str(path));pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
   check('exactOwnedParentSocketPeer',pid==parent['pid'] and uid==os.getuid() and identity==host.original.socket_identity(path,s.host.runtime) and host.original.same_process(parent),pid=pid,uid=uid,start=parent['start'],socket=identity)
   controls=OUTPUT/'fixture-control.json';events=OUTPUT/'fixture-events.jsonl'
   fixture=s.host.launch('recipient',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(controls),str(events)],env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0'))
   def observed():return inspection.inspect(events,s.data('clients'))
   first=wait(observed);check('exactLaunchedFixturePID',first['pid']==fixture.pid);address=first['address'];report['fixtureIdentity']={'pid':first['pid'],'address':address,'title':first['title']}
   def inject(commands,expected=0):
    s.guard();assert host.original.same_process(parent) and identity==host.original.socket_identity(path,s.host.runtime)
    result=subprocess.run([build['client']],input=commands,text=True,capture_output=True,env=dict(s.host.env,ELM_PARENT_INPUT_QA='1'),cwd=s.host.runtime,timeout=5)
    messages=[json.loads(line) for line in result.stdout.splitlines()]
    check('parentClientNormalExit' if expected==0 else 'parentClientRejectedRequest',result.returncode==expected,commands=commands,messages=messages,stderr=result.stderr,exitCode=result.returncode)
    return messages
   initial=inject('motion 1 1\nquit\n')
   check('naturalInitialParentMotionAccepted',len(initial)==2 and initial[0].get('ready') is True and initial[1].get('accepted') is True)
   # Qualify the native publication log as an observable before using its count.
   inject('pointer-capability 0\nquit\n');wait(lambda:{'absent':True} if not s.data('devices')['mice'] else None)
   calibration=(OUTPUT/'hyprland.log').read_text(errors='replace')
   inject('pointer-capability 1\nquit\n');wait(lambda:s.data('devices')['mice'] if len(s.data('devices')['mice'])==1 else None)
   wait(lambda:'New aquamarine pointer with name wl_pointer' in (OUTPUT/'hyprland.log').read_text(errors='replace')[len(calibration):])
   check('publicationLogCalibratedOnActualNewDevice',True)
   report['capabilityBursts']=[]
   for index,(cycles,final) in enumerate([(3,0),(4,1),(16,1)]):
    label='burst-'+str(cycles)+'-final-'+str(final)
    check(label+':oneCurrentDeviceBeforeBurst',len(s.data('devices')['mice'])==1)
    before=wait(observed);wire_before=(OUTPUT/'hyprland.log').read_text(errors='replace')
    messages=inject(f'pointer-burst {cycles} {final}\nquit\n')
    check(label+':parentBurstAccepted',len(messages)==2 and messages[1]['accepted'] is True)
    def device_state():
     devices=s.data('devices')['mice']
     return {'devices':devices} if len(devices)==final else None
    devices=wait(device_state)
    until=time.monotonic()+.25
    while time.monotonic()<until:s.guard();time.sleep(.02)
    wire=(OUTPUT/'hyprland.log').read_text(errors='replace')[len(wire_before):]
    caps=re.findall(r'wl_seat[#@][0-9]+\.capabilities\(([0-9]+)\)',wire)
    publications=re.findall(r'New aquamarine pointer with name wl_pointer',wire)
    check(label+':allCapabilityTransitionsObserved',len(caps)>=2*cycles+(1-final),capabilities=caps)
    report['capabilityBursts'].append({'cycles':cycles,'final':final,'capabilities':caps,'publications':len(publications),'devices':devices,'wire':wire})
    check(label+':onlyCurrentDeviceAnnounced',len(publications)==final,announcements=len(publications),expected=final)
    after=wait(observed)
    check(label+':noInventedPhysicalButtons',after['counts']['button-press']==before['counts']['button-press'] and after['counts']['button-release']==before['counts']['button-release'])
    if not final:
     inject('pointer-capability 1\nquit\n');wait(lambda:s.data('devices')['mice'] if len(s.data('devices')['mice'])==1 else None)
    target=wait(observed);monitor=next(m for m in s.data('monitors') if m['name']=='WAYLAND-1');point=[target['size'][0]/2,target['size'][1]/2];px,py=(round(v) for v in inspection.parent_point(target,point,monitor,[800,600]))
    expected=[px*(monitor['width']/monitor['scale'])/800-target['at'][0]+monitor['x'],py*(monitor['height']/monitor['scale'])/600-target['at'][1]+monitor['y']]
    seq=target['sequence'];inject(f'motion {px} {py}\npress 272\nrelease 272\nquit\n')
    def delivered():
     latest=observed()
     return latest if latest and inspection.delivered_since(latest,seq,'button-release',expected,button=1) else None
    current=wait(delivered)
    presses=[e for e in inspection.delivered_since(current,seq,'button-press',button=1) if e['eventType']==4]
    releases=[e for e in inspection.delivered_since(current,seq,'button-release',button=1) if e['eventType']==7]
    check(label+':actualRecipientPhysicalPair',len(presses)==len(releases)==1 and all(abs(e['x']-expected[0])<1.1 and abs(e['y']-expected[1])<1.1 for e in presses+releases),press=presses,release=releases,expected=expected)
   control('quit');fixture.wait(timeout=5);check('recipientNormalExit',fixture.returncode==0);fixture=None
   for path,sha in report['inputs'].items():assert host.digest(path)==sha,path
   report['passed']=True
  finally:
   if cover is not None and cover.poll() is None:
    tmp=cover_controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':'quit'}));tmp.replace(cover_controls);cover.wait(timeout=5)
   if fixture is not None and fixture.poll() is None:control('quit');fixture.wait(timeout=5)
   registered={row['pid'] for proc,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
finally:
 if OUTPUT.exists():
  shutil.copytree(OUTPUT,OUT/'native-evidence',dirs_exist_ok=True)
 if s is not None:report['privateHost']=s.evidence;report['cleanupPassed']=bool(not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
 else:report['cleanupPassed']=False
 report['passed']=report['passed'] and report['cleanupPassed']
 report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
