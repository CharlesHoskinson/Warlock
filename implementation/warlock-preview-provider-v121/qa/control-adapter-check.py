"""Exercise actual popup adapter singleton control ordering and exhaustion."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-adapter-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['assets/popup-adapter.js','qa/control-adapter-replay.js','qa/control-adapter-check.py']
report={'passed':False,'inputs':{name:sha(root/name) for name in names},'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name in names:
  p=out/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,p)
 p=subprocess.run(['node',str(out/'inputs/qa/control-adapter-replay.js'),str(out/'inputs/assets/popup-adapter.js')],capture_output=True,text=True,timeout=180)
 (out/'replay.stdout').write_text(p.stdout);(out/'replay.stderr').write_text(p.stderr);report['exitCode']=p.returncode
 assert p.returncode==0,p.stderr or p.stdout
 report['evidence']=json.loads(p.stdout);assert report['evidence']['passed']
 assert all(sha(root/name)==value for name,value in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:700]}),flush=True);sys.exit(not report['passed'])
