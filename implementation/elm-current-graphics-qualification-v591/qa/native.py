"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-keyboardless-current-runtime-v216';GUI=ROOT
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False,'performanceAcceptance':False,'webgpuHardwareQualified':False,'fullJourneyAcceptance':False};apps=[];s=None;loaded=False
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,value,**evidence):
 report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged observation deadline')
try:
 binding=json.loads((ROOT/'qa/runner-binding.json').read_text());build_path=Path(binding['buildReport']);assert host.digest(build_path)==binding['buildReportSHA256'];preflight=json.loads((ROOT/'qa/preflight.json').read_text());assert preflight['passed'];
 for path,digest in preflight['inputs'].items():assert host.digest(Path(path))==digest;build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(GUI/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/grab_guard.py',POINTER,FIXTURE,CORE/'candidate_host.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(build_path.parent/'inputs/adapter/daemon.py'),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client'));apps.append(web)
   def frames(prefix):
    return [json.loads(line[len(prefix):]) for line in (OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines() if line.startswith(prefix)]
   def gpu_observation(identity='1'):
    prefix='gpu-probe: id='+identity+' '
    values=[json.loads(line[len(prefix):])['body'] for line in (OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines() if line.startswith(prefix)]
    return values[-1] if values else None
   gpu=wait(gpu_observation);report['gpu']=gpu
   check('sharedBarExecutesWebGLShaderReadback',gpu['webgl'].get('error')==0 and all(abs(actual-expected)<=1 for actual,expected in zip(gpu['webgl']['pixel'],[17,193,71,255])) and len(gpu['webgl']['pixel'])==4,probe=gpu)
   renderer=gpu['webgl'].get('unmaskedRenderer') or ''
   check('sharedBarReportsRendererIdentity',bool(renderer) and not any(name in renderer.lower() for name in ['llvmpipe','softpipe','swiftshader','software','swrast']),renderer=renderer,vendor=gpu['webgl'].get('unmaskedVendor'))
   diagnostics=wait(lambda:frames('native-gpu-info: '));report['nativeGPU']=diagnostics[-1]
   native_gpu=diagnostics[-1]['text']
   check('nativeEngineReportsHardwareRenderer',('Intel' in native_gpu or 'NVIDIA' in native_gpu) and not any(name in native_gpu.lower() for name in ['llvmpipe','softpipe','swiftshader']),diagnostic=native_gpu)
   check('probeRetiresShaderObjects',gpu['shaderResourcesRetired'])
   gpu_png=OUTPUT/'elm-shared-gpu.png';subprocess.run(['grim',str(gpu_png)],env=s.env,check=True,timeout=5)
   canvas=gpu['canvas'];point=(round(canvas['x']+canvas['width']/2),round(canvas['y']+canvas['height']/2))
   converter=Path('/usr/bin/magick');report['inputs'][str(converter)]=host.digest(converter)
   sampled=subprocess.run([str(converter),str(gpu_png),'-crop',f'1x1+{point[0]}+{point[1]}','-depth','8','rgb:-'],capture_output=True,timeout=5)
   assert sampled.returncode==0 and len(sampled.stdout)==3,sampled.stderr
   pixel=list(sampled.stdout)
   check('shaderPixelsActuallyDisplayedByNativeBar',all(abs(actual-expected)<=3 for actual,expected in zip(pixel,[17,193,71])),point=point,pixel=pixel,screenshotSHA256=host.digest(gpu_png))
   check('webgpuCapabilityHasExplicitResult',gpu['webgpu']['status'] in ['unavailable','no-adapter','executed','failed'],webgpu=gpu['webgpu'],secureContext=gpu['secureContext'])
   check('secureOriginAndSandboxRemainEnabled',gpu['secureContext'] is True and 'sandbox=1' in (OUTPUT/'elm-webview.log').read_text(errors='replace'))
   sys.path.insert(0,str(ROOT/'qa'));from webgpu_claim import classify
   browser=gpu['webgpu'];report['browserWebGPU']=classify(gpu);check('browserCapabilityRecordConsistent',report['browserWebGPU']['capabilityRecordValid']);report['browserWebGPU']['scope']='API/device/compute probe only; browser render and physical adapter attribution separate'
   if browser['status']=='executed':check('webGPUComputeKnownResult',browser.get('value')==42 and browser.get('validation') is None,probe=browser)
   added=s.ctl('output','create','headless','QA-GPU-SECOND').strip();check('privateSecondGraphicsOutputCreated',added=='ok')
   wait(lambda:any(m['name']=='QA-GPU-SECOND' for m in s.data('monitors')))
   check('secondGraphicsOutputConfigured',s.ctl('eval','hl.monitor({output="QA-GPU-SECOND",mode="640x480@60",position="800x0",scale=1})').strip()=='ok')
   second_gpu=wait(lambda:gpu_observation('2'));report['secondGPU']=second_gpu
   check('secondSharedBarExecutesShader',second_gpu['webgl'].get('error')==0 and second_gpu['shaderResourcesRetired'],probe=second_gpu)
   check('privateSecondGraphicsOutputRemoved',s.ctl('output','remove','QA-GPU-SECOND').strip()=='ok');wait(lambda:len(s.data('monitors'))==1)
   sys.path.insert(0,str(ROOT/'qa'));from sampling import sample_tree,summary
   samples=[];identity=start_time(web.pid)
   for i in range(6):
    s.guard();samples.append(sample_tree(web.pid,identity));time.sleep(1 if i<5 else 0)
   report['calibration']={'samples':samples,'summary':summary(samples),'scope':'Five-second instrumented idle sampling only; no input/presentation latency, approved budgets or long-soak verdict'}
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['scope']='Current owning205/206/AQ155 runtime216, QA-only GUI521-derived WebGL/readback/native-display and optional browser WebGPU compute; no production host selection, budgets, motion, physical/hybrid displays, AT/IME or full journey acceptance'
   report['passed']=True
  finally:
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
