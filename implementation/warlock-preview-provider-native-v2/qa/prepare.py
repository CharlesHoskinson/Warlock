"""Build and freeze the new native probe before serial protected launch."""
import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
pre=json.loads((REPO/'implementation/elm-preview-source-native-v504/qa/preflight.json').read_text())
for path,digest in pre['inputs'].items():assert sha(path)==digest,path
for value in pre['pair'].values():assert sha(value['path'])==value['sha256']
provider=REPO/'implementation/warlock-preview-provider-v5/native'
inputs=dict(pre['inputs'])
for p in [*provider.glob('*'),ROOT/'probe.cpp',ROOT/'fixture.py',*ROOT.joinpath('qa').glob('*.py')]:
 if p.is_file():inputs[str(p)]=sha(p)
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0','gio-2.0'],text=True))
command=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(provider),str(ROOT/'probe.cpp'),str(provider/'preview-provider-bootstrap.cpp'),str(provider/'preview_uri.cpp'),'-o',str(OUT/'provider-probe'),*flags]
result=subprocess.run(command,capture_output=True,text=True,timeout=180)
(OUT/'compile.stdout').write_text(result.stdout);(OUT/'compile.stderr').write_text(result.stderr)
report={'passed':result.returncode==0,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'argv':command,'exitCode':result.returncode,'inputs':inputs}
if result.returncode==0:
 inputs[str(OUT/'provider-probe')]=sha(OUT/'provider-probe');pre.update(inputs=inputs,providerProbe=str(OUT/'provider-probe'),nativeLaunched=False,nativeAcceptance=False,fullReleaseAccepted=False)
 assert all(sha(path)==digest for path,digest in inputs.items())
 (ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(result.returncode!=0)
