"""Compile real Elm fixture modules with the held GUI toolchain, in CPU QA."""
import hashlib,json,os,pathlib,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v3/qa')
import toolchain
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').glob('*.elm')};files['elm.json']=sha(ROOT/'elm.json')
shutil.copytree(ROOT/'src',OUT/'inputs/src');shutil.copy2(ROOT/'elm.json',OUT/'inputs/elm.json')
held=toolchain.verify();shutil.copytree(toolchain.ROOT/held['elmHome'],OUT/'mutable-elm-home')
report={'passed':False,'scope':scope,'inputs':files,'toolchain':held,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 command=[str(toolchain.ROOT/held['compiler']),'make','src/DesignDemo.elm','--optimize','--output='+str(OUT/'design-demo.js')]
 p=subprocess.run(command,cwd=OUT/'inputs',env=dict(os.environ,ELM_HOME=str(OUT/'mutable-elm-home')),capture_output=True,text=True,timeout=180)
 (OUT/'compile.stdout').write_text(p.stdout);(OUT/'compile.stderr').write_text(p.stderr);report['command']=command;report['exitCode']=p.returncode
 assert p.returncode==0,p.stderr or p.stdout
 toolchain.verify();assert all(sha(ROOT/rel)==value for rel,value in files.items())
 report['artifactSHA256']=sha(OUT/'design-demo.js');report['artifact']=str(OUT/'design-demo.js');report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
