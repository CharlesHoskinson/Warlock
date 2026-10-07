"""Validate adversarial boundaries and synchronous callback progress."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('native-outbox-protocol-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=['assets/native-preview-control-outbox.js','qa/native-outbox-protocol.js','qa/native-outbox-protocol-check.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 p=subprocess.run(['node','qa/native-outbox-protocol.js','assets/native-preview-control-outbox.js'],cwd=out/'inputs',capture_output=True,text=True,timeout=180)
 (out/'checks.stdout').write_text(p.stdout);(out/'checks.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 e=json.loads(p.stdout);assert e['passed'] and e['reentrantDepth']==1 and e['fullUint64BindingAndEpoch']
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items());report.update(passed=True,evidence=e)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}));sys.exit(not report['passed'])
