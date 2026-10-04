"""Protected actual-Elm plus actual-C retirement ordering reproduction."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('repro-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
report={'passed':False,'nativeAcceptance':False,'releaseAcceptance':False,
 'scope':'Actual compiled held Controller ordering and actual held C atomic preflight, exact recorded producer fields; no GUI, native process, socket or production change',
 'commands':[],'profiles':{},'inputs':{}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy(source,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 report['inputs'][str(source)]=sha(source)
def command(name,argv,cwd):
 p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode})
 assert p.returncode==0,p.stderr[-5000:]
 print(name,0,flush=True);return p.stdout
try:
 evidence=json.loads((ROOT/'qa/native-evidence.json').read_text())
 assert sha(evidence['sourceLog'])==evidence['sourceLogSHA256']
 failure=json.loads(Path(evidence['sourceFailureReport']).read_text());assert not failure['passed'] and failure['cleanupPassed'] and len(failure['checks'])==133
 report['nativeFailure']={'report':evidence['sourceFailureReport'],'sha256':sha(evidence['sourceFailureReport']),'logSHA256':evidence['sourceLogSHA256']}
 for label,lane,hold in [('v69','elm-menu-post-close-selection-v69','6b06b40645a8d8fa07cab93756985e4d23151a6f21f2254db7432acc893102ea'),('v87','elm-menu-staged-family-barrier-v87','c3172da2ef407113e440e27ed419ccc8e62c909ce08943c53fed16a56c4681ca')]:
  source=REPO/'implementation'/lane;manifest=source/'qa/held-source-manifest.json';assert sha(manifest)==hold
  packet=json.loads(manifest.read_text());assert packet['sourceHeld'] and packet['evidenceIntegrityPassed']
  for relative,row in packet['files'].items():assert sha(source/relative)==row['sha256'],relative
  workspace=OUT/label/'inputs';workspace.mkdir(parents=True)
  for p in [source/'elm.json',*sorted((source/'src').glob('*.elm'))]:copy(p,workspace/p.relative_to(source))
  copy(source/'src/MenuSurfaceReplay.elm',workspace/'source-worker/MenuSurfaceReplay.elm')
  for p in [ROOT/'src/MenuSurfaceReplay.elm',ROOT/'qa/repro.cjs',ROOT/'qa/native-evidence.json',Path(__file__)]:copy(p,workspace/p.relative_to(ROOT))
  binary=OUT/label/'worker.js'
  command(label+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(binary)],workspace)
  result=OUT/label/'repro.json'
  command(label+'-repro',['node',str(workspace/'qa/repro.cjs'),str(binary),str(workspace/'qa/native-evidence.json'),str(result)],workspace)
  data=json.loads(result.read_text());assert data['passed'] and data['allExplicitAssertionsCompleted']
  report['profiles'][label]={'passed':True,'result':str(result),'resultSHA256':sha(result),'sourceHoldSHA256':hold}
 native=REPO/'implementation/elm-geometry-host-carrier-v57/native';workspace=OUT/'host/inputs';workspace.mkdir(parents=True)
 for p in [native/'host.c',*sorted(native.glob('*.h'))]:copy(p,workspace/'native'/p.name)
 copy(ROOT/'qa/commit-probe.c',workspace/'qa/commit-probe.c')
 flags=shlex.split(command('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],workspace))
 binary=OUT/'host/commit-probe'
 command('actual-host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host/host.d'),'qa/commit-probe.c','-o',str(binary),*flags],workspace)
 for label in ['v69','v87']:
  text=command(label+'-actual-host-preflight',[str(binary),report['profiles'][label]['result']],workspace)
  assert json.loads(text)['passed']
 deps=shlex.split((OUT/'host/host.d').read_text().replace('\\\n',' ').split(':',1)[1])
 report['compilerDependencies']={str((workspace/p).resolve()) if not Path(p).is_absolute() else p:sha((workspace/p).resolve()) for p in deps}
 for path,wanted in report['inputs'].items():assert sha(path)==wanted,path
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
