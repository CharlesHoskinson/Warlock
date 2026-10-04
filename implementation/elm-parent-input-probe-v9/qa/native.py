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
report={'passed':False,'mainDesktopActions':False,'scope':'Parent-seat injection plus exact one GTK recipient coordinates for four unrotated single-output modes only; no cursor/pixel/multioutput/stale-callback/release acceptance','checks':[]}
s=None;fixture=None
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
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
   maps=s.evidence['westonMaps']['files'];check('exactParentInputModuleMapped',maps.get(str(Path(build['module']).resolve()))==build['moduleSHA256'])
   parent=next(row for proc,row in s.host.processes if row['name']=='weston');assert host.original.same_process(parent)
   path=s.host.runtime/'weston-host';identity=host.original.socket_identity(path,s.host.runtime)
   with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(2);connection.connect(str(path));pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
   check('exactOwnedParentSocketPeer',pid==parent['pid'] and uid==os.getuid() and identity==host.original.socket_identity(path,s.host.runtime) and host.original.same_process(parent),pid=pid,uid=uid,start=parent['start'],socket=identity)
   controls=OUTPUT/'fixture-control.json';events=OUTPUT/'fixture-events.jsonl'
   fixture=s.host.launch('recipient',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(controls),str(events)],env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0'))
   def observed():return inspection.inspect(events,s.data('clients'))
   first=wait(observed);address=first['address'];report['fixtureIdentity']={'pid':first['pid'],'address':address,'title':first['title']}
   def inject(commands,expected=0):
    s.guard();assert host.original.same_process(parent) and identity==host.original.socket_identity(path,s.host.runtime)
    result=subprocess.run([build['client']],input=commands,text=True,capture_output=True,env=dict(s.host.env,ELM_PARENT_INPUT_QA='1'),cwd=s.host.runtime,timeout=5)
    messages=[json.loads(line) for line in result.stdout.splitlines()]
    check('parentClientNormalExit' if expected==0 else 'parentClientRejectedRequest',result.returncode==expected,commands=commands,messages=messages,stderr=result.stderr)
    return messages
   modes=[(800,600,1),(640,480,1),(960,640,2),(800,600,1)]
   for index,(width,height,scale) in enumerate(modes):
    if index:
     receipt=s.ctl('eval',f'hl.monitor({{output="WAYLAND-1",mode="{width}x{height}@60",position="0x0",scale={scale},transform=0}})').strip();check('childModeChangeRequested',receipt=='ok',mode=[width,height,scale],receipt=receipt)
    monitor=wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['width']==width and m['height']==height and m['scale']==scale),None))
    current=wait(observed);check('sameActualRecipientAcrossModes',current['address']==address and current['pid']==first['pid'],mode=[width,height,scale],observed=current)
    # This is wire-level queued viewport evidence, not pixel presentation proof.
    wait(lambda:'set_destination(800, 600)' in (OUTPUT/'hyprland.log').read_text(errors='replace'))
    points=[(current['size'][0]/2,current['size'][1]/2),(24,24),(current['size'][0]-24,current['size'][1]-24)]
    for point in points:
     before=wait(observed);seq=before['sequence'];parentPoint=inspection.parent_point(before,point,monitor,[800,600]);px,py=(round(v) for v in parentPoint)
     # Expected logical recipient point accounts for integer parent-coordinate quantization.
     expected=[px*(width/scale)/800-before['at'][0]+monitor['x'],py*(height/scale)/600-before['at'][1]+monitor['y']]
     messages=inject(f'motion {px} {py}\npress 272\nrelease 272\nquit\n')
     check('threeParentRequestsAccepted',len(messages)==4 and messages[0].get('ready') is True and all(m.get('accepted') is True for m in messages[1:]),mode=[width,height,scale],parentPoint=[px,py])
     after=wait(lambda:observed() if observed() and inspection.delivered_since(observed(),seq,'button-release',expected,button=1) else None)
     presses=inspection.delivered_since(after,seq,'button-press',expected,button=1);releases=inspection.delivered_since(after,seq,'button-release',expected,button=1)
     check('actualGTKRecipientAndCoordinates',len(presses)==1 and len(releases)==1 and after['counts']['button-press']==before['counts']['button-press']+1 and after['counts']['button-release']==before['counts']['button-release']+1,mode=[width,height,scale],widgetPoint=point,parentPoint=[px,py],expected=expected,press=presses,release=releases)
   before=wait(observed);inject('motion -1 0\nquit\n',expected=6);after=wait(observed)
   check('rejectedParentMotionDoesNotDeliverButtons',after['counts']['button-press']==before['counts']['button-press'] and after['counts']['button-release']==before['counts']['button-release'],before=before['counts'],after=after['counts'])
   control('quit');fixture.wait(timeout=5);check('recipientNormalExit',fixture.returncode==0);fixture=None
   for path,sha in report['inputs'].items():assert host.digest(path)==sha,path
   report['passed']=True
  finally:
   if fixture is not None and fixture.poll() is None:control('quit');fixture.wait(timeout=5)
except Exception as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
finally:
 if OUTPUT.exists():
  shutil.copytree(OUTPUT,OUT/'native-evidence',dirs_exist_ok=True)
 if s is not None:report['privateHost']=s.evidence;report['cleanupPassed']=bool(s.evidence.get('cleanup',{}).get('passed'))
 else:report['cleanupPassed']=False
 report['passed']=report['passed'] and report['cleanupPassed']
 report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
