"""Verify retirement against the actual full-GUI optimized Elm package."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];out=r/'qa'/('retirement-async-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'inputs':{},'scope':'Actual optimized immutable Elm independently delivered sibling retirement; native resources and WebKit control continuity remain separate.'}
try:
 build=next(r.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for rel,value in proof['inputs'].items():assert sha(r/rel)==value,rel
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 paths=[r/'qa/retirement-async-replay.js',r/'qa/native-source-fixture.json',build.parent/'inputs/assets/preview-replay.js']
 for p in paths:report['inputs'][str(p)]=sha(p);shutil.copy2(p,out/p.name)
 p=subprocess.run(['node',str(out/'retirement-async-replay.js'),str(out/'preview-replay.js'),str(out/'native-source-fixture.json')],capture_output=True,text=True,timeout=180)
 (out/'replay.stdout').write_text(p.stdout);(out/'replay.stderr').write_text(p.stderr)
 report['exitCode']=p.returncode;assert p.returncode==0,p.stderr or p.stdout
 report['evidence']=json.loads(p.stdout);assert report['evidence']['passed'];report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:800]}),flush=True);sys.exit(not report['passed'])
