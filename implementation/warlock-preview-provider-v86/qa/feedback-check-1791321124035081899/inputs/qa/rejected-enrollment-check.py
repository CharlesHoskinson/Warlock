"""Compile the C rejection path and replay actual retained proof through Elm."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('rejected-check-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=ROOT.parent/'warlock-preview-provider-v65';manifest=parent/'component-manifest.json'
held=json.loads(manifest.read_text());assert held['passed']
buildPath=pathlib.Path(held['buildReport']);build=json.loads(buildPath.read_text());assert build['passed']
for name,row in held['files'].items():assert sha(parent/name)==row['sha256'],name
# The Elm production modules and native bridge remain unchanged in this
# derivative. Use the exact parent's optimized program, never inherited JS.
for folder in ['src','native','adapter','assets']:
 for p in (parent/folder).glob('*'):
  if p.is_file():assert sha(ROOT/folder/p.name)==sha(p),(folder,p.name)
for section in ['compilerDependencies','linkedLibraries','tools']:
 for path,row in build[section].items():assert sha(pathlib.Path(path))==row['sha256'],path
elm=buildPath.parent/'inputs/assets/preview-replay.js'
assert sha(elm)==build['compiledAssetPackage']['files']['preview-replay.js']
inputs={str(manifest):sha(manifest),str(buildPath):sha(buildPath),str(elm):sha(elm)}
for p in (ROOT/'native').glob('*'):
 if p.is_file():inputs[str(p)]=sha(p);target=OUT/'inputs/native'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for name in ['rejected-enrollment-check.py','rejected-enrollment-replay.js']:
 p=ROOT/'qa'/name;inputs[str(p)]=sha(p);target=OUT/'inputs/qa'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'compiledElm':{'path':str(elm),'sha256':sha(elm)},'productionUnchangedFrom':str(manifest),'claim':'Actual native C/Broker retained rejection and optimized Elm known-job/terminal ACK with a synthetic owning native socket observation fault. No compositor, physical capture pixels, whole concrete model refinement or release acceptance.'}
def run(name,argv):
 p=subprocess.run(argv,cwd=OUT/'inputs',capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 binary=OUT/'rejected-enrollment-tests'
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/rejected-enrollment-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(binary),*flags])
 run('node-syntax',['node','--check','qa/rejected-enrollment-replay.js'])
 evidence=json.loads(run('actual-c-elm-settlement',['node','qa/rejected-enrollment-replay.js',str(binary),str(elm)]))
 assert evidence['passed'] and evidence['checks']>=10 and not evidence['nativeAcceptance']
 assert all(sha(pathlib.Path(path))==value for path,value in inputs.items())
 report.update(passed=True,evidence=evidence)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
sys.exit(not report['passed'])
