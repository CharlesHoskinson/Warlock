"""Changed full bridge and optimized Elm: retained resume intent and proof."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('resume-check-'+str(time.time_ns()));OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=list(ROOT.glob('qa/build-*/report.json'));assert len(paths)==1
buildPath=paths[0];build=json.loads(buildPath.read_text());assert build['passed']
for name,value in build['inputs'].items():assert sha(ROOT/name)==value,name
for section in ['compilerDependencies','linkedLibraries','tools']:
 for name,row in build[section].items():assert sha(pathlib.Path(name))==row['sha256'],name
elm=buildPath.parent/'inputs/assets/preview-replay.js';assert sha(elm)==build['compiledAssetPackage']['files']['preview-replay.js']
inputs={str(buildPath):sha(buildPath),str(elm):sha(elm)}
for p in (ROOT/'native').glob('*'):
 if p.is_file():inputs[str(p)]=sha(p);target=OUT/'inputs/native'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for name in ['resume-enrollment-check.py','resume-enrollment-replay.js']:
 p=ROOT/'qa'/name;inputs[str(p)]=sha(p);target=OUT/'inputs/qa'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'buildReport':str(buildPath),'compiledElm':{'path':str(elm),'sha256':sha(elm)},'claim':'Actual owning C bootstrap/socket/Broker, monotonic native observation fixture and current optimized Elm. Retained resume cutoff, original receiver query guard, real issued rejection registration and exact settlement; no actual compositor or pixels.'}
def run(name,argv):
 p=subprocess.run(argv,cwd=OUT/'inputs',capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']));binary=OUT/'resume-enrollment-tests'
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/resume-enrollment-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(binary),*flags])
 cases=[]
 for mode in ['normal','resume-expire','replace-receiver']:
  d=json.loads(run(mode,[str(binary),mode]));assert d['passed'] and not d['nativeAcceptance'];cases.append(d)
 run('node-syntax',['node','--check','qa/resume-enrollment-replay.js'])
 elmEvidence=json.loads(run('actual-c-elm-rejected-resume',['node','qa/resume-enrollment-replay.js',str(binary),str(elm)]));assert elmEvidence['passed'] and elmEvidence['checks']==11
 assert all(sha(pathlib.Path(name))==value for name,value in inputs.items())
 report.update(passed=True,cases=cases,elmEvidence=elmEvidence,checks=sum(d['checks'] for d in cases)+elmEvidence['checks'])
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
