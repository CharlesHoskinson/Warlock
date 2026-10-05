"""Compile independent pixel oracle and freeze exact native launch prerequisites."""
import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 old=REPO/'implementation/warlock-preview-provider-native-v2/qa/preflight.json';pre=json.loads(old.read_text());assert pre['passed']
 for path,digest in pre['inputs'].items():assert sha(path)==digest,path
 owner=REPO/'implementation/warlock-client-capture-v5';descriptor=json.loads((owner/'native-build-report.json').read_text());assert descriptor['result']=='pass'
 assert descriptor['binary']==pre['pair']['core']['path'] and descriptor['sha256']==pre['pair']['core']['sha256']
 inputs=dict(pre['inputs']);inputs[str(old)]=sha(old)
 for p in [*owner.glob('*.json'),*owner.joinpath('native').glob('*'),*owner.joinpath('candidate').glob('*'),ROOT/'fixture.py',ROOT/'pixels.cpp',*ROOT.joinpath('qa').glob('*.py')]:
  if p.is_file():inputs[str(p)]=sha(p)
 inputs[descriptor['plugin']['path']]=descriptor['plugin']['sha256'];inputs[descriptor['pluginBuildReport']]=descriptor['pluginBuildReportSHA256']
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libpng'],text=True));cmd=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(ROOT/'pixels.cpp'),'-o',str(OUT/'pixels'),*flags];result=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(OUT/'compile.stdout').write_text(result.stdout);(OUT/'compile.stderr').write_text(result.stderr);r.update(argv=cmd,exitCode=result.returncode);assert result.returncode==0,result.stderr
 pre['pair']['plugin']=descriptor['plugin'];inputs[str(OUT/'pixels')]=sha(OUT/'pixels');assert all(sha(path)==digest for path,digest in inputs.items())
 pre.update(inputs=inputs,pixelOracle=str(OUT/'pixels'),nativeLaunched=False,nativeAcceptance=False,fullReleaseAccepted=False,scope='Distinct client MAIN surface pass on owning core205/derived492/AQ155, independent PNG color/dimension/context/physical FD checks only; no eligible production capture or S09 release acceptance')
 (ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');r.update(passed=True,inputs=inputs,pair=pre['pair'])
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
