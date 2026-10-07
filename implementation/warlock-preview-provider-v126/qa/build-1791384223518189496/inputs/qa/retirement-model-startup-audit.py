"""Retain exact failed v2 startup before any qualification command ran."""
import hashlib,json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];runner=root/'qa/retirement-delivery-model-check-v2.py';out=root/'qa'/('retirement-model-startup-failure-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=subprocess.run(['/usr/bin/python3','-B',str(runner)],capture_output=True,text=True,timeout=180)
(out/'startup.stdout').write_text(p.stdout);(out/'startup.stderr').write_text(p.stderr)
assert p.returncode==1 and 'FileNotFoundError' in p.stderr and 'retirement-delivery-model-check-v2-v2.py' in p.stderr
(out/'report.json').write_text(json.dumps({'passed':False,'recordingPassed':True,'inputs':{'qa/retirement-delivery-model-check-v2.py':sha(runner),'qa/retirement-model-startup-audit.py':sha(pathlib.Path(__file__))},'artifacts':{'startup.stdout':sha(out/'startup.stdout'),'startup.stderr':sha(out/'startup.stderr')},'startupExitCode':p.returncode,'commandsExecuted':0,'error':'Generated runner referenced nonexistent repeated v2 filename. No proof command executed. Fresh v3 corrects only runner filename.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(out/'report.json')
