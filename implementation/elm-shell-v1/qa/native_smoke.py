"""Root-owned serial isolated GTK/WebKit layer-surface smoke; no main routing."""
import datetime,hashlib,importlib.util,json,os,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
HOST=REPO/'implementation/maximized-stack-v2/candidate_host.py'
spec=importlib.util.spec_from_file_location('reviewed_elm_fixture_host',HOST);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
qa=host.original.qa;qa.require_qa_scope()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-fixture-host-'+str(time.time_ns()))
REPORT=ROOT/'qa'/('native-smoke-'+str(time.time_ns())+'.json')
result=dict(scope='Isolated Elm fixture rendering and read-only host transport; not native application effects, host selection, accessibility or GPU qualification',passed=False,mainDesktopActions=False,output=str(OUTPUT))
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
s=None;proc=None
try:
 build=json.loads((ROOT/'build/build-report.json').read_text());assert build['passed']
 for f,sha in build['files'].items():assert host.digest(ROOT/f)==sha,f
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  env=dict(s.env,GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',NO_AT_BRIDGE='1')
  use_layer='--xdg' not in sys.argv
  result['surfaceRole']='layer' if use_layer else 'xdg'
  command=[str(ROOT/'build/elm-host'),'--assets',str(ROOT/'assets'),'--qa-exit-after-render']+(['--layer'] if use_layer else [])
  proc=s.host.launch('elm-fixture',command,env=env)
  started=time.monotonic();deadline=started+18;layers=None;render=None;diagnostic=False
  while time.monotonic()<deadline:
   s.guard()
   log=(OUTPUT/'elm-fixture.log').read_text(errors='replace')
   if not diagnostic and time.monotonic()-started>3 and proc.poll() is None:
    diagnostic=True
    grab=subprocess.run(['grim',str(OUTPUT/'diagnostic.png')],env=s.env,capture_output=True,text=True,timeout=5)
    result['diagnosticCaptureExit']=grab.returncode
    result['diagnosticLayers']=s.data('layers')
    result['diagnosticClients']=s.data('clients')
   if 'render-report: ' in log:
    render=json.loads(next(line.split('render-report: ',1)[1] for line in log.splitlines() if line.startswith('render-report: ')))
    layers=s.data('layers')
    if use_layer and 'elm-shell-fixture-v1' not in json.dumps(layers):raise RuntimeError('Fixture layer was not mapped')
    image=OUTPUT/'elm-fixture.png'
    capture=subprocess.run(['grim',str(image)],env=s.env,capture_output=True,text=True,timeout=5)
    if capture.returncode:raise RuntimeError('private capture failed: '+capture.stderr)
    result['image']=dict(path=str(image),sha256=host.digest(image),bytes=image.stat().st_size)
    break
   if proc.poll() is not None:raise RuntimeError('Host exited before render report: '+log[-3000:])
   time.sleep(.03)
  if render is None:raise RuntimeError('Host smoke deadline')
  proc.wait(timeout=8)
  assert proc.returncode==0,proc.returncode
  result['renderReport']=render;result['layers']=layers;result['hostExitCode']=proc.returncode
  final=(OUTPUT/'elm-fixture.log').read_text()
  assert 'sandbox=1' in final and 'host-exit: failure=0 rendered=1' in final
  assert render['body']['families']==2 and render['body']['actionsDisabled']
  result['declaredSandboxEnabled']=True;result['hardwareRenderingQualified']=False
  # Retire remaining owned engine/private-bus auxiliaries BEFORE compositor teardown.
  registered={row['pid'] for _,row in s.host.processes}
  auxiliaries=[row for row in s.host.descendants() if row['pid'] not in registered]
  result['auxiliaryRetirement']=[dict(identity=row,scope='explicit SIGTERM/identity disappearance; not a wait-status normal-exit proof') for row in auxiliaries]
  for row in reversed(auxiliaries):s.host.stop(row)
  result['passed']=True
except Exception as e:result['error']=repr(e);result['passed']=False
result['privateHost']=s.evidence if s else None
if s:
 result['cleanupPassed']=not s.evidence.get('cleanupErrors') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone',False)
 result['passed']=result['passed'] and result['cleanupPassed']
result['filesSHA256']={str(p):host.digest(p) for p in [HOST,ROOT/'build/elm-host',ROOT/'build/build-report.json',ROOT/'assets/elm.js',Path(__file__)]}
REPORT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],report=str(REPORT),output=str(OUTPUT),error=result.get('error'))));raise SystemExit(not result['passed'])
