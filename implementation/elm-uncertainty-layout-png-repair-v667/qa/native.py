"""Root launches only, serial protected private native renderer campaign.
Actual640 Bar/Popup assets + compiled-root synthetic fixture presentations.
This does not authenticate proofs, run a real backend or establish native AT.
"""
import hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,traceback
from png_inspection import inspect_png
ROOT=pathlib.Path(__file__).resolve().parents[1];CORE=ROOT.parent/'elm-grant-retirement-runtime-v595'
spec=importlib.util.spec_from_file_location('layout_private_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);host.original.qa.require_qa_scope()
assert os.environ.get('ELM_LAYOUT_NATIVE_OUTPUT'),'Root must select a fresh native evidence directory outside frozen662'
OUT=pathlib.Path(os.environ['ELM_LAYOUT_NATIVE_OUTPUT']).absolute()
assert OUT.is_relative_to(ROOT.parent) and not OUT.is_relative_to(ROOT) and not OUT.exists()
OUT.mkdir(parents=True);RUNTIME=pathlib.Path('/home/hoskinson/window-integration-qa')/('elm-layout-662-'+str(time.time_ns()))
KEYS=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
report={'passed':False,'checks':[],'layoutFindings':[],'nativeAuthorityQualified':False,'ATCompliance':False,'mainDesktopActions':False,'scope':'Actual private WebKit renderer fixture; actual640 root presentations with synthetic transport/title; native keyboard and PNG capture; viewport widths within unchanged800x600output, not physical narrow-output acceptance.'}
def check(name,condition,**e):report['checks'].append({'name':name,'passed':bool(condition),**e});assert condition,name
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
session=None;apps=[]
try:
 manifest=json.loads((ROOT/'component-manifest.json').read_bytes())
 for relative,expected in manifest['files'].items():check('frozen_preparation_'+relative,digest(ROOT/relative)==expected['sha256'])
 report['preparationManifestSHA256']=digest(ROOT/'component-manifest.json')
 dependency=json.loads((ROOT/'qa/current-dependencies.json').read_bytes());check('dependency_report_hash',digest(dependency['report'])==dependency['sha256']);dependencies=json.loads(pathlib.Path(dependency['report']).read_bytes());check('dependency_preflight_passed',dependencies['passed'])
 for p,h in dependencies['dependencyPins'].items():check('held_dependency_'+p,digest(p)==h)
 pointer=json.loads((ROOT/'qa/current-preparation.json').read_bytes());check('preparation_report_hash',digest(pointer['report'])==pointer['sha256']);prep=json.loads(pathlib.Path(pointer['report']).read_bytes());check('preparation_passed',prep['passed'])
 for p,h in prep['sourcePins'].items():check('held_source_'+p,digest(p)==h)
 report['inputPins']={str(p):digest(p) for p in [pathlib.Path(__file__),ROOT/'qa/webkit_fixture.py',ROOT/'qa/png_inspection.py',KEYS,CORE/'candidate_host.py',pathlib.Path(pointer['report'])]}
 report['inputPins'].update(prep['sourcePins']);cases=json.loads(pathlib.Path(prep['cases']).read_bytes())
 with host.PrivateHyprSession(RUNTIME,dict(os.environ),800,600,LUA,mesa_vendor=True) as session:
  def wait(fn):
   deadline=time.monotonic()+6
   while time.monotonic()<deadline:
    session.guard();value=fn()
    if time.monotonic()>=deadline:raise RuntimeError('Original six-second observation deadline')
    if value:return value
    time.sleep(.04)
   raise RuntimeError('Original six-second observation deadline')
  for role in ['bar','popup']:
   control=RUNTIME/('control-'+role+'.json');shots=OUT/('pixels-'+role);shots.mkdir(mode=0o700)
   env=dict(session.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   app=session.host.launch('layout-'+role,['/usr/bin/python3','-B',str(ROOT/'qa/webkit_fixture.py'),prep['assets'],str(control),str(shots),role],env=env);apps.append(app)
   logpath=RUNTIME/('layout-'+role+'.log');log=lambda:logpath.read_text(errors='replace') if logpath.exists() else ''
   client=wait(lambda:next((w for w in session.data('clients') if w['title']=='ELM-LAYOUT-662-'+role),None));session.ctl('dispatch','setfloating','address:'+client['address']);session.ctl('dispatch','focuswindow','address:'+client['address']);wait(lambda:'fixture-loaded: '+role in log())
   serial=0
   def command(kind,**extra):
    global serial
    serial+=1;tmp=control.with_suffix('.new');tmp.write_text(json.dumps({'id':serial,'kind':kind,**extra}));tmp.chmod(0o600);os.replace(tmp,control);return serial
   def measure():
    identity=command('measure')
    def read():
     for line in log().splitlines():
      if line.startswith('layout-report: '):
       obj=json.loads(line.split(': ',1)[1])
       if obj['command']==identity:return obj['body']
     return None
    return wait(read)
   for width in [320,480,800]:
    command('resize',width=width);wait(lambda:measure()['width']==width)
    for case in cases:
     if role=='popup' and case['frame']['mode']=='closed':continue
     # Each case came from an independent actual root trace; reset the real
     # renderer to avoid inventing newer publications or bypassing freshness.
     ready_before=log().count('presentation-ready');command('reload');wait(lambda:log().count('presentation-ready')>ready_before)
     applied_before=log().count('presentation-applied');command('present',frame=case['frame']);wait(lambda:log().count('presentation-applied')>applied_before)
     body=measure();check(role+str(width)+case['name']+':actual_publication',body['publication']==case['frame']['publication'],dom=body)
     for b in body['buttons']:
      if b['detail'] and b['detail']['text']=='Awaiting native confirmation':
       finding={'role':role,'width':width,'case':case['name'],'identity':b['identity'],'detail':b['detail'],'disabled':b['disabled'],'accessibleName':b['ariaLabel'],'fullyVisible':b['detail']['visible']==b['detail']['total'],'accessibleUncertainty':'awaiting native confirmation' in b['ariaLabel'].lower()};report['layoutFindings'].append(finding)
     if role=='popup':
      for status in body['status']:
       report['layoutFindings'].append({'role':role,'width':width,'case':case['name'],'kind':'read-only-explanation','status':status,'fullyVisible':status['visible']==status['total']})
     shot=command('snapshot');wait(lambda:(shots/(str(shot)+'.png')).exists());png=shots/(str(shot)+'.png')
     picture=inspect_png(png)
     check(role+str(width)+case['name']+':actual_native_pixel_dimensions_and_rendered_colors',picture['width']==body['width'] and picture['height']==body['height'] and picture['distinctColors']>8,PNG=str(png),dimensions=[picture['width'],picture['height']],distinctColors=picture['distinctColors'])
     if role=='bar' and case['name']=='unknown':
      opener=next(b for b in body['buttons'] if b['identity']=='bar:applications');refresh=next(b for b in body['buttons'] if b['identity']=='bar:recovery-refresh');check('unknown_refresh_accessible_read_only_name',not refresh['disabled'] and 'without retrying actions' in refresh['ariaLabel'])
      command('focus',frame={'surfaceProtocol':2,'kind':'surface-focus','publication':case['frame']['publication'],'lease':case['frame']['lease'],'targets':[opener['id']]});wait(lambda:measure()['active']==opener['id'])
      p=subprocess.run([str(KEYS)],input='key 15 1\nkey 15 0\nsleep 100\nsync\n',capture_output=True,text=True,env=session.env,timeout=5);check('native_tab_normal_exit',p.returncode==0);wait(lambda:measure()['active']==refresh['id']);check('native_tab_skips_disabled_uncertain_target',True)
      before=len([l for l in log().splitlines() if l.startswith('fixture-native: ') and 'surface-action' in l]);p=subprocess.run([str(KEYS)],input='key 28 1\nkey 28 0\nsleep 100\nsync\n',capture_output=True,text=True,env=session.env,timeout=5);check('native_enter_normal_exit',p.returncode==0)
      actions=wait(lambda:[json.loads(l.split(': ',1)[1]) for l in log().splitlines() if l.startswith('fixture-native: ') and 'surface-action' in l] if len([l for l in log().splitlines() if l.startswith('fixture-native: ') and 'surface-action' in l])>before else None);check('native_enter_exact_read_only_renderer_action',len(actions)==before+1 and actions[-1]['id']=='bar:recovery-refresh' and actions[-1]['publication']==case['frame']['publication'])
   command('quit');wait(lambda:app.poll() is not None);check(role+':normal_fixture_exit',app.returncode==0);apps.remove(app)
  report['passed']=True
except BaseException:report['failure']=traceback.format_exc()
finally:
 for p in apps:
  if p.poll() is None:p.terminate()
 for p in apps:
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
 if session is not None:
  report['privateHost']=session.evidence
  report['cleanupPassed']=not session.evidence.get('cleanupErrors') and not session.evidence.get('unexpectedInnerDescendants') and not session.evidence.get('remainingDescendants') and session.evidence.get('runtimeGone')
  report['passed']=report['passed'] and bool(report['cleanupPassed'])
 if RUNTIME.exists():shutil.copytree(RUNTIME,OUT/'native-evidence',symlinks=True)
 report['nativeEvidence']=str(RUNTIME);report['layoutAcceptance']=False;report['nativeExecuted']=True
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
sys.exit(0 if report['passed'] else 1)
