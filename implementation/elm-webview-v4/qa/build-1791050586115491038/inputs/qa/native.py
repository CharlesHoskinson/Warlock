"""Serialized real window-to-Elm DOM and graphics observation; no live desktop routing."""
import hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
HOST=REPO/'implementation/maximized-stack-v2/candidate_host.py';spec=importlib.util.spec_from_file_location('elm_webview_private_host',HOST);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-native-webview-'+str(time.time_ns()))
report={'passed':False,'mainDesktopActions':False,'scope':'Actual read-only native projection in Elm DOM, retained screenshot and observed graphics backend; no full GPU/IME/AT/layering or application-effect qualification','output':str(OUTPUT)}
apps=[];s=None;plugin=None;loaded=False
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
try:
 build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(ROOT/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 authority=REPO/'implementation/elm-authority-v3';pair=json.loads((authority/'qa/slice-manifest.json').read_text())['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 report['buildReport']=str(build_path);report['buildReportSHA256']=host.digest(build_path);report['authorityPair']=pair
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   sys.path.insert(0,str(ROOT/'adapter'));from endpoint import start_time
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   fixture=s.host.launch('native-fixture',['/usr/bin/python3','-B',str(authority/'qa/fixture.py'),str(OUTPUT/'fixture-control.json')],env=env);apps.append(fixture)
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(ROOT/'adapter/daemon.py'),'--authority-config',str(config_path),'--layer','--qa-exit-after-render'],env=env);apps.append(web)
   deadline=time.monotonic()+20;render=None
   while time.monotonic()<deadline:
    s.guard();text=(OUTPUT/'elm-webview.log').read_text(errors='replace')
    if 'render-report: ' in text:
     render=json.loads(next(line.split('render-report: ',1)[1] for line in text.splitlines() if line.startswith('render-report: ')));break
    if web.poll() is not None:raise RuntimeError('Webview exited before render report: '+text[-2500:])
    time.sleep(.04)
   assert render is not None,'Native DOM deadline'
   report['renderReport']=render;assert render['body']['fixturePresent'] and render['body']['actionsDisabled'] and render['body']['secureContext']
   screenshot=OUTPUT/'elm-native.png';p=subprocess.run(['grim',str(screenshot)],env=s.env,capture_output=True,text=True,timeout=5);assert p.returncode==0,p.stderr
   report['screenshot']={'path':str(screenshot),'sha256':host.digest(screenshot)}
   pixel=subprocess.check_output(['magick',str(screenshot),'-format','%[pixel:p{790,410}]','info:'],text=True,timeout=5).strip();report['canvasPresentedPixel']=pixel
   gpu=render['body']['gpu'];report['webgpuExposed']=gpu['webgpuExposed']
   report['webglReadbackPassed']=gpu.get('pixel')==[0,255,255,255] and gpu.get('error')==0
   renderer=gpu.get('renderer','').lower();report['hardwareWebGLObserved']=report['webglReadbackPassed'] and any(tag in renderer for tag in ['intel','nvidia','radeon','amd']) and not any(tag in renderer for tag in ['llvmpipe','softpipe','swiftshader','software'])
   descendants=s.host.descendants();graphics=[]
   for row in descendants:
    pid=row['pid']
    try:
     command=Path('/proc',str(pid),'comm').read_text().strip()
     if 'WebKit' not in command:continue
     maps=Path('/proc',str(pid),'maps').read_text();(OUT/('process-'+str(pid)+'.maps')).write_text(maps)
     nodes=[]
     for fd in Path('/proc',str(pid),'fd').iterdir():
      try:
       target=str(fd.readlink())
       if target.startswith('/dev/dri/') or target.startswith('/dev/nvidia'):nodes.append(target)
      except OSError:pass
     graphics.append({'identity':row,'command':command,'graphicsDevices':sorted(set(nodes)),'hardwareDriverMapped':any(x in maps for x in ['iris_dri.so','radeonsi_dri.so','libnvidia-eglcore'])})
    except (OSError,PermissionError) as error:graphics.append({'identity':row,'observationError':type(error).__name__})
   report['graphicsProcesses']=graphics
   web.wait(timeout=8);log=(OUTPUT/'elm-webview.log').read_text();assert web.returncode==0,log[-2000:]
   assert 'backend-exit: waited=1 normal=1 code=0' in log;report['normalHostAndBackendExit']=True
   # Separate engine diagnostic view; never navigate the application view away.
   diagnostic=s.host.launch('webkit-gpu-info',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--gpu-info','--qa-exit-after-render'],env=env);apps.append(diagnostic)
   diagnostic.wait(timeout=20);report['gpuInfoExitCode']=diagnostic.returncode;report['gpuInfoLog']=str(OUTPUT/'webkit-gpu-info.log')
   assert diagnostic.returncode==0,(OUTPUT/'webkit-gpu-info.log').read_text()[-1000:]
   report['passed']=True
  finally:
   for proc in reversed(apps):
    if proc.poll() is None:
     owned=next(row for registered,row in s.host.processes if registered is proc);s.host.stop(owned,proc);proc.wait(timeout=5)
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   report['auxiliaryRetirement']=[]
   for row in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):
    report['auxiliaryRetirement'].append({'identity':row,'scope':'SIGTERM/disappearance; not a normal wait-status claim'});s.host.stop(row)
except Exception as error:report['error']=repr(error)
report['privateHost']=s.evidence if s else None
if s:
 report['cleanupPassed']=not s.evidence.get('cleanupErrors') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone',False);report['passed']=report['passed'] and report['cleanupPassed']
report['inputs']={str(p.relative_to(ROOT)):host.digest(p) for p in [ROOT/'qa/native.py',ROOT/'adapter/daemon.py',ROOT/'adapter/endpoint.py',ROOT/'native/host.c',ROOT/'src/Main.elm',ROOT/'assets/adapter.js']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'output':str(OUTPUT),'error':report.get('error')}));raise SystemExit(not report['passed'])
