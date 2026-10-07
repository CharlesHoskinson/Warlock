"""Preserve ancestor88 counterexample before changing fresh GUI89 source."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-async-ancestor88-'+str(time.time_ns()));out.mkdir()
parent=root.parent/'warlock-preview-provider-v88';m=parent/'component-manifest.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'ancestorComponent':str(m),'ancestorSHA256':sha(m),'nativeAcceptance':False,'fullReleaseAccepted':False,'inputs':{},
 'scope':'Additional cross-actor counterexample against held GUI88 compiled package; does not alter its bounded33-control component evidence. New GUI89 source has not been compiled or accepted.'}
try:
 d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld'];build=pathlib.Path(d['buildReport'])
 paths=[root/'qa/retirement-async-replay.js',root/'qa/native-source-fixture.json',build.parent/'inputs/assets/preview-replay.js']
 for p in paths:report['inputs'][str(p)]=sha(p);shutil.copy2(p,out/p.name)
 p=subprocess.run(['node',str(out/'retirement-async-replay.js'),str(out/'preview-replay.js'),str(out/'native-source-fixture.json')],capture_output=True,text=True,timeout=180)
 (out/'replay.stdout').write_text(p.stdout);(out/'replay.stderr').write_text(p.stderr);report['exitCode']=p.returncode
 assert p.returncode==0,p.stderr or p.stdout
 report['evidence']=json.loads(p.stdout);report['passed']=report['evidence']['passed']
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:700]}),flush=True);sys.exit(not report['passed'])
